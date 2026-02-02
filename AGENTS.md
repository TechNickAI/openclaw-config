# Project Context for AI Assistants

## Project Overview

Shareable configuration for OpenClaw AI assistant — templates, memory architecture, and integration skills.

## Tech Stack

- Skills: Standalone UV scripts (Python 3.11+, inline dependencies)
- Tests: pytest via `uv run --with pytest pytest tests/ -v`
- No project-level dependencies — each skill is self-contained

## Project Structure

- `skills/` — Integration CLIs (Parallel, Limitless, Fireflies, Quo, OpenClaw)
- `templates/` — AGENTS.md, SOUL.md, USER.md templates for OpenClaw instances
- `memory/` — Example memory architecture structure
- `tests/` — Skill tests (integration tests auto-skip without API keys)

## Code Conventions

DO:
- Skills are standalone UV scripts with `# /// script` inline dependencies
- Each skill has `SKILL.md` (metadata) + executable script (same name as directory)
- Bump `VERSION` file and skill's `SKILL.md` version on changes
- Tests skip gracefully when API keys unavailable

DON'T:
- Add pyproject.toml — this is not a Python package
- Share code between skills — each is self-contained
- Commit API keys or `.env` files

## Git Workflow

Commit style: Conventional or emoji prefix, Co-Authored-By for AI commits.

Example: `Rewrite Parallel.ai skill from Bash to Python`
