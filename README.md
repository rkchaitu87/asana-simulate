# Asana-like Workspace Simulation (SQLite)

This repository generates a realistic Asana-like enterprise workspace database in SQLite, including:
- organizations, teams, users, team memberships
- projects, sections
- tasks + subtasks (self-referential hierarchy)
- comments, tags + task_tags
- project-specific custom fields + task values

The goal is to produce realistic seed data suitable for downstream agent training/evaluation.


## Setup (Windows)
```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m src.main


## OUTPUT
output/asana_simulation.sqlite

Repo contains a reproducible generator for an Asana-like enterprise workspace in SQLite. Run python -m src.main to regenerate output/asana_simulation.sqlite.