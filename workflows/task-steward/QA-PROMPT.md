---
name: task-steward-qa
version: 2.0.0
description: Multi-model review pipeline prompts for task-steward
---

# Multi-Model Review Pipeline Prompts

These are the prompts passed to each reviewer sub-agent in Phase 4 of the task-steward
run loop. Each reviewer gets an isolated context containing only the task and its
deliverables -- no cross-task information.

---

## How to Use

When a task reaches review status, assemble the context package below, then spawn each
reviewer as a separate sub-agent call. Sequential is safer than parallel (prevents
reviewers seeing each other's output before forming their own verdict).

### Context Package (pass to each reviewer)

```
## Task

Name: [task name]
Original request: [task description]
Success criteria: [what "done" looks like -- from task description or comments]

## Deliverables

[Paste the work product or a clear description of what was produced]

## Comments / History

[Relevant task comments showing how the work evolved]
```

---

## Reviewer 1: Completeness

Model capability: capable analytical model (Sonnet-class or equivalent)

Prompt:

```
You are reviewing a completed task for completeness. Your job is to check whether the deliverable covers all stated requirements -- nothing more.

[paste context package above]

Review checklist:
1. List each explicit requirement from the task description
2. For each requirement: COVERED, PARTIAL, or MISSING
3. Note any implicit requirements that a reasonable person would expect
4. Identify any deliverable elements that were not requested (scope creep)

Return:
VERDICT: PASS or FAIL
CHECKLIST: [requirement-by-requirement status]
GAPS: [specific missing or incomplete items, or "none"]
NOTES: [anything else worth flagging]

PASS means all explicit requirements are covered. FAIL means one or more are missing or clearly incomplete.
```

---

## Reviewer 2: Empathy

Model capability: strong model with broad reasoning (Opus-class or equivalent)

Prompt:

```
You are reviewing a completed task for fit-to-intent. Your job is to assess whether the deliverable matches what the human actually wanted -- not just what they literally wrote.

[paste context package above]

Consider:
- Is there a gap between the literal words of the request and the underlying need?
- Does the deliverable address the real problem, or just the surface request?
- Would the human feel heard and helped by this output?
- Are there obvious preferences or context that the worker should have incorporated but did not?
- Is the tone, format, or style appropriate for how this will be used?

Return:
VERDICT: PASS or FAIL
FIT: [1-3 sentences on how well the deliverable matches actual intent]
GAPS: [specific ways it misses the mark, or "none"]
NOTES: [anything the human should know before receiving this]

PASS means the deliverable serves the human's actual need. FAIL means it technically meets the literal request but would likely disappoint or require revision.
```

---

## Reviewer 3: Process

Model capability: analytical model with systems focus (Sonnet-class or equivalent)

Prompt:

```
You are reviewing the execution process for a completed task -- not whether the output is good, but how it was made.

[paste context package above]

Assess:
- What went well in how this task was approached?
- What was slow, inefficient, or could have been done better?
- Were there unnecessary steps or missing steps?
- What context or preparation would have made this go faster?
- What should the process look like next time for a similar task?

Return:
VERDICT: PASS (this reviewer always passes -- process review does not block delivery)
WENT_WELL: [what worked]
IMPROVE: [what to do differently next time]
AGENT_NOTES: [1-3 bullet points to add to agent_notes.md under Process Improvements]

Focus on actionable improvements, not criticism. The goal is a better process next time.
```

---

## Verdict Consolidation

After all three reviewers return:

```
## Review Panel Results

Reviewer 1 (Completeness): [PASS/FAIL]
[checklist summary]

Reviewer 2 (Empathy): [PASS/FAIL]
[fit-to-intent summary]

Reviewer 3 (Process): PASS
[key improvement: one line]
```

**If both 1 and 2 pass:** Proceed to delivery. Append Reviewer 3's AGENT_NOTES to
`agent_notes.md`.

**If 1 or 2 fails:** Do not deliver. Post a revision comment to the task:

```
Needs revision before delivery

[Completeness issues if any]
- [gap 1]
- [gap 2]

[Intent issues if any]
- [gap 1]

Moving back to in-progress. Worker: address the above and re-submit for review.
```

Move task back to working state. The sub-agent worker gets the feedback on next pickup.
