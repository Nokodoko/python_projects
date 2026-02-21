# agentic_instructions.md — python_projects/ansible

## Purpose
Ansible Tower/AWX project creation script using the awxkit API library.

## Technology
- Language: Python 3
- Libraries: awxkit (Ansible Tower API SDK)

## Contents
- `project_creator.py` — Creates an Ansible Tower project via the API: connects to Tower, defines project parameters (Git SCM), and posts the project.

## Key Functions
- Script-level: Initializes awxkit API connection, defines project data dict, creates project via `tower.projects.post()`.

## Data Types
- `project_data` dict with keys: name, description, organization, scm_type, scm_url, scm_branch, scm_update_on_launch.

## Logging
- `print()` for creation confirmation with project name and ID.

## CRUD Entry Points
- **Run**: `python3 project_creator.py`
- **Config**: Update base_url, username, password, and scm_url before use.

## Style Guide
- awxkit API pattern for Tower resource management
- Dictionary-based resource definition
