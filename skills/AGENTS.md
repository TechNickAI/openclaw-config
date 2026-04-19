# Skills Development Guide

How to build, structure, and maintain OpenClaw skills.

## What Skills Are

Skills are self-contained tools that extend OpenClaw's capabilities. Each skill lives in
its own directory under `skills/` and is either:

- **Executable** — a runnable script (Python or Bash) that the gateway invokes as a CLI
- **Documentation-only** — a SKILL.md that teaches the agent how to perform a task using
  existing tools (no script needed)

Skills are standalone. No shared code between skills, no project-level dependencies.
Each skill carries its own inline dependency declaration.

## Directory Structure

```
skills/
  my-skill/
    SKILL.md          # Required — metadata + documentation
    my-skill          # Optional — executable script (name matches directory)
```

The executable script name must match the directory name exactly, with no file
extension.

## SKILL.md Format

Every skill requires a SKILL.md with YAML frontmatter followed by markdown
documentation.

### Required Fields

```yaml
name: my-skill
version: 0.1.0
description: One-line description of what the skill does
triggers:
  - keyword that activates this skill
  - alternate phrasing
  - related concept
metadata:
  openclaw:
    emoji: "\U0001F527"
```

- **name** — kebab-case, matches the directory name
- **version** — semver (bump on every change)
- **description** — concise, action-oriented (what it does, not what it is)
- **triggers** — 5-10 phrases that should activate this skill. Include synonyms,
  alternate phrasings, and the specific domain terms users would say
- **emoji** — single emoji shown in skill listings

### Optional Fields

```yaml
metadata:
  openclaw:
    emoji: "\U0001F525"

    # API key configuration (for skills that call external APIs)
    apiKey:
      env: SERVICE_API_KEY # environment variable name
      getFrom: https://... # URL where user can get the key

    # Platform restriction
    platform: macos # only available on this platform

    # Deprecation
    deprecated: true
    replacement: other-skill # what to use instead

    # Binary dependencies
    requires:
      bins: [some-binary]

    # Complex installation steps
    install:
      - id: tool-name
        kind: go
        module: github.com/org/tool@latest
        bins: [tool-name]
        label: "Install tool (go install)"

    # Skill category
    category: productivity
```

Use `apiKey.env` and `apiKey.getFrom` for API key configuration — not `primaryEnv` or
other variants.

### Markdown Content

After the frontmatter, document the skill for the AI agent that will use it. Structure
varies by skill type, but generally include:

- What the skill does and when to use it
- Setup instructions (API keys, prerequisites)
- Available commands (for executable skills)
- Usage examples
- Edge cases or limitations

## Python Script Conventions

### Shebang and Dependencies

Every Python skill starts with:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["httpx>=0.28"]
# ///
```

The `uv run --script` shebang makes the script self-installing — dependencies are
resolved automatically on first run. No virtualenv, no pip install.

### Script Structure

Follow this ordering:

```python
#!/usr/bin/env -S uv run --script
# /// script
# ...
# ///
"""Module docstring — one line describing the skill CLI."""

# Standard library imports
import json
import os
import sys

# Third-party imports
import httpx

# Constants
API_URL = "https://api.example.com"
DEFAULT_LIMIT = 10

# --- Helpers ---

def get_api_key() -> str | None:
    """Get API key from environment."""
    return os.environ.get("SERVICE_API_KEY", "").strip() or None

def error(message: str, hint: str | None = None) -> NoReturn:
    """Print error message to stderr and exit."""
    print(f"Error: {message}", file=sys.stderr)
    if hint:
        print(hint, file=sys.stderr)
    sys.exit(1)

# --- Commands ---

def cmd_list(args: list[str]) -> None: ...
def cmd_get(args: list[str]) -> None: ...

def cmd_help() -> None:
    """Show help message."""
    print("""my-skill CLI - Description of the skill

Commands:
  list                 List items
  get <id>             Get a specific item by ID

Environment:
  SERVICE_API_KEY      Required - API key for the service

Examples:
  my-skill list
  my-skill get abc123

Get your API key: https://...""")

# --- Entry point ---

def main() -> None:
    """Main entry point."""
    args = sys.argv[1:]
    command = args[0] if args else "help"

    commands = {
        "list": cmd_list,
        "get": cmd_get,
    }

    if command in ("help", "--help", "-h"):
        cmd_help()
    elif command in commands:
        commands[command](args[1:])
    else:
        error(f"Unknown command: {command}", "Run 'my-skill help' for available commands")

if __name__ == "__main__":
    main()
```

### CLI Pattern: sys.argv + Commands Dict

The standard pattern for skill CLIs:

- Parse commands from `sys.argv[1:]` — no CLI framework needed
- Route via a `commands` dict inside `main()`
- Accept `help`, `--help`, and `-h` for help text
- Command functions receive `args: list[str]` (remaining arguments after the command)

**When to use argparse instead:** When a subcommand has complex flag combinations
(multiple optional flags like `--person`, `--from`, `--to`, `--limit`). Simple
positional arguments don't need argparse.

### Error Handling

Every script must include the `error()` helper:

```python
from typing import NoReturn

def error(message: str, hint: str | None = None) -> NoReturn:
    """Print error message to stderr and exit."""
    print(f"Error: {message}", file=sys.stderr)
    if hint:
        print(hint, file=sys.stderr)
    sys.exit(1)
```

Use it for all fatal errors. The `hint` parameter provides actionable guidance:

```python
error("FIREFLIES_API_KEY not set", "Get your key from: https://app.fireflies.ai/...")
```

For API skills, also handle HTTP errors:

```python
try:
    response.raise_for_status()
except httpx.HTTPStatusError as exc:
    error(f"API error {exc.response.status_code}: {exc.response.text}")
```

### API Key Pattern

```python
def get_api_key() -> str | None:
    """Get API key from environment."""
    return os.environ.get("SERVICE_API_KEY", "").strip() or None
```

- Environment variable naming: `SERVICE_API_KEY` (uppercase, underscored)
- Return `None` when not set (don't raise — let the caller decide when a key is needed)
- Validate early in commands that need the key:

```python
def cmd_list(args: list[str]) -> None:
    api_key = get_api_key()
    if not api_key:
        error("SERVICE_API_KEY not set", "Get your key from: https://...")
```

### Output Format

- **API wrapper skills** — output JSON (the agent parses it)
- **Utility skills** — output plain text when human-readable is more useful
- Use `json.dumps(data, indent=2)` for JSON output
- Write errors to stderr, data to stdout

### Type Hints

Use modern Python type syntax throughout:

```python
# Yes
def get_items(limit: int = 10) -> list[dict[str, Any]]: ...
def get_api_key() -> str | None: ...

# No
def get_items(limit: int = 10) -> List[Dict[str, Any]]: ...
def get_api_key() -> Optional[str]: ...
```

## Bash Script Conventions

For simple wrappers around existing CLIs:

```bash
#!/usr/bin/env bash
# Description of what this wrapper does

set -euo pipefail

# Validate prerequisites before any work
case "${1:-}" in
    "" | --version | --help | -h | help) ;;
    *)
        if [[ -z "${SERVICE_API_KEY:-}" ]]; then
            echo "Error: SERVICE_API_KEY not set" >&2
            exit 1
        fi
        ;;
esac

# ... implementation
```

- Always `set -euo pipefail`
- Errors to stderr
- Validate API keys before doing work
- Allow `--help`, `--version`, and no-arg invocation without authentication

## Documentation-Only Skills

When a skill teaches the agent a methodology rather than wrapping a tool, it needs only
a SKILL.md — no executable script. The entire skill lives in the markdown documentation.

Examples: prompt engineering techniques, delegation strategies, workflow design
patterns.

Keep documentation-only SKILL.md files focused and actionable. The agent reads this at
runtime, so every paragraph should earn its place.

## Testing

Skills are tested with pytest via uv:

```bash
uv run --with pytest pytest tests/ -v
```

- Test files live in `tests/` at the repo root (not inside skill directories)
- Integration tests that need API keys should skip gracefully:

```python
import pytest
import os

pytestmark = pytest.mark.skipif(
    not os.environ.get("SERVICE_API_KEY"),
    reason="SERVICE_API_KEY not set"
)
```

## Checklist for New Skills

- [ ] Directory name is kebab-case, matches script name (if executable)
- [ ] SKILL.md has all required fields (name, version, description, triggers, emoji)
- [ ] Version starts at 0.1.0
- [ ] Script uses `#!/usr/bin/env -S uv run --script` shebang (Python)
- [ ] Inline dependencies declared with `# /// script` block
- [ ] `requires-python = ">=3.13"`
- [ ] Has `error()` helper function
- [ ] Has `get_api_key()` if calling an external API
- [ ] Handles `help`, `--help`, and `-h`
- [ ] Commands dict inside `main()`, not module-level
- [ ] `if __name__ == "__main__": main()` at bottom
- [ ] SKILL.md uses `apiKey.env` / `apiKey.getFrom` (not `primaryEnv`)
- [ ] Bump root `VERSION` file
- [ ] Update `README.md` skill table
