#!/bin/env python3
"""Vivaldi Tab Killer - close tabs by pattern matching.

Uses Chrome DevTools Protocol (CDP) over HTTP to discover and close
tabs reliably. Falls back to SNSS session file parsing for discovery
if CDP is unavailable (requires Vivaldi restart with debug port).

CDP setup: ~/.config/vivaldi-stable.conf must contain:
  --remote-debugging-port=9222
"""
import glob
import os
import struct
import subprocess as sp
import sys
from typing import Dict, List, Optional

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
