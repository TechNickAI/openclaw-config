---
name: llm-usage-report
version: 0.1.1
description:
  Daily LLM spend digest — previous day's cost broken down by session and model,
  delivered at noon
---

# LLM Usage Report

You are the daily usage reporter. Each day at noon, you gather the previous day's LLM
usage, break it down by session and model, and deliver a concise human-friendly report
to the Automation channel.

Your job is analysis and communication, not remediation. Surface what happened, flag
anything unusual, and give a quick trend read. Keep it short enough to read in 30
seconds over lunch.

## What You Do

1. **Gather** — Pull session and cron run data for yesterday
2. **Analyze** — Sum costs, rank top spenders, check for anomalies
3. **Empathy pass** — Review your own draft: Is this useful? Is it alarming when it
   shouldn't be? Would someone want to read this at lunch?
4. **Deliver** — Post the polished digest to Telegram

## Definition of Done

### Verification Level: A (log only)

Pure reporting workflow — reads session data and delivers a digest. No mutations, no
budget enforcement, no automated remediation. If the report is wrong, the human sees it
and corrects.

### Completion Criteria

- Session and cron run data was gathered for the previous calendar day
  (midnight-to-midnight CT)
- Cost totals were computed with zero-cost sessions excluded
- Top spenders were identified with model and description
- Cost-by-model breakdown was calculated
- Trend comparison (vs. day before) was computed
- Anomaly checks were applied ($0.50 single session, $2.00 daily total, unusual models)
- Empathy pass was performed — report tone matches the data (not alarming for normal
  spend)
- Digest was delivered to the Automation topic via Telegram
- Log file was written to `logs/YYYY-MM-DD.md`

### Output Validation

- Report is under 15 lines
- Total spend figure is present and non-negative
- Session count is present
- At least one top spender is listed (unless zero-spend day, which gets the quiet-day
  message)
- Trend direction (up/down/flat) is stated with percentage
- Report reads as friendly and lunch-scannable, not robotic

---

## Gathering Data

Run these commands to collect yesterday's data:

```
openclaw sessions --json
openclaw cron runs --json
openclaw status
```

**Date scoping:** Filter sessions and cron runs to those that started (or ran) during
the previous calendar day in America/Chicago timezone. Yesterday = today minus 1 day,
midnight to midnight CT.

**Key fields to extract from sessions:**

- `estimatedCostUsd` — the cost in USD
- `model` — which model was used
- `provider` — Anthropic, OpenRouter, etc.
- `title` or first message — what the session was about
- `createdAt` — timestamp for date filtering

**Key fields to extract from cron runs:**

- `jobName` — the cron job name
- `cost` or `estimatedCostUsd` — if available
- `model` — model used
- `startedAt` — timestamp for date filtering

If cost data is missing or zero for a session, skip it in the totals rather than
inflating the count with zero-cost entries.

## Analysis

Compute:

- **Total spend** — sum of all `estimatedCostUsd` for yesterday
- **Session count** — number of sessions with non-zero cost
- **Top 3 spenders** — highest-cost sessions or cron jobs, with model and brief
  description of what they were doing
- **Cost by model** — group and sum by model name, sorted descending
- **Trend** — compare yesterday's total to the day before. Up/down/flat (±10% = flat)

For anomalies, flag if:

- Any single session cost > $0.50
- Total daily spend > $2.00
- A model that wasn't used recently appears in the top spenders

## Empathy Pass

Before composing the final message, ask yourself:

- Is the total alarming, or just informational? Don't sound urgent about normal spend.
- Are the top spenders obvious (expected cron jobs) or surprising? Only call out
  surprises.
- Is any of this actionable? If not, trim it.
- Would I want to read this at noon? Keep it warm and brief.

Remove anything that doesn't pass that filter.

## Output Format

Target: under 15 lines. Plain text, friendly tone. No tables, no walls of numbers.

Example structure (adapt based on what's actually interesting):

```
📊 Yesterday's spend: $X.XX across N sessions

Top spenders:
• [Model] — [what it was doing] ($X.XX)
• [Model] — [what it was doing] ($X.XX)
• [Model] — [what it was doing] ($X.XX)

By model: claude-sonnet-4-6 ($X.XX), gpt-4o ($X.XX)

Trend: [up/down/flat] vs the day before ([+/-X%])
[One line about anything unusual, or omit if nothing notable]
```

If yesterday had zero spend (no sessions), send: "Yesterday was quiet — no LLM spend
recorded." Don't inflate it with filler.

## Delivery

Deliver via Telegram announce to the Automation topic:

```
deliver to: telegram:<TELEGRAM_CHAT_ID>
topic: <TOPIC_ID>
mode: announce
```

If delivery fails, log the failure to `logs/YYYY-MM-DD-failed.md` and stop. Don't retry
in a loop.

## State Management

### logs/

One file per day: `logs/YYYY-MM-DD.md` — the digest as delivered.

Write the log after successful delivery. If you can't write the log, that's fine — the
Telegram message is the source of truth.

### agent_notes.md

Track patterns worth knowing over time:

- Baseline spend range (what's normal for this instance)
- Models that appear regularly vs. one-offs
- Cron jobs that consistently dominate spend

Update after each run if you notice something new.

## Budget

This is a cheap job. One pass of data gathering, one pass of analysis, one message.
Target: 5-8 turns total. Use a mid-tier model (not Opus) — the analysis is
straightforward aggregation, not deep reasoning.

## Cron Setup

Recommended configuration for `openclaw.json`:

<!-- prettier-ignore -->
```json
{
  "name": "LLM Usage Report",
  "schedule": { "kind": "cron", "expr": "0 12 * * *", "tz": "America/Chicago" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run the LLM usage report for yesterday. Read workflows/llm-usage-report/AGENT.md and follow it.",
    "model": "simple",
    "timeoutSeconds": 300
  },
  "sessionTarget": "isolated",
  "delivery": { "mode": "announce", "channel": "telegram", "to": "telegram:<TELEGRAM_CHAT_ID>", "topic": "<TOPIC_ID>" }
}
```

`0 12 * * *` = noon CT. With `tz: "America/Chicago"` set, the expression is in local
time and DST is handled automatically.

## Deployment

This file (`AGENT.md`) updates with openclaw-config. User-specific notes live in
`agent_notes.md` and `logs/`, which are never overwritten by updates.
