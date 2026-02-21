# agentic_instructions.md — python_projects/grok

## Purpose
Grok AI chat client with streaming responses, persistent conversation threads, and prompt modification support.

## Technology
- Language: Python 3
- Libraries: requests, argparse, json
- API: Grok backend API (streaming)

## Contents
- `grok.py` — CLI chat client: sends prompts to Grok API with streaming token output, supports named chat persistence via JSON files, and prompt modification.
- `prompt.md` — Default prompt template documentation.

## Key Functions
- `grok.py::api() -> str` — Retrieves Grok API key from environment.
- `grok.py::load_chat(filename) -> list` — Loads persisted chat thread from JSON file.
- `grok.py::save_chat(filename, chat_thread)` — Saves chat thread to JSON file.
- `grok.py::stream_response(api_url, headers, prompt)` — Streams and prints API response tokens line by line.
- `grok.py::main()` — Argparse-based CLI: handles payload, --chats, --prompt flags.

## Data Types
- Chat history as `list` of prompt strings, persisted as JSON.

## Logging
- `print()` with `flush=True` for streaming output.
- Error messages for non-200 status codes.

## CRUD Entry Points
- **Run**: `python3 grok.py "your prompt"` or `echo "prompt" | python3 grok.py`
- **Chat persistence**: `python3 grok.py --chats mythread "question"`
- **Prompt modification**: `python3 grok.py --prompt "prefix" "question"`
- **Config**: `GROK_API` environment variable.

## Style Guide
- `argparse` for CLI argument parsing
- Streaming response with `iter_lines()`
- JSON file persistence for conversation history
- stdin fallback when no positional argument provided
