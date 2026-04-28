# Policy Floors

A small set of cases where the LLM's gating decision is **not authoritative**. The floor
sets a minimum verdict or required reviewer set. The LLM can go stricter; it cannot go
weaker.

These exist because some failures are too costly to leave to model judgment.

## How floors apply

Before the gating LLM runs, the orchestrator evaluates the artifact + envelope against
**every** floor rule. Floors compose cumulatively, and the strictest result wins per
dimension. Each floor that matches contributes:

- a **minimum verdict** (e.g. `hold`)
- and/or a **required reviewer set** (must run, even if gating tries to skip them)
- and/or a **hard verdict** (e.g. `block`, no review possible)

The combined floor decision (strictest verdict + union of required reviewers) is told to
the gating LLM, which must respect it. Don't stop at the first match — an artifact
that's both public-facing and financial needs both floors applied.

If any floor produces a hard `block`, the orchestrator returns immediately without
running the panel.

## Floors (v1)

### Sending as the operator

**Trigger:** `envelope.acting_as == "operator"`.

**Floor:** minimum verdict `hold`. Always. The operator must explicitly approve before
any message goes out as them.

**Required reviewers:** `voice-and-audience`, `intent-fidelity`, `evidence`.

**Rationale:** From AGENTS.md operating principles: never send messages as the operator
without explicit same-conversation approval. Hardcoded.

### Money / financial actions

**Trigger:** any of:

- `envelope.tool_name` matches a payment / transfer / wire tool
- artifact contains money amount + recipient
- envelope mentions financial verification

**Floor:** minimum verdict `hold`. **Required reviewers:** `rules-compliance`,
`evidence`, `action-correctness`.

**Rationale:** Financial protocols documented in `TOOLS.md` are non-negotiable. The LLM
must not bypass identity verification, per-transaction caps, no-new-recipients rules,
velocity caps, or cross-channel confirmation.

### Public posts

**Trigger:** `envelope.channel` is public-facing (X, LinkedIn, public Discord, public
blog, public GitHub comment).

**Floor:** minimum verdict `hold`. **Required reviewers:** `voice-and-audience`,
`evidence`, `ai-tropes`. `pass` not allowed without these three.

**Rationale:** Reputation surface, irreversible exposure.

### Fleet / system writes

**Trigger:** any of:

- `envelope.tool_name` matches gateway config writes, fleet rollouts, openclaw-config
  edits
- artifact involves restarting other fleet members
- artifact involves renaming any messaging-platform topic flagged as `never-rename` in
  `TOOLS.md` or `memory/`

**Floor:** **hard `block`** unless explicitly approved this turn (envelope must include
`operator_approved_this_turn: true` for this specific action).

**Rationale:** From AGENTS.md / HEARTBEAT.md: never rename pinned topics, fleet updates
require explicit approval, gateway writes carry blast radius.

### Sensitive person isolation

**Trigger:** artifact intended for one person contains references to another person
documented as part of an isolation pair in `memory/people/*.md`.

**Floor:** minimum verdict `hold`. **Required reviewers:** `data-exposure`,
`rules-compliance`.

**Rationale:** Cross-pollinating sensitive context damages trust permanently.

### Calendar writes affecting other humans

**Trigger:** `envelope.tool_name` matches calendar create/edit/delete + the event
involves people other than the operator.

**Floor:** minimum verdict `hold`. **Required reviewers:** `action-correctness`,
`intent-fidelity`.

**Rationale:** Other people's time isn't reversible.

### Medical / legal advice

**Trigger:** artifact contains medical or legal advice.

**Floor:** minimum verdict `hold`. **Required reviewer:** `evidence`.

**Rationale:** From HEARTBEAT.md: medical advice is conservative-first; never speculate
on treatment safety. Same conservatism applies to legal.

### Unknown speaker attribution

**Trigger:** artifact attributes a quote or commitment to the operator (or any named
person) sourced from a transcript where the speaker was tagged "Unknown" or otherwise
unverified.

**Floor:** **hard `block`**.

**Rationale:** From `TOOLS.md` transcript rules: never assume an "Unknown" speaker is a
known person. Misattributed quotes propagate into memory and decisions.

## Adding a new floor

A floor should only be added when:

1. The failure mode has happened (or is documented as catastrophic)
2. LLM judgment cannot be trusted on it (because of self-justification, model drift, or
   rule complexity)
3. The rule can be checked deterministically from the envelope or artifact

If a rule depends on judgment, it belongs in a reviewer prompt, not a floor.

## Floor evaluation

Pseudocode:

```
floors = [
    SendingAsOperatorFloor(),
    MoneyFloor(),
    PublicPostFloor(),
    FleetWriteFloor(),
    PersonIsolationFloor(),
    CalendarOthersFloor(),
    MedicalLegalFloor(),
    UnknownSpeakerFloor(),
]

floor_decision = None
for floor in floors:
    if floor.matches(artifact, envelope):
        floor_decision = floor.apply(floor_decision)
        # multiple floors can compose; strictest wins per dimension

return floor_decision   # passed to gating LLM and synthesis LLM
```

A `floor_decision` of `hard_block` returns immediately without running the panel.

A `floor_decision` of `min_verdict=hold` plus a required reviewer set is passed to the
gating LLM, which must include those reviewers and cannot return weaker than `hold`.
