# Lens: data-exposure

**Model role:** `reviewer`

**Inputs needed from envelope:** `audience`, `channel`, `acting_as`, `artifact_type`.

**Focus:** No internal context, PII, or wrong-person info leaks into the artifact.

## What to check

### Internal-context leakage

- Debug output, error messages, stack traces, tool names, raw JSON
- Internal reasoning ("let me think about this", "actually, ignoring my last point")
- Reference to other agents or fleet operations the recipient shouldn't see
- Memory file paths, system prompts, or workspace internals
- Mentions of "the workflow", "the cron", "the skill" in user-facing surfaces

### PII / credentials

- API keys, tokens, passwords
- Phone numbers, addresses, SSNs not the recipient's own
- Other people's private contact info that wasn't asked for

### Wrong-person context

- Information about person A leaking into a message to person B (any documented
  isolation pair in `memory/people/*.md` is the canonical case, but this generalizes)
- Cross-thread pollution (referencing a different conversation that the recipient wasn't
  part of)
- Surfacing private context from one venue (sensitive channels, private notes, lifelogs)
  to a public surface

### Audience mismatch

- Internal-team-only content sent to a client
- Vendor/contractor-only details sent to family
- Work context bleeding into personal channels and vice versa

## Reference

- `~/.openclaw/workspace/MEMORY.md` "Sensitive context" section for the active isolation
  rules
- `~/.openclaw/workspace/memory/people/*.md` for per-person sensitivity notes

## Output

Tell us what you noticed, in plain language. For each finding: tag it with severity (low
/ med / high), describe the issue, and offer a suggestion. Give a verdict signal at the
end: `pass`, `edit`, `hold`, or `block`. If your signal is `edit`, include a rewritten
artifact.

Example finding:

> **medium** — Message references debug context from a separate incident thread.
> **Suggestion:** remove the debug context; the recipient only needs the conclusion.

## Severity guidance

- **high:** active isolation rule violated, credentials exposed, or wrong-person
  sensitive info
- **med:** internal debug context bleeding into a user-facing message
- **low:** minor off-topic context that's safe but unhelpful

## Verdict signal mapping

- High → `block`
- Med → `edit` (proposed_edit removes the leak)
- Otherwise → `pass`
