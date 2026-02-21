# agentic_instructions.md — python_projects/scripts

## Purpose
Desktop automation scripts for Arch Linux: Vivaldi browser tab management via CDP, process management, password utilities, keyboard brightness control, wallpaper fetching, and various system utilities.

## Technology
- Language: Python 3
- Libraries: subprocess, json, argparse, websocket, requests
- Protocols: Chrome DevTools Protocol (CDP) via WebSocket
- External tools: fzf, gum, dmenu, wezterm, xdotool, wmctrl, notify-send
- Browser: Vivaldi (with remote debugging port 9222)

## Contents
- `tabTiler.py` — Vivaldi tab tiler: CDP-based tab selection, stacking, tiling, and untiling via React component handlers. Self-respawns in wezterm for floating window picker.
- `tabkill.py` — Tab/process killer using CDP + fzf selection.
- `vivaldi_base.py` — Base CDP client for Vivaldi: WebSocket connection, JS evaluation, tab queries.
- `vivaldi_leader.py` — Vivaldi leader key integration.
- `killer.py` — System process killer with fzf/dmenu selection.
- `helpers.py` — Shared helpers: dmenu wrapper, notify-send wrapper.
- `pass.py` — Password manager integration with dmenu/fzf selection.
- `genpass.py` — Password generator utility.
- `keybrightnessUp.py` / `keybrightnessDown.py` — Keyboard LED brightness control scripts.
- `wallhaven.py` — Wallhaven API wallpaper fetcher.
- `gitup.py` — Bulk git pull/push across multiple repositories.
- `jokes.py` — Joke API client.
- `perplexity.py` / `perplexity_annotated.py` — Perplexity AI client.
- `gcsearch.py` — Google Cloud search utility.
- `something.py` — Miscellaneous utility.

## Key Functions
- `tabTiler.py` — Full tab lifecycle: list tabs via CDP, gum multi-select, create tab stacks, tile with layout selection.
- `vivaldi_base.py` — CDP WebSocket client: connect, evaluate JS, query DOM, manage tabs.
- `killer.py` — Lists processes via `ps`, pipes to fzf/dmenu, kills selected PID.
- `helpers.py::dmenu(color, prompt) -> str` — Styled dmenu launcher.
- `helpers.py::notify_send(msg, criticality) -> str|None` — Desktop notification.

## Data Types
- Tab objects from CDP (id, title, url, windowId).
- WebSocket message JSON for CDP commands.

## Logging
- `print()` for output.
- File-based debug logging in tabTiler.py (`/tmp/tabtiler-debug.log`).
- notify-send for user notifications.

## CRUD Entry Points
- **Run**: `python3 <script>.py [args]`
- **tabTiler modes**: `--list`, `--untile`, `--stack`, `--switch`
- **Config**: Vivaldi must have `--remote-debugging-port=9222` in vivaldi-stable.conf.

## Style Guide
- Type annotations on all function signatures
- `argparse` for complex CLIs, `sys.argv` for simple ones
- `subprocess.Popen` with `communicate()` pattern
- CDP WebSocket protocol for browser automation
- Self-respawn pattern for floating terminal windows
- Constants as module-level UPPER_SNAKE_CASE

```python
TILE_MODES: Dict[str, str] = {
    "grid": "Tile to grid",
    "vertical": "Tile vertically",
    "horizontal": "Tile horizontally",
}
```
