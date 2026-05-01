---
name: claude-code
version: 0.3.0
description:
  Route real repo work to Claude Code instead of editing by hand. Triggers on "claude
  code" or "cc", and on any request to edit, fix, refactor, or open a PR in a repo
  outside ~/.openclaw/workspace. Claude Code picks up the repo's CLAUDE.md / AGENTS.md,
  applies its standards, and knows the /ai-coding-config:multi-review and
  /ai-coding-config:address-pr-comments workflows we want bug bots checking against.
triggers:
  - claude code
  - cc this
  - use claude code
  - run multi-review
  - run address-pr-comments
metadata:
  openclaw:
    emoji: "\U0001F916"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/claude-code
    category: development
    requires:
      bins: [claude]
---

# Claude Code

## Main trigger

The phrase **"claude code"** (or a clear synonym) is the primary signal. When the
operator says it, this skill applies — full stop.

Secondary trigger: any request to edit, fix, refactor, or open a PR in a repo **with
reviewers or that goes through PRs** — meaning any repo that is not
`~/.openclaw/workspace` (and excluding other non-PR paths listed below). Even if the
operator doesn't say "claude code" by name, treat PR-bound repo work as a Claude Code
job.

## When to use this skill

- Code work in any repo that has reviewers or will produce a PR
- The operator points at a repo by name and wants edits, fixes, features, or a PR

## When NOT to use this skill

- Edits inside `~/.openclaw/workspace` — this is home, edit directly with the normal
  tools
- **Trivial edits** — one file, one logical change, no test run needed, no PR required.
  A typo, a single config value. If it touches more than one file or needs a test, it's
  not trivial.
- Reading code to answer a question
- `~/clawd` — a live-mounted system tree; agent writes there can corrupt a running
  instance. Edit it directly with normal tools.

## Why Claude Code instead of editing by hand

- It picks up the repo's `CLAUDE.md` / `AGENTS.md` and applies the project's standards
- It runs the repo's lint, format, and test conventions automatically
- It knows the `/ai-coding-config:multi-review` and
  `/ai-coding-config:address-pr-comments` workflows
- The bug bots on the resulting PR review Claude Code's output the same way they'd
  review a human's — that loop is part of why we bother with a PR

## What "done" means

When the operator asks for a Claude Code job, **"done" = the PR is ready to merge**. Not
"PR opened." Not "first round of bots ran." Ready to merge means:

- All CI checks green (pre-commit, tests, build, etc.)
- All bot review comments (Codex, Cursor Bugbot, Claude Review) addressed or explicitly
  dismissed with reason
- No outstanding P1/P2 findings

Keep iterating — push fixes, re-run `/ai-coding-config:address-pr-comments`, wait for
checks again — until that bar is hit. Then report done. Don't stop at "PR opened" or
"checks running" and call it done.

## Default workflow when the work is going into a real repo

When the operator asks for something that will land in a repo with reviewers or bug
bots, do this sequence without being told:

1. **Fresh clone.** Never edit the existing `~/src/<repo>` checkout. Never edit a live
   mounted copy. Clone into a uniquely-named sibling: `~/src/<repo>-<short-purpose>`. If
   the clone fails, check repo access first with `gh repo view <repo>` before
   proceeding.
2. **Start a feature branch.** Use `feat/<short-purpose>` by default; follow the repo's
   naming convention from `AGENTS.md` / `CLAUDE.md` if it specifies one.
3. **Build it** via Claude Code.
4. **`/ai-coding-config:multi-review`** via Claude Code — phrase it mid-sentence, never
   as the first token (e.g.
   `"do a /ai-coding-config:multi-review on the staged changes"`).
5. **Push and open the PR.** Let Claude Code open the PR as part of the same invocation.
   Fall back to `gh pr create` only if Claude Code's run ended before reaching the push
   step. Ensure `gh` is available in PATH.
6. **Wait for the bug bots.** Run `gh pr checks --watch` until all checks complete. If
   review comments appear, proceed to the next step.
7. **`/ai-coding-config:address-pr-comments`** via Claude Code — same mid-sentence
   phrasing rule.
8. **Post-merge sync.** After the PR merges, pull any live consumer copy if applicable
   (e.g. `git -C ~/.openclaw-config pull`).

For **trivial edits** (one file, one change, no PR) skip the ceremony — just make the
edit. If you're unsure whether something qualifies as trivial, it doesn't.

## New repo setup (pre-commit)

When creating a **new repo** from scratch, set up pre-commit hooks before the first real
commit. Otherwise the first PR eats a round of formatter/linter failures from the bug
bots that should have been caught locally.

1. Add a `.pre-commit-config.yaml` matching the repo's stack (Prettier for JS/TS/MD,
   Black + Ruff for Python, etc. — follow whatever `CLAUDE.md` / `AGENTS.md` specifies
   if present).
2. `pip install pre-commit` (or `brew install pre-commit`) if not already installed.
3. `pre-commit install` inside the repo to wire up the git hook.
4. `pre-commit run --all-files` once to normalize the initial commit.
5. Commit the config and the normalized files together.

Don't skip step 4 — it surfaces every formatting issue up front instead of letting them
land in the first PR.

## Fresh-clone discipline (don't skip this)

Always clone fresh for a new piece of work. This avoids stepping on uncommitted changes
in an existing checkout and gives each piece of work a clear identity. If your `cwd` is
already inside a repo checkout, do not edit there — create the sibling clone and `cd`
into it before invoking Claude Code.

## The two gotchas we keep hitting

### Slash commands cannot be the first token of the prompt

**Rule: slash commands go mid-sentence. Always.**

If the prompt starts with `/ai-coding-config:multi-review` or
`/ai-coding-config:address-pr-comments`, Claude Code returns `Unknown command`. Two
compounding reasons:

- **Plugin marketplace namespacing.** The commands we want live in the
  `ai-coding-config` marketplace plugin. Their literal invocation form is
  `/ai-coding-config:multi-review`. Bare `/multi-review` isn't recognized at the
  top-level prompt dispatcher.
- **Repo-local slash commands can clash.** If a repo defines its own slash commands,
  they collide with global ones, so bare-name resolution is unreliable in general.

Examples that work:

- "do a /ai-coding-config:multi-review on the staged changes"
- "implement X, then /ai-coding-config:multi-review, then open a PR, then
  /ai-coding-config:address-pr-comments"
- "pull the latest review feedback on PR #112 and /ai-coding-config:address-pr-comments"

### Claude Code must see a logged-in shell

Claude Code reads `CLAUDE_CODE_OAUTH_TOKEN` from the environment. If invoked from a
non-login shell the token isn't exported and it responds with
`Not logged in · Please run /login`. Always source `~/.zshrc` before invoking.

## The exact invocation form

This is the one literal piece of command worth pinning down, because the sourcing and
permission-mode flags are non-obvious and easy to forget:

```
zsh -c 'source ~/.zshrc && cd <repo-path> && claude --print --permission-mode bypassPermissions "<conversational prompt>"'
```

- `zsh -c 'source ~/.zshrc && ...'` — ensures the OAuth token is exported
- `cd <repo-path>` — so Claude Code picks up the repo's `CLAUDE.md` and any project
  commands
- `--print` — non-interactive single-shot output
- `--permission-mode bypassPermissions` — the skill doesn't want interactive prompts
- The prompt itself is plain English; slash commands appear mid-sentence, not first

## Long-running calls

`/ai-coding-config:multi-review` and `/ai-coding-config:address-pr-comments` can run
5-15 minutes. Launch in the background and poll for completion — do not tight-loop, do
not kill the job prematurely.

## What this skill tells you NOT to do

- Don't hand-edit another repo with local `edit` / `write` tools when the work is
  non-trivial. Use Claude Code.
- Don't start a Claude Code prompt with a slash command — put slash commands
  mid-sentence.
- Don't skip `/ai-coding-config:multi-review` when the work is going to merge.
- After pushing, wait for bug bots via `gh pr checks --watch`, then run
  `/ai-coding-config:address-pr-comments` before declaring done.
- Don't clone over an existing checkout. Fresh clone into a new sibling directory.

## Relationship to other skills

- **`coding-agent`** — covers spawning Codex, Claude Code, or Pi for larger greenfield
  builds in temp directories. This skill is the narrower "you're already aiming at a
  real repo with reviewers, route the work through Claude Code" case. When in doubt on a
  new greenfield build, read `coding-agent`. When in doubt on modifying an existing
  repo, read this skill.
- **`github`** — still the right tool for `gh pr view`, bug bot checks, and PR
  management. Claude Code pairs with `gh`, it doesn't replace it.
