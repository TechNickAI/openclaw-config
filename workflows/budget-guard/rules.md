# Budget Guard — Instance Rules

Per-fleet configuration for `budget-guard`. This file is instance-owned and is NOT
overwritten by `openclaw-config` updates once it exists.

## Delivery

- **Channel:** `telegram`
- **Target chat:** `469214633`
- **Topic:** `70103` (📋 Automation)

## Mode

- `mode: dry_run` — set to `enforce` only after Nick has seen at least 3 days of
  dry-run output and approved the decision list.

## Global cap

- `global_monthly_cap_usd: 200` — start generous; the report shows real spend has
  been well under this. Adjust after one month.

## Essential crons (warn-only, never auto-disabled)

These crons are load-bearing for the fleet's ability to keep running. They can
generate warnings but `budget-guard` will never disable them automatically.

- `cron-healthcheck`
- `budget-guard-daily` (this workflow itself)
- `llm-usage-report`
- `security-sentinel-*`
- Any cron whose name contains `forward-motion` (drives stuck-thread recovery)

## Per-cron budgets

Format:

```yaml
- cron_id: <uuid>
  name: <human name>
  monthly_cap_usd: <number>
  notes: <why this cap>
```

Starting list — populate after the first dry-run shows real spend per cron:

```yaml
budgets:
  # Filled in after first dry-run aggregate. Until then, only the global cap
  # applies and individual crons cannot be auto-disabled.
  []
```

## Per-agent-label budgets

For long-running named sessions (Cora's main thread, sub-agent labels). Same
shape as cron budgets:

```yaml
agent_budgets:
  - label: "cora-main"
    monthly_cap_usd: 100
    notes: "Cora's main session — generous, this is the primary surface."
  - label: "ecosystem-intel-*"
    monthly_cap_usd: 25
    notes: "All ecosystem-intel sub-agents combined."
```

## Hard rules

- Never disable a cron not named in `budgets:`.
- Never disable an `essential_crons` entry.
- Never act on data older than 24 hours.
- Always log the spend numbers that triggered the action.
- Default to inaction when uncertain.

## Pilot cohort

- `pilot_cohort: [nick]` until rung 2.
- Add `asa` after rung 1 passes ≥ 3 days dry-run with no false-positive disables.
