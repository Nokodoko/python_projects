# agentic_instructions.md — python_projects/ddog

## Purpose
Datadog API client scripts for querying dashboards, usage statistics, and other resources from the Datadog Gov API.

## Technology
- Language: Python 3
- Libraries: requests
- API: Datadog Gov API (api.ddog-gov.com)

## Contents
- `ddog_api.py` — CLI dispatch script: queries dashboards or usage stats based on CLI argument. Uses match/case for routing.
- `dashboards.py` — Dashboard-specific API queries.

## Key Functions
- `ddog_api.py::usage()` — Fetches hourly usage stats from Datadog API.
- `ddog_api.py::dashboards()` — Fetches dashboard lists from Datadog API.
- `ddog_api.py::selection(input)` — Match/case dispatcher for CLI argument routing.

## Data Types
- JSON API responses parsed via `response.json()`.
- Header dicts with DD-API-KEY and DD-APPLICATION-KEY.

## Logging
- `print()` for results and status codes.

## CRUD Entry Points
- **Run**: `python3 ddog_api.py dashboards` or `python3 ddog_api.py usage`
- **Config**: Environment variables `DD_API_KEY`, `DD_APP_KEY`, `EM_API_KEY`, `EM_APP_KEY`.

## Style Guide
- `match/case` dispatch (Python 3.10+)
- `os.getenv()` for credential loading
- `requests.get()` with header dicts
- `sys.argv[1]` for CLI argument

```python
def selection(input):
    match input:
        case "dashboards":
            dashboards()
        case "usage":
            usage()
```
