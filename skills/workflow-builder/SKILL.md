---
name: workflow-builder
version: 0.4.0
description:
  Design, build, and maintain autonomous OpenClaw workflows (stewards). Use when
  creating new workflow agents, improving existing ones, evaluating automation
  opportunities, or debugging workflow reliability. Triggers on "build a workflow",
  "create a steward", "automate this process", "workflow audit", "what should I
  automate", "create a cron job", "schedule a recurring task", "build a scheduled job".
triggers:
  - build a workflow
  - create a steward
  - automate this process
  - workflow audit
  - what should I automate
  - create a cron job
  - schedule a recurring task
  - build a scheduled job
metadata:
  openclaw:
    emoji: "🏗️"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/workflow-builder
    category: productivity
---

# Workflow Builder 🏗️

The meta-skill for designing and building autonomous OpenClaw workflows. A workflow
(steward) is an autonomous agent that runs on a schedule, maintains state, learns over
time, and does real work without prompting.

**Skills vs Workflows:**

- **Skill** = single-purpose tool (how to use a CLI, API, or pattern)
- **Workflow** = autonomous agent with state, learning, and scheduling

---

## Part 1: Should You Automate This?

Not everything deserves a workflow. Use this framework to decide.

### The Automation Audit

For any candidate task, score these dimensions:

| Dimension             | Question                                                                       | Score |
| --------------------- | ------------------------------------------------------------------------------ | ----- |
| **Frequency**         | How often? (daily=3, weekly=2, monthly=1, rare=0)                              | 0-3   |
| **Repetitiveness**    | Same steps every time? (always=3, mostly=2, sometimes=1, never=0)              | 0-3   |
| **Judgment Required** | Needs creative thinking? (none=3, low=2, medium=1, high=0)                     | 0-3   |
| **Time Cost**         | Minutes per occurrence × frequency per month / 60 = hours/month                | raw   |
| **Safety**            | How safe to automate? (harmless if wrong=3, annoying=2, costly=1, dangerous=0) | 0-3   |

**Decision:**

- Score ≥ 10 + Time Cost > 2 hrs/month → **Build a workflow**
- Score 7-9 → **Add to heartbeat checklist** (batch with other checks)
- Score < 7 → **Keep manual** or add as a cron one-liner

### ROI Calculator

```
Setup Time (hours) × $50 = Setup Cost
Time Saved (hours/month) × $50 = Monthly Value
Payback = Setup Cost / Monthly Value

< 2 months payback → Build it now
2-6 months → Build when you have time
> 6 months → Probably not worth it
```

### Workflow vs Heartbeat vs Cron

| Approach               | When to Use                                         |
| ---------------------- | --------------------------------------------------- |
| **Workflow (steward)** | Needs state, learning, rules, multi-step processing |
| **Heartbeat item**     | Quick check, batch with others, context-aware       |
| **Cron (isolated)**    | Exact timing, standalone, different model           |
| **Cron (main)**        | One-shot reminder, system event injection           |

**Rule of thumb:** If it needs `rules.md` and `agent_notes.md`, it's a workflow. If it's
a 2-line check, add it to HEARTBEAT.md.

---

## Part 2: Workflow Anatomy

Every workflow follows this structure:

```
workflows/<name>/
├── AGENT.md          # The algorithm (updates with openclaw-config)
├── rules.md          # User preferences (never overwritten by updates)
├── agent_notes.md    # Learned patterns (grows over time, optional for some types)
├── state/            # Continuation state for multi-step work (optional)
│   └── active-work.json
└── logs/             # Execution history (auto-pruned)
    └── YYYY-MM-DD.md
```

### AGENT.md — The Algorithm

This is the workflow's brain. It ships with openclaw-config and can be updated.

**Standard sections** (adapt to your workflow — not all are required):

```markdown
---
name: <workflow-name>
version: <semver>
description: <one-line description>
---

# <Workflow Name>

<One paragraph: what this workflow does and why it exists.>

## Prerequisites

<What tools/access/labels/setup are needed before first run.>

## First Run — Setup Interview

<Interactive setup that creates rules.md. Ask preferences, scan existing data, suggest
smart defaults. Always let the user skip/bail early.>

## Regular Operation

<The main loop: what to read, how to process, when to alert, what to log.>

## Housekeeping

<Daily/weekly maintenance: log pruning, data cleanup, self-audit.>
```

### rules.md — User Preferences

Created during first-run setup interview. **Never overwritten** by updates.

**Pattern:**

```markdown
# <Workflow> Rules

## Account

- account: user@example.com
- alert_channel: whatsapp (or: none, telegram, slack)

## Preferences

- <workflow-specific settings>

## VIPs / Exceptions

- <people or patterns to handle specially>
```

### agent_notes.md — Learned Patterns

The workflow writes here as it learns. Accumulates over time.

**Pattern:**

```markdown
# Agent Notes

## Patterns Observed

- <sender X always sends receipts on Fridays>
- <task type Y usually takes 2 hours>

## Failures & Corrections

### YYYY-MM-DD: <brief description>

- What happened: <what the workflow did>
- Why it was wrong: <why it was incorrect>
- Correct action: <what should have happened>
- New rule: <guardrail to prevent recurrence>
- Applied to: <where the rule was added, e.g., rules.md VIP section>

## Improvement Proposals

- <AGENT.md is ambiguous about X — suggest clarifying to Y>
- <Tool Z fails silently when API is down — suggest adding health check>

## Optimizations

- <batch processing senders A, B, C saves 3 API calls>
```

### logs/ — Execution History

One file per day, auto-pruned after 30 days.

**Pattern:**

```markdown
# <Workflow> Log — YYYY-MM-DD

## Run: HH:MM

### Actions

- Processed: N items
- Actions: archived X, deleted Y, alerted on Z
- Errors: none
- Duration: ~Ns

### Scorecard

| Dimension    | Stars          | Notes                         |
| ------------ | -------------- | ----------------------------- |
| Completeness | ⭐⭐⭐⭐ (4)   | 1 item deferred (API timeout) |
| Accuracy     | ⭐⭐⭐⭐⭐ (5) | All classifications clear     |
| Judgment     | ⭐⭐⭐ (3)     | Unsure about sender X         |
| Overall      | ⭐⭐⭐⭐ (4)   |                               |

Confidence: HIGH

Source: self | verified (indicate whether cross-context verifier ran)
```

### Definition of Done

Every workflow must declare what "done" looks like for a single run. This is the
contract between the workflow and whoever (human or auditor) evaluates it.

**Three components:**

#### Completion Criteria

Concrete, checkable conditions that constitute a successful run. Not "process emails"
but:

- All unread emails in target labels have been classified
- No email remained in an ambiguous state without escalation
- All actions logged with item IDs

These are binary pass/fail checks. If any fail, the run is incomplete.

#### Output Validation

Structural checks to run on the output before declaring done:

- Expected output format (log entry, state update, notification sent)
- Required fields present (item counts, action summaries, error list)
- Side effects confirmed (database updated, labels applied, alerts delivered)

These can be checked deterministically — no LLM judgment needed.

#### Quality Rubric

3-5 scored dimensions specific to this workflow, each on a 1-5 gold star scale:

| Score      | Meaning                                                       |
| ---------- | ------------------------------------------------------------- |
| ⭐⭐⭐⭐⭐ | Excellent — no issues, confident in all decisions             |
| ⭐⭐⭐⭐   | Good — minor uncertainties, all resolved reasonably           |
| ⭐⭐⭐     | Acceptable — some judgment calls the user might disagree with |
| ⭐⭐       | Poor — likely errors, should flag for human review            |
| ⭐         | Failed — wrong actions taken, rollback recommended            |

**Example rubric for an email steward:**

| Dimension        | What it measures                                    |
| ---------------- | --------------------------------------------------- |
| Completeness     | Were all eligible items processed?                  |
| Accuracy         | Were classifications/actions correct?               |
| Judgment quality | Were edge cases handled well or properly escalated? |
| Alert relevance  | Were alerts appropriate (not noisy, not silent)?    |

The rubric goes in AGENT.md. Scores go in the run log. Over time, score trends reveal
drift — a workflow averaging 4.5 that drops to 3.2 over a week signals something
changed.

#### Verification Level

Not every workflow needs cross-context verification. The right level depends on two
questions: **can you undo it?** and **who sees the output?**

```
                        Only user sees it       Others see it
                        ─────────────────       ─────────────
Reversible              Level A: Log only       Level B: Self-score
Irreversible            Level B: Self-score     Level C: Full verify
```

**Level A — Log only.** Just log what you did. No scorecard, no verification. For
read-only workflows, reports, and briefings where the output is informational.

**Level B — Self-score + circuit breakers.** Score each run on the quality rubric.
Auto-demote trust level if quality drops. No cross-context verification — the scorecard
catches drift over time without the per-run token cost. For workflows whose actions are
reversible or only affect the user.

**Level C — Full verification.** Self-score + cross-context verifier + circuit breakers.
The fresh-context reviewer earns its cost because mistakes can't be undone and other
people are affected. For workflows that send messages, publish content, or take
irreversible actions visible to others.

**Declare the level in AGENT.md** so both the workflow and auditor know what's expected.

**Examples:**

| Workflow         | Reversible? | Audience | Level           |
| ---------------- | ----------- | -------- | --------------- |
| email-steward    | Yes         | User     | B — Self-score  |
| calendar-steward | Yes         | User     | A — Log only    |
| contact-steward  | Partial     | User     | B — Self-score  |
| forward-motion   | No          | Others   | C — Full verify |
| llm-usage-report | Yes         | User     | A — Log only    |

---

## Part 3: Design Patterns

### Pattern 1: Setup Interview

Every workflow should start with an interactive setup that creates `rules.md`.

**Best practices:**

1. Check prerequisites first (API access, labels, etc.)
2. Ask questions one category at a time
3. Offer smart defaults based on scanning existing data
4. Let the user skip or bail early ("looks good, skip to the end")
5. Summarize rules in plain language before saving
6. Always include an escape hatch: `alert_channel: none`

### Pattern 2: Graduated Trust

Trust is earned by performance, not elapsed time. Use run scorecard scores (see
Definition of Done) to gate autonomy levels.

```
Level 1 — Supervised:
  Human reviews all actions before execution.
  Advance → 20 consecutive runs at ⭐⭐⭐⭐ or above

Level 2 — Monitored:
  Acts autonomously, human reviews logs daily.
  Advance → 50 consecutive runs at ⭐⭐⭐⭐ or above
  Demote  → 3 runs below ⭐⭐⭐

Level 3 — Autonomous:
  Acts and logs, human reviews weekly.
  Advance → 100 consecutive runs at ⭐⭐⭐⭐ or above
  Demote  → 3 runs below ⭐⭐⭐ → back to Level 2

Level 4 — Trusted:
  Fully autonomous, quality auditor watches trends.
  Demote  → quality auditor flags degradation → back to Level 3
```

**Store trust state in `rules.md`** so the user can see and override it:

```markdown
## Trust

- trust_level: 2
- consecutive_good_runs: 14
- cooldown_remaining: 0
```

The workflow reads these at the start of each run and updates them at the end:

- **Level 1:** Present proposed actions, wait for approval before executing
- **Level 2-4:** Execute, then log actions for review

**Starting point:** New workflows default to Level 1. But for low-stakes workflows
(health checks, notifications, reports), **the user should promote to Level 2 during
setup** to avoid unnecessary babysitting. The setup interview should offer this choice:
"Should I run independently and you review the logs, or would you prefer to approve each
action first?"

**Why Level 1 scores are trustworthy despite self-reporting:** At Level 1, the human
reviews every proposed action before execution. If the workflow consistently proposes
wrong actions that the human corrects, the human will notice — even if the self-scores
are inflated. Human review IS the verification gate at Level 1. Cross-context
verification activates at Level 2 to replace the human as the independent check.

Write confidence thresholds to `rules.md` so the user can tune them.

### Pattern 3: Sub-Agent Orchestration

Match intelligence to task complexity, and **always use sub-agents for loops.**

#### Rule: Never Loop Over Collections in the Orchestrator

**Any time you iterate over a list (contacts, emails, tasks, records), spawn a sub-agent
per item.** This preserves the parent context for coordination and prevents pollution.

**Pattern:**

```
Orchestrator (parent):
1. Fetch the list (from API, file, database)
2. Query tracking state to filter already-processed items
3. FOR EACH new item: Spawn a sub-agent with that item's details
4. Sub-agent processes one item, returns structured result
5. Parent collects results, updates tracking state, alerts if needed

Sub-agent:
- Receives: One item + context needed for that item
- Does: All the reasoning, decision-making, work
- Returns: Structured summary (status, action taken, errors, alerts)
- Never accesses parent's full context
```

**Why:** Each sub-agent gets a fresh context window. Parent stays clean for
orchestration logic. No pollution from per-item reasoning.

#### Model Selection: Check-Work Tiering for High-Frequency Jobs

For jobs running every few minutes (e.g., every 5 min, every 15 min):

**Two-stage pattern:**

```
Stage 1 (Cheap): Use simple to ask "Is there any work to do?"
  - Cheap to run often
  - Quick predicate check (yes/no)
  - Examples: "Any new emails?", "Any cron job failures?", "Any security alerts?"

Stage 2 (Expensive): If yes, spawn work/think to do the actual work
  - Only spawned when there's real work
  - Has full context for reasoning/decisions
  - Saves tokens on empty runs
```

**Example:**

```
Cron job runs every 5 minutes:
1. simple runs: "Are there any unprocessed emails in my inbox?"
   → Returns boolean (with brief explanation)
2. If yes: Spawn work to "Process and categorize these 3 emails"
   → Does the actual work
3. If no: Skip expensive processing, return early
   → Save ~90% tokens on empty runs
```

**Model selection for different complexities:**

```
High-frequency checks (every 5-15 min) → simple to check, work/think to act
Obvious/routine items → Spawn sub-agent (cheaper model: work)
Important/nuanced items → Handle yourself or spawn a powerful sub-agent (think)
Quality verification → Can use a strong model as QA reviewer (think as sub-agent)
Uncertain items → Sub-agents escalate to you rather than guessing
```

**Note:** Don't hardcode model IDs (they go stale fast). Use role-based aliases:
`cheap`, `simple`, `work`, `chat`, `think`, `verify`.

### Pattern 4: State Externalization — Contextual State vs Tracking State

**Critical:** Chat history is a cache, not the source of truth. After every meaningful
step, write state to disk. But distinguish between two types:

#### 4a. Contextual State (Markdown only)

**What:** Information the agent reasons about or learns over time. **Examples:**
`agent_notes.md`, `rules.md`, daily logs, decision summaries. **Format:** Markdown.
Always human-readable. **Why markdown:** These belong in context so the agent can reason
about them.

```markdown
# agent_notes.md

## Patterns Observed

- Contact X always sends updates on Tuesdays
- Task type Y typically needs 2-hour blocks

## Mistakes Made

- Once skipped important sender — now review sender importance before filtering
```

#### 4b. Tracking State (SQLite only)

**What:** Deduplication, "have I seen this?", processed IDs, state queries.
**Examples:** `processed.db` with tables for seen IDs, statuses, timestamps. **Format:**
SQLite database with structured queries. **Why SQLite:** The agent doesn't reason about
this — it only queries it. SQLite gives O(1) lookups without loading the entire history
into context.

⚠️ **NEVER use JSON for state files.** You are an LLM, not a JSON parser. JSON is useful
for API responses and tool output flags, but state files should be markdown
(human-readable) or SQLite (queryable). JSON state files create noise, parsing errors,
and waste context on structure rather than content.

The workflow's `db-setup.md` defines the specific schema. The calling LLM writes the SQL
— don't over-prescribe queries in AGENT.md. Just describe what should happen (e.g.,
"check if already processed", "mark as classified", "clean up entries older than 90
days") and let the LLM write the appropriate queries.

#### Schema Versioning & Migration

Every workflow that uses SQLite should track schema versions using SQLite's built-in
`PRAGMA user_version` (an integer stored in the database header — no extra tables):

1. **Put the schema inline in AGENT.md** — the LLM needs it to write queries anyway
2. **Declare the expected version** (e.g., `PRAGMA user_version: 1`)
3. **Each run checks:** `PRAGMA user_version`
   - Matches → proceed
   - Lower or missing → create tables / apply migrations / set user_version
4. **If legacy state files exist** (e.g., `processed.md`), migrate entries and archive

See `workflows/contact-steward/AGENT.md` for a reference implementation.

**Rule in AGENT.md:** "On every run, read contextual state first (agent_notes.md,
rules.md). Query tracking state via SQLite — one version check, then targeted queries.
After processing, update both as needed. Never load tracking history into context."

### Pattern 5: Error Handling & Alerting

Every workflow must handle failures gracefully:

1. **Log errors** to daily log with full context
2. **Alert on critical failures** (unless `alert_channel: none`)
3. **Never fail silently** — if something breaks, the human should know
4. **Quarantine, don't destroy** — use labels/tags, not deletion
5. **Route all errors to one place** — consistent error channel

**Alert hierarchy** (prevents alert fatigue from multiple channels):

- **Real-time alerts:** Circuit breakers only — trust level demotions, single-⭐ events.
  These are push notifications that demand attention.
- **Periodic reports:** Quality auditor findings — delivered on schedule (daily/weekly),
  not pushed. The human pulls these during review.
- **Audit-session only:** Improvement proposals in agent_notes.md — surfaced during
  monthly audits, not pushed to the user.

One urgent channel, one periodic channel, one on-demand channel. If a struggling
workflow sends alerts from all three, something is wrong with the alert configuration.

### Pattern 6: Integration Points

Workflows should declare how they connect to other workflows:

```markdown
## Integration Points

### Receives From

- email-steward: Emails needing follow-up → creates task

### Sends To

- task-steward: Creates tasks when work is discovered
- message channel: Alerts when human attention needed

### Shared State

- None (or: reads from workflows/shared/contacts.md)
```

### Pattern 7: Cross-Context Verification

LLMs have a blind spot for their own errors — research shows a 64.5% failure rate when
asked to self-correct in the same context. The fix: review in a **fresh context** that
never sees the worker's reasoning.

**When to use:** Any workflow where output quality matters and mistakes have
consequences. Not needed for purely informational logs or low-stakes summaries.

**Pattern:**

```
After the worker completes its run:

1. Orchestrator extracts ONLY the final output:
   - Actions taken (with IDs/details)
   - The quality rubric from Definition of Done
   - NOT the conversation history or intermediate reasoning

2. Spawn a FRESH sub-agent (the "verifier") with:
   - The extracted output
   - The quality rubric
   - A verifier prompt (see template below)

3. Verifier returns:
   - Dimension scores (numeric, 1-5)
   - Flagged issues (with severity: critical / warning / minor)
   - Overall confidence: HIGH / MEDIUM / LOW
```

**Verifier prompt template:**

```
Score each dimension in the provided quality rubric on a 1-5 scale. For each:
- State the score (numeric)
- Cite specific actions/decisions that justify the score
- Flag issues with severity: critical (wrong action taken), warning
  (questionable judgment), or minor (suboptimal but acceptable)

Scoring calibration:
- 5 means zero issues found. Reserve for genuinely flawless work.
- 3-4 is the honest range for most competent runs.
- Below 3 means you found concrete errors, not just uncertainties.

You are reviewing work done by another agent. You have no access to the
agent's reasoning — only its output. If an action seems wrong, flag it.
If you can't determine whether an action was correct from the output alone,
flag that as a transparency issue.

Return: dimension scores, flagged issues with severity, overall confidence
(HIGH/MEDIUM/LOW).

4. Orchestrator acts on the verification:
   - All clear (no critical, overall ⭐⭐⭐⭐ or above) → proceed, log scores
   - Warnings (overall ⭐⭐⭐) → proceed, log concerns, note in agent_notes.md
   - Critical issues (overall ⭐⭐ or below) → roll back if possible, alert human
```

**Key principles:**

- The verifier must NOT see the worker's reasoning — fresh context is the mechanism
- Context separation matters more than model diversity — same model works fine
- Using a different model is a bonus, not a requirement
- Cost is modest: ~5K tokens for verification vs 50K+ for the work session
- Budget the verification cost into the workflow's token estimate

**When NOT to verify cross-context:**

- Workflows at verification Level A or B (see Definition of Done → Verification Level)
- Trivially verifiable output (e.g., "did the API call succeed?" — just check the
  status)
- Workflows at trust Level 1 (Supervised) where human is already reviewing everything

Cross-context verification is reserved for **verification Level C** workflows — those
that take irreversible actions visible to other people.

### Pattern 8: Run Scorecard

Every run should score itself. This creates the data trail that drives graduated trust,
quality auditing, and self-improvement.

**The scorecard goes in the daily log** (see logs/ format above). Dimensions come from
the workflow's quality rubric in its Definition of Done.

**Scoring guidelines for the workflow:**

```markdown
When scoring your run, be honest — overconfident scores are worse than conservative
ones.

- ⭐⭐⭐⭐⭐: No doubts. Every action was clearly correct.
- ⭐⭐⭐⭐: Minor uncertainties, but all resolved with reasonable confidence.
- ⭐⭐⭐: Some judgment calls that could go either way. The user might disagree.
- ⭐⭐: Likely errors. Something felt wrong but you proceeded anyway.
- ⭐: Known wrong action. Should not have been taken.

Confidence reflects your certainty in the scores themselves:

- HIGH: Clear-cut run, scores are reliable
- MEDIUM: Some ambiguity, scores are best-effort
- LOW: Significant uncertainty — flag for human review regardless of scores
```

**What to do with scores:**

- **Track trends:** A single ⭐⭐⭐ run is fine. Five consecutive ⭐⭐⭐ runs means
  something is off — the workflow should note this in agent_notes.md and alert the
  human. (This is an informational alert, not a trust level change. Trust demotion only
  triggers on runs scoring ⭐⭐ or below — see circuit breakers in Pattern 9.)
- **Feed into graduated trust:** Star ratings gate autonomy level changes (see
  Pattern 2)
- **Enable quality auditing:** The quality auditor (see Part 4) reads these scores to
  detect drift across workflows
- **Drive self-improvement:** Low stars + the "Notes" column tell the self-improvement
  loop what to focus on (see Pattern 9)

### Pattern 9: Self-Improvement Loop

Workflows should get better over time, not just repeat the same mistakes.

**Three mechanisms:**

#### Structured Failure Logging

When verification catches an issue (score < 3 on any dimension, or cross-context
verifier flags something), log it in `agent_notes.md` with enough detail to prevent
recurrence:

```markdown
## Failures & Corrections

### YYYY-MM-DD: Archived important email from sender X

- What happened: Classified as promotional, archived
- Why it was wrong: Sender X sends invoices that look like marketing
- Correct action: Should have flagged for review
- New rule: Always check sender X against VIP list before archiving
- Applied to: rules.md VIP section (added sender X)
```

#### Active Guardrails from Past Mistakes

The run loop should **read agent_notes.md failures before processing**, not after. Turn
past mistakes into pre-flight checks:

```
Each Run:
1. Read rules.md
2. Read agent_notes.md — specifically the Failures & Corrections section
3. Build a mental checklist of known pitfalls for this run
4. Process items with those guardrails active
5. Score the run
6. If new failures found, add to agent_notes.md
```

This transforms `agent_notes.md` from a passive history into an active safety net.

#### Circuit Breakers

These implement the demotion rules from Pattern 2's graduated trust. The run loop checks
these at the end of each run using the `consecutive_good_runs` and `cooldown_remaining`
fields in `rules.md`.

```
If 3 consecutive runs below ⭐⭐⭐ overall:
  → Demote one trust level (Level 4→3, 3→2, 2→1)
  → Reset consecutive_good_runs to 0
  → Alert human: "Workflow quality degraded. Demoted to Level N."
  → Log the pattern in agent_notes.md

If a single run scores ⭐ on any dimension:
  → Immediate alert to human
  → Roll back actions if possible
  → Set cooldown_remaining to 10 in rules.md
  → Reset consecutive_good_runs to 0
  (Cooldown decrements by 1 each run. No trust level advancement while
  cooldown_remaining > 0, even if scores recover.)
```

#### Proposing Improvements

When a workflow identifies a recurring pattern it can't fix itself (e.g., the AGENT.md
instructions are ambiguous, or a tool is unreliable), it should:

1. Log the pattern in `agent_notes.md` under "## Improvement Proposals"
2. Include: what's failing, how often, what would fix it
3. The quality auditor or monthly audit surfaces these for the human to act on

Workflows don't edit their own AGENT.md — that's upstream-owned. They propose; the human
decides.

---

## Part 4: Scheduling & Execution

### How Workflows Run

Workflows are triggered by **cron jobs** (isolated sessions):

```bash
# Example: email steward runs every 30 minutes during business hours
openclaw cron add \
  --name "Email Steward" \
  --cron "*/30 8-22 * * *" \
  --tz "YOUR_TIMEZONE" \
  --session isolated \
  --message "Run email steward workflow. Read workflows/email-steward/AGENT.md and follow it." \
  --model work \
  --announce
```

### Cron Configuration Guidelines

| Workflow Type                                | Schedule                    | Model Pattern               | Session  |
| -------------------------------------------- | --------------------------- | --------------------------- | -------- |
| High-frequency checks (every 5-15 min)       | Every 5-15 min              | simple (check) → work (act) | Isolated |
| High-frequency triage (email, notifications) | Every 15-30 min             | work                        | Isolated |
| Daily reports/summaries                      | Once daily at fixed time    | think                       | Isolated |
| Weekly reviews/audits                        | Weekly cron                 | think + thinking            | Isolated |
| Reactive (triggered by events)               | Via webhook or system event | Varies                      | Isolated |

**Note on Check-Work Tiering:**

- If a job runs multiple times per hour, use the two-stage pattern: cheap check (simple)
  → expensive work (work/think)
- This cuts token costs on empty runs (when there's no work to do)
- Example: "Email arrived?" (simple) → "Process these 5 emails" (work) only if yes
- Apply to: health checks, inbox scans, notification monitors, cron job monitors

### Delivery

- **Routine runs:** Omit `--announce` (or set delivery to `none`) — work silently, only
  alert when something needs attention
- **Reports/summaries:** Use `--announce` — delivers a summary to the configured channel
  after completion
- **Errors/alerts:** Always deliver via the workflow's configured alert channel

Note: Isolated cron jobs **default to announce delivery** (summary posted after run).
Set `delivery: none` explicitly if you want silent operation.

### Quality Auditor Jobs

A quality auditor is a separate cron job whose sole purpose is reviewing other
workflows' output quality over time. It's the "separation of concerns" approach to
verification — the workflow verifies itself per-run, the auditor verifies the workflow
across runs.

**When to add a quality auditor:**

- When a workflow handles high-stakes actions (deleting data, sending messages, managing
  contacts)
- When a workflow runs frequently enough that manual log review is impractical
- When you want to catch gradual quality drift that per-run scoring misses

**Quality auditor pattern:**

```
Schedule: Daily or weekly (cheap model — this is a read-and-analyze job)

Each run:
1. Read the target workflow's logs from the past N days
2. Extract all run scorecards
3. Check for:
   - Score drift (average dropping over time)
   - Recurring LOW confidence runs
   - Repeated errors or the same failure pattern
   - Dimension-specific degradation (e.g., accuracy stable but judgment declining)
   - Score inflation: compare self-scores vs verifier scores across runs. A persistent
     delta (self > verifier) signals the workflow is overrating itself.
4. Spot-check a sample of actions (at least 3 or 10% of the period, whichever is larger)
   against reality — this requires access to the same tools as the audited workflow:
   - Did the email-steward archive something it shouldn't have?
   - Did the contact-steward create a duplicate?
   - Did the task-steward miss a deadline?
5. Check agent_notes.md for unresolved "Improvement Proposals"
6. Report:
   - Quality trend summary (improving / stable / degrading)
   - Flagged anomalies with severity
   - Improvement suggestions
   - Whether the workflow's trust level should change
```

**Auditor output goes to the human, not back into the workflow.** The auditor
recommends; the human decides whether to adjust rules, update AGENT.md, or change trust
levels.

**Example cron:**

```bash
openclaw cron add \
  --name "Email Steward QA" \
  --cron "0 9 * * 1" \
  --tz "YOUR_TIMEZONE" \
  --session isolated \
  --message "Audit email-steward quality. Read logs from the past 7 days, analyze scorecards, spot-check 3 random actions, report trends." \
  --model work \
  --announce
```

---

## Part 5: Building a New Workflow

### Step-by-Step Process

1. **Identify the opportunity** (use the Automation Audit above)
2. **Define the scope** — What does "done" look like for one run?
3. **List prerequisites** — What tools, access, labels are needed?
4. **Design the setup interview** — What preferences does the user need to set?
5. **Write AGENT.md** — The algorithm, following the anatomy above
6. **Test manually** — Run the AGENT.md instructions yourself first
7. **Set up cron** — Schedule for autonomous operation
8. **Monitor first week** — Watch logs, tune rules, build agent_notes

### AGENT.md Template

```markdown
---
name: <name>-steward
version: 0.1.0
description: <one-line description>
---

# <Name> Steward

<What this workflow does and why.>

## Prerequisites

- **<Tool>** configured with <access>
- **<Labels/tags>** created: <list>
- **Alert channel** configured (or none)

## First Run — Setup Interview

If `rules.md` doesn't exist or is empty:

### 0. Prerequisites Check

<Verify all tools and access work.>

### 1. Basics

<Core configuration questions.>

### 2. Preferences

<How aggressive, what to touch, what to skip.>

### 3. Data Scan (Optional)

<Offer to scan existing data and suggest rules.>

### 4. Alert Preferences

<What triggers alerts vs silent processing.>

### 5. Confirm & Save

<Summarize in plain language, save rules.md. Set initial trust level to Level 1
(Supervised) unless user requests Level 2.>

## Definition of Done

What constitutes a successful run of this workflow.

### Completion Criteria

<Binary pass/fail checks. Example:>

- All eligible items in scope have been processed or explicitly deferred
- No item left in an ambiguous state without escalation
- All actions logged with item identifiers

### Output Validation

<Structural checks — no LLM judgment needed. Example:>

- Log entry created with action summary and item counts
- Database updated for all processed items
- Alerts delivered for flagged items (if any)

### Quality Rubric

<3-5 scored dimensions on the ⭐ scale. Example:>

| Dimension    | What it measures                                    |
| ------------ | --------------------------------------------------- |
| Completeness | Were all eligible items processed?                  |
| Accuracy     | Were classifications/actions correct?               |
| Judgment     | Were edge cases handled well or properly escalated? |
| Alerting     | Were alerts appropriate (not noisy, not silent)?    |

### Verification Level

<A or B or C — see Verification Level framework in Part 2. Determines which quality
infrastructure this workflow uses:>

- **A** — Log only (no scorecard, no verification)
- **B** — Self-score + circuit breakers (no cross-context verification)
- **C** — Full verification (self-score + cross-context verifier + circuit breakers)

## Database (only if this workflow tracks processed items)

**PRAGMA user_version: 1**

<Schema definition inline — CREATE TABLE, indexes, column descriptions.> <Setup &
migration instructions — what to do if database is missing, version is lower, or legacy
state files exist.>

## Regular Operation

### Your Tools

<List all tools/commands the workflow uses.>

### Each Run

**Preparation:**

1. Read `rules.md` for preferences, trust level, and trust counters
2. Read `agent_notes.md` — specifically Failures & Corrections as pre-flight guardrails
3. Ensure database is ready (see Database section — one quick version check)

**Processing:** 4. <Scan/fetch new items> 5. Query `processed.db` to filter items
already handled 6. FOR EACH new item: Spawn a sub-agent to process it (see Sub-Agent
Orchestration) 7. After each item, update `processed.db` with status 8. Collect
sub-agent results 9. Alert if anything needs attention

**Quality Gate** (adapt to this workflow's verification level):

10. Append actions to today's log in `logs/`

For **Level A** workflows: stop here. Log only.

For **Level B** workflows (self-score + circuit breakers):

11. Score this run using the quality rubric. Log the scorecard with `Source: self`.
12. Act on scores: ⭐⭐⭐⭐ or above → proceed. ⭐⭐⭐ → log concerns. Below ⭐⭐⭐ →
    alert human.
13. Update `agent_notes.md` if you learned something new.
14. Update trust counters in `rules.md`. Check circuit breakers (Pattern 9).

For **Level C** workflows (full verification):

11. Draft scorecard using the quality rubric (do NOT log yet).
12. Spawn a fresh cross-context verifier with ONLY the actions taken + the quality
    rubric (Pattern 7 — verifier must NOT see worker reasoning).
13. Log the authoritative scorecard: use VERIFIER's scores. Note self-vs-verifier delta
    in agent_notes.md if gap > 1 star on any dimension. Mark `Source: verified`.
14. Act on the verified scores: ⭐⭐⭐⭐ or above → proceed. ⭐⭐⭐ → log concerns.
    Below ⭐⭐⭐ → alert human, roll back if possible.
15. Update `agent_notes.md` if you learned something new.
16. Update trust counters in `rules.md`. Check circuit breakers (Pattern 9).

### Judgment Guidelines

<When to act vs leave alone. Confidence thresholds.>

## Housekeeping

- Delete logs older than 30 days
- <Any other periodic cleanup>
- Review agent_notes.md Improvement Proposals — surface unresolved items

## Integration Points

<How this connects to other workflows.>
```

### Checklist Before Deploying

**Structure & Setup:**

- [ ] AGENT.md follows the standard anatomy
- [ ] Setup interview creates rules.md with all needed preferences
- [ ] Setup interview sets initial trust level (Level 1 default)
- [ ] Has clear judgment guidelines (when to act vs leave alone)

**State Management:**

- [ ] **Tracking state:** If workflow queries "have I seen this?", uses `processed.db`
      (SQLite), not markdown lists
- [ ] **Contextual state:** agent_notes.md and rules.md are markdown, not JSON
- [ ] **Sub-agents:** Any loop over a collection spawns sub-agents per item, not in
      orchestrator

**Verification & Quality** (match to declared verification level):

- [ ] **Verification level** declared in AGENT.md (A, B, or C)
- [ ] **Definition of Done:** Completion criteria, output validation, and quality rubric
      are all defined in AGENT.md (all levels)
- [ ] **Run scorecard:** Each run scores itself on the quality rubric (Level B and C)
- [ ] **Circuit breakers:** 3 consecutive runs below ⭐⭐⭐ triggers demotion (Level B
      and C)
- [ ] **Cross-context verification:** Verifier sub-agent configured (Level C only)
- [ ] **Self-improvement:** agent_notes.md has Failures & Corrections section; run loop
      reads it as pre-flight guardrails (Level B and C)

**Operations:**

- [ ] Error handling: logs errors, alerts on critical failures
- [ ] Housekeeping: auto-prunes old logs and cleans up stale tracking entries (e.g.,
      `DELETE FROM processed WHERE last_checked < ...`)
- [ ] Integration points documented
- [ ] Cron job configured with appropriate schedule/model
- [ ] First week monitoring plan in place

---

## Part 6: Maintaining Workflows

### Monthly Audit (15 min per workflow)

For each active workflow:

1. **Score trends** — Pull the past month's scorecards. Is the average stable,
   improving, or degrading? Any dimension consistently low?
2. **Review logs** — Any recurring errors? Silent failures? Patterns the workflow didn't
   catch?
3. **Check agent_notes.md** — Has it learned useful patterns? Are there unresolved
   Improvement Proposals? Are Failures & Corrections entries still relevant?
4. **Trust level check** — Is the current level appropriate? Should it advance or demote
   based on score history?
5. **Review rules.md** — Still accurate? Preferences changed?
6. **ROI check** — Still saving time? Worth the token cost?
7. **Integration health** — Connected workflows still working?
8. **Quality auditor review** — If a QA job exists, review its reports. If not, consider
   adding one.

### When to Retire a Workflow

- ROI drops below 1x (costs more than it saves)
- The underlying process changed significantly
- A better approach exists (new tool, API, or workflow)
- It causes more problems than it solves

To retire: disable the cron job, archive the workflow directory, note in
`memory/decisions/`.

---

## Part 7: Security Considerations

### For Workflows from ClawHub

⚠️ **ClawHub has had malicious skills.** Before installing any workflow:

1. **Inspect before installing:** `npx clawhub inspect <slug> --files`
2. **Check for VirusTotal flags:** ClawHub scans automatically; heed warnings
3. **Download to /tmp for review:** `npx clawhub install <slug> --dir /tmp/review`
4. **Review all files manually** — look for:
   - External API calls to unknown domains
   - Eval/exec of dynamic code
   - Hardcoded API keys or crypto addresses
   - Instructions to disable safety features
   - Data exfiltration patterns (sending data to external services)
5. **Never install directly into your workspace** without review

### For Your Own Workflows

- Workflows should only access tools they need
- Alert channels should be explicit (no silent external sends)
- Quarantine before delete (labels > trash > permanent deletion)
- Log all actions for auditability

---

## Existing Workflows Reference

**Note:** Existing workflows predate the v0.3.0 verification patterns (Definition of
Done, scorecards, cross-context verification, circuit breakers). New workflows should
include the full quality infrastructure. When updating existing workflows, adopt
patterns in this order: Definition of Done → Run Scorecard → Circuit Breakers →
Graduated Trust → Cross-Context Verification (each builds on the previous).

### email-steward

- **Purpose:** Inbox debris removal
- **Schedule:** Configured via cron (typically every 30 min during business hours)
- **Tools:** gog CLI (Gmail)
- **Key pattern:** Setup interview → graduated trust → sub-agent delegation
- **Notable:** Uses `agent_notes.md` heavily for learning sender patterns

### task-steward

- **Purpose:** Task board management with QA verification
- **Schedule:** Can run via heartbeat or cron (see its AGENT.md for guidance)
- **Tools:** Asana MCP
- **Key pattern:** Task classification → work execution → quality gate (think QA) →
  delivery
- **Notable:** Spawns think as QA sub-agent — demonstrates strong model as worker, not
  just orchestrator
