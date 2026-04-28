# First-Time Setup

The skill checks for `~/.openclaw/workspace/memory/review/rules.md` at the start of
every run. If it doesn't exist, run the setup interview before the actual review. If it
does, read it and apply the operator's preferences.

## When to run setup

- First time the skill is invoked on this fleet member
- Operator runs the skill with `--reconfigure` or asks "redo review setup"
- `rules.md` exists but is missing required fields (the skill should diff what's there
  vs what's expected and ask only the missing questions)

## The interview

Run as a conversational sequence. Ask one question per turn. Always offer "skip" and
"use the default" options. Summarize the resulting `rules.md` in plain language before
saving.

### Question: Reviewer model

> Review works best when the reviewer is a different model family than the calling agent
> (independence is the whole point). Looking at your `TOOLS.md` aliases, options that
> look like a good independent reviewer here: <list 2-3 candidates from a different
> family than the primary>. Or you can name a specific model. What should I use?

If `TOOLS.md` has no model aliases at all, prompt the operator to pick a model directly
(any non-primary family works).

Save as `reviewer_model:` in rules.md.

### Question: Cost vs thoroughness posture

> Three postures, pick one:
>
> **Frugal**, run the empathy lens always, plus 1-2 others only when the artifact looks
> risky. Skip review entirely on low-stakes drafts. Lowest token cost.
>
> **Balanced** _(default)_, run empathy plus the gating LLM's recommended subset.
> Moderate token cost.
>
> **Thorough**, run all 8 lenses for any human-facing artifact. Highest token cost,
> highest catch rate.

Save as `posture:` in rules.md.

### Question: Speed vs care

> When the verdict is `edit`, do you want the skill to:
>
> **Auto-apply** the edits and return the rewritten artifact (faster, less control)
>
> **Surface the edits** as a diff for you to approve (slower, more control)
>
> **Default by stakes** _(recommended)_, auto-apply for low-stakes, surface for
> high-stakes (`acting_as: operator`, public posts, money, send-to-others)

Save as `edit_handling:` in rules.md.

### Question: Always-on lenses

> Are there any lenses you want to **always** run, regardless of what the gating LLM
> picks? Empathy is already always-on for human-facing artifacts.
>
> Common pinned lenses: `rules-compliance` (if you have strict person-isolation),
> `voice-and-audience` (if you regularly write as someone else).

Save as `always_run:` array in rules.md.

### Question: Custom lenses

> Do you have any review concerns that aren't covered by the 8 default lenses? You can
> write a custom lens as a markdown file at
> `~/.openclaw/workspace/memory/review/lenses/<name>.md` and it'll get included in the
> panel.
>
> Examples: `family-context.md` (special rules for messages to family),
> `legal-review.md` (contract-specific checks), `brand-voice.md` (company voice rules).
>
> Want to draft one now, or skip and come back later?

If yes, walk them through writing a custom lens (use existing lenses as templates,
~30-60 line prompt files).

### Question: Logging detail

> Reviews log to `memory/review/log/YYYY-MM-DD.md`. How much detail do you want?
>
> **Minimal**, verdict + one-line rationale per run
>
> **Standard** _(default)_, verdict, rationale, lens findings summary
>
> **Verbose**, full per-lens findings + reasoning trail (useful for tuning the skill
> itself)

Save as `log_level:` in rules.md.

### Wrap up

Show the operator a plain-language summary:

> Saved. Here's how I'll review for you:
>
> - Using `<model>` for review (different family from your primary, good)
> - `<posture>` posture, so I'll run empathy plus the gating LLM's pick on most
>   artifacts
> - I'll `<edit_handling>` when the verdict is edit
> - Always running: `<always_run>`
> - Custom lenses: `<list or "none yet">`
> - Logging: `<log_level>`
>
> You can change any of this by editing `~/.openclaw/workspace/memory/review/rules.md`
> directly, or by asking me to "redo review setup".

Then proceed with the actual review the operator originally invoked.

## rules.md template

```markdown
# Review Skill, Rules

## Reviewer

- reviewer_model: <alias or full path>
- fallback_to_caller: true # if the alias resolves to nothing, use the calling agent's
  model and stamp degraded

## Posture

- posture: balanced # frugal | balanced | thorough
- edit_handling: default_by_stakes # auto_apply | surface | default_by_stakes
- log_level: standard # minimal | standard | verbose

## Lens Selection

- always_run: [empathy]
- never_run: [] # lenses to suppress entirely (use sparingly, the gating LLM is usually
  right)

## Custom Lenses

- custom_lens_dir: ~/.openclaw/workspace/memory/review/lenses/
- (drop any .md file here, name it after the lens, and the orchestrator will include it)

## Notes

- (free-form notes the operator wants to remember about how reviews work for them)
```

## Reading rules.md at runtime

The orchestrator reads rules.md as plain markdown. No parser. Treat it as context the
LLM reasons about, the same way `TOOLS.md` and `MEMORY.md` get read. Apply the
preferences as soft constraints in the gating prompt:

> Operator preferences (from rules.md):
>
> - posture: <value> → adjust how many lenses you select
> - always_run: <list> → include these in `lenses` no matter what
> - never_run: <list> → exclude these from `lenses`
> - custom_lens_dir contents: <list of .md files found> → consider including by name
>   when relevant
