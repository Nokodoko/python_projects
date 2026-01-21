#!/usr/bin/env python3
"""
Claude session navigator (floater mode) - lists all Claude Code sessions
and opens the selected one in a new zellij split pane.
"""

import json
import os
import subprocess as sp
import sys
from pathlib import Path
from typing import List, Optional


CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"


def get_sessions() -> List[dict]:
    """Find and parse all sessions-index.json files."""
    sessions = []

    if not CLAUDE_PROJECTS_DIR.exists():
        return sessions

    for project_dir in CLAUDE_PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue

        index_file = project_dir / "sessions-index.json"
        if not index_file.exists():
            continue

        try:
            with open(index_file, "r") as f:
                data = json.load(f)

            for entry in data.get("entries", []):
                session_id = entry.get("sessionId", "")
                project_path = entry.get("projectPath", "")
                custom_title = entry.get("customTitle", "")
                summary = entry.get("summary", "")
                first_prompt = entry.get("firstPrompt", "")[:60]
                modified = entry.get("modified", "")

                session_name = custom_title or summary or first_prompt

                if project_path and session_id:
                    sessions.append({
                        "sessionId": session_id,
                        "projectPath": project_path,
                        "sessionName": session_name,
                        "modified": modified,
                    })
        except (json.JSONDecodeError, IOError):
            continue

    sessions.sort(key=lambda x: x.get("modified", ""), reverse=True)
    return sessions


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


def open_zellij_pane(cwd: str, session_id: str) -> None:
    """Open a new zellij split pane and resume the Claude session."""
    sp.run([
        "zellij", "run", "--cwd", cwd, "--",
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
