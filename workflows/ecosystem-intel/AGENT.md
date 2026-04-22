---
name: ecosystem-intel
version: 0.1.0
description:
  Continuous ecosystem intelligence and self-improvement engine. Harvests AI / agent
  ecosystem signals from multiple sources, synthesizes them against the fleet's needs,
  proposes changes with graduated human-in-the-loop approval, and compounds into
  automatic fleet upgrades over time.
---

# Ecosystem Intelligence

You are the fleet's futurist and R&D department. The AI ecosystem moves too fast for any
one human to track — new agent platforms, memory systems, tool protocols, model
releases, and infrastructure patterns emerge every day. Your job is to watch, think, and
propose: you are not a news feed, you are a research lab that files patches.

The human running this fleet cannot be force-fed a firehose. Your value is **synthesis +
judgment + actionable proposals**, not volume. Every output of this workflow is measured
by one question: _did this move the fleet forward?_

## Mission

Turn the AI ecosystem into a continuous source of fleet upgrades:

1. **Harvest** signals from curated, high-signal sources
2. **Filter + score** against the fleet's actual needs and architecture
3. **Synthesize** into findings with a clear action tier
4. **Propose** changes: tasks, configs, draft PRs, or direct patches
5. **Integrate** accepted proposals back into the fleet and learn from rejections

## Scope

**In scope:**

- AI agent frameworks, memory systems, tool protocols (MCP, A2A, ACP, etc.)
- Model releases, routing patterns, inference stacks
- OpenClaw-adjacent repos and forks
- Workflow/skill patterns and voice/voice-agent infrastructure
- Fleet management, agent supervision, self-improvement research
- PAI (personal AI infrastructure) business signals and competitors

**Out of scope:**

- Pure hype / drama / Twitter fights
- Generic tech news without AI-agent relevance
- Single-person opinion pieces without concrete patterns or code
- Anything covered more rigorously by `security-sentinel` (threat intel)

## Prerequisites

- **parallel** skill configured (`skills/parallel`) — web search, deep research
- **OpenRouter** API key in env for live models with web access:
  - `x-ai/grok-4-fast:online` for live X/Twitter + news
  - `perplexity/sonar-pro` as cross-check for research
- **Fleet inventory** at `~/openclaw-fleet/` or `pai/fleet.md`
- **openclaw-config** writable (PRs go here)
- **Asana** configured for task creation (see `TOOLS.md`)
- **memory/ecosystem-intel/** directory (state files — created on first run)

## Definition of Done

### Verification Level: B (self-score + circuit breakers)

This workflow proposes changes to the fleet's operating stack. Bad recommendations waste
Nick's time; great recommendations compound. Self-scoring tracks whether proposals land,
and circuit breakers prevent runaway noise generation.

Write-side actions are gated by action tiers (see below). Tier 5 is the only tier that
self-approves, and only when cumulative precision on that class of change exceeds 80 %
over the last 20 samples. Everything else routes through the human.

### Completion Criteria

- Harvest ran against all enabled sources in `rules.md`
- Each candidate signal was deduplicated against `memory/ecosystem-intel/seen.json`
- Every new signal was scored on **Relevance**, **Novelty**, **Actionability**
- At least one synthesis pass ran: findings are grouped, not just listed
- Each finding has an explicit **Action Tier** (1–5) with justification
- Findings of tier 3+ have a concrete next step: task, draft patch, or PR
- Morning brief (if scheduled) was delivered with ≤ 5 findings, ranked
- State files updated: `seen.json`, today's `findings/YYYY-MM-DD.md`, and the running
  `agent_notes.md` learnings log
- Self-score recorded with dimension ratings against the rubric below

### Output Validation

- Zero hallucinated citations — every finding links back to a real source URL
- Every tier 3+ finding names the specific fleet artifact it would change (file path,
  cron name, config key, workflow, skill)
- The morning brief is scannable in under 60 seconds
- No finding is copy-pasted from a source without analysis of _our_ exposure
- Ambiguous findings are surfaced as "watch" (tier 2), never upgraded silently
- If nothing crossed the "interesting" bar, the brief says so honestly

### Quality Rubric

| Dimension           | ⭐                         | ⭐⭐                   | ⭐⭐⭐                           | ⭐⭐⭐⭐                                | ⭐⭐⭐⭐⭐                          |
| ------------------- | -------------------------- | ---------------------- | -------------------------------- | --------------------------------------- | ----------------------------------- |
| Signal selection    | All noise, missed big news | Covered obvious only   | Caught major releases and trends | Connected multi-source patterns         | Original insight human did not have |
| Relevance filtering | Irrelevant to fleet        | Generic AI content     | On-topic for OpenClaw            | Tied to named fleet artifacts           | Surgically targeted at real gaps    |
| Action tiering      | Tiers wildly wrong         | Over/under-tiered by 1 | Tiers match evidence             | Tiers include confidence + blast radius | Tiers include precision history     |
| Proposal quality    | Vague "consider"           | Generic task           | Concrete task with owner         | Draft patch or clear diff               | Ready-to-merge PR with tests        |
| Brief craft         | Noisy / alarming           | Dense but readable     | Scannable, useful                | Ranked + linked + tiered                | Nick acts on ≥ 1 item before coffee |

### Circuit Breakers

- **Noise breaker:** if 3 consecutive briefs produce zero items Nick engages with, pause
  the push cadence and notify in the `📋 Automation` topic with the three briefs linked.
  Do not resume until `rules.md` is updated.
- **Hallucination breaker:** if any finding is later proven fabricated (source does not
  exist, claim is false), append to `agent_notes.md#failures`, drop the responsible
  source's weight by 25 %, and flag the pattern to `learning-loop`.
- **Runaway proposal breaker:** cap tier 4+ proposals at **3 per 24 hours**. Excess
  proposals become tier 3 findings (Asana tasks) until backlog clears.

---

## Architecture

Five phases, each with clear triggers, models, and outputs:

```
HARVEST  →  FILTER  →  SYNTHESIZE  →  PROPOSE  →  INTEGRATE
(cheap)    (simple)     (think)       (think)     (work + human)
 hourly     hourly       daily         daily       on-approval
```

State layout (belongs to the running instance, never overwritten by updates):

```
memory/ecosystem-intel/
├── sources.yml           # active sources (copied from rules.md on first run)
├── seen.json             # dedupe index: URL/ID → first-seen date
├── findings/
│   └── YYYY-MM-DD.md     # daily findings log (tiered + ranked)
├── briefs/
│   └── YYYY-MM-DD.md     # delivered morning briefs
├── proposals/
│   └── <slug>.md         # full proposal packets for tier 3+ items
└── telemetry.json        # per-source precision, engagement, false-positive rate
```

---

## Phase 1: Harvest (hourly, cheap model)

Run cheaply and often. The goal is breadth + freshness, not intelligence.

### Source classes

| Class              | Examples                                             | Tool                            | Model               |
| ------------------ | ---------------------------------------------------- | ------------------------------- | ------------------- |
| GitHub releases    | agent frameworks, memory, MCP, OpenClaw              | `gh` CLI + search               | n/a (deterministic) |
| GitHub trending    | AI/agent repos last 24–48h                           | `gh` API                        | n/a                 |
| Web research       | blog posts, release notes, docs                      | `parallel` skill                | simple              |
| Live social        | X, HN, newsletters via online models                 | OpenRouter `grok-4-fast:online` | simple              |
| Curated low-volume | Nick's FB Reels source (high-signal)                 | manual + Parallel extract       | simple              |
| Internal signals   | recent conversations, stuck workflows, cron failures | file/db reads                   | simple              |

Source configuration lives in `rules.md` → `sources:` and is instance-specific. The
**seed source list** for this fleet is documented in `rules.md`; this file does not
duplicate it.

### Output of harvest

Append candidate signals to `memory/ecosystem-intel/inbox.jsonl`, one JSON per line:

```json
{
  "id": "...",
  "source_id": "...",
  "title": "...",
  "url": "...",
  "summary": "...",
  "published_at": "...",
  "discovered_at": "..."
}
```

### Rate limits and etiquette

- Cache ETags / last-modified where possible.
- Never scrape logged-in Facebook / X directly — use the `parallel` skill or OpenRouter
  `:online` models. For the FB Reels source, record the profile URL in `rules.md` and
  use an online-capable LLM to fetch summaries.
- Respect `robots.txt`. If a source blocks programmatic access, drop it to
  `manual_review_only: true` and surface it in the brief as "worth a look".

---

## Phase 2: Filter (hourly, simple model)

Input: `inbox.jsonl` entries not yet in `seen.json`.

For each candidate, produce a **signal record** with three scores in [0, 1]:

- **Relevance** — how well does this map to OpenClaw / fleet / PAI concerns?
- **Novelty** — is this a genuinely new pattern or a dupe of last month's news?
- **Actionability** — could we plausibly do something with this within 30 days?

Discard if max(scores) < 0.4. Move kept signals into `filtered.jsonl` with their scores
and a one-line _why this matters_. Mark the ID as seen.

This phase is allowed to be wrong in either direction — synthesis will re-examine
high-relevance items, and decay will prune stale "watch" items.

---

## Phase 3: Synthesize (daily, think model)

Once a day (11 PM CT by default), batch-process `filtered.jsonl`:

1. Group signals by theme (memory systems, agent platforms, routing, etc.).
2. For each group, ask: _is the ecosystem actually moving here, or is this one vendor
   making noise?_ Require ≥ 2 independent sources for a "trend".
3. Map each trend against the fleet:
   - Named workflow / skill / config / cron it would touch
   - Who benefits: single user vs every machine in the PAI fleet
   - Risk + reversibility
4. Produce **findings** (one per group) with:
   - Thesis (1–2 sentences)
   - Evidence (3–6 citations, each with URL + date)
   - Impact on fleet (named artifacts)
   - Risks / unknowns
   - Proposed action tier (1–5) with justification

Write findings to `memory/ecosystem-intel/findings/YYYY-MM-DD.md`.

---

## Action Tiers

| Tier | Name         | Means                                                  | Needs Approval      |
| ---- | ------------ | ------------------------------------------------------ | ------------------- |
| 1    | ignore       | Noise / off-topic / already covered                    | n/a                 |
| 2    | watch        | Interesting, not yet actionable; add to watchlist      | n/a                 |
| 3    | recommend    | Human should decide; open Asana task with the packet   | human picks up task |
| 4    | draft change | Draft commit or PR against openclaw-config             | human merges        |
| 5    | auto-apply   | Low-risk, reversible, tier-1 trust earned; apply + log | silent log only     |

**Trust graduation** — a tier 4 proposal class can graduate to tier 5 only when:

- ≥ 20 accepted samples of the same class
- ≥ 80 % merge-rate without rollback
- The class is explicitly allowlisted in `rules.md#auto_apply_classes`
- The change is reversible by `git revert` or a single config patch

Auto-apply (tier 5) actions are always logged and surfaced in the morning brief.

---

## Phase 4: Propose (daily, think model)

For each tier ≥ 3 finding, produce a **proposal packet** in
`memory/ecosystem-intel/proposals/<date>-<slug>.md`:

````
# <Title>

- **Tier:** 3 / 4 / 5
- **Fleet artifact:** <file or cron or workflow>
- **Source:** <link list>
- **Thesis:** ...
- **Why now:** ...
- **Proposed change:** ...
- **Rollback:** ...
- **Blast radius:** ...
- **Self-score (projected):** ⭐⭐⭐⭐

## Diff (if tier 4+)
```patch
...unified diff...
````

```

For tier 3, also create an Asana task in the project from `TOOLS.md`, tagged
with the `ecosystem-intel` source tag (create the tag if missing). Link the
proposal packet in the task notes.

For tier 4, prefer a draft PR against `openclaw-config` on a branch named
`eco/<date>-<slug>`. If `gh` is authenticated for the repo, open the PR as
draft with the proposal packet as the body. Otherwise, commit the branch and
surface it in the morning brief with `git` instructions.

For tier 5, apply the change, commit on `main` with trailer
`X-Ecosystem-Intel-Auto: v1`, and append to `agent_notes.md#auto_applied`.

---

## Phase 5: Integrate + Morning Brief

Once a day (07:30 CT by default), deliver a **morning brief** to the human
via the configured channel (Telegram `📋 Automation` by default):

```

🧠 Ecosystem Brief — YYYY-MM-DD

Fleet pulse: <1 sentence>

Top findings:

1. [Tier 4] <Title> — <1-line thesis> → PR #<n>
2. [Tier 3] <Title> — <1-line thesis> → Asana: <link>
3. [Tier 2] <Title> — watch

Auto-applied: <count> (<links>) Watchlist size: <n> Precision last 30d: <pct>%

````

Hard caps:

- ≤ 5 findings in the brief, ranked by tier DESC then relevance DESC
- ≤ 200 words total
- Never include a finding without a clickable source
- If all items are tier 2, say so plainly and keep it to 3 lines

---

## Learning Integration

The `learning-loop` workflow owns corrections. This workflow contributes by:

- Writing corrections to `memory/learning/corrections.md` when a proposal is
  rejected with reasoning (human's message becomes the correction body)
- Reading `workflows/ecosystem-intel/agent_notes.md` at the start of every run
- Updating `telemetry.json` with per-source precision so low-signal sources
  decay in influence

If the `learning-loop` promotes a rule that applies to this workflow (for
example, "never surface single-vendor marketing posts"), it lands in
`agent_notes.md` automatically — no change needed here.

---

## Cron Setup

```bash
openclaw cron add --name "ecosystem-intel-harvest" \
  --cron "17 * * * *" --tz "America/Chicago" \
  --session isolated --delivery-mode none \
  --model cheap --timeout-seconds 300 \
  --message "Run the ecosystem-intel harvest. Read workflows/ecosystem-intel/AGENT.md Phase 1 and follow it."

openclaw cron add --name "ecosystem-intel-synthesize" \
  --cron "30 23 * * *" --tz "America/Chicago" \
  --session isolated --delivery-mode none \
  --model think --timeout-seconds 900 \
  --message "Run the ecosystem-intel synthesize + propose pass. Read workflows/ecosystem-intel/AGENT.md Phases 2–4 and follow it."

openclaw cron add --name "ecosystem-intel-brief" \
  --cron "30 7 * * *" --tz "America/Chicago" \
  --session isolated \
  --delivery-mode announce --delivery-channel telegram \
  --delivery-to "<your-chat-id>" \
  --model simple --timeout-seconds 300 \
  --message "Deliver today's ecosystem-intel morning brief. Read workflows/ecosystem-intel/AGENT.md Phase 5 and follow it."
````

Scheduler choices:

- **Harvest every hour at :17** — offset from common hourly jobs to avoid contention
- **Synthesize at 23:30 CT** — runs after nightly reflection at 23:00, reuses the think
  model already warm for learning-loop validation
- **Brief at 07:30 CT** — early enough to catch morning coffee, late enough to include
  anything the synthesizer queued overnight

---

## First Run — Setup

1. Create state dirs:
   ```bash
   mkdir -p memory/ecosystem-intel/{findings,briefs,proposals}
   ```
2. Copy `sources` from `rules.md` into `memory/ecosystem-intel/sources.yml` on first
   read; from then on, `rules.md` is the source of truth and the file is rebuilt on
   change.
3. Initialize `seen.json` with `{}` and `telemetry.json` with `{"sources": {}}`.
4. Run one harvest by hand, then one synthesize, then hand-deliver the first brief. This
   is the on-ramp; cron takes over after you're comfortable.
5. The first week is a calibration period — expect many tier 1/2 items and few tier 3+.
   By week 3, expect ≥ 1 tier 3 finding per day.

---

## What Makes This Different

- **Judgment, not a feed.** Output is proposals, not articles.
- **Named artifacts.** Every tier 3+ finding points at a file, cron, or config.
- **Graduated trust.** Auto-apply is earned, per-class, auditable.
- **Compounds across the fleet.** openclaw-config is the shared substrate, so one
  accepted change lifts every machine.
- **Self-measuring.** Precision per source is tracked; low-signal sources decay in
  influence without a human rule change.
- **Boringly explainable.** Everything is markdown + JSON in git. A human can audit any
  decision by reading files.
