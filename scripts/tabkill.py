#!/bin/env python3
"""Vivaldi Tab Killer - close tabs by pattern matching.

Uses Chrome DevTools Protocol (CDP) over HTTP to discover and close
tabs reliably. Falls back to SNSS session file parsing for discovery
if CDP is unavailable (requires Vivaldi restart with debug port).

Modes:
  (default)   Search by pattern, confirm, close matched tabs
  --others    Close every tab in the focused window except the active tab
  --window    Close the entire focused Vivaldi window (all its tabs) while
              leaving sibling Vivaldi windows of the same process alive

CDP setup: ~/.config/vivaldi-stable.conf must contain:
  --remote-debugging-port=9222
"""
import argparse
import glob
import os
import struct
import subprocess as sp
import sys
from typing import Any, Dict, List, Optional

import helpers as h
import vivaldi_base as vb


PROMPT: str = "Kill tabs:"
SESSIONS_DIR: str = os.path.expanduser("~/.config/vivaldi/Default/Sessions")


# -- SNSS fallback for tab discovery when CDP is not available --


def parse_snss_tabs(filepath: str) -> List[Dict[str, str]]:
    """Parse a Vivaldi SNSS Tabs_ file and extract tab titles and URLs.

    SNSS v3 format:
      Header: 4-byte magic 'SNSS' + 4-byte version (LE uint32)
      Commands: 2-byte size (LE uint16) + payload of that size
      Type 1 commands contain tab navigation data.
    """
    tabs: List[Dict[str, str]] = []

    try:
        with open(filepath, "rb") as f:
            magic: bytes = f.read(4)
            if magic != b"SNSS":
                return tabs

            _ = struct.unpack("<I", f.read(4))  # skip version

            while True:
                size_bytes: bytes = f.read(2)
                if len(size_bytes) < 2:
                    break

                size: int = struct.unpack("<H", size_bytes)[0]
                if size == 0 or size > 500000:
                    break

                payload: bytes = f.read(size)
                if len(payload) < size:
                    break

                cmd_type: int = payload[0]
                if cmd_type != 1 or size < 50:
                    continue

                data: bytes = payload[1:]
                try:
                    url_len: int = struct.unpack_from("<I", data, 12)[0]
                    if url_len == 0 or url_len > 10000:
                        continue

                    url: str = data[16 : 16 + url_len].decode(
                        "ascii", errors="replace"
                    )

                    title_offset: int = 16 + url_len + 2
                    if title_offset + 4 > len(data):
                        tabs.append({"id": "", "url": url, "title": url})
                        continue

                    title_len: int = struct.unpack_from(
                        "<I", data, title_offset
                    )[0]
                    if title_len == 0 or title_len > 5000:
                        tabs.append({"id": "", "url": url, "title": url})
                        continue

                    title_start: int = title_offset + 4
                    title_bytes: bytes = data[
                        title_start : title_start + title_len * 2
                    ]
                    title: str = title_bytes.decode(
                        "utf-16-le", errors="replace"
                    )

                    tabs.append({"id": "", "url": url, "title": title})
                except (struct.error, IndexError):
                    pass

    except (OSError, IOError) as e:
        h.notify_send(f"Failed to read session file: {e}", "critical")

    return tabs


def get_latest_tabs_file() -> Optional[str]:
    """Find the most recently modified Tabs_ file in Sessions dir."""
    pattern: str = os.path.join(SESSIONS_DIR, "Tabs_*")
    files: List[str] = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def dmenu_input(prompt: str, items: str = "") -> str:
    """Show a yellow-themed dmenu prompt. Returns user input or empty on cancel."""
    dmenu_command: List[str] = [
        "dmenu", "-m", "1", "-i", "-l", "20",
        "-fn", "VictorMono Nerd Font Mono:size=11",
        "-nf", "yellow", "-nb", "black",
        "-sf", "yellow", "-sb", "black",
        "-t", "Tab Killer", "-bc", "yellow",
        "-p", prompt,
    ]

    proc = sp.Popen(
        dmenu_command, stdin=sp.PIPE, stdout=sp.PIPE, text=True
    )
    output, _ = proc.communicate(input=items)

    if proc.returncode != 0:
        return ""

    return output.strip()


def get_active_tab_in_focused_window(ws_url: str) -> Optional[Dict[str, Any]]:
    """Return the currently active tab in the last-focused Vivaldi window.

    Uses chrome.tabs.query({active:true, lastFocusedWindow:true}) which
    is the source of truth Vivaldi itself uses for "the focused tab".
    Returns {id, windowId, title, url} or None on failure.
    """
    expr: str = (
        "chrome.tabs.query({active: true, lastFocusedWindow: true})"
        ".then(function(tabs) {"
        "  if (!tabs || !tabs.length) return null;"
        "  var t = tabs[0];"
        "  return {id: t.id, windowId: t.windowId,"
        "          title: t.title, url: t.url};"
        "})"
    )
    result: Any = vb.cdp_ws_evaluate(ws_url, expr)
    if isinstance(result, dict) and "id" in result:
        return result
    return None


def list_tabs_in_window(ws_url: str, window_id: int) -> List[Dict[str, Any]]:
    """Return all tabs in the given Vivaldi window via chrome.tabs.query."""
    expr: str = (
        f"chrome.tabs.query({{windowId: {int(window_id)}}})"
        ".then(function(tabs) {"
        "  return tabs.map(function(t) {"
        "    return {id: t.id, title: t.title, url: t.url,"
        "            active: t.active, pinned: t.pinned};"
        "  });"
        "})"
    )
    result: Any = vb.cdp_ws_evaluate(ws_url, expr)
    if isinstance(result, list):
        return result
    return []


def close_tabs_by_chrome_ids(ws_url: str, tab_ids: List[int]) -> int:
    """Close tabs using chrome.tabs.remove. Returns the count closed.

    chrome.tabs.remove accepts an array and removes all in one call,
    which is faster and more reliable than per-tab CDP /json/close
    requests when we already have chrome tab IDs (not CDP target IDs).
    """
    if not tab_ids:
        return 0

    import json as _json

    ids_json: str = _json.dumps([int(x) for x in tab_ids])
    expr: str = (
        f"new Promise(function(resolve) {{"
        f"  chrome.tabs.remove({ids_json}, function() {{"
        f"    if (chrome.runtime.lastError) {{"
        f"      resolve({{closed: 0, error: chrome.runtime.lastError.message}});"
        f"    }} else {{"
        f"      resolve({{closed: {len(tab_ids)}}});"
        f"    }}"
        f"  }});"
        f"}})"
    )
    result: Any = vb.cdp_ws_evaluate(ws_url, expr)
    if isinstance(result, dict):
        return int(result.get("closed", 0))
    return 0


def close_window(ws_url: str, window_id: int) -> bool:
    """Close an entire Vivaldi window via chrome.windows.remove(windowId).

    This closes the window chrome and every tab inside it. Sibling windows
    of the same Vivaldi process are unaffected -- the WebSocket / CDP path
    targets a single windowId rather than the OS process.
    """
    expr: str = (
        f"new Promise(function(resolve) {{"
        f"  chrome.windows.remove({int(window_id)}, function() {{"
        f"    if (chrome.runtime.lastError) {{"
        f"      resolve({{ok: false, error: chrome.runtime.lastError.message}});"
        f"    }} else {{"
        f"      resolve({{ok: true}});"
        f"    }}"
        f"  }});"
        f"}})"
    )
    result: Any = vb.cdp_ws_evaluate(ws_url, expr)
    if isinstance(result, dict):
        return bool(result.get("ok", False))
    return False


def cmd_window() -> None:
    """--window: close the entire focused Vivaldi window (all tabs).

    Sibling Vivaldi windows of the same process are left untouched.
    Discovery mirrors cmd_others exactly: chrome.tabs.query with
    {active:true, lastFocusedWindow:true} yields the focused windowId,
    then chrome.windows.remove(windowId) drops the whole window.
    """
    if not vb.cdp_available():
        h.notify_send(
            "CDP not available -- restart Vivaldi with debug port (9222)",
            "critical",
        )
        sys.exit(1)

    ws_url: Optional[str] = vb.find_vivaldi_ui_ws()
    if not ws_url:
        h.notify_send("Cannot find Vivaldi UI WebSocket target", "critical")
        sys.exit(1)

    active: Optional[Dict[str, Any]] = get_active_tab_in_focused_window(ws_url)
    if not active:
        h.notify_send("Could not identify focused Vivaldi window", "critical")
        sys.exit(1)

    window_id: int = int(active["windowId"])
    window_tabs: List[Dict[str, Any]] = list_tabs_in_window(ws_url, window_id)
    tab_count: int = len(window_tabs)

    # Confirm via dmenu -- show what is about to die so 30-tab windows don't
    # vanish accidentally. Empty input cancels (same convention as cmd_others).
    preview_lines: str = "\n".join(
        f"{(t.get('title') or t.get('url') or '').strip()}  |  {t.get('url', '')}"
        for t in window_tabs
    )
    active_label: str = (active.get("title") or active.get("url") or "").strip()
    confirm: str = dmenu_input(
        f"Close window ({tab_count} tab(s))? Focus: {active_label[:60]}  [Enter=yes]",
        preview_lines,
    )
    if confirm == "":
        h.notify_send("Cancelled", "low")
        return

    ok: bool = close_window(ws_url, window_id)
    if ok:
        h.notify_send(
            f"Closed window (windowId={window_id}, {tab_count} tab(s))", "low"
        )
    else:
        h.notify_send(
            f"Failed to close window windowId={window_id}", "critical"
        )
        sys.exit(1)


def cmd_others() -> None:
    """--others: close every tab in the focused window except the active tab."""
    if not vb.cdp_available():
        h.notify_send(
            "CDP not available -- restart Vivaldi with debug port (9222)",
            "critical",
        )
        sys.exit(1)

    ws_url: Optional[str] = vb.find_vivaldi_ui_ws()
    if not ws_url:
        h.notify_send("Cannot find Vivaldi UI WebSocket target", "critical")
        sys.exit(1)

    active: Optional[Dict[str, Any]] = get_active_tab_in_focused_window(ws_url)
    if not active:
        h.notify_send("Could not identify focused tab", "critical")
        sys.exit(1)

    window_tabs: List[Dict[str, Any]] = list_tabs_in_window(
        ws_url, int(active["windowId"])
    )
    if not window_tabs:
        h.notify_send("No tabs found in focused window", "critical")
        sys.exit(1)

    active_id: int = int(active["id"])
    victims: List[Dict[str, Any]] = [
        t for t in window_tabs if int(t.get("id", -1)) != active_id
    ]

    if not victims:
        h.notify_send("Only one tab in this window -- nothing to close", "low")
        return

    # Confirm via dmenu list so the user can see what is about to die
    preview_lines: str = "\n".join(
        f"{(t.get('title') or t.get('url') or '').strip()}  |  {t.get('url', '')}"
        for t in victims
    )
    keep_label: str = (active.get("title") or active.get("url") or "").strip()
    confirm: str = dmenu_input(
        f"Close {len(victims)} tab(s)? Keep: {keep_label[:60]}  [Enter=yes]",
        preview_lines,
    )
    if confirm == "":
        h.notify_send("Cancelled", "low")
        return

    victim_ids: List[int] = [int(t["id"]) for t in victims]
    closed: int = close_tabs_by_chrome_ids(ws_url, victim_ids)

    msg: str = f"Closed {closed}/{len(victim_ids)} tab(s); kept: {keep_label[:60]}"
    h.notify_send(msg, "low")


def parse_args() -> argparse.Namespace:
    """Parse CLI flags."""
    parser = argparse.ArgumentParser(
        description="Vivaldi Tab Killer - close tabs by pattern or invert-focus",
    )
    parser.add_argument(
        "-o", "--others",
        action="store_true",
        help="Close every tab in the focused window EXCEPT the active tab",
    )
    parser.add_argument(
        "-W", "--window",
        action="store_true",
        help="Close the entire focused Vivaldi window (all its tabs); "
             "sibling Vivaldi windows are unaffected",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point: search for tabs by pattern and close matches via CDP."""
    args: argparse.Namespace = parse_args()

    if args.window:
        cmd_window()
        return

    if args.others:
        cmd_others()
        return

    use_cdp: bool = vb.cdp_available()

    if use_cdp:
        raw_tabs: List[Dict[str, str]] = vb.cdp_list_tabs()
        if not raw_tabs:
            h.notify_send("CDP connected but no tabs found", "critical")
            sys.exit(1)
    else:
        # Fall back to SNSS parsing for discovery only
        tabs_file: Optional[str] = get_latest_tabs_file()
        if not tabs_file:
            h.notify_send("No Vivaldi session files found", "critical")
            sys.exit(1)

        raw_tabs = parse_snss_tabs(tabs_file)
        if not raw_tabs:
            h.notify_send("No tabs found in session file", "critical")
            sys.exit(1)

    tabs: List[Dict[str, str]] = vb.deduplicate_tabs(raw_tabs)

    # Step 1: Plain text input -- user types a pattern (e.g. "datadog")
    search_term: str = dmenu_input(PROMPT)
    if not search_term:
        h.notify_send("Cancelled", "low")
        sys.exit(1)

    matched: List[Dict[str, str]] = vb.match_tabs(tabs, search_term)

    if not matched:
        h.notify_send(f'No tabs matching "{search_term}"', "low")
        sys.exit(0)

    # Step 2: Show matches, confirm with Enter or cancel with Escape
    confirm_lines: str = "\n".join(vb.format_tab_line(t) for t in matched)
    confirm: str = dmenu_input(
        f"Close {len(matched)} tab(s)?  [Enter=yes]", confirm_lines
    )
    if confirm == "":
        h.notify_send("Cancelled", "low")
        sys.exit(0)

    if not use_cdp:
        h.notify_send(
            f'Found {len(matched)} match(es) but cannot close tabs: '
            f'restart Vivaldi to enable debug port (9222)',
            "critical",
        )
        sys.exit(1)

    # Close matched tabs via CDP
    closed: int = 0
    failed: int = 0
    for tab in matched:
        tab_id: str = tab.get("id", "")
        if not tab_id:
            failed += 1
            continue
        if vb.cdp_close_tab(tab_id):
            closed += 1
        else:
            failed += 1

    msg: str = f'Closed {closed}/{len(matched)} tab(s) matching "{search_term}"'
    if failed > 0:
        msg += f" ({failed} failed)"
    h.notify_send(msg, "low")



if __name__ == "__main__":
    main()
