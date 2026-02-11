#!/usr/bin/env python3
"""
Claude session navigator - lists all Claude Code sessions and opens
a new zellij pane in the selected project directory.
"""

import json
import os
import subprocess as sp
import sys
from pathlib import Path
from typing import List, Optional


CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"


def parse_session_jsonl(jsonl_path: Path) -> Optional[dict]:
    """Parse a session .jsonl file to extract session info."""
    custom_title = ""
    first_prompt = ""
    project_path = ""
    session_id = jsonl_path.stem
    modified = ""

    try:
        with open(jsonl_path, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Get custom title if present
                if entry.get("type") == "custom-title":
                    custom_title = entry.get("customTitle", "")

                # Get project path from user messages
                if entry.get("type") == "user" and not project_path:
                    project_path = entry.get("cwd", "")

                # Get first prompt from user messages
                if entry.get("type") == "user" and not first_prompt:
                    msg = entry.get("message", {})
                    content = msg.get("content", [])
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            first_prompt = item.get("text", "")[:60]
                            break
                        elif isinstance(item, str):
                            first_prompt = item[:60]
                            break

        # Get modified time from file
        modified = jsonl_path.stat().st_mtime

        session_name = custom_title or first_prompt or session_id
        if project_path and session_id:
            return {
                "sessionId": session_id,
                "projectPath": project_path,
                "sessionName": session_name,
                "modified": modified,
            }
    except (IOError, OSError):
        pass
    return None


def get_sessions() -> List[dict]:
    """Find and parse all sessions from index files and individual .jsonl files."""
    sessions = []
    indexed_sessions = set()  # Track sessions found in index files

    if not CLAUDE_PROJECTS_DIR.exists():
        return sessions

    for project_dir in CLAUDE_PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue

        index_file = project_dir / "sessions-index.json"

        # Try to read from sessions-index.json first
        if index_file.exists():
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

                    # Use customTitle, then summary, then firstPrompt as session name
                    session_name = custom_title or summary or first_prompt

                    if project_path and session_id:
                        indexed_sessions.add(session_id)
                        sessions.append({
                            "sessionId": session_id,
                            "projectPath": project_path,
                            "sessionName": session_name,
                            "modified": modified,
                        })
            except (json.JSONDecodeError, IOError):
                pass

        # Scan individual .jsonl files for sessions not in index
        for jsonl_file in project_dir.glob("*.jsonl"):
            session_id = jsonl_file.stem
            # Skip subagent sessions and already indexed sessions
            if session_id.startswith("agent-") or session_id in indexed_sessions:
                continue

            session = parse_session_jsonl(jsonl_file)
            # Skip sessions with very short names (likely typos/tests)
            if session and len(session.get("sessionName", "")) >= 3:
                sessions.append(session)

    # Sort by modified date (most recent first)
    sessions.sort(key=lambda x: x.get("modified", 0) if isinstance(x.get("modified"), (int, float)) else 0, reverse=True)
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


def resume_session(cwd: str, session_id: str) -> None:
    """Change to project directory and exec into claude session."""
    os.chdir(cwd)
    os.execvp("claude", ["claude", "--resume", session_id, "--dangerously-skip-permissions"])


def main() -> None:
    sessions = get_sessions()

    if not sessions:
        print("No Claude sessions found")
        sys.exit(1)

    # Build mapping of display name -> session data
    # Use index to handle duplicate names
    session_map = {}
    display_names = []
    for i, s in enumerate(sessions):
        name = s["sessionName"].replace("\n", " ")
        # Add index suffix if name already exists
        display_name = name
        if name in session_map:
            display_name = f"{name} ({i})"
        session_map[display_name] = s
        display_names.append(display_name)

    # Run gum selection
    selected = gum_select(display_names)

    if not selected:
        sys.exit(0)

    # Look up session data
    session = session_map.get(selected)
    if not session:
        print(f"Session not found: {selected}")
        sys.exit(1)

    project_path = session["projectPath"]
    session_id = session["sessionId"]

    if not os.path.isdir(project_path):
        print(f"Directory not found: {project_path}")
        sys.exit(1)

    # Resume claude session in current pane
    resume_session(project_path, session_id)


if __name__ == "__main__":
    main()
