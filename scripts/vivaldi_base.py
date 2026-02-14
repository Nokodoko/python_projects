#!/bin/env python3
"""Vivaldi base module - shared CDP and dmenu utilities.

Provides Chrome DevTools Protocol helpers, tab management functions,
and Vivaldi-themed dmenu wrappers for use by all Vivaldi scripts.

CDP setup: ~/.config/vivaldi-stable.conf must contain:
  --remote-debugging-port=9222
"""
import json
import subprocess as sp
import urllib.error
import urllib.request
from typing import Dict, List, Optional


# -- CDP constants --

CDP_PORT: int = 9222
CDP_BASE: str = f"http://localhost:{CDP_PORT}"


# -- dmenu theming --

DMENU_FONT: str = "VictorMono Nerd Font Mono:size=11"
VIVALDI_FG: str = "#EF3939"
VIVALDI_BG: str = "black"


# -- CDP helpers --


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


# -- tab utilities --


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


# -- dmenu helpers --


def dmenu_vivaldi(prompt: str, items: str = "") -> str:
    """Show a Vivaldi-themed (red) dmenu prompt. Returns user input or empty on cancel."""
    dmenu_command: List[str] = [
        "dmenu", "-m", "0", "-i", "-l", "20",
        "-fn", DMENU_FONT,
        "-nf", VIVALDI_FG, "-nb", VIVALDI_BG,
        "-sf", VIVALDI_FG, "-sb", VIVALDI_BG,
        "-p", prompt,
    ]

    proc = sp.Popen(
        dmenu_command, stdin=sp.PIPE, stdout=sp.PIPE, text=True
    )
    output, _ = proc.communicate(input=items)

    if proc.returncode != 0:
        return ""

    return output.strip()


if __name__ == "__main__":
    pass
