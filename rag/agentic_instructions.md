# agentic_instructions.md — python_projects/rag

## Purpose
RAG (Retrieval-Augmented Generation) context file selector: uses fd + fzf to select files, reads their contents, and collects a user prompt for LLM context injection.

## Technology
- Language: Python 3
- Libraries: subprocess
- External tools: fd (file finder), fzf (fuzzy selector), bat (file previewer)

## Contents
- `rag.py` — Multi-step pipeline: fd lists files, fzf presents multi-select with bat preview, selected file contents are read and collected, user prompt is gathered interactively.
- `Makefile` — Run target.

## Key Functions
- `runner(cmd) -> str` — Generic subprocess runner with error handling.
- `flist(text_input) -> List[str]` — Builds fzf command with multi-select, reverse layout, border, and bat preview.
- `fd(path) -> str` — Runs fd to find all files in a directory.
- `context() -> Optional[List[str]]` — Full pipeline: fd -> fzf -> read selected files -> return contents.
- `user_prompt() -> str` — Interactive multi-line prompt collection (empty line terminates).
- `collector()` — Combines context and prompt (incomplete).

## Data Types
- File contents as `List[str]`.
- fzf output as newline-separated file paths.

## Logging
- `print()` for output and errors.

## CRUD Entry Points
- **Run**: `python3 rag.py /path/to/search`
- **Dependencies**: fd, fzf, bat installed on system.

## Style Guide
- `subprocess.Popen` with `communicate()` for piped process chains
- `sys.argv[1]` for directory path argument
- Type annotations with `Optional[List[str]]`

```python
def context() -> Optional[List[str]]:
    fzf_command = flist(FZF_SELECTOR_PROMPT)
    selector = sp.Popen(fzf_command, stdin=sp.PIPE, stdout=sp.PIPE, text=True)
    fzf_output, fzf_err = selector.communicate(input=fd(DIR_PATH))
    file_contents = []
    for file_path in values:
        with open(file_path, 'r') as file:
            file_contents.append(file.read().strip())
    return file_contents
```
