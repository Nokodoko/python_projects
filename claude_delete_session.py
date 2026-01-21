#!/usr/bin/env python3
"""
Claude session deleter - lists all Claude Code sessions and deletes
the selected one after confirmation.
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
                full_path = entry.get("fullPath", "")

                # Use customTitle, then summary, then firstPrompt as session name
                session_name = custom_title or summary or first_prompt

                if project_path and session_id:
                    sessions.append({
                        "sessionId": session_id,
                        "projectPath": project_path,
                        "sessionName": session_name,
                        "modified": modified,
                        "fullPath": full_path,
                        "indexFile": str(index_file),
                    })
        except (json.JSONDecodeError, IOError):
            continue

    sessions.sort(key=lambda x: x.get("modified", ""), reverse=True)
    return sessions


def gum_select(items: List[str], header: str = "Delete Claude Session") -> Optional[str]:
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


def confirm_delete(session_name: str, project_path: str) -> bool:
    """Ask for confirmation using gum."""
    result = sp.run(
        [
            "gum", "confirm",
            f"Delete '{session_name}' from {project_path}?",
            "--affirmative", "Delete",
            "--negative", "Cancel"
        ],
        capture_output=False
    )
    return result.returncode == 0


def delete_session(session_id: str, sessions: List[dict]) -> bool:
    """Delete the session file and remove from index."""
    session = next((s for s in sessions if s["sessionId"] == session_id), None)
    if not session:
        print(f"Session not found: {session_id}")
        return False

    full_path = session.get("fullPath", "")
    index_file = session.get("indexFile", "")

    # Delete the session file
    if full_path and os.path.exists(full_path):
        os.remove(full_path)

    # Update the index file
    if index_file and os.path.exists(index_file):
        with open(index_file, "r") as f:
            data = json.load(f)

        data["entries"] = [e for e in data.get("entries", []) if e.get("sessionId") != session_id]

        with open(index_file, "w") as f:
            json.dump(data, f, indent=2)

    return True


def main() -> None:
    sessions = get_sessions()

    if not sessions:
        print("No Claude sessions found")
        sys.exit(1)

    # Build mapping of display name -> session data
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

    session_name = session["sessionName"]
    project_path = session["projectPath"]
    session_id = session["sessionId"]

    if not confirm_delete(session_name, project_path):
        print("Cancelled")
        sys.exit(0)

    if delete_session(session_id, sessions):
        print(f"Deleted session: {session_id}")
    else:
        print("Failed to delete session")
        sys.exit(1)


if __name__ == "__main__":
    main()
