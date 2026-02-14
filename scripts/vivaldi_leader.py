#!/bin/env python3
"""Vivaldi leader key dispatcher.

Invoked by Alt+V in dwm. Shows a dmenu with available Vivaldi actions
and dispatches to the selected script.

Add new actions to the ACTIONS dict below.
"""
import subprocess as sp
import sys

import helpers as h
import vivaldi_base as vb


PROMPT: str = "Vivaldi:"

# -- action registry --
# key: single char shortcut
# label: human-readable description shown in dmenu
# cmd: command list to execute

ACTIONS: dict = {
    "t": {
        "label": "Tab Kill",
        "cmd": ["/home/n0ko/programming/python_projects/scripts/tabkill.py"],
    },
}


def format_action_line(key: str, action: dict) -> str:
    """Format an action for display in dmenu: key  label."""
    return f"{key}  {action['label']}"


def main() -> None:
    """Show action menu and dispatch to selected Vivaldi script."""
    lines: str = "\n".join(
        format_action_line(k, v) for k, v in sorted(ACTIONS.items())
    )

    choice: str = vb.dmenu_vivaldi(PROMPT, lines)
    if not choice:
        return

    # Extract the key (first non-space character)
    key: str = choice.strip().split()[0] if choice.strip() else ""

    if key not in ACTIONS:
        h.notify_send(f'Unknown Vivaldi action: "{key}"', "low")
        sys.exit(1)

    cmd = ACTIONS[key]["cmd"]
    sp.Popen(cmd)


if __name__ == "__main__":
    main()
