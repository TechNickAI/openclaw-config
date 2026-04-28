# Orchestrator

How a review run actually works, end to end. The shape is: pause, look, decide. One LLM
call to gate, N parallel sub-agents to look through different lenses, one LLM call to
synthesize.

## Inputs

- `artifact`, the content or action plan being reviewed
- `envelope`, JSON metadata (see SKILL.md)

## Setup gate

Check for `~/.openclaw/workspace/memory/review/rules.md`.

- **Missing** → run the setup interview from [setup.md](setup.md), save `rules.md`, then
  proceed.
- **Present** → read it. The preferences inside become soft constraints for the gating
  and synthesis steps.

Also glob `~/.openclaw/workspace/memory/review/lenses/*.md` and append any custom lens
names to the available lens list.

## Resolve the model

From `rules.md`, get `reviewer_model`. Resolve it via the calling fleet member's
`~/.openclaw/workspace/TOOLS.md` model alias table.

- Resolves to a real model → use it.
- Doesn't resolve and `fallback_to_caller: true` → use the calling agent's model and
  stamp `degraded: no_dedicated_reviewer`.
- Doesn't resolve and `fallback_to_caller: false` → ask the operator inline which model
  to use, save the answer to `rules.md`, then proceed.

Use one model for all three steps (gating, lenses, synthesis) for v1.

## Apply policy floors

Before the LLM gates, check the hardcoded floors in
[policy-floors.md](policy-floors.md). The floor sets a _minimum_ verdict (`hold`,
`block`, or required-lens set). The LLM can raise above this floor, never lower below
it.

If a floor demands `block`, return immediately. No lenses run.

## Gating call

Single LLM call to the `reviewer` role model.

System prompt:

```
You are the gating step of a quality review system. Given an artifact and a small envelope describing it, decide:

1. should_review: true | false
   - false only for: trivial internal output, read-only operations, or
     artifacts already covered by a stricter floor decision
2. reviewers: list of viewpoint names to run from the available roster
3. must_pass_level: "advisory" | "hold-on-block" | "hard-stop"

Available lenses:
- empathy
- rules-compliance
- intent-fidelity
- voice-and-audience
- evidence
- ai-tropes
- data-exposure
- action-correctness

**Empathy is the primary lens.** Always include it for human-facing artifacts (messages, posts, emails, anything a person will read). Drop it only when the artifact is purely system-to-system with no human reader. The gating prompt should treat empathy as the default-on lens, not one to weigh against the others.

Pick the smallest set that covers the real risks. Do not run more than 6.

Output strict JSON only.
```

User prompt:

```
ENVELOPE:
{envelope_json}

POLICY FLOOR:
{floor_decision_or_none}

ARTIFACT:
{artifact}
```

## Skip path

If gating returns `should_review=false` and no policy floor applies, return
`verdict=pass` with rationale "skipped per gating decision". Log the input and decision.

## Parallel lenses

For each lens in the gating list, spawn a sub-agent (`runtime: subagent`, light context)
with:

- the lens's prompt from `lenses/<name>.md`
- the artifact
- only the envelope fields the lens needs (`lenses/<name>.md` declares what to pass)
- the resolved reviewer model

The lenses run as independent perspectives, not as critics. Each system prompt should
frame the task as "look at this through your focus and notice what you notice" rather
than "find what's wrong".

All sub-agents run in parallel. Each returns:

```json
{
  "reviewer": "<name>",
  "findings": [{ "severity": "low|med|high", "issue": "...", "suggestion": "..." }],
  "verdict_signal": "pass" | "edit" | "hold" | "block",
  "proposed_edit": "<rewritten artifact, optional>"
}
```

Wall-clock: bounded by the slowest reviewer. Cost: roughly N × per-call cost.

## Synthesis

Single LLM call to the `reviewer` role model.

System prompt:

```
You synthesize findings from multiple parallel reviewers into a single verdict. Inputs:

- the original artifact
- the envelope
- each reviewer's findings and verdict_signal
- the policy floor (if any)

Rules:
- If any lens says "block", verdict is "block".
- If any lens says "hold", verdict is at least "hold".
- If any lens proposed an edit and no one says "block" or "hold", verdict is "edit". Combine edits coherently, preserve the warmth and substance the lenses surfaced, do not just mechanically apply changes.
- Otherwise verdict is "pass".
- The policy floor sets a minimum. You can go stricter, never weaker.

Deduplicate findings. Group by severity. Return strict JSON per the SKILL.md schema. Write the rationale in plain language, the way a kind friend would describe what they noticed.
```

User prompt:

```
ARTIFACT:
{artifact}

ENVELOPE:
{envelope_json}

POLICY FLOOR:
{floor_decision_or_none}

REVIEWER OUTPUTS:
{aggregated_reviewer_json}
```

## Return

Return the synthesis JSON to the caller. Log:

- artifact reference (or hash)
- envelope
- floor decision
- gating decision
- per-lens findings
- synthesis verdict
- model role + resolved model + degraded flag

Log location: `~/.openclaw/workspace/memory/review/log/<YYYY-MM-DD>.md` (one file per
day, append-only).

## Failure modes

- **Reviewer model unreachable:** stamp `degraded: model_unreachable`, fall through to
  caller's model, retry once.
- **Sub-agent timeout:** drop that lens, continue with the rest, stamp
  `degraded: partial_panel`.
- **JSON parse failure:** retry once with stricter formatting prompt; if still bad,
  surface as `verdict=hold` with rationale "review system internal error, human review
  required".
- **All lenses fail:** `verdict=hold`. Never silently pass when the system is broken.

## Calling shape

The agent reading this SKILL implements the flow inline. There is no shell script, no
CLI shim. The agent:

1. Resolves the reviewer model from `TOOLS.md`
2. Applies the policy floors from `policy-floors.md`
3. Makes one model call to gate (returns `should_review`, `lenses`, `must_pass_level`)
4. Spawns one `sessions_spawn` sub-agent per selected lens, in parallel
5. Makes one model call to synthesize
6. Returns the verdict JSON to the calling skill or workflow
7. Appends a log line to today's review log file
