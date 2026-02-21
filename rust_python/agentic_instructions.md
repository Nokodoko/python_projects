# agentic_instructions.md — python_projects/rust_python

## Purpose
Rust-Python interop project using maturin (PyO3) to create Python extensions written in Rust.

## Technology
- Language: Rust + Python
- Build tool: maturin (PyO3 bindings)
- Rust edition: 2021

## Contents
- `matur/Cargo.toml` — Rust crate configuration with pyo3 dependency and cdylib crate type.
- `matur/Cargo.lock` — Dependency lock file.
- `matur/test.py` — Python test script for the compiled Rust extension.
- `matur/src/` — Rust source (if present).
- `matur/string_as_sum/` — String-to-sum conversion example.
- `matur/target/` — Rust build artifacts (excluded).

## Key Functions
- Rust functions exposed to Python via PyO3 `#[pyfunction]` attribute.
- `test.py` — Imports and tests the compiled Rust module.

## Data Types
- PyO3-bridged types between Rust and Python.

## Logging
- `print()` in Python test scripts.

## CRUD Entry Points
- **Build**: `cd matur && maturin develop` (builds and installs in current virtualenv)
- **Test**: `python3 test.py`
- **Dependencies**: `pip install maturin`, Rust toolchain

## Style Guide
- maturin project structure (Cargo.toml + pyproject.toml)
- PyO3 attribute macros for Python bindings
