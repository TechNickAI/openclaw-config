---
name: workflow-builder
version: 0.1.0
description: Design, build, and maintain autonomous OpenClaw workflows (stewards). Use when creating new workflow agents, improving existing ones, evaluating automation opportunities, or debugging workflow reliability. Triggers on "build a workflow", "create a steward", "automate this process", "workflow audit", "what should I automate".
metadata:
  openclaw:
    emoji: "🏗️"
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

| Dimension | Question | Score |
|---|---|---|
| **Frequency** | How often? (daily=3, weekly=2, monthly=1, rare=0) | 0-3 |
| **Repetitiveness** | Same steps every time? (always=3, mostly=2, sometimes=1, never=0) | 0-3 |
| **Judgment Required** | Needs creative thinking? (none=3, low=2, medium=1, high=0) | 0-3 |
| **Time Cost** | Minutes per occurrence × frequency per month / 60 = hours/month | raw |
| **Safety** | How safe to automate? (harmless if wrong=3, annoying=2, costly=1, dangerous=0) | 0-3 |

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

| Approach | When to Use |
|---|---|
| **Workflow (steward)** | Needs state, learning, rules, multi-step processing |
| **Heartbeat item** | Quick check, batch with others, context-aware |
| **Cron (isolated)** | Exact timing, standalone, different model |
| **Cron (main)** | One-shot reminder, system event injection |

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
<Interactive setup that creates rules.md. Ask preferences, scan existing
data, suggest smart defaults. Always let the user skip/bail early.>

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

## Mistakes Made
- <once archived an important email — now check for X before archiving>

## Optimizations
- <batch processing senders A, B, C saves 3 API calls>
```

### logs/ — Execution History

One file per day, auto-pruned after 30 days.

**Pattern:**
```markdown
# <Workflow> Log — YYYY-MM-DD

## Run: HH:MM
- Processed: N items
- Actions: archived X, deleted Y, alerted on Z
- Errors: none
- Duration: ~Ns
```

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

Start conservative, get more aggressive as confidence grows.

```
Week 1: Only act on obvious items (>95% confidence)
Week 2: Expand to likely items (>85% confidence), log edge cases
Week 3: Review agent_notes.md, adjust thresholds
Week 4+: Stable operation with periodic self-audit
```

Write confidence thresholds to `rules.md` so the user can tune them.

### Pattern 3: Sub-Agent Orchestration

Match intelligence to task complexity:

```
Obvious/routine items → Spawn sub-agent (cheaper model: Haiku/Sonnet)
Important/nuanced items → Handle yourself or spawn a powerful sub-agent (Opus)
Quality verification → Can use a strong model as QA reviewer (Opus as sub-agent)
Uncertain items → Sub-agents escalate to you rather than guessing
```

**Note:** Don't hardcode model IDs (they go stale fast). Use aliases like
`sonnet`, `opus`, `haiku` or reference the model by capability level.

### Pattern 4: State Externalization (Compaction-Safe)

**Critical:** Chat history is a cache, not the source of truth. After every
meaningful step, write state to disk.

```markdown
# state/active-work.json (or inline in agent_notes.md)

{
  "current_phase": "processing",
  "next_action": "Review batch 2 of inbox",
  "last_completed": "Batch 1: archived 12, deleted 3",
  "resume_prompt": "Continue inbox processing from message ID xyz",
  "updated_at": "2026-02-18T14:30:00Z"
}
```

**Rule in AGENT.md:** "On every run, read state first. Either advance it or
explicitly conclude it."

### Pattern 5: Error Handling & Alerting

Every workflow must handle failures gracefully:

1. **Log errors** to daily log with full context
2. **Alert on critical failures** (unless `alert_channel: none`)
3. **Never fail silently** — if something breaks, the human should know
4. **Quarantine, don't destroy** — use labels/tags, not deletion
5. **Route all errors to one place** — consistent error channel

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

---

## Part 4: Scheduling & Execution

### How Workflows Run

Workflows are triggered by **cron jobs** (isolated sessions):

```bash
# Example: email steward runs every 30 minutes during business hours
openclaw cron add \
  --name "Email Steward" \
  --cron "*/30 8-22 * * *" \
  --tz "America/Chicago" \
  --session isolated \
  --message "Run email steward workflow. Read workflows/email-steward/AGENT.md and follow it." \
  --model sonnet \
  --announce
```

### Cron Configuration Guidelines

| Workflow Type | Schedule | Model | Session |
|---|---|---|---|
| High-frequency triage (email, notifications) | Every 15-30 min | Sonnet | Isolated |
| Daily reports/summaries | Once daily at fixed time | Opus | Isolated |
| Weekly reviews/audits | Weekly cron | Opus + thinking | Isolated |
| Reactive (triggered by events) | Via webhook or system event | Varies | Main or Isolated |

### Delivery

- **Routine runs:** Omit `--announce` (or set delivery to `none`) — work silently, only alert when something needs attention
- **Reports/summaries:** Use `--announce` — delivers a summary to the configured channel after completion
- **Errors/alerts:** Always deliver via the workflow's configured alert channel

Note: Isolated cron jobs **default to announce delivery** (summary posted after run).
Set `delivery: none` explicitly if you want silent operation.

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
<Summarize in plain language, save rules.md.>

## Regular Operation

### Your Tools
<List all tools/commands the workflow uses.>

### Each Run
1. Read `rules.md` for preferences
2. Read `agent_notes.md` for learned patterns (if exists)
3. <Scan/fetch new items>
4. <Process items based on rules>
5. Alert if anything needs attention
6. Append to today's log in `logs/`
7. Update `agent_notes.md` if you learned something

### Judgment Guidelines
<When to act vs leave alone. Confidence thresholds.>

## Housekeeping
- Delete logs older than 30 days
- <Any other periodic cleanup>

## Integration Points
<How this connects to other workflows.>
```

### Checklist Before Deploying

- [ ] AGENT.md follows the standard anatomy
- [ ] Setup interview creates rules.md with all needed preferences
- [ ] Has clear judgment guidelines (when to act vs leave alone)
- [ ] Error handling: logs errors, alerts on critical failures
- [ ] Housekeeping: auto-prunes old logs
- [ ] Integration points documented
- [ ] Cron job configured with appropriate schedule/model
- [ ] First week monitoring plan in place

---

## Part 6: Maintaining Workflows

### Monthly Audit (15 min per workflow)

For each active workflow:

1. **Review logs** — Any recurring errors? Silent failures?
2. **Check agent_notes.md** — Has it learned useful patterns?
3. **Review rules.md** — Still accurate? Preferences changed?
4. **ROI check** — Still saving time? Worth the token cost?
5. **Integration health** — Connected workflows still working?

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
- **Key pattern:** Task classification → work execution → quality gate (Opus QA) → delivery
- **Notable:** Spawns Opus as QA sub-agent — demonstrates strong model as worker, not just orchestrator
