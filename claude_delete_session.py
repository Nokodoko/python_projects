#!/usr/bin/env python3
"""
Claude session deleter - lists all Claude Code sessions with multi-select
and deletes selected sessions after confirmation.
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

    try:
        with open(jsonl_path, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if entry.get("type") == "custom-title":
                    custom_title = entry.get("customTitle", "")

                if entry.get("type") == "user" and not project_path:
                    project_path = entry.get("cwd", "")

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

        modified = jsonl_path.stat().st_mtime
        session_name = custom_title or first_prompt or session_id
        if project_path and session_id:
            return {
                "sessionId": session_id,
                "projectPath": project_path,
                "sessionName": session_name,
                "modified": modified,
                "jsonlPath": str(jsonl_path),
                "projectDir": str(jsonl_path.parent),
            }
    except (IOError, OSError):
        pass
    return None


def get_sessions() -> List[dict]:
    """Find and parse all sessions from index files and individual .jsonl files."""
    sessions = []
    indexed_sessions = set()

    if not CLAUDE_PROJECTS_DIR.exists():
        return sessions

    for project_dir in CLAUDE_PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue

        index_file = project_dir / "sessions-index.json"

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
                    full_path = entry.get("fullPath", "")

                    session_name = custom_title or summary or first_prompt

                    if project_path and session_id:
                        indexed_sessions.add(session_id)
                        sessions.append({
                            "sessionId": session_id,
                            "projectPath": project_path,
                            "sessionName": session_name,
                            "modified": modified,
                            "fullPath": full_path,
                            "indexFile": str(index_file),
                            "projectDir": str(project_dir),
                        })
            except (json.JSONDecodeError, IOError):
                pass

        for jsonl_file in project_dir.glob("*.jsonl"):
            session_id = jsonl_file.stem
            if session_id.startswith("agent-") or session_id in indexed_sessions:
                continue

            session = parse_session_jsonl(jsonl_file)
            if session and len(session.get("sessionName", "")) >= 3:
                sessions.append(session)

    sessions.sort(key=lambda x: x.get("modified", 0) if isinstance(x.get("modified"), (int, float)) else 0, reverse=True)
    return sessions


def gum_multi_select(items: List[str], header: str = "Delete Claude Sessions (tab to select, enter to confirm)") -> List[str]:
    """Run gum filter with multi-select and return selected lines."""
    if not items:
        print("No Claude sessions found")
        return []

    input_text = "\n".join(items)

    proc = sp.Popen(
        ["gum", "filter", "--no-limit", "--header", header],
        stdin=sp.PIPE,
        stdout=sp.PIPE,
        text=True,
    )
    output, _ = proc.communicate(input=input_text)

    if proc.returncode != 0:
        return []

    return [line for line in output.strip().split("\n") if line]


def confirm_delete(count: int, names: List[str]) -> bool:
    """Ask for confirmation using gum."""
    preview = "\n".join(f"  - {n}" for n in names[:10])
    if count > 10:
        preview += f"\n  ... and {count - 10} more"

    result = sp.run(
        [
            "gum", "confirm",
            f"Delete {count} session(s)?\n{preview}",
            "--affirmative", "Delete",
            "--negative", "Cancel",
        ],
    )
    return result.returncode == 0


def delete_session(session: dict) -> bool:
    """Delete the session file and remove from index."""
    session_id = session["sessionId"]
    project_dir = session.get("projectDir", "")

    # Delete the session .jsonl file
    full_path = session.get("fullPath", "")
    if full_path and os.path.exists(full_path):
        os.remove(full_path)
    else:
        # Try finding the .jsonl directly
        jsonl_path = session.get("jsonlPath", "")
        if jsonl_path and os.path.exists(jsonl_path):
            os.remove(jsonl_path)
        elif project_dir:
            candidate = Path(project_dir) / f"{session_id}.jsonl"
            if candidate.exists():
                os.remove(candidate)

    # Also delete any agent subdirectory for this session
    if project_dir:
        session_dir = Path(project_dir) / session_id
        if session_dir.is_dir():
            import shutil
            shutil.rmtree(session_dir)

    # Update the index file if this session was indexed
    index_file = session.get("indexFile", "")
    if index_file and os.path.exists(index_file):
        try:
            with open(index_file, "r") as f:
                data = json.load(f)

            data["entries"] = [e for e in data.get("entries", []) if e.get("sessionId") != session_id]

            with open(index_file, "w") as f:
                json.dump(data, f, indent=2)
        except (json.JSONDecodeError, IOError):
            pass

    return True


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

    selected = gum_multi_select(display_names)

    if not selected:
        sys.exit(0)

    to_delete = []
    for name in selected:
        session = session_map.get(name)
        if session:
            to_delete.append((name, session))

    if not to_delete:
        print("No matching sessions found")
        sys.exit(1)

    if not confirm_delete(len(to_delete), [n for n, _ in to_delete]):
        print("Cancelled")
        sys.exit(0)

    deleted = 0
    for name, session in to_delete:
        if delete_session(session):
            print(f"Deleted: {name}")
            deleted += 1
        else:
            print(f"Failed: {name}")

    print(f"\n{deleted}/{len(to_delete)} sessions deleted")


if __name__ == "__main__":
    main()
