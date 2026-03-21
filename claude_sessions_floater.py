#!/usr/bin/env python3
"""
Claude session navigator (floater mode) - lists all Claude Code sessions
and opens the selected one in a new zellij split pane.
"""

import os
import subprocess as sp
import sys
from typing import List, Optional

from claude_sessions import get_sessions


def gum_select(items: List[str], header: str = "Claude Sessions") -> Optional[str]:
    """Run gum filter with the given items and return the selected line."""
    if not items:
        print("No Claude sessions found")
        return None

    input_text = "\n".join(items)

    proc = sp.Popen(
        ["gum", "filter", "--header", header],
        stdin=sp.PIPE,
        stdout=sp.PIPE,
        text=True
    )
    output, _ = proc.communicate(input=input_text)

    if proc.returncode != 0:
        return None

    return output.strip()


def update_active_cwd(project_path: str) -> None:
    """Write the project path to the focus-tracking file so fp and lazygit update."""
    cwd_file = f"/tmp/cmdr-{os.getuid()}-active-cwd"
    try:
        with open(cwd_file, "w") as f:
            f.write(project_path + "\n")
    except OSError:
        pass


def open_zellij_pane(cwd: str, session_id: str) -> None:
    """Resume the Claude session in the current pane (swallow pattern)."""
    update_active_cwd(cwd)
    os.chdir(cwd)
    os.execvp("claude", [
        "claude", "--resume", session_id, "--dangerously-skip-permissions"
    ])


def main() -> None:
    sessions = get_sessions()

    if not sessions:
        print("No Claude sessions found")
        sys.exit(1)

    session_map = {}
    display_names = []
    for i, s in enumerate(sessions):
        name = s["sessionName"].replace("\n", " ")
        display_name = name
        if name in session_map:
            display_name = f"{name} ({i})"
        session_map[display_name] = s
        display_names.append(display_name)

    selected = gum_select(display_names)

    if not selected:
        sys.exit(0)

    session = session_map.get(selected)
    if not session:
        print(f"Session not found: {selected}")
        sys.exit(1)

    project_path = session["projectPath"]
    session_id = session["sessionId"]

    if not os.path.isdir(project_path):
        print(f"Directory not found: {project_path}")
        sys.exit(1)

    open_zellij_pane(project_path, session_id)


if __name__ == "__main__":
    main()
