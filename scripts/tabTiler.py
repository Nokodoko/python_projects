#!/bin/env python3
"""Vivaldi Tab Tiler - select, stack, tile, and untile tabs in Vivaldi.

Lists open Vivaldi tabs, presents a multi-select picker via gum
inside a floating wezterm window, then highlights the selected tabs
in Vivaldi and triggers tiling via React component handlers.

Modes:
  (default)   Pick tabs -> pick layout -> stack selected tabs -> tile
  --list      Show currently tiled tabs, optionally re-tile them
  --untile    Remove current tiling
  --stack     Pick tabs -> create a new Vivaldi tab stack
  --switch    List existing tab stacks and switch to a selected one

Self-respawn pattern: when launched without a TTY (e.g. from a DWM
keybinding), the script re-execs itself inside wezterm. When running
inside wezterm (with a TTY), it proceeds with the interactive picker.

CDP setup: ~/.config/vivaldi-stable.conf must contain:
  --remote-debugging-port=9222
"""
import argparse
import json
import os
import shlex
import subprocess as sp
import sys
import tempfile
import time
import uuid
from typing import Any, Dict, List, Optional


import helpers as h
import vivaldi_base as vb


TILE_MODES: Dict[str, str] = {
    "grid": "Tile to grid",
    "vertical": "Tile vertically",
    "horizontal": "Tile horizontally",
}
DEFAULT_TILE_MODE: str = "grid"
VIVALDI_WM_CLASS: str = "vivaldi-stable"
WEZTERM_CLASS: str = "wezterm-tabtiler"
SCRIPT_PATH: str = os.path.abspath(__file__)
LOG_FILE: str = "/tmp/tabtiler-debug.log"


def _log(msg: str) -> None:
    """Append a debug line to the persistent log file."""
    with open(LOG_FILE, "a") as f:
        f.write(f"{msg}\n")


def respawn_in_wezterm() -> None:
    """Re-exec this script inside a floating wezterm window.

    Passes through all CLI arguments so flags like --list, --untile,
    --stack work when launched from a DWM keybinding.
    """
    os.execvp("wezterm", [
        "wezterm", "start", "--always-new-process",
        "--class", WEZTERM_CLASS,
        "--", "python3", SCRIPT_PATH, *sys.argv[1:],
    ])


# -- CDP tab queries --


def get_chrome_tabs(ws_url: str) -> Optional[List[Dict[str, Any]]]:
    """Query chrome.tabs.query({}) via the Vivaldi UI WebSocket.

    Returns a list of {id, index, windowId, title, url, vivExtData} dicts,
    or None on failure.  vivExtData is parsed from JSON into a dict.
    """
    expr: str = (
        "chrome.tabs.query({}).then(function(tabs) {"
        "  return tabs.map(function(t) {"
        "    var ext = {};"
        "    try { ext = JSON.parse(t.vivExtData || '{}'); } catch(e) {}"
        "    return {id: t.id, index: t.index, windowId: t.windowId,"
        "            title: t.title, url: t.url, vivExtData: ext};"
        "  });"
        "})"
    )
    result: Any = vb.cdp_ws_evaluate(ws_url, expr)
    if isinstance(result, list):
        return result
    return None


def get_tiled_tabs(ws_url: str) -> List[Dict[str, Any]]:
    """Return currently tiled tabs with their tiling metadata.

    Reads the TilingToggle React component state for the active tileId,
    then finds all pages whose vivExtData.tiling.id matches.
    Returns list of {id, title, url, tiling: {id, index, layout, type}}.
    """
    result: Any = vb.cdp_ws_evaluate(ws_url, '''
    (function() {
        var btn = document.querySelector("button[name=TilingToggle]");
        if (!btn) return {error: "no TilingToggle"};
        var fiberKey = Object.keys(btn).find(function(k) {
            return k.startsWith("__reactFiber");
        });
        var f = btn[fiberKey];
        for (var i = 0; i < 5; i++) f = f.return;
        var tileId = f.stateNode.state.tileId;
        if (!tileId) return {tiledTabs: [], tileId: null};

        var tabStrip = document.querySelector(".tab-strip");
        if (!tabStrip) return {error: "no tab-strip"};
        var fk2 = Object.keys(tabStrip).find(function(k) {
            return k.startsWith("__reactFiber");
        });
        var f2 = tabStrip[fk2];
        for (var d = 0; d < 10; d++) {
            if (f2.stateNode && f2.stateNode.handleClick) break;
            f2 = f2.return;
            if (!f2) return {error: "no handleClick"};
        }
        var pages = f2.stateNode.props.pages;
        var pagesSize = pages.size || pages.length || 0;
        var tiled = [];
        for (var i = 0; i < pagesSize; i++) {
            var page = pages.get ? pages.get(i) : pages[i];
            var ext = page.vivExtData || {};
            if (ext.tiling && ext.tiling.id === tileId) {
                tiled.push({
                    id: page.id, title: page.title || "",
                    url: page.url || "", tiling: ext.tiling
                });
            }
        }
        return {tiledTabs: tiled, tileId: tileId};
    })()
    ''')

    if isinstance(result, dict) and "tiledTabs" in result:
        return result["tiledTabs"]
    return []


# -- Vivaldi tab selection via React --


def select_tabs_vivaldi(ws_url: str, tab_urls: List[str]) -> bool:
    """Select tabs using Vivaldi's internal React tab selection API.

    chrome.tabs.highlight() doesn't update Vivaldi's internal selection
    state, so tiling only acts on 2 tabs. Instead, we access the tab
    strip React component and call handleClick to simulate ctrl+click
    multi-selection that Vivaldi's tiling system recognizes.
    """
    urls_json: str = json.dumps(tab_urls)
    expr: str = f'''
    (function() {{
        var tabStrip = document.querySelector('.tab-strip');
        if (!tabStrip) return {{error: 'no tab-strip element'}};

        var fiberKey = Object.keys(tabStrip).find(function(k) {{
            return k.startsWith('__reactFiber');
        }});
        if (!fiberKey) return {{error: 'no react fiber'}};

        // Walk up the fiber tree to find the component with handleClick
        var f = tabStrip[fiberKey];
        for (var depth = 0; depth < 10; depth++) {{
            if (f.stateNode && f.stateNode.handleClick) break;
            f = f.return;
            if (!f) return {{error: 'no handleClick found within 10 levels'}};
        }}
        var component = f.stateNode;
        if (!component || !component.handleClick) {{
            return {{error: 'component missing handleClick'}};
        }}

        var pages = component.props.pages;
        if (!pages) return {{error: 'no pages prop'}};

        var targetUrls = {urls_json};
        var matched = [];
        var usedIndices = {{}};

        // Match pages by URL, preserving selection order
        for (var u = 0; u < targetUrls.length; u++) {{
            var pagesSize = pages.size || pages.length || 0;
            for (var idx = 0; idx < pagesSize; idx++) {{
                if (usedIndices[idx]) continue;
                var page = pages.get ? pages.get(idx) : pages[idx];
                if (page && page.url === targetUrls[u]) {{
                    matched.push(page);
                    usedIndices[idx] = true;
                    break;
                }}
            }}
        }}

        if (matched.length < 2) {{
            var samplePage = pages.get ? pages.get(0) : pages[0];
            var pageKeys = samplePage ? Object.keys(samplePage).slice(0, 10) : [];
            return {{
                error: 'matched ' + matched.length + '/' + targetUrls.length,
                pagesSize: pages.size || pages.length || 0,
                sampleKeys: pageKeys,
                firstTargetUrl: targetUrls[0]
            }};
        }}

        // First tab: plain click (replaces current selection)
        component.handleClick(matched[0], {{
            ctrlKey: false, shiftKey: false, metaKey: false
        }});

        // Remaining tabs: ctrl+click to add to selection
        for (var i = 1; i < matched.length; i++) {{
            component.handleClick(matched[i], {{
                ctrlKey: true, shiftKey: false, metaKey: false
            }});
        }}

        return {{selected: matched.length}};
    }})()
    '''
    result: Any = vb.cdp_ws_evaluate(ws_url, expr)
    _log(f"select_tabs_vivaldi result: {result}")

    if isinstance(result, dict):
        if "error" in result:
            _log(f"select_tabs_vivaldi error: {result}")
            return False
        return result.get("selected", 0) >= 2
    return False


# -- Tiling via CDP --


def untile_via_cdp(ws_url: str) -> bool:
    """Untile any currently tiled tabs. Returns True if something was untiled."""
    _log("untiling existing tiles")
    result: Any = vb.cdp_ws_evaluate(ws_url, '''
    (function() {
        var btn = document.querySelector("button[name=TilingToggle]");
        if (!btn) return {untiled: false, reason: "no button"};
        var fiberKey = Object.keys(btn).find(function(k) {
            return k.startsWith("__reactFiber");
        });
        var f = btn[fiberKey];
        for (var i = 0; i < 5; i++) f = f.return;
        var component = f.stateNode;
        if (component.state.tileId) {
            component.untile();
            return {untiled: true};
        }
        return {untiled: false, reason: "no active tiling"};
    })()
    ''')
    if isinstance(result, dict):
        return result.get("untiled", False)
    return False


def send_tile_via_cdp(ws_url: str, mode: str = DEFAULT_TILE_MODE) -> bool:
    """Tile tabs by calling Vivaldi's React tile button handler via CDP.

    Keyboard shortcuts and synthetic events don't reach Vivaldi's tiling
    system. Instead, we open the Page Tiling popup in the status bar,
    find the matching button, and call its onMouseUp React handler directly.
    """
    btn_title: str = TILE_MODES.get(mode, TILE_MODES[DEFAULT_TILE_MODE])
    _log(f"tile via CDP: mode={mode} btn_title={btn_title}")

    # Untile any existing tiling first
    untile_via_cdp(ws_url)
    time.sleep(0.15)

    # Open the tiling popup by setting React component state
    vb.cdp_ws_evaluate(ws_url, '''
    (function() {
        var btn = document.querySelector("button[name=TilingToggle]");
        if (!btn) return;
        var fiberKey = Object.keys(btn).find(function(k) {
            return k.startsWith("__reactFiber");
        });
        var f = btn[fiberKey];
        for (var i = 0; i < 5; i++) f = f.return;
        f.stateNode.setState({drawerOpen: true});
    })()
    ''')
    time.sleep(0.1)  # let popup render

    # Call the matching tile button's onMouseUp handler
    expr: str = f'''
    (function() {{
        var buttons = document.querySelectorAll(".PageTiling-Button");
        var target = null;
        buttons.forEach(function(btn) {{
            if (btn.getAttribute("title") === "{btn_title}") target = btn;
        }});
        if (!target) return "no button: {btn_title}";
        var propsKey = Object.keys(target).find(function(k) {{
            return k.startsWith("__reactProps");
        }});
        var props = target[propsKey];
        if (!props || !props.onMouseUp) return "no onMouseUp";
        props.onMouseUp({{
            type: "mouseup", button: 0,
            target: target, currentTarget: target,
            preventDefault: function(){{}},
            stopPropagation: function(){{}}
        }});
        return true;
    }})()
    '''
    result: Any = vb.cdp_ws_evaluate(ws_url, expr)
    _log(f"tile result: {result}")

    # Close the popup
    vb.cdp_ws_evaluate(ws_url, '''
    (function() {
        var btn = document.querySelector("button[name=TilingToggle]");
        if (!btn) return;
        var fiberKey = Object.keys(btn).find(function(k) {
            return k.startsWith("__reactFiber");
        });
        var f = btn[fiberKey];
        for (var i = 0; i < 5; i++) f = f.return;
        f.stateNode.setState({drawerOpen: false});
    })()
    ''')

    return result is True


# -- Tab stacking via vivExtData.group --


def create_tab_stack(ws_url: str, tab_ids: List[int]) -> Optional[str]:
    """Create a Vivaldi tab stack from the given tab IDs.

    Sets vivExtData.group to a shared UUID on each tab via chrome.tabs.update,
    then moves tabs to be adjacent so Vivaldi recognizes the stack.
    Returns the group UUID on success, None on failure.
    """
    if len(tab_ids) < 2:
        _log("create_tab_stack: need at least 2 tabs")
        return None

    group_id: str = str(uuid.uuid4())
    tab_ids_json: str = json.dumps(tab_ids)
    _log(f"creating tab stack: group={group_id} tabs={tab_ids}")

    expr: str = f'''
    (function() {{
        var tabIds = {tab_ids_json};
        var groupId = "{group_id}";
        var errors = [];
        var done = 0;

        return new Promise(function(resolve) {{
            // First, get current vivExtData for each tab and set group
            tabIds.forEach(function(tabId) {{
                chrome.tabs.get(tabId, function(tab) {{
                    if (chrome.runtime.lastError) {{
                        errors.push({{id: tabId, error: chrome.runtime.lastError.message}});
                        done++;
                        if (done === tabIds.length) resolve({{errors: errors, grouped: done - errors.length}});
                        return;
                    }}
                    var extData = {{}};
                    try {{ extData = JSON.parse(tab.vivExtData || "{{}}"); }} catch(e) {{}}
                    extData.group = groupId;
                    chrome.tabs.update(tabId, {{vivExtData: JSON.stringify(extData)}}, function() {{
                        if (chrome.runtime.lastError) {{
                            errors.push({{id: tabId, error: chrome.runtime.lastError.message}});
                        }}
                        done++;
                        if (done === tabIds.length) {{
                            // After grouping, move tabs to be adjacent
                            // Get the index of the first tab to anchor the stack
                            chrome.tabs.get(tabIds[0], function(firstTab) {{
                                if (chrome.runtime.lastError || !firstTab) {{
                                    resolve({{errors: errors, grouped: done - errors.length, groupId: groupId}});
                                    return;
                                }}
                                var baseIndex = firstTab.index;
                                var movesDone = 0;
                                // Move remaining tabs next to the first one
                                for (var i = 1; i < tabIds.length; i++) {{
                                    chrome.tabs.move(tabIds[i], {{index: baseIndex + i}}, function() {{
                                        movesDone++;
                                        if (movesDone === tabIds.length - 1) {{
                                            resolve({{errors: errors, grouped: done - errors.length, groupId: groupId}});
                                        }}
                                    }});
                                }}
                                if (tabIds.length === 1) {{
                                    resolve({{errors: errors, grouped: done - errors.length, groupId: groupId}});
                                }}
                            }});
                        }}
                    }});
                }});
            }});
        }});
    }})()
    '''
    result: Any = vb.cdp_ws_evaluate(ws_url, expr)
    _log(f"create_tab_stack result: {result}")

    if isinstance(result, dict):
        if result.get("errors"):
            _log(f"create_tab_stack errors: {result['errors']}")
        if result.get("grouped", 0) >= 2:
            return group_id
    return None


# -- gum pickers --


def format_picker_line(tab: Dict[str, Any]) -> str:
    """Format a tab for the gum picker: title  |  url."""
    title: str = tab.get("title", "")
    url: str = tab.get("url", "")

    if title and title != url:
        return f"{title}  |  {url}"
    return url


SELECT_ALL_SENTINEL: str = "⟐ [Select All]"
UNSELECT_ALL_SENTINEL: str = "⟐ [Unselect All]"


def _run_gum_filter(
    tmp_path: str,
    header: str,
    *,
    no_limit: bool = True,
    pre_selected: Optional[List[str]] = None,
) -> List[str]:
    """Low-level gum filter invocation on a temp file.

    Returns the list of selected lines (may be empty on cancel/timeout).
    When pre_selected is provided, those specific items start selected.
    """
    flags: str = "--no-limit" if no_limit else ""
    if pre_selected:
        for item in pre_selected:
            flags += f" --selected={shlex.quote(item)}"

    shell_cmd: str = (
        f"cat '{tmp_path}' | "
        f"gum filter {flags} --height=20 "
        f"--header='{header}' "
        f"--indicator.foreground='#118DFF' "
        f"--selected-indicator.foreground='#118DFF' "
        f"--match.foreground='#118DFF' "
        f"--header.foreground='#118DFF' "
        f"--placeholder='Type to search...'"
    )

    try:
        result = sp.run(
            ["sh", "-c", shell_cmd],
            stdout=sp.PIPE,
            text=True,
            timeout=120,
        )
    except sp.TimeoutExpired:
        return []

    if result.returncode != 0:
        return []

    return [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]


def run_gum_picker(lines: List[str], header: str = "Tab to select, Enter to confirm:") -> List[str]:
    """Run gum filter --no-limit interactively (must be inside wezterm).

    Writes lines to a temp file and pipes to gum to avoid shell escaping
    issues with printf (which interprets \\n, \\t, etc. in URLs/titles).

    Includes a "[Select All]" sentinel at the top. When selected, a second
    pass runs with all items pre-selected so the user can confirm or
    deselect individual items before pressing Enter.

    Returns the list of selected lines (may be empty on cancel).
    """
    while True:
        # Phase 1: picker with Select All sentinel
        picker_lines: List[str] = [SELECT_ALL_SENTINEL] + lines
        fd, tmp_path = tempfile.mkstemp(prefix="tabtiler-", suffix=".txt")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("\n".join(picker_lines))

            selected: List[str] = _run_gum_filter(tmp_path, header)
        finally:
            os.unlink(tmp_path)

        if not selected:
            return []

        # Phase 2: if Select All chosen, re-run with everything pre-selected
        # and an Unselect All escape hatch
        if SELECT_ALL_SENTINEL not in selected:
            break

        phase2_lines: List[str] = [UNSELECT_ALL_SENTINEL] + lines
        fd2, tmp_path2 = tempfile.mkstemp(prefix="tabtiler-all-", suffix=".txt")
        try:
            with os.fdopen(fd2, "w") as f:
                f.write("\n".join(phase2_lines))

            selected = _run_gum_filter(
                tmp_path2,
                "All selected — deselect any to exclude, Enter to confirm:",
                pre_selected=lines,
            )
        finally:
            os.unlink(tmp_path2)

        if not selected:
            return []

        # Unselect All chosen: loop back to Phase 1
        if UNSELECT_ALL_SENTINEL in selected:
            continue

        break

    # Strip sentinels from final result
    return [s for s in selected if s not in (SELECT_ALL_SENTINEL, UNSELECT_ALL_SENTINEL)]


def pick_tile_mode() -> str:
    """Present gum filter for tile layout. Returns mode key (grid/vertical/horizontal).

    Uses ``gum filter`` with ``--height`` set to the number of options plus
    padding (for the search prompt, header, and spacing) so all choices are
    visible immediately while still supporting fuzzy search/typing to narrow
    the list.
    """
    # Build display lines: "grid        — Tile to grid"
    display_lines: List[str] = []
    key_map: Dict[str, str] = {}
    for key, desc in TILE_MODES.items():
        line: str = f"{key:<12} — {desc}"
        display_lines.append(line)
        key_map[line] = key

    try:
        mode_result = sp.run(
            ["gum", "filter",
             "--header", "Select tile layout:",
             "--header.foreground", "#118DFF",
             "--indicator.foreground", "#118DFF",
             "--match.foreground", "#118DFF",
             "--height", str(len(display_lines) + 3),
             "--placeholder", "Type to filter..."],
            input="\n".join(display_lines),
            stdout=sp.PIPE, text=True, timeout=30,
        )
    except sp.TimeoutExpired:
        return DEFAULT_TILE_MODE

    chosen: str = mode_result.stdout.strip()
    return key_map.get(chosen, DEFAULT_TILE_MODE)


# -- tab resolution helpers --


def filter_user_tabs(chrome_tabs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter out internal Vivaldi pages from a chrome.tabs result."""
    return [
        t for t in chrome_tabs
        if t.get("url", "") not in (
            "about:blank", "chrome://vivaldi-webui/startpage",
        )
        and not t.get("url", "").startswith("chrome-extension://")
        and t.get("title", "").strip()
    ]


def resolve_selections(selected_lines: List[str], tabs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map gum picker output lines back to tab objects."""
    selected_tabs: List[Dict[str, Any]] = []
    for sel in selected_lines:
        for tab in tabs:
            if format_picker_line(tab) == sel:
                selected_tabs.append(tab)
                break
        else:
            _log(f"NO MATCH for: {sel!r}")
    return selected_tabs


# -- preflight --


def preflight() -> str:
    """Run common startup checks. Returns the Vivaldi UI WebSocket URL or exits."""
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

    return ws_url


# -- mode handlers --


def cmd_list(ws_url: str) -> None:
    """--list: show currently tiled tabs; optionally re-tile a subset."""
    tiled: List[Dict[str, Any]] = get_tiled_tabs(ws_url)

    if not tiled:
        h.notify_send("No tabs currently tiled", "low")
        return

    # Show tiled tabs in picker (no-limit multi-select)
    picker_lines: List[str] = [format_picker_line(t) for t in tiled]
    _log(f"--list: {len(tiled)} tiled tabs")
    selected_lines: List[str] = run_gum_picker(
        picker_lines,
        header="Currently tiled (select to re-tile, Enter for all):",
    )

    # User cancelled
    if selected_lines is None:
        return

    # If nothing selected (bare Enter), use all tiled tabs
    if not selected_lines:
        return

    # Pick new tile layout
    tile_mode: str = pick_tile_mode()
    _log(f"--list: re-tile mode={tile_mode}")

    # Resolve which tabs to re-tile
    if len(selected_lines) == len(tiled):
        # All selected or none selected -> re-tile all
        target_urls: List[str] = [t["url"] for t in tiled]
    else:
        targets: List[Dict[str, Any]] = resolve_selections(selected_lines, tiled)
        if len(targets) < 2:
            h.notify_send("Select at least 2 tabs to tile", "low")
            return
        target_urls = [t["url"] for t in targets]

    # Untile current, select new set, tile
    sel_ok: bool = select_tabs_vivaldi(ws_url, target_urls)
    if not sel_ok:
        h.notify_send("Failed to select tabs in Vivaldi", "critical")
        sys.exit(1)

    time.sleep(0.2)
    tile_ok: bool = send_tile_via_cdp(ws_url, tile_mode)
    if tile_ok:
        h.notify_send(f"Re-tiled {len(target_urls)} tabs ({tile_mode})", "low")
    else:
        h.notify_send("Failed to tile", "critical")
        sys.exit(1)


def cmd_untile(ws_url: str) -> None:
    """--untile: remove current tiling."""
    untiled: bool = untile_via_cdp(ws_url)
    if untiled:
        h.notify_send("Untiled tabs", "low")
        _log("--untile: SUCCESS")
    else:
        h.notify_send("No active tiling to remove", "low")
        _log("--untile: nothing to untile")


def cmd_stack(ws_url: str) -> None:
    """--stack: pick tabs and create a new Vivaldi tab stack."""
    chrome_tabs: Optional[List[Dict[str, Any]]] = get_chrome_tabs(ws_url)
    if not chrome_tabs:
        h.notify_send("No tabs found via chrome.tabs", "critical")
        sys.exit(1)

    tabs: List[Dict[str, Any]] = filter_user_tabs(chrome_tabs)
    if not tabs:
        h.notify_send("No tabs found", "critical")
        sys.exit(1)

    picker_lines: List[str] = [format_picker_line(t) for t in tabs]
    _log(f"--stack: {len(tabs)} tabs available")
    selected_lines: List[str] = run_gum_picker(
        picker_lines,
        header="Select tabs for new stack (2+ required):",
    )

    if not selected_lines:
        _log("--stack: cancelled")
        return

    selected_tabs: List[Dict[str, Any]] = resolve_selections(selected_lines, tabs)
    if len(selected_tabs) < 2:
        h.notify_send("Select at least 2 tabs to stack", "low")
        return

    tab_ids: List[int] = [t["id"] for t in selected_tabs]
    group_id: Optional[str] = create_tab_stack(ws_url, tab_ids)

    if group_id:
        h.notify_send(f"Created tab stack with {len(selected_tabs)} tabs", "low")
        _log(f"--stack: SUCCESS group={group_id}")
    else:
        h.notify_send("Failed to create tab stack", "critical")
        _log("--stack: FAIL")
        sys.exit(1)


def cmd_switch(ws_url: str) -> None:
    """--switch: list existing tab stacks and activate the selected one."""
    chrome_tabs: Optional[List[Dict[str, Any]]] = get_chrome_tabs(ws_url)
    if not chrome_tabs:
        h.notify_send("No tabs found via chrome.tabs", "critical")
        sys.exit(1)

    tabs: List[Dict[str, Any]] = filter_user_tabs(chrome_tabs)

    # Group tabs by vivExtData.group UUID
    stacks: Dict[str, List[Dict[str, Any]]] = {}
    for tab in tabs:
        ext: Dict[str, Any] = tab.get("vivExtData", {})
        group_id: Optional[str] = ext.get("group")
        if group_id:
            stacks.setdefault(group_id, []).append(tab)

    # Filter out "stacks" with only one tab (not really a stack)
    stacks = {gid: members for gid, members in stacks.items() if len(members) >= 2}

    if not stacks:
        h.notify_send("No tab stacks found", "low")
        _log("--switch: no stacks found")
        return

    _log(f"--switch: found {len(stacks)} stacks")

    # Build picker lines: one line per stack showing member tab titles
    picker_lines: List[str] = []
    stack_index: List[str] = []  # parallel list of group IDs
    for gid, members in stacks.items():
        titles: List[str] = [m.get("title", "untitled") for m in members]
        # Truncate long titles for readability
        display_titles: List[str] = [
            t[:50] + "..." if len(t) > 50 else t for t in titles
        ]
        line: str = f"[{len(members)} tabs]  {' | '.join(display_titles)}"
        picker_lines.append(line)
        stack_index.append(gid)

    # Single-select gum picker for stacks
    fd, tmp_path = tempfile.mkstemp(prefix="tabtiler-switch-", suffix=".txt")
    try:
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(picker_lines))

        shell_cmd: str = (
            f"cat '{tmp_path}' | "
            f"gum filter --height=20 "
            f"--header='Switch to stack:' "
            f"--indicator.foreground='#118DFF' "
            f"--match.foreground='#118DFF' "
            f"--header.foreground='#118DFF' "
            f"--placeholder='Type to search...'"
        )

        try:
            result = sp.run(
                ["sh", "-c", shell_cmd],
                stdout=sp.PIPE,
                text=True,
                timeout=120,
            )
        except sp.TimeoutExpired:
            return

        if result.returncode != 0 or not result.stdout.strip():
            _log("--switch: cancelled")
            return

        selected_line: str = result.stdout.strip()
    finally:
        os.unlink(tmp_path)

    # Find which stack was selected
    selected_gid: Optional[str] = None
    for i, line in enumerate(picker_lines):
        if line == selected_line:
            selected_gid = stack_index[i]
            break

    if not selected_gid:
        _log(f"--switch: could not match selection: {selected_line!r}")
        h.notify_send("Could not identify selected stack", "critical")
        return

    # Activate the first tab of the selected stack
    first_tab: Dict[str, Any] = stacks[selected_gid][0]
    tab_id: int = first_tab["id"]
    _log(f"--switch: activating tab {tab_id} in stack {selected_gid}")

    activate_expr: str = f'''
    (function() {{
        return new Promise(function(resolve) {{
            chrome.tabs.update({tab_id}, {{active: true}}, function(tab) {{
                if (chrome.runtime.lastError) {{
                    resolve({{error: chrome.runtime.lastError.message}});
                }} else {{
                    resolve({{activated: tab.id, title: tab.title}});
                }}
            }});
        }});
    }})()
    '''
    activate_result: Any = vb.cdp_ws_evaluate(ws_url, activate_expr)
    _log(f"--switch: activate result: {activate_result}")

    if isinstance(activate_result, dict) and "activated" in activate_result:
        stack_size: int = len(stacks[selected_gid])
        h.notify_send(
            f"Switched to stack ({stack_size} tabs): {first_tab.get('title', '')}",
            "low",
        )
        _log("--switch: SUCCESS")
    else:
        h.notify_send("Failed to switch to stack", "critical")
        _log(f"--switch: FAIL result={activate_result}")
        sys.exit(1)


def cmd_tile(ws_url: str) -> None:
    """Default: pick tabs -> pick layout -> stack -> tile."""
    chrome_tabs: Optional[List[Dict[str, Any]]] = get_chrome_tabs(ws_url)
    if not chrome_tabs:
        h.notify_send("No tabs found via chrome.tabs", "critical")
        sys.exit(1)

    tabs: List[Dict[str, Any]] = filter_user_tabs(chrome_tabs)
    if not tabs:
        h.notify_send("No tabs found", "critical")
        sys.exit(1)

    # -- build picker lines --
    picker_lines: List[str] = [format_picker_line(t) for t in tabs]

    # -- interactive gum picker --
    _log("--- new run ---")
    _log(f"picker_lines count: {len(picker_lines)}")
    selected_lines: List[str] = run_gum_picker(
        picker_lines,
        header="Tab to select, Enter to tile:",
    )
    _log(f"gum returned {len(selected_lines)} lines: {selected_lines!r}")

    if not selected_lines:
        _log("no selection, exiting")
        return

    if len(selected_lines) < 2:
        _log("fewer than 2 selected")
        h.notify_send("Select at least 2 tabs to tile", "low")
        return

    # -- resolve selections --
    selected_tabs: List[Dict[str, Any]] = resolve_selections(selected_lines, tabs)
    selected_urls: List[str] = [t["url"] for t in selected_tabs]
    _log(f"selected {len(selected_tabs)} tabs: {selected_urls}")

    if len(selected_tabs) < 2:
        h.notify_send("Could not resolve selected tabs", "critical")
        _log("FAIL: could not resolve tabs")
        sys.exit(1)

    # -- pick tile mode --
    tile_mode: str = pick_tile_mode()
    _log(f"tile_mode={tile_mode}")

    # -- stack selected tabs first --
    tab_ids: List[int] = [t["id"] for t in selected_tabs]
    group_id: Optional[str] = create_tab_stack(ws_url, tab_ids)
    if group_id:
        _log(f"stacked tabs: group={group_id}")
        time.sleep(0.2)  # let the stack settle in the UI
    else:
        _log("stack creation failed, proceeding with select+tile only")

    # -- select tabs via Vivaldi's internal React API --
    sel_ok: bool = select_tabs_vivaldi(ws_url, selected_urls)
    _log(f"select_tabs_vivaldi returned {sel_ok}")
    if not sel_ok:
        h.notify_send("Failed to select tabs in Vivaldi", "critical")
        _log("FAIL: select_tabs_vivaldi")
        sys.exit(1)

    # -- tile via CDP --
    time.sleep(0.2)  # let selection settle
    tile_ok: bool = send_tile_via_cdp(ws_url, tile_mode)
    _log(f"send_tile_via_cdp returned {tile_ok}")
    if tile_ok:
        h.notify_send(f"Tiled {len(selected_tabs)} tabs ({tile_mode})", "low")
        _log("SUCCESS")
    else:
        h.notify_send("Failed to send tile shortcut", "critical")
        _log("FAIL: send_tile_via_cdp")
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    """Parse CLI flags."""
    parser = argparse.ArgumentParser(
        description="Vivaldi Tab Tiler - tile, stack, and manage tabs",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-l", "--list",
        action="store_true",
        help="List currently tiled tabs; optionally re-tile",
    )
    group.add_argument(
        "-u", "--untile",
        action="store_true",
        help="Remove current tab tiling",
    )
    group.add_argument(
        "-s", "--stack",
        action="store_true",
        help="Select tabs and create a new Vivaldi tab stack",
    )
    group.add_argument(
        "-w", "--switch",
        action="store_true",
        help="List existing tab stacks and switch to a selected one",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point: parse flags and dispatch to the appropriate handler."""
    # -- self-respawn if not inside a wezterm pane --
    # DWM may inherit a TTY from startx, so isatty() is unreliable.
    # WEZTERM_PANE is only set inside an actual wezterm terminal.
    if "WEZTERM_PANE" not in os.environ:
        respawn_in_wezterm()
        # execvp does not return

    args: argparse.Namespace = parse_args()
    ws_url: str = preflight()

    if args.list:
        cmd_list(ws_url)
    elif args.untile:
        cmd_untile(ws_url)
    elif args.stack:
        cmd_stack(ws_url)
    elif args.switch:
        cmd_switch(ws_url)
    else:
        cmd_tile(ws_url)


if __name__ == "__main__":
    main()
