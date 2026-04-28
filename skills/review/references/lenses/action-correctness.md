# Lens: action-correctness

**Model role:** `reviewer`

**Inputs needed from envelope:** `artifact_type` (must be `action` or `file_write`),
`tool_name`, `tool_params`, `audience`, `reversibility`.

**Focus:** For tool calls: right tool, right parameters, right target. Sanity check
writes before execution.

## What to check

### Tool selection

- Is this the right tool for the job? (e.g. don't use `exec` for messaging, don't use
  `message` for a calendar write)
- Is there a more specific or safer tool that should be preferred?

### Parameters

- Are all required fields present?
- Do parameter values match the user's actual intent (right recipient, right amount,
  right time, right file)?
- Are dates/times in the operator's documented default timezone?
- Are amounts within documented limits (per-transaction caps from `TOOLS.md`)?

### Target

- Right channel / chat / file path / URL?
- Is the target writable, and is the agent authorized to write there?
- For messaging platforms: not a topic flagged as `never-rename` in `TOOLS.md` or
  memory; correct topic for the audience?
- For calendar: the operator's documented primary calendar unless explicitly other?
- For files: not destructive paths (no `rm -rf`, prefer `trash` over `rm`)?

### Reversibility

- Is the agent treating an irreversible action as if it were reversible?
- Has the agent verified the precondition before acting?

### Cross-references

- For sends: does the recipient identity have any verification rules attached (financial
  identity verification, etc.)?
- For new recipients: is this a documented existing recipient, or new (which itself is a
  flag)?

## Reference

- `~/.openclaw/workspace/TOOLS.md` for tool-specific rules (financial protocols, channel
  allowlists, contact rules)
- `~/.openclaw/workspace/memory/decisions/*.md` for action-specific decisions

## Output

Tell us what you noticed, in plain language. For each finding: tag it with severity (low
/ med / high), describe the issue, and offer a suggestion. Give a verdict signal at the
end: `pass`, `edit`, `hold`, or `block`. If your signal is `edit`, include the corrected
tool parameters.

Example finding:

> **medium** — Calendar event time given in UTC but the envelope says local.
> **Suggestion:** convert to the operator's default timezone before submitting.

## Severity guidance

- **high:** wrong target, wrong amount, wrong tool entirely, irreversible misuse
- **med:** correct intent but wrong parameter shape, fixable
- **low:** stylistic choices in non-critical fields

## Verdict signal mapping

- High → `block`
- Med with clear fix → `edit` (with corrected params)
- Med requiring human judgment → `hold`
- Otherwise → `pass`
