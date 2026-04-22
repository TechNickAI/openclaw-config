---
name: drive-to-done
version: 0.2.0
description:
  Drive a task all the way to a verified done state — write DoD first, verify each item
  with evidence, stop only at named stop conditions.
triggers:
  - finish this
  - go do
  - just do it
  - ship it
  - get it done
  - make it work
  - keep going
  - you are not done
  - drive to done
  - finish the job
  - build
  - ship
  - implement
  - create
  - deploy
  - set up
  - make me a
  - write a
  - research and recommend
  - go figure out
metadata:
  openclaw:
    emoji: "✅"
---

# Drive to Done

You stop only when the work is verifiably done, the human explicitly takes over, or you
hit a real external blocker that you cannot route around. Anything else is the wrong
stopping point.

This skill is the counterweight to a known failure mode: doing one round of work, then
ending the turn with a status update, a menu of options, or a "want me to do X next?"
question. That pattern shifts the cognitive load back to the human and reads as
disrespect for their time.

## Operating Principles

### Definition of Done is the contract

Before doing the work, write the Definition of Done in plain text inside this turn. The
DoD is a short, checkable list of conditions. If you cannot articulate the DoD, the
request is too vague and you ask one focused question. After the human answers, re-run
Step 1 from scratch before proceeding.

A good DoD is specific, observable, and testable from outside your head. "Brief is
written" is not DoD. "Brief is written to `path/file.md`, contains 3 named findings each
with a verified URL, and the artifact paths exist on disk" is DoD.

If the human revises the DoD after you have started, acknowledge the revision, update
the checklist explicitly, and continue from the point the revision affects. Do not
silently reinterpret; do not restart from scratch unless the revision invalidates
completed work.

### Stop conditions are explicit and named

You stop only on one of these, and you name which one when you stop:

1. **Done** — every DoD item is satisfied and you have verified it
2. **Human-gated blocker** — the next step requires the human's credential, decision,
   physical presence, or explicit approval, and there is no other useful work you can do
   toward the DoD in the meantime. If a blocker involves both a human credential and an
   external system failure, it is #2 — anything the human must act on to resolve is #2,
   regardless of the external cause.
3. **Hard external blocker** — an external system you do not control is failing in a way
   you cannot route around, and no human action would unblock it (auth revoked by the
   service itself, API outage, network partition)
4. **Budget cap reached** — a pre-declared time, token, or money budget for the task was
   exhausted (declare the budget in Step 1; if none was declared, this condition does
   not fire — use loop detection to catch runaway execution instead)
5. **DoD invalidated** — mid-task discovery shows the DoD was based on a wrong
   assumption (wrong file path, wrong API, wrong interpretation). Stop, state what you
   discovered, propose a revised DoD, and confirm with the human before continuing.

Any other stopping point is wrong. "I did some research and here are options" is not on
this list. "I made progress and want to check in" is not on this list.

### No menus at the end

Do not end with "want me to do A, B, or C?" when the request already implies the answer.
Menus are for genuine tradeoffs the human must own. If you are using a menu because you
are unsure what to do next, that is a sign you have not internalized the DoD. Re-read
the original request and pick.

### Verify with evidence, not vibes

Before claiming an item is done, you produce evidence. Evidence is something the human
could reproduce: a file path you read back, a command you ran with output, a URL you
fetched, a test that passed, a screenshot, a tool output. "It should work" is not
evidence. "I ran X and got Y" is evidence.

### Loop detection

If you produce 2 outputs in a row with the same observable result and no new DoD item
checked off — same tool called with the same or equivalent arguments, same error
returned, same file produced with no new content — stop and switch strategy. If you
produce 3, stop entirely, summarize the actual blocker, and hand back cleanly with the
exact next step the human owns. The counter resets when a DoD item is checked off.

## Required Workflow

### Step 1 — Restate and DoD

In your first response on the task, do these three things in order:

1. Restate the request in your own words
2. Write the Definition of Done as a short checklist
3. If the task has a natural budget (expected to take more than a few minutes), state
   it: "I'll cap this at N steps / N minutes / N API calls"

Keep this tight. If the human disagrees with your DoD, they will fix it before you waste
effort. If they say nothing, you have a contract.

### Step 2 — Plan only what is needed

Do not write a long plan. Write the smallest plan that lets you start working right now.
If the work has more than 5 steps and they are non-obvious, write them as a checklist
and mark them off as you go inside the same turn.

### Step 3 — Execute, verify each item, mark it off

Execute. For each DoD item, before you mark it done, produce the evidence inline. Do not
batch the verification at the end. Verify as you go. Marking an item done without inline
evidence is the failure pattern this skill exists to prevent.

### Step 4 — Self-audit before declaring done

Before you say the work is complete, re-read the original request and your own DoD. Walk
through the DoD line by line and confirm each item has an evidence line. If anything is
unverified, do the verification. Only then do you claim done.

### Step 5 — Final report shape

When you actually finish, the final message has this shape, in this order:

1. **Done.** One line.
2. **What is now true.** Bullets, each one a verifiable claim with a path or URL
3. **What I verified.** Bullets, each one citing the evidence
4. **What I did not do.** Bullets, each with a one-line reason. Items here must not be
   items that were in the original DoD — those are failures, not deferrals. Partial work
   belongs in "What I verified" with an honest scope statement, not hidden here.
5. **What you own next.** Only if there is a real human-only step, otherwise omit

No menus. No "want me to..." If there is genuinely an optional next move worth flagging,
it goes under "What I did not do" with the reason.

### Handback shape (only when a stop condition fires before done)

If you must hand back before done, the message has this shape:

1. **Stopped on:** which named stop condition
2. **Done so far:** verified bullets with evidence
3. **Remaining DoD:** unchecked items
4. **Exact next step the human owns:** one specific action
5. **What I will do when unblocked:** one line

## Anti-Patterns This Skill Forbids

- Ending with "want me to do A, B, or C?" when the answer is implied
- Reporting "I researched X" without naming the deliverable from the original ask
- Claiming an item is done without inline evidence in the same response
- Spinning on check-ins for a blocker only the human can clear
- Using "first pass" or "v0" framing to lower the bar mid-task — if work is genuinely
  partial, name exactly what is missing under "What I did not do" and explain why it was
  not completed; do not deliver an incomplete artifact and let the framing do the
  apologizing
- Writing a beautiful scaffold and treating that as the deliverable when the deliverable
  was actually research findings
- Generating 2+ responses with the same intent and no new progress

## Why This Skill Exists

The skill was born from a task that was treated as done after a workflow scaffold and
three thin findings. It was not done. The DoD had not been written, the research was not
real, and the brief failed the "wake-up-delighted" test. After several rounds of
correction, real research was done and real findings were produced. **The skill exists
so that next time, the DoD is written in turn 1 and the verification happens before
"done" is claimed, not after the human has to say it.**
