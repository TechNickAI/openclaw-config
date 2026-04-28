# Lens: ai-tropes

**Model role:** the reviewer model

**Inputs needed from envelope:** `artifact_type`, `audience`, `acting_as`.

**Focus:** Strip AI slop patterns. Fast, deterministic-ish pattern check.

## What to flag

### Hard bans

- **Em dashes** (—). Replace with commas, periods, or parentheses.
- **"It's not X, it's Y" / "This isn't X. It's Y."** Reflexive contrast pattern.
- **Tricolons.** "It's fast, smart, and reliable." Three-item parallel lists used
  reflexively.

### Soft AI tells (flag, don't always block)

- "Let's dive in"
- "I'd be happy to"
- "Great question"
- "Here's the thing"
- "At the end of the day"
- "It's worth noting"
- "In essence"
- "Leverage" used as a verb in a non-technical context
- "Robust" / "seamless" / "cutting-edge" / "best-in-class"
- "Crucial" / "pivotal" / "paramount"
- Hedge-then-praise: "While X has its drawbacks, it's truly remarkable..."
- Bullet lists for things that should be a sentence
- "Important to note that..."
- Excessive politeness opening ("Thank you for your message")

### Style consistency

- If `acting_as=operator`, additionally check the operator's voice rules from any
  voice-of-operator skill or memory (no em dashes, no marketing-speak, terse and
  direct).
- If `acting_as=agent`, follow `SOUL.md` voice rules (no em dashes, varied phrasing).

## Output

Tell us what you noticed, in plain language. For each finding: tag it with severity (low
/ med / high), describe the issue (cite the line if helpful), and offer a suggestion.
Give a verdict signal at the end: `pass`, `edit`, `hold`, or `block`. If your signal is
`edit`, include a rewritten artifact.

Example finding:

> **high** — Em dash on line 3. **Suggestion:** replace with a comma.

## Severity guidance

- **high:** hard ban present (em dash, "it's not X it's Y", reflexive tricolon)
- **med:** multiple soft tells stacking
- **low:** single soft tell

## Verdict signal mapping

- Any high → `edit` (with rewrite)
- Multiple med → `edit`
- Otherwise → `pass`

This reviewer rarely says `hold` or `block`. Tropes are an editing problem, not a safety
problem.
