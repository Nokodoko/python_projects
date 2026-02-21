# agentic_instructions.md — python_projects/aws

## Purpose
AWS administration scripts for IAM user listing with dmenu selection and STS caller identity display.

## Technology
- Language: Python 3
- Libraries: subprocess, json, pandas
- External tools: aws CLI, dmenu
- Module: helpers (local)

## Contents
- `awsListUsers.py` — Lists AWS IAM users via `aws iam list-users`, extracts UserName fields, presents in dmenu for selection.
- `awsid.py` — Runs `aws sts get-caller-identity`, displays results as a pandas DataFrame.

## Key Functions
- `awsListUsers.py::list_users(userlist: List[str]) -> List[str]` — Executes aws CLI, parses JSON response, extracts usernames.
- `awsid.py::sts_caller(cmd: List[str]) -> None` — Executes STS identity call, displays as DataFrame.

## Data Types
- JSON-parsed AWS responses as Python dicts/lists.
- `pd.DataFrame` for tabular output.

## Logging
- `print()` for output and errors.
- `sys.exit(1)` on subprocess failure.

## CRUD Entry Points
- **Run**: `python3 awsListUsers.py` or `python3 awsid.py`
- **Dependencies**: aws CLI configured, pandas installed.

## Style Guide
- Type annotations on function signatures
- `subprocess.Popen` with `communicate()`
- JSON list comprehension for field extraction
- dmenu integration via helpers module

```python
def list_users(userlist: List[str]) -> List[str]:
    ls = sp.Popen(userlist, stdin=sp.PIPE, stdout=sp.PIPE,
                  stderr=sp.PIPE, text=True)
    users, err = ls.communicate()
    everyone = json.loads(users.strip())
    names = [item['UserName'] for item in everyone['Users']]
    return names
```
