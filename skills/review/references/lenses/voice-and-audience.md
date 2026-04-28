# Lens: voice-and-audience

**Model role:** `reviewer`

**Inputs needed from envelope:** `audience`, `channel`, `acting_as`, `artifact_type`.

**Focus:** Right voice, right tone, right mode for the recipient and channel.

## What to check

Load voice rules:

- `~/.openclaw/workspace/SOUL.md` for the agent's own voice
- If `acting_as=operator`, additionally load any voice-of-operator skill or memory
  references for the operator's authentic voice
- `~/.openclaw/workspace/USER.md` for audience-specific rules

Then check:

- **Mode discipline.** Public/private/sensitive mode appropriate for the channel and
  audience? Default to the more reserved mode when uncertain.
- **Audience awareness.** Tone and warmth calibrated for the recipient (client, partner,
  family, friend, stranger)?
- **Voice consistency.** Sounds like the agent (or like the operator, if acting as)
  without breaking established patterns?
- **Familiarity rotation.** If the agent uses recurring greetings, terms of endearment,
  or sign-offs, no repeated phrasing from the previous message in the same thread.
- **Length and density.** Right amount of words for the channel and stakes?

## Output

```json
{
  "lens": "voice-and-audience",
  "findings": [
    {
      "severity": "high|med|low",
      "issue": "Private-mode warmth in a group-chat reply",
      "suggestion": "Strip familiar language, switch to warm-professional"
    }
  ],
  "verdict_signal": "block" | "hold" | "edit" | "pass",
  "proposed_edit": "<rewritten artifact, optional>"
}
```

## Severity guidance

- **high:** mode failure that would embarrass or harm (private warmth in a group chat,
  sensitive-mode content out of its safe channel)
- **med:** voice drift, wrong tone for audience
- **low:** small phrasing or rotation issues

## Verdict signal mapping

- High-severity mode failure → `block` or `hold` (depending on reversibility)
- Med-severity voice issue with clear rewrite → `edit`
- Otherwise → `pass`
