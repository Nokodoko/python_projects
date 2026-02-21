# agentic_instructions.md — python_projects

## Purpose
Collection of Python scripts and tools for system automation, AWS administration, Datadog API interaction, AI/LLM integration, data processing (pandas/xlsx), Vivaldi browser control, and desktop utilities on Arch Linux.

## Technology
- Language: Python 3
- Libraries: requests, pandas, flask, langchain, aiohttp, openpyxl, xlsxwriter, subprocess
- External tools: dmenu, fzf, gum, notify-send, wezterm, aws CLI, kubectl
- APIs: Datadog, OpenAI, Grok, AWS IAM/STS

## Contents
- `helpers.py` — Helper module: dmenu wrapper function, notify-send wrapper with criticality levels.
- `claude_sessions.py` / `claude_sessions_floater.py` / `claude_delete_session.py` — Claude Code session management utilities.
- `fzf.py` — fzf integration utility.
- `kube.py` — Kubernetes utility script.
- `json_to_xlsx.py` / `xlsx_to_json.py` — JSON/Excel conversion utilities.
- `pandas_tests.py` / `working_pandas_fs_integration.py` — Pandas data processing experiments.
- `rag.py` — RAG (Retrieval-Augmented Generation) context file selector.
- `audio.py` — Audio utility.
- `prac.py` / `pyd.py` / `pyoperators.py` — Python practice/learning scripts.
- `rotateimage.py` — Image rotation utility.
- `test_workbook.py` — Excel workbook testing.
- `newScript.py` / `path.py` / `responsetest.py` — Miscellaneous utilities.

### Subdirectories
- `ai/` — AI/LLM clients (Ollama local, OpenAI via langchain).
- `ansible/` — Ansible Tower project creation via awxkit API.
- `asus/` — ASUS router management via aiohttp/asusrouter library.
- `aws/` — AWS IAM user listing and STS caller identity scripts.
- `ddog/` — Datadog API clients for dashboards and usage stats.
- `grok/` — Grok AI chat client with persistent conversation threads.
- `hooks/` — Flask webhook test server.
- `json_scripting/` — JSON processing with pandas (kubectl, AWS output).
- `pandas_scripts/` — Pandas/Excel data processing and Datadog integration list management.
- `rag/` — RAG file selector with fzf multi-select and user prompt collection.
- `rust_python/` — Rust-Python interop via maturin (PyO3).
- `scripts/` — Desktop automation: Vivaldi tab tiler, process killer, password manager, keyboard brightness, wallpaper fetcher, etc.

## Key Functions
- `helpers.py::dmenu(color, prompt) -> str` — Launches dmenu with custom styling, returns selection.
- `helpers.py::notify_send(msg, criticality) -> str|None` — Sends desktop notification via notify-send.
- `scripts/tabTiler.py` — Vivaldi tab tiling via Chrome DevTools Protocol (CDP).
- `scripts/killer.py` — Process killer with fzf/dmenu selection.
- `scripts/wallhaven.py` — Wallpaper fetcher from Wallhaven API.
- `aws/awsListUsers.py::list_users(userlist) -> List[str]` — Lists AWS IAM users, returns usernames.
- `ddog/ddog_api.py::dashboards()`, `usage()` — Datadog API queries.

## Data Types
- Pandas DataFrames for tabular data processing.
- JSON-serialized conversation threads (grok).
- Excel workbooks via xlsxwriter/openpyxl.

## Logging
- `print()` for stdout output.
- `subprocess.Popen` for shell integration.
- notify-send for desktop notifications.

## CRUD Entry Points
- **Run**: `python3 <script>.py [args]` or `./script.py` (with shebang)
- **Dependencies**: pip install (requests, pandas, flask, langchain, etc.)

## Style Guide
- `#!/bin/env python3` shebang
- Type annotations on function signatures and variables
- `subprocess.Popen` with `communicate()` for shell commands
- `match/case` for dispatch (Python 3.10+)
- `sys.argv` for CLI arguments, `argparse` for complex CLIs
- Helper modules imported locally

```python
def dmenu(color: str, prompt: str) -> str:
    dmenu_command: List[str] = ["dmenu", "-m", "0", "-fn", "VictorMono:size=20",
                                "-nf", "green", "-nb", "black",
                                "-nf", color, "-sb", "black", "-p", prompt]
    dmenu = sp.Popen(dmenu_command, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    output, err = dmenu.communicate()
    return output.strip()
```
