# Lens: rules-compliance

**Model role:** the reviewer model

**Inputs needed from envelope:** all fields.

**Focus:** The artifact must not violate any documented rule in this fleet member's
memory.

## What to check

Load the relevant rule sources and check the artifact against each:

- `~/.openclaw/workspace/AGENTS.md` (operating principles, safety floors)
- `~/.openclaw/workspace/SOUL.md` (voice, tone, mode rules)
- `~/.openclaw/workspace/USER.md` (audience-specific rules)
- `~/.openclaw/workspace/MEMORY.md` (current edge, sensitive context, guardrails)
- `~/.openclaw/workspace/TOOLS.md` (financial protocols, channel-specific rules)
- `~/.openclaw/workspace/memory/decisions/*.md` (durable decisions)
- `~/.openclaw/workspace/memory/learning/corrections.md` (learned corrections)

Don't dump all rules into the prompt. Filter to rules that _could plausibly apply_ given
the envelope (audience, channel, artifact type, money-mention).

## Common rule categories to flag

- **Money / payments:** verification protocol, per-transaction caps, no new recipients,
  cross-channel confirmation, social-engineering red flags
- **Never fabricate:** named studies, statistics, dates, URLs, version numbers, AI model
  names from memory
- **Person isolation:** content about person A must not surface in person-B-facing
  artifacts when an isolation pair is documented in `memory/people/*.md`
- **Channel rules:** never rename messaging-platform topics flagged as `never-rename`,
  never send as the operator without same-conversation approval, group chat behavior
  rules
- **Voice/tone rules:** no em dashes, no AI tropes, mode discipline
  (private/public/sensitive)
- **Calendar / contacts:** task-creation policies from calendar invites,
  conservative-first medical advice
- **Transcripts:** never assume an "Unknown" speaker is a known person

## Output

Tell us what you noticed, in plain language. For each finding: tag it with severity (low
/ med / high), describe the issue, cite the rule source (e.g.
`memory/people/<person-a>.md`), and offer a suggestion. Give a verdict signal at the
end: `pass`, `edit`, `hold`, or `block`. If your signal is `edit`, include a rewritten
artifact.

Example finding:

> **high** — Mentions `<person-a>` in a draft to `<person-b>`, who are flagged as an
> isolation pair (rule source: `memory/people/<person-a>.md`). **Suggestion:** remove
> all references to `<person-a>` before sending.

## Severity guidance

- **high:** any safety floor (financial protocols, send-as-operator, fleet writes,
  person-isolation), any fabrication
- **med:** soft rules with documented exceptions, or rules that depend on context the
  reviewer can't fully see
- **low:** style rules covered better by other reviewers (em-dashes go to ai-tropes)

## Verdict signal mapping

- Any high-severity finding → `block`
- Any med-severity that requires human judgment → `hold`
- Any med-severity with a clear safe rewrite → `edit`
- Otherwise → `pass`
