# agentic_instructions.md — python_projects/asus

## Purpose
ASUS router management client using the asusrouter library for retrieving network data.

## Technology
- Language: Python 3
- Libraries: aiohttp, asyncio, asusrouter
- Pattern: Async I/O

## Contents
- `asus.py` — Connects to an ASUS router via asusrouter library, retrieves network data using async/await.
- `creds.py` — Credential provider module (hostname, username, password).
- `__init__.py` — Package init (empty).

## Key Functions
- `asus.py` script-level: Creates aiohttp session, connects to router, fetches `AsusData.NETWORK`, disconnects.
- `creds.py::hostname()`, `username()`, `password()` — Credential accessor functions.

## Data Types
- `AsusRouter` — Router connection instance.
- `AsusData.NETWORK` — Network data enum.

## Logging
- `print(data)` for network data output.

## CRUD Entry Points
- **Run**: `python3 -m asus.asus` (as package)
- **Config**: Update credentials in `creds.py`.

## Style Guide
- Async/await with `asyncio.new_event_loop()` manual loop management
- Relative import for credentials (`from . import creds`)
- Cleanup pattern: disconnect + close session
