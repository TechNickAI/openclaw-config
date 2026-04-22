# Ecosystem Intel — Instance Rules

Instance-specific configuration for the `ecosystem-intel` workflow. Override freely per
machine. This file is instance-owned: it is NOT overwritten by `openclaw-config` updates
once it exists.

## Delivery

- **Brief channel:** `telegram`
- **Brief target (chat id):** `<TELEGRAM_CHAT_ID>`
- **Brief topic (thread id):** `<TELEGRAM_THREAD_ID>` (📋 Automation)
- **Alert topic:** `<TELEGRAM_THREAD_ID>`

## Cadence

- Harvest: every hour at minute 17
- Synthesize: daily 23:30 CT
- Brief: daily 07:30 CT
- Telemetry rollup: weekly Sunday 01:30 CT

## Confidence + Auto-apply

- `auto_apply_enabled: false` (start with human-in-the-loop)
- Once precision ≥ 80 % over 20 accepted samples per class, ask Nick before flipping the
  class-specific flag in `auto_apply_classes` below.

### `auto_apply_classes` (all disabled to start)

- [ ] `doc_typo_fix` — doc-only typos / dead links in openclaw-config
- [ ] `source_weight_decay` — reducing weight of a low-signal source
- [ ] `watchlist_expire` — aging out tier 2 items past their expiry
- [ ] `cron_schedule_nudge` — ±5 min jitter on non-critical crons
- [ ] `skill_version_bump` — skill version bump when upstream has a tagged release
      matching our pinned major

Everything else is tier ≤ 4.

## Hard rules (never overridden)

- Never open a non-draft PR without human approval.
- Never merge to `main` on any repo the human owns.
- Never modify `SOUL.md`, `USER.md`, `IDENTITY.md`, or any file under `templates/`
  without explicit approval.
- Never add or remove fleet machines from `pai/fleet.md` automatically.
- Never touch Venmo, finance, medical, or health files. Refer to guardrails in
  `TOOLS.md` and `memory/decisions/`.
- Never send proposals to `#naughty` or DMs of other humans. Brief goes to the
  Automation topic only.

## Sources

Format:

```yaml
- id: <stable-slug>
  name: <human name>
  kind:
    github_releases | github_trending | rss | blog | social_online | manual | internal
  url: <where to look or query>
  weight: 0.0 - 1.0 # starting trust
  tags: [list, of, themes]
  notes: short explanation
```

Starting source list:

```yaml
sources:
  - id: openclaw-core
    name: OpenClaw core repo
    kind: github_releases
    url: https://github.com/openclaw/openclaw
    weight: 1.0
    tags: [openclaw, infrastructure]
    notes: Highest weight — anything here directly affects us.

  - id: openclaw-config
    name: OpenClaw Config (this repo)
    kind: github_releases
    url: https://github.com/TechNickAI/openclaw-config
    weight: 0.95
    tags: [openclaw, config, fleet]
    notes: Our own changes are a signal for what the fleet is adopting.

  - id: mcp-spec
    name: Model Context Protocol
    kind: github_releases
    url: https://github.com/modelcontextprotocol
    weight: 0.9
    tags: [protocols, tools]
    notes: MCP + friends define the tool-call substrate we ride on.

  - id: anthropic-engineering
    name: Anthropic Engineering
    kind: blog
    url: https://www.anthropic.com/engineering
    weight: 0.9
    tags: [models, agents, patterns]
    notes: Agent patterns blogs are often directly actionable.

  - id: openai-docs
    name: OpenAI Docs + blog
    kind: blog
    url: https://openai.com/research
    weight: 0.75
    tags: [models, tools]
    notes: Codex and agent-SDK updates matter.

  - id: claude-code-releases
    name: Claude Code releases
    kind: github_releases
    url: https://github.com/anthropics/claude-code
    weight: 0.9
    tags: [runtime, openclaw-base]
    notes: OpenClaw rides Claude Code — breaking changes are ours.

  - id: grok-online-pulse
    name: Grok :online ecosystem pulse
    kind: social_online
    url: "openrouter:x-ai/grok-4-fast:online"
    weight: 0.7
    tags: [live, social, news]
    notes: Use for "what is X saying about agents this week" style queries.

  - id: parallel-research
    name: Parallel deep research
    kind: manual
    url: "parallel skill"
    weight: 0.9
    tags: [deep-research]
    notes: Pull this when a trend needs multi-source confirmation.

  - id: hn-ai-agents
    name: Hacker News AI + agents
    kind: rss
    url: https://hnrss.org/newest?q=%28AI+OR+agent+OR+LLM%29
    weight: 0.55
    tags: [community]
    notes: Medium weight — signal is real but so is noise.

  - id: indydevdan
    name: IndyDevDan
    kind: blog
    url: https://www.youtube.com/@indydevdan
    weight: 0.7
    tags: [practitioners]
    notes: Curated watchlist voice (MEMORY.md).

  - id: ai-jason
    name: AI Jason
    kind: blog
    url: https://www.youtube.com/@AIJasonZ
    weight: 0.7
    tags: [practitioners]
    notes: Curated watchlist voice (MEMORY.md).

  - id: nate-jones
    name: Nate Jones
    kind: blog
    url: https://www.natesnewsletter.xyz
    weight: 0.7
    tags: [practitioners]
    notes: Curated watchlist voice (MEMORY.md).

  - id: fb-reels-nick-curated
    name: Nick-curated FB Reels account
    kind: manual
    url: https://www.facebook.com/profile.php?id=61587274601783
    weight: 0.85
    tags: [curated, high-signal, low-volume]
    notes: |
      High-signal, low-volume source Nick hand-picked. Nick cannot tell
      from the profile URL who it is — it is a Reels tab account. Use
      `grok-4-fast:online` or `parallel` search for fresh extracts;
      never attempt raw scraping. If the fetch fails repeatedly,
      demote to `manual_review_only: true` and surface in the brief.

  - id: fleet-telemetry
    name: Internal fleet telemetry
    kind: internal
    url: "cron-jobs.json + workflows/*/logs/"
    weight: 0.85
    tags: [fleet, self]
    notes: Our own stuck workflows / cron failures are the richest signal.

  - id: agent-platforms
    name: Agent platforms watchlist
    kind: manual
    url: |
      https://github.com/langchain-ai/langgraph
      https://github.com/coleam00/paperclip
      https://github.com/metaskills/experts
      https://github.com/openai/openai-agents-python
    weight: 0.75
    tags: [platforms]
    notes: Explicit watchlist to track platform churn.
```

## Scoring knobs

- Min score to keep: `0.4`
- Min score to recommend (tier 3): `0.7`
- Min score to draft (tier 4): `0.8`
- Trend requires ≥ 2 sources: `true`
- Max findings per brief: `5`
- Brief word limit: `200`

## Watchlist retention

- Tier 2 expires after: `21 days` unless re-seen
- After expiry: auto-apply class `watchlist_expire` archives them once enabled
