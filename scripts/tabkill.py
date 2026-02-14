#!/bin/env python3
"""Vivaldi Tab Killer - close tabs by pattern matching.

Uses Chrome DevTools Protocol (CDP) over HTTP to discover and close
tabs reliably. Falls back to SNSS session file parsing for discovery
if CDP is unavailable (requires Vivaldi restart with debug port).

CDP setup: ~/.config/vivaldi-stable.conf must contain:
  --remote-debugging-port=9222
"""
import glob
import json
import os
import struct
import subprocess as sp
import sys
import urllib.error
import urllib.request
from typing import Dict, List, Optional

import helpers as h


CDP_PORT: int = 9222
CDP_BASE: str = f"http://localhost:{CDP_PORT}"
PROMPT: str = "Kill tabs:"
SESSIONS_DIR: str = os.path.expanduser("~/.config/vivaldi/Default/Sessions")


def cdp_get(path: str) -> Optional[str]:
    """HTTP GET to the CDP endpoint. Returns body text or None on failure."""
    try:
        req = urllib.request.Request(f"{CDP_BASE}{path}")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, OSError, TimeoutError):
        return None


def cdp_available() -> bool:
    """Check if the CDP debug port is accepting connections."""
    return cdp_get("/json/version") is not None


def cdp_list_tabs() -> List[Dict[str, str]]:
    """Fetch open tabs from Vivaldi via CDP. Returns list of {id, title, url}."""
    body: Optional[str] = cdp_get("/json")
    if body is None:
        return []

    tabs: List[Dict[str, str]] = []
    try:
        entries = json.loads(body)
        for entry in entries:
            if entry.get("type") != "page":
                continue
            tabs.append({
                "id": entry.get("id", ""),
                "title": entry.get("title", ""),
                "url": entry.get("url", ""),
            })
    except (json.JSONDecodeError, KeyError):
        pass

    return tabs


def cdp_close_tab(tab_id: str) -> bool:
    """Close a tab by its CDP target ID. Returns True on success."""
    body: Optional[str] = cdp_get(f"/json/close/{tab_id}")
    if body is None:
        return False
    return "Target is closing" in body


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


# -- shared logic --


def deduplicate_tabs(tabs: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate tabs and filter out empty/blank entries."""
    seen: set = set()
    unique: List[Dict[str, str]] = []

    for tab in tabs:
        title: str = tab["title"].strip()
        url: str = tab["url"].strip()

        if not title and not url:
            continue
        if url in ("about:blank", "chrome://vivaldi-webui/startpage"):
            continue

        key: str = f"{title}|{url}"
        if key in seen:
            continue
        seen.add(key)
        unique.append({"id": tab.get("id", ""), "title": title, "url": url})

    return unique


def match_tabs(
    tabs: List[Dict[str, str]], pattern: str
) -> List[Dict[str, str]]:
    """Return tabs whose title or URL matches the pattern (case-insensitive)."""
    pattern_lower: str = pattern.lower()
    matched: List[Dict[str, str]] = []

    for tab in tabs:
        title_lower: str = tab["title"].lower()
        url_lower: str = tab["url"].lower()
        if pattern_lower in title_lower or pattern_lower in url_lower:
            matched.append(tab)

    return matched


def format_tab_line(tab: Dict[str, str]) -> str:
    """Format a tab for display in dmenu: title | url."""
    title: str = tab["title"]
    url: str = tab["url"]

    if title and title != url:
        return f"{title}  |  {url}"
    return url


def dmenu_input(prompt: str, items: str = "") -> str:
    """Show a yellow-themed dmenu prompt. Returns user input or empty on cancel."""
    dmenu_command: List[str] = [
        "dmenu", "-m", "0", "-i", "-l", "20",
        "-fn", "VictorMono:size=20",
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


def main() -> None:
    """Entry point: search for tabs by pattern and close matches via CDP."""
    use_cdp: bool = cdp_available()

    if use_cdp:
        raw_tabs: List[Dict[str, str]] = cdp_list_tabs()
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

    tabs: List[Dict[str, str]] = deduplicate_tabs(raw_tabs)

    # Step 1: Plain text input — user types a pattern (e.g. "datadog")
    search_term: str = dmenu_input(PROMPT)
    if not search_term:
        h.notify_send("Cancelled", "low")
        sys.exit(1)

    matched: List[Dict[str, str]] = match_tabs(tabs, search_term)

    if not matched:
        h.notify_send(f'No tabs matching "{search_term}"', "low")
        sys.exit(0)

    # Step 2: Show matches, confirm with Enter or cancel with Escape
    confirm_lines: str = "\n".join(format_tab_line(t) for t in matched)
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
        if cdp_close_tab(tab_id):
            closed += 1
        else:
            failed += 1

    msg: str = f'Closed {closed}/{len(matched)} tab(s) matching "{search_term}"'
    if failed > 0:
        msg += f" ({failed} failed)"
    h.notify_send(msg, "low")



if __name__ == "__main__":
    main()
