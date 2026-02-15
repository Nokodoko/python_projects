#!/bin/env python3
"""Vivaldi base module - shared CDP and dmenu utilities.

Provides Chrome DevTools Protocol helpers, tab management functions,
and Vivaldi-themed dmenu wrappers for use by all Vivaldi scripts.

CDP setup: ~/.config/vivaldi-stable.conf must contain:
  --remote-debugging-port=9222
"""
import base64
import json
import os
import socket
import struct
import subprocess as sp
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


# -- CDP constants --

CDP_PORT: int = 9222
CDP_HOST: str = "localhost"
CDP_BASE: str = f"http://{CDP_HOST}:{CDP_PORT}"

# Vivaldi UI extension ID (stable across installations)
VIVALDI_EXT_ID: str = "mpognobbkildjkofajifpdfhcoklimli"


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


def cdp_activate_tab(tab_id: str) -> bool:
    """Bring a tab to the foreground by its CDP target ID. Returns True on success."""
    body: Optional[str] = cdp_get(f"/json/activate/{tab_id}")
    if body is None:
        return False
    return "Target activated" in body


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


# -- CDP WebSocket helpers --


def _ws_connect(ws_url: str) -> socket.socket:
    """Open a raw WebSocket connection to a CDP target.

    Parses ws://host:port/path from ws_url, performs the HTTP upgrade
    handshake, and returns the connected socket ready for framing.
    """
    # Parse ws://host:port/path
    stripped: str = ws_url.replace("ws://", "")
    host_port, _, path = stripped.partition("/")
    host, _, port_str = host_port.partition(":")
    port: int = int(port_str) if port_str else 80
    path = "/" + path

    key: str = base64.b64encode(os.urandom(16)).decode()
    sock: socket.socket = socket.create_connection((host, port), timeout=5)
    request: str = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    )
    sock.sendall(request.encode())

    # Consume the HTTP 101 response
    response: bytes = b""
    while b"\r\n\r\n" not in response:
        response += sock.recv(4096)

    return sock


def _ws_send(sock: socket.socket, msg: str) -> None:
    """Send a text frame over a WebSocket connection (client-masked)."""
    data: bytes = msg.encode("utf-8")
    frame: bytearray = bytearray([0x81])  # FIN + text opcode
    mask_key: bytes = os.urandom(4)
    length: int = len(data)

    if length < 126:
        frame.append(0x80 | length)
    elif length < 65536:
        frame.append(0x80 | 126)
        frame.extend(struct.pack(">H", length))
    else:
        frame.append(0x80 | 127)
        frame.extend(struct.pack(">Q", length))

    frame.extend(mask_key)
    frame.extend(
        bytearray(data[i] ^ mask_key[i % 4] for i in range(length))
    )
    sock.sendall(frame)


def _ws_recv(sock: socket.socket) -> str:
    """Read one WebSocket text frame and return the payload as a string."""
    header: bytes = sock.recv(2)
    length: int = header[1] & 0x7F

    if length == 126:
        length = struct.unpack(">H", sock.recv(2))[0]
    elif length == 127:
        length = struct.unpack(">Q", sock.recv(8))[0]

    data: bytes = b""
    while len(data) < length:
        data += sock.recv(length - len(data))

    return data.decode("utf-8")


def find_vivaldi_ui_ws() -> Optional[str]:
    """Find the Vivaldi UI page WebSocket URL from CDP targets.

    Scans /json for the target of type "app" whose URL belongs to the
    Vivaldi extension (window.html). Returns the webSocketDebuggerUrl
    or None if not found.
    """
    body: Optional[str] = cdp_get("/json")
    if body is None:
        return None

    try:
        for target in json.loads(body):
            if (
                target.get("type") == "app"
                and VIVALDI_EXT_ID in target.get("url", "")
                and "window.html" in target.get("url", "")
            ):
                return target.get("webSocketDebuggerUrl")
    except (json.JSONDecodeError, KeyError):
        pass

    return None


def cdp_ws_evaluate(ws_url: str, expression: str) -> Any:
    """Evaluate a JS expression via CDP WebSocket and return the result.

    Sends Runtime.evaluate with awaitPromise=True so both sync and
    async (Promise-returning) expressions work. Returns the unwrapped
    value on success, or None on failure.
    """
    sock: Optional[socket.socket] = None
    try:
        sock = _ws_connect(ws_url)
        msg: str = json.dumps({
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True,
            },
        })
        _ws_send(sock, msg)
        raw: str = _ws_recv(sock)
        parsed: Dict = json.loads(raw)
        return (
            parsed.get("result", {})
            .get("result", {})
            .get("value")
        )
    except (OSError, TimeoutError, json.JSONDecodeError, struct.error):
        return None
    finally:
        if sock is not None:
            sock.close()


if __name__ == "__main__":
    pass
