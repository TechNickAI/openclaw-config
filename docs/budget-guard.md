# Budget Guard

Per-cron and per-agent monthly LLM spend caps with automatic disable on breach.

## What it does

Once a day at 11:55 CT, `budget-guard` reads month-to-date spend and compares
each cron / agent label against caps declared in `workflows/budget-guard/rules.md`.

| State | Threshold | Action |
| --- | --- | --- |
| `ok` | < 80 % of cap | nothing |
| `warn` | 80 – 99 % | one-time daily warning to `📋 Automation` |
| `breach` | ≥ 100 % | disable the cron, log it, post to `📋 Automation` |

Essential crons (listed in `rules.md#essential_crons`) max out at `warn`.
They never auto-disable.

## Why we built it

`llm-usage-report` shows yesterday's spend at noon. By the time you see the
report, a runaway cron has already burned 24h of budget. Budget guard catches
the runaway in-flight and stops it.

The pattern is borrowed from `paperclipai/paperclip`'s "Cost Control" primitive.
Paperclip enforces budgets at the agent level inside their control plane. We
enforce at the cron level because that matches the OpenClaw fleet's actual unit
of deployment.

## Setup

```bash
openclaw cron add --name "budget-guard-daily" \
  --cron "55 11 * * *" --tz "America/Chicago" \
  --session isolated --delivery-mode none \
  --model cheap --timeout-seconds 300 \
  --message "Run the budget-guard daily pass. Read workflows/budget-guard/AGENT.md and follow it."
```

First run lives in dry-run mode. Edit `rules.md`:

- Set per-cron caps under `budgets:` after one run shows you what real spend
  looks like.
- Flip `mode: dry_run` → `mode: enforce` after 3 days of clean dry-run output.

## Rolling back

- Disable the cron: `openclaw cron remove <id>`.
- Re-enable a cron that budget-guard disabled:
  `openclaw cron update <id> --enabled true`.
- Logs persist in `workflows/budget-guard/logs/YYYY-MM.jsonl` even after the
  workflow is removed.

## Related

- [Ecosystem Intel rollout](../memory/ventures/ecosystem-intel-rollout.md) — this
  workflow is the first feature shipped through the test → friendlies → fleet
  ladder.
- [Paperclip](https://paperclip.ing/) — upstream concept source. We do not
  depend on Paperclip at runtime.
