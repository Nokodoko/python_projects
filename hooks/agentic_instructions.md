# agentic_instructions.md — python_projects/hooks

## Purpose
Simple Flask webhook test server for receiving and logging POST requests.

## Technology
- Language: Python 3
- Framework: Flask

## Contents
- `test_hook.py` — Flask app with a `/webhook` POST endpoint that prints received JSON and returns success status.

## Key Functions
- `respond()` — Flask route handler for POST /webhook: prints request JSON, returns 200 with status: success.

## Data Types
- `request.json` — Incoming JSON payload (dict).

## Logging
- `print(request.json)` for incoming webhook data.

## CRUD Entry Points
- **Run**: `python3 test_hook.py` (starts on port 5000)
- **Test**: `curl -X POST -H "Content-Type: application/json" -d '{"test": "data"}' http://localhost:5000/webhook`
- **Dependencies**: `pip install flask`

## Style Guide
- Flask decorator pattern (`@app.route`)
- Debug mode enabled for development
- Inline comments with usage instructions
