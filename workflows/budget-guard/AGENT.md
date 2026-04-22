---
name: budget-guard
version: 0.1.0
description:
  Per-agent and per-cron monthly spend caps with automatic disable on breach.
  Feature pulled from paperclipai/paperclip's "Cost Control" primitive and adapted
  to the OpenClaw fleet shape.
source_upstream: paperclipai/paperclip @ 2026-04-22
source_feature: "Monthly budgets per agent. When they hit the limit, they stop."
---

# Budget Guard

You are the fleet's circuit breaker on LLM spend. Every cron and every long-running
session has a declared monthly budget. When a job crosses its cap, you disable it and
report the breach. When a job approaches its cap, you warn. When nothing is wrong, you
stay silent.

`llm-usage-report` reports what happened. Budget guard **prevents** what shouldn't
happen. That is the difference.

## Why this exists

Paperclip ships "Monthly budgets per agent. When they hit the limit, they stop."
We already gather cost data daily in `llm-usage-report`, but we never act on it.
A single mis-written prompt in a frequent cron can burn hundreds of dollars before
the next day's report lands on Nick's plate. Budget guard closes that loop.

## Definition of Done

### Verification Level: B (self-score + circuit breakers)

This workflow mutates cron state (can disable a cron). All mutations are reversible
by re-enabling, and every mutation is logged with the reason + spend numbers.

### Completion Criteria

- Monthly spend per cron / per agent label was computed for the current calendar
  month up to now
- Each cron with a declared budget in `rules.md#budgets` was checked
- Crons at ≥ 100% of cap were disabled via `openclaw cron update` (or logged for
  manual disable when the CLI is not available)
- Crons at ≥ 80% of cap got a single warning in the Automation topic (dedupe: one
  warning per cron per day)
- Breach + warning events were written to `logs/YYYY-MM.jsonl`
- A short summary was delivered to the Automation topic only if anything actually
  happened (silent on quiet days)

### Output Validation

- No cron is disabled that is not named in `rules.md#budgets`
- No cron is disabled without a breach log entry
- The hard global cap (`rules.md#global_monthly_cap`) pauses ALL non-essential
  crons if exceeded, not just the highest spender

### Circuit Breakers

- **Overreach breaker:** never disable more than 3 crons in a single run. If more
  would trip, pause, alert the human, and stop.
- **Essential breaker:** the list in `rules.md#essential_crons` can never be
  auto-disabled. They warn-only.
- **Data-gap breaker:** if the spend source (`openclaw cost` / session data)
  returned an error or empty set, do NOT act. Warn instead.

## Architecture

Three phases, each cheap:

```
AGGREGATE  →  EVALUATE  →  ACT
(cheap)       (cheap)       (cheap + mutation-gated)
daily 11:55   daily 11:55   daily 11:55 (right before llm-usage-report)
```

### Phase 1 — Aggregate

Run `openclaw cost --since month-start --by cron --json` (or equivalent session
data query). Produce a map: `{cron_id: usd_spent_this_month}`. Include a second
map for `{agent_label: usd_spent_this_month}`. Write to
`logs/aggregate-YYYY-MM-DD.json`.

### Phase 2 — Evaluate

For each entry in `rules.md#budgets`:

- Look up actual spend from Phase 1
- Compute `pct = spent / cap`
- Classify: `ok` (<80%), `warn` (80–99%), `breach` (≥100%)

Produce a decision list. Essential crons are never marked `breach`; they cap at
`warn` with an explicit note.

### Phase 3 — Act

For each `breach` decision:

1. Check the overreach breaker — if this would be the 4th disable in the run, stop.
2. Run `openclaw cron update <id> --enabled false` and capture the response.
3. Append to `logs/YYYY-MM.jsonl` with `{date, cron_id, spent, cap, action:
   "disabled", reason}`.
4. Add to the outbound summary.

For each `warn` decision (not already warned today):

1. Append to `logs/YYYY-MM.jsonl` with `{action: "warned"}`.
2. Add to the outbound summary.

If the outbound summary is empty, deliver nothing. Otherwise, post to Telegram
Automation topic:

```
💰 Budget Guard — YYYY-MM-DD

Disabled (N):
  • <cron-name> — $X.XX / $Y.YY cap (Z%) — disabled. Re-enable: openclaw cron update <id> --enabled true
Warnings (M):
  • <cron-name> — $X.XX / $Y.YY cap (Z%)

Total month-to-date: $A.AA / $B.BB global cap
```

## Cron Setup

One daily check at 11:55 CT, just before `llm-usage-report` at noon so the report
can reflect any actions taken.

```bash
openclaw cron add --name "budget-guard-daily" \
  --cron "55 11 * * *" --tz "America/Chicago" \
  --session isolated --delivery-mode none \
  --model cheap --timeout-seconds 300 \
  --message "Run the budget-guard daily pass. Read workflows/budget-guard/AGENT.md and follow it."
```

The workflow itself posts to the Automation topic when there is something to say;
`--delivery-mode none` avoids a second message from the cron runner.

## First Run — Setup

1. Populate `rules.md#budgets` with starting caps. Err on the side of generous for
   the first month; the goal is to catch runaways, not to micro-manage normal spend.
2. Run once in dry-run mode (`--dry-run` flag described in `scripts/aggregate.sh`)
   and confirm the decision list looks right.
3. Enable the cron only after Nick has seen one dry-run output.

## Rollout Pipeline (per ecosystem-intel-rollout.md)

- **Rung 1 (Nick's box, ≥3 days dry-run):** cron runs, writes logs, emits summary,
  but every `disable` is a no-op (logged as `action: "would-disable"`). Nick reads
  the output for 3 mornings.
- **Rung 2 (friendlies, Åsa opt-in):** enable real disable on Nick's fleet, plus
  one friendly fleet. Two weeks of clean operation.
- **Rung 3 (full fleet):** merge to openclaw-config main, include in next release.
- **Rung 4 (graduate):** after 20 disable events across fleet at ≥ 80% correct
  classification, the `monthly_cap_enforcement` class can go tier-5 auto-apply in
  ecosystem-intel.

## Rollback

Reversible at every rung:

- Phase 1–2 are read-only. Safe to run.
- Phase 3 disables crons. To re-enable: `openclaw cron update <id> --enabled true`.
- To disable the whole workflow: remove the `budget-guard-daily` cron. The logs
  persist so re-enabling later keeps history.

## Attribution

This workflow is a minimal port of Paperclip's "Cost Control" primitive:

> "Monthly budgets per agent. When they hit the limit, they stop. No runaway costs."
> — paperclip.ing/llms.txt

Paperclip enforces this at their control-plane level; we enforce it at the cron
level, which matches the fleet's actual unit of deployment. We do not depend on
Paperclip at runtime.
