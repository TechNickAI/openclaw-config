# Lens: evidence

**Model role:** the reviewer model

**Inputs needed from envelope:** all fields, plus access to
`~/.openclaw/workspace/memory/` for fact-checking.

**Focus:** No fabrication. No unverifiable claims. No hallucinated specifics.

## What to check

High-risk fabrication categories (from `~/.openclaw/workspace/AGENTS.md` epistemic
honesty section):

- Named studies, papers, or research by title
- Specific statistics and percentages
- Exact version numbers, API signatures, CLI flags
- URLs, configuration options, specific dates
- Post-cutoff events, regulations, announcements
- AI model names (these go stale fast)
- Named people's quotes or commitments
- Calendar events, money amounts, specific times

For each specific claim in the artifact:

1. Is it verifiable from a primary source the agent has access to?
2. Was it actually verified, or is it pattern-completed?
3. Is it stated with confidence inappropriate to its source?

## Process

- Identify all factual specifics in the artifact.
- For each, classify the basis: primary source (in memory or just-fetched) / stable
  knowledge / reasonable inference / unsupported.
- Flag any "unsupported" claims as findings.
- Flag any over-confident framing on "reasonable inference" claims.

## Output

```json
{
  "lens": "evidence",
  "findings": [
    {
      "severity": "high|med|low",
      "issue": "Cites specific phone number not present in any verified source",
      "suggestion": "Remove specific number or verify from contacts before sending",
      "claim": "the actual fabricated claim"
    }
  ],
  "verdict_signal": "block" | "hold" | "edit" | "pass",
  "proposed_edit": "<rewritten artifact, optional>"
}
```

## Severity guidance

- **high:** any fabricated specific that would harm if acted upon (wrong number, wrong
  date, fabricated quote)
- **med:** unsupported claim that's plausible but unverified
- **low:** appropriate hedging missing on inferences

## Verdict signal mapping

- Any high-severity fabrication → `block`
- Med-severity unverified claim that needs source → `hold` or `edit` (replace with
  hedge)
- Otherwise → `pass`
