# agentic_instructions.md — python_projects/ai

## Purpose
AI/LLM client scripts using LangChain for both local (Ollama) and cloud (OpenAI) model interactions.

## Technology
- Language: Python 3
- Libraries: langchain, langchain_ollama, langchain_core
- Models: Ollama llama3.2 (local), OpenAI ChatGPT (cloud)

## Contents
- `local_ai.py` — Local AI chat using Ollama with LangChain prompt templates and chain invocation. Interactive question loop.
- `oai.py` — OpenAI ChatGPT client using LangChain's ChatOpenAI with multi-shot prompting via HumanMessage/SystemMessage.

## Key Functions
- `local_ai.py::main loop` — Interactive Q&A loop using Ollama model chain.
- `oai.py` — Multi-shot prompt prediction via `chat_model.predict_messages()`.

## Data Types
- `HumanMessage`, `SystemMessage` — LangChain message types.
- `ChatMessagePromptTemplate` — LangChain prompt template.

## Logging
- `print()` for output.

## CRUD Entry Points
- **Run**: `python3 local_ai.py` or `python3 oai.py`
- **Dependencies**: `pip install langchain langchain-ollama`
- **Config**: `OPENAI_API_KEY` environment variable for oai.py.

## Style Guide
- Type annotations on variables
- LangChain chain pattern: `prompt | model`
- Multi-shot prompting via message lists
