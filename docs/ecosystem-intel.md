# Ecosystem Intelligence

> The AI ecosystem moves too fast for any one human to track. This workflow makes your
> fleet get better while you sleep.

`ecosystem-intel` is a workflow that lives in `workflows/ecosystem-intel/` and runs
across every machine that syncs from `openclaw-config`. It watches curated sources,
synthesizes what matters, and proposes concrete changes to your fleet — with
human-in-the-loop approval that graduates to self-approval once trust is earned.

## Why This Exists

Most "AI news" tools give you a longer list. This workflow does the opposite: it hides
everything that does not advance the fleet, and the output is measured by one metric —
_did you act on it?_

It is built for PAI (personal AI infrastructure) operators who run more than one
instance of OpenClaw and cannot afford to hand-curate what each machine adopts.
`openclaw-config` is the shared substrate, so one accepted change lifts every machine in
the fleet.

## The Five Phases

```
HARVEST  →  FILTER  →  SYNTHESIZE  →  PROPOSE  →  INTEGRATE
```

- **Harvest** (hourly, cheap model) — pulls signals from sources you configure
- **Filter** (hourly, simple model) — scores each signal on relevance, novelty, and
  actionability, drops the noise
- **Synthesize** (daily, think model) — groups signals into _findings_ with evidence,
  fleet impact, risks, and a proposed _action tier_
- **Propose** (daily, think model) — emits Asana tasks, draft commits, or draft PRs for
  anything tier 3 or higher
- **Integrate** — delivers a morning brief and (once earned) self-applies the
  lowest-risk changes

## Action Tiers

Every finding ends with a tier:

| Tier | Name         | What happens                                 |
| ---- | ------------ | -------------------------------------------- |
| 1    | ignore       | noted in `seen.json`, nothing else           |
| 2    | watch        | added to watchlist, ages out after 21d       |
| 3    | recommend    | Asana task created, surfaced in brief        |
| 4    | draft change | draft PR or branch against `openclaw-config` |
| 5    | auto-apply   | applied + logged (only for earned classes)   |

Tier 5 is opt-in per change class in `rules.md#auto_apply_classes`. A class only
graduates after ≥ 20 accepted samples at ≥ 80 % merge-without-rollback.

## What You Get Every Morning

A single Telegram post in your `📋 Automation` topic, under 200 words:

```
🧠 Ecosystem Brief — 2026-04-22

Fleet pulse: Memory tooling is clearly converging on
typed + graph layers; agent platforms are stable week-over-week.

1. [Tier 4] Replace librarian embeddings call with bge-m3 native
   — PR eco/2026-04-22-librarian-bge-m3
2. [Tier 3] Add ACP transport support to coding-agent skill
   — Asana: https://...
3. [Tier 2] Watch: paperclip agent framework (3 sources, still early)

Auto-applied: 0
Watchlist: 7 items
Precision last 30d: 76%
```

If nothing crossed the interesting bar, the brief says so honestly. No padding.

## Configuring Sources

All source configuration lives in `workflows/ecosystem-intel/rules.md#sources`. Each
source has:

- `id` — stable slug used in telemetry
- `kind` — one of `github_releases`, `github_trending`, `rss`, `blog`, `social_online`,
  `manual`, `internal`
- `url` — where to look (or the query / skill reference)
- `weight` — starting trust in `[0, 1]`
- `tags` — themes used for grouping during synthesis

Weights decay automatically when a source produces low-precision findings. You never
have to hand-tune a dead blog.

## Hard Rules (never overridden)

- No non-draft PRs without human approval.
- No merges to `main` on any human-owned repo.
- No edits to `SOUL.md`, `USER.md`, `IDENTITY.md`, or `templates/`.
- No automatic fleet membership changes.
- No Venmo / finance / medical / health files (see `TOOLS.md`).
- Briefs only go to the Automation topic. Never to DMs or `#naughty`.

## Installation

Once `openclaw-config` is synced and `workflows/ecosystem-intel/` exists:

1. Copy `rules.md` targets (brief channel / chat id / topic) to your instance values.
2. Run the first harvest by hand to seed `memory/ecosystem-intel/`.
3. Add the three crons documented in the workflow `AGENT.md` (harvest / synthesize /
   brief).
4. Watch the first 7 days. Reject noisy findings with reasoning — the `learning-loop`
   workflow converts your rejections into durable rules.

## Where State Lives

```
memory/ecosystem-intel/
├── sources.yml           # live sources (rebuilt from rules.md on change)
├── seen.json             # dedupe index
├── findings/YYYY-MM-DD.md
├── briefs/YYYY-MM-DD.md
├── proposals/<slug>.md
└── telemetry.json        # per-source precision, engagement
```

All of it is markdown + JSON in git. Every decision the workflow makes is inspectable by
a human reading files — no vector stores, no hidden agent memory.

## How It Compounds

Three things compound over time:

1. **Source precision.** Sources that produce real changes gain weight; sources that
   produce noise decay. You never have to hand-prune.
2. **Action-class trust.** Change classes that merge cleanly can graduate to auto-apply,
   one class at a time, with a human toggle.
3. **Learning-loop integration.** Rejected proposals become corrections. Corrections
   become patterns. Patterns become operating heuristics in
   `workflows/ecosystem-intel/agent_notes.md` — which every future run reads before it
   proposes anything.

After ~6 weeks of calibration, the expected outcome is:

- ~1 tier-3+ finding every day
- ~1 tier-4 PR per week that merges cleanly
- ~1 tier-5 auto-applied change per week
- Nick spends < 10 min/day on ecosystem intake instead of hours

## Related Workflows

- **learning-loop** — owns corrections → patterns → rules
- **security-sentinel** — threat intel; we explicitly do _not_ duplicate its job
- **task-steward** — owns Asana task hygiene; we only create tasks
- **forward-motion** — surfaces stuck agents; we read its signals as internal telemetry

## Status

`v0.1.0` — first-run calibration. Expect churn in `rules.md` over the first two weeks as
the source list and scoring knobs settle.
