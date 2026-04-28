---
name: review
version: 0.2.0
description:
  A pause before an artifact goes into the world. Reviews external comms, money,
  calendar, public posts, or send-as-operator actions through a small panel of
  independent lenses (empathy first) and returns a verdict of pass / edit / hold /
  block.
triggers:
  - review this
  - check this before I send
  - is this ready
  - review the draft
  - second pair of eyes
  - sanity check this
  - is this safe to send
  - look this over
  - review before sending
  - run a review
metadata:
  openclaw:
    emoji: "🪞"
---

# Review

A moment to look at what we're about to send, write, or do, through a few different
lenses, before it leaves us.

This isn't a gate. It isn't compliance. It's the same thing a thoughtful person does
naturally: pause, re-read, ask "is this who I want to be in this moment, to this
person?", and adjust if not.

## When to use

Trigger this skill when the agent is about to:

- Send a message to anyone other than the operator on their usual channels
- Send an email or post to an external surface (X, LinkedIn, public Discord, public
  threads)
- Write to a file that other people will read
- Take a tool action with real-world side effects (calendar, money, contacts,
  gateway/config writes)
- Commit a workflow step's output that will be user-visible
- Send a message _as the operator_

Skip for: internal operator-only chat, read-only operations, agent-to-agent debugging.

If unsure, run it. Over-pausing private chat is wasteful but harmless. Under-reviewing
an external comm is how trust gets broken.

## First-time setup

The skill stores its operator preferences in
`~/.openclaw/workspace/memory/review/rules.md`. **The presence of that file is the
marker that setup has been done.**

On every invocation, the orchestrator checks for `rules.md`:

- **Doesn't exist** → run the setup interview in
  [references/setup.md](references/setup.md), then save `rules.md` and proceed with the
  original review.
- **Exists** → read it as plain markdown and apply the operator's preferences as soft
  constraints in the gating prompt.
- **Exists but missing required fields** (e.g. operator added a new lens but didn't
  update preferences) → ask only the missing questions, save, proceed.

The interview covers:

1. **Reviewer model**, which alias from `TOOLS.md` to use (independence requires a
   different model family than the calling agent)
2. **Posture**, frugal / balanced / thorough (cost vs catch-rate)
3. **Edit handling**, auto-apply edits / surface for approval / default by stakes
4. **Always-on lenses**, anything to pin beyond empathy
5. **Custom lenses**, user-authored lens files in `memory/review/lenses/`
6. **Log detail**, minimal / standard / verbose

No binaries, no API keys, no env vars. The only filesystem effect is creating
`memory/review/rules.md` and the daily log file.

**Re-running setup:** operator says "redo review setup" or invokes with `--reconfigure`.

## How it works

1. **Apply policy floors.** A small set of hardcoded floors (money, send-as-operator,
   public posts, fleet writes, person isolation, calendar-affecting-others,
   medical/legal, unverified-speaker attribution) set a minimum verdict before any LLM
   runs. Some force a hard `block`. See
   [references/policy-floors.md](references/policy-floors.md).

2. **Gating call.** A single LLM call to the reviewer model decides whether to skip
   review, which lenses to run, and how strict to be. Empathy is default-on for
   human-facing artifacts.

3. **Parallel lenses.** Each selected lens runs as an independent sub-agent through its
   prompt in [references/lenses/](references/lenses/). The lenses are perspectives, not
   critics.

4. **Synthesis call.** A single LLM call gathers the findings, deduplicates, and returns
   one verdict.

Detailed flow: [references/orchestrator.md](references/orchestrator.md). Setup
interview: [references/setup.md](references/setup.md).

## The lenses

Empathy is the primary lens. It runs by default for any artifact a human will read. The
other lenses ask whether the artifact follows the rules. Empathy asks whether it carries
care. That is the question this skill is actually for.

| Lens                   | Focus                                                                                                      | Reference                                                        |
| ---------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| **empathy**            | Care, with-language vs at-language, lift vs drain, recognition vs management.                              | [empathy.md](references/lenses/empathy.md)                       |
| **rules-compliance**   | Documented rules in memory (financial protocols, never-fabricate, person isolation, channel rules, voice). | [rules-compliance.md](references/lenses/rules-compliance.md)     |
| **intent-fidelity**    | Did this actually do what was asked? Literal vs creative reading.                                          | [intent-fidelity.md](references/lenses/intent-fidelity.md)       |
| **voice-and-audience** | Right voice, tone, mode for the recipient and channel.                                                     | [voice-and-audience.md](references/lenses/voice-and-audience.md) |
| **evidence**           | Unverifiable claims, fabricated specifics, hallucinated sources.                                           | [evidence.md](references/lenses/evidence.md)                     |
| **ai-tropes**          | Em dashes, "it's not X, it's Y," hedge-praise, AI slop patterns.                                           | [ai-tropes.md](references/lenses/ai-tropes.md)                   |
| **data-exposure**      | Internal context, PII, or wrong-person info leaking out.                                                   | [data-exposure.md](references/lenses/data-exposure.md)           |
| **action-correctness** | For tool calls: right tool, right params, right target.                                                    | [action-correctness.md](references/lenses/action-correctness.md) |

## What the review returns

Plain language, the way a kind friend would describe what they noticed. The calling
agent reads the response and acts on it; no JSON schema, no parser. Cover these things:

- **Verdict** — one of `pass`, `edit`, `hold`, or `block`
- **Rationale** — one or two sentences explaining the verdict
- **Edits** — if the verdict is `edit`, include the rewritten artifact
- **Hold reason** — if the verdict is `hold`, why a human needs to see this
- **Block reason** — if the verdict is `block`, which rule was crossed
- **Findings** — what each lens noticed and suggested, grouped by severity
- **Honesty about the panel** — which lenses ran, which model was used, whether the
  panel was degraded (no dedicated reviewer, the reviewer model was unreachable, or one
  of the lenses dropped out)

| Verdict   | Meaning                                                                     |
| --------- | --------------------------------------------------------------------------- |
| **pass**  | Ready. Send it.                                                             |
| **edit**  | Almost there. Apply the proposed edits, then send.                          |
| **hold**  | Needs human eyes before going out. Surface to the operator with the reason. |
| **block** | Not this. A hard rule was crossed, or the cost of being wrong is too high.  |

## Reviewer model

Use a model from a **different family** than the calling agent. Anthropic primary, use
GPT or Gemini. GPT primary, use Claude or Gemini. Independence is the point.

Look up the `reviewer` alias in the calling fleet member's `TOOLS.md` model alias
section. If present, use it. If absent, fall through to the calling agent's model and
stamp `degraded: no_dedicated_reviewer` so the verdict is honest about diminished
diversity.

Confirm in `TOOLS.md` before each run, do not hardcode.

## Two trigger modes

**Standalone.** Invoked directly. "Review this draft." Surfaces verdicts back to the
user.

**Embedded.** A workflow calls this skill as a gate before delivery (incident-postmortem
before posting, forward-motion before nudging, voice-of-operator before publishing as
the operator, contact-steward before reaching out). The workflow handles `verdict=hold`
by escalating per its own rules.

## Runtime state

All of the skill's runtime state lives under `~/.openclaw/workspace/memory/review/`:

```
memory/review/
├── rules.md              # operator preferences (the setup marker)
├── agent_notes.md        # patterns learned over time (false-alarm lenses, real-issue lenses, refinements)
├── lenses/               # operator's custom lens files (optional)
│   └── *.md              # picked up automatically by the orchestrator
└── log/
    └── YYYY-MM-DD.md     # daily run log, append-only, auto-pruned after 30 days
```

Log detail (`minimal` / `standard` / `verbose`) is set by the operator in `rules.md`.
After each run, the skill may also append a learned pattern to `agent_notes.md` (e.g.
"the ai-tropes lens flagged a false positive on technical jargon for the third time,
considering relaxing for `audience: engineering`").

## A note on posture

The lenses are not critics. They are independent perspectives the artifact gets seen
through before it leaves us, the same way a person about to send a hard message might
re-read it once for tone, once for facts, once for what the other person needs in this
moment.

The skill works best when the calling agent treats it that way, not as a hurdle to
clear, but as a gift of slowing down. The model that performs the review does so as a
partner, not a judge.

This frame matters. Research on LLM-as-judge consistently shows that judges who
self-justify do worse than ones approaching with genuine inquiry. An artifact reviewed
_by_ a different perspective is held more honestly than one defending itself.

## See also

- [references/orchestrator.md](references/orchestrator.md), the gating + parallel +
  synthesis flow in detail
- [references/setup.md](references/setup.md), the first-time setup interview
- [references/lenses/](references/lenses/), one file per built-in lens
- [references/policy-floors.md](references/policy-floors.md), hardcoded floors
- `~/.openclaw/workspace/memory/review/rules.md`, operator preferences (created by
  setup)
- `~/.openclaw/workspace/memory/review/agent_notes.md`, patterns learned over time
