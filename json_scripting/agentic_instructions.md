# agentic_instructions.md — python_projects/json_scripting

## Purpose
JSON processing scripts that parse CLI tool output (kubectl, aws) into pandas DataFrames.

## Technology
- Language: Python 3
- Libraries: json, subprocess, pandas

## Contents
- `json_testing.py` — Runs `aws sts get-caller-identity`, parses JSON output into a normalized pandas DataFrame.
- `json_pandas.py` — JSON-to-pandas processing utility.
- `Makefile` — Build/run targets.

## Key Functions
- `json_testing.py` script-level: Executes AWS CLI, parses JSON, normalizes into DataFrame, prints result.

## Data Types
- `pd.DataFrame` from `pd.json_normalize()`.

## Logging
- `print()` for DataFrame output and errors.

## CRUD Entry Points
- **Run**: `python3 json_testing.py` or `make`

## Style Guide
- `subprocess.Popen` for CLI execution
- `json.loads()` for JSON parsing
- `pd.json_normalize()` for flattening nested JSON into DataFrames
