---
name: todoist
version: 0.2.0
description: Manage Todoist tasks, projects, and labels via official CLI
triggers:
  - todoist
  - task management
  - todo list
  - create task
  - complete task
metadata:
  openclaw:
    emoji: "✅"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/todoist
    category: productivity
    requires:
      bins: [td]
    install:
      - id: todoist-cli
        kind: node
        package: "@doist/todoist-cli"
        bins: [td]
        label: Install Todoist CLI (npm)
    apiKey:
      env: TODOIST_API_TOKEN
      getFrom: https://todoist.com/app/settings/integrations/developer
---

# Todoist ✅

Task and project management via the official Todoist CLI (`td` from
`@doist/todoist-cli`). No wrapper script — call `td` directly.

## Setup

Before using any commands, ensure `td` is installed and authenticated.

### Check if installed

```bash
command -v td
```

If missing, install it:

```bash
npm install -g @doist/todoist-cli
```

### Check if authenticated

```bash
td auth status
```

If not authenticated, guide the user:

1. "You'll need a Todoist API token. Grab one from
   https://todoist.com/app/settings/integrations/developer"
2. Once they provide it: `td auth token <THEIR_TOKEN>`
3. Verify: `td auth status` should show their email and name

The token can also be set via `TODOIST_API_TOKEN` environment variable (useful for
OpenClaw gateway config).

## Daily Views

```bash
td today                              # Due today + overdue
td upcoming                           # Next 7 days
td upcoming 14                        # Next 14 days
td inbox                              # Inbox tasks
td completed                          # Completed today
td completed --since 2026-04-01       # Completed since date
td stats                              # Karma, streaks, totals
```

## List & Filter Tasks

```bash
td task list                          # All active tasks
td task list --project "Work"         # By project name
td task list --label "urgent"         # By label
td task list --priority p1            # By priority
td task list --filter "today | overdue"  # Todoist filter syntax
td task list --assignee me            # Assigned to me
td task list --json                   # JSON output when needed
td task list --all                    # All results (no 300 limit)
```

### Todoist Filter Syntax

Filters are powerful — some useful patterns:

- `today` — due today
- `overdue` — past due
- `today | overdue` — both
- `no date` — tasks without a due date
- `p1` — priority 1 (urgent)
- `#Work` — in project "Work"
- `@urgent` — has label "urgent"
- `assigned to: me` — assigned to me
- `created before: -7 days` — created in last week
- `due before: tomorrow` — due today or earlier

## Task Details

```bash
td task view id:abc123                # View by ID
td task view "Buy groceries"          # View by name
```

## Create Tasks

```bash
# Structured creation — use this for precise control
td task add "Buy groceries" --due tomorrow --priority p2
td task add "Review PR" --project "Work" --labels "code,urgent"
td task add "Write report" --description "Q1 summary" --due "next friday"
td task add "Team standup" --due "every weekday at 9am"

# Natural language quick-add — use for casual/conversational input
td add "Call dentist tomorrow at 3pm #health p1"
```

## Update Tasks

```bash
td task update id:xxx --content "New title"
td task update id:xxx --due "next monday" --priority p3
td task update id:xxx --labels "work,urgent"
td task update id:xxx --description "Updated notes"
```

## Complete / Reopen / Delete

```bash
td task complete id:xxx
td task uncomplete id:xxx             # Reopen
td task delete id:xxx --yes           # --yes skips confirmation prompt
```

## Move Tasks

```bash
td task move id:xxx --project "Work"
td task move id:xxx --section "In Progress"
```

## Projects

```bash
td project list                       # All projects
td project list --json                # JSON output
td project view "Work"                # Project details
td project create --name "New Project" --color berry_red
```

## Sections

```bash
td section list --project "Work"
td section create --project "Work" --name "In Progress"
```

## Labels

```bash
td label list
td label create --name "urgent" --color red
```

## Comments

```bash
td comment add id:xxx --content "Progress update"
td comment list id:xxx
```

## Activity

```bash
td activity                           # Recent activity log
```

## Output

Plain text by default — readable by humans and LLMs. Add `--json` to any list command
when you need to extract specific fields programmatically.

Use `--quiet` to suppress success messages (create commands still print the ID).

## Agent Tips

- Use `td task add` for structured creation with flags — not `td add`
- `td add` is natural language only (like Todoist's quick-add bar)
- References accept names (`"Work"`) or explicit IDs (`id:xxx`)
- Delete always requires `--yes` to confirm
- Recurring tasks: use `--due "every monday"` or `"every weekday at 9am"`
- Priority scale: p1 (urgent/red) → p4 (no priority) — p1 is highest

## Troubleshooting

| Symptom                 | Fix                                                |
| ----------------------- | -------------------------------------------------- |
| `td: command not found` | `npm install -g @doist/todoist-cli`                |
| `No API token found`    | `td auth token <TOKEN>` or set `TODOIST_API_TOKEN` |
| `HTTP 429`              | Rate limited — wait a moment and retry             |
| `HTTP 403`              | Token invalid or expired — re-authenticate         |

## Workflow Integration

Works with the `task-steward` workflow for automated task management.
