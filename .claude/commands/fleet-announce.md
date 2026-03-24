---
description:
  "Announce a fleet update to users — send a personalized message from each person's bot
  explaining what changed and why they should care"
argument-hint: "<what changed> [--only ali,thomas] [--skip gil]"
version: 1.0.0
---

# Fleet Announcement 📢

<objective>
Send a personalized notification to fleet users about a change Nick rolled out. Each
message comes from that person's own bot, in the bot's voice, explaining the update in
terms that matter to them.
</objective>

<fleet-data>
Fleet files: `~/openclaw-fleet/*.md` — one per remote server. These contain each
machine's installed skills, workflows, cron jobs, and feature usage. **Read these before
drafting to determine relevance.**

**Machines & contacts:**

| Person   | SSH Host | Bot Name  | Telegram ID   | Bot Emoji |
| -------- | -------- | --------- | ------------- | --------- |
| Ali      | ali      | ShantiMa  | 1168760671    | 💜        |
| Julianna | julianna | Ace       | 6701636293    | 🐾        |
| Thomas   | thomas   | Roxy      | 6510624576    | 💪        |
| Gil      | gil      | Bob Steel | [check store] | 🤖        |

</fleet-data>

<process>

## 1. Determine Relevance

Not every update applies to everyone. Check `~/openclaw-fleet/<name>.md` for what each
person actually uses.

**Include when:**

- Update affects core behavior everyone gets (BOOT.md, AGENTS.md, gateway, session
  handling)
- Update is about a feature/workflow they actively use
- Nick explicitly says to include them

**Skip when:**

- Update is about a feature they don't have (e.g., email steward but no email steward
  configured)
- Update is purely infrastructure and invisible to them
- They're not actively using their bot

If `--only` or `--skip` flags are provided in the argument, respect those.

## 2. Draft Messages

**Consistent format:**

```
🔧 AI Ecosystem Update

[1-2 sentences: what changed, plain language, no jargon]

What this means for you: [1-2 sentences: what they'll notice differently]

Nick built this one. ✨
```

**Rules:**

- **Header:** Always `🔧 AI Ecosystem Update`
- **Voice:** Write as the person's bot (match their IDENTITY.md personality)
- **Tone:** Warm, brief, non-technical. These are regular people, not engineers
- **Credit Nick:** Always. These people know Nick maintains their AI
- **Empathy first:** What they'll experience, not what changed under the hood
- **No jargon:** "gateway" → "I need to restart". "Compaction" → never say this
- **Length:** 3-5 sentences max. Notification, not changelog
- **Emoji:** 🔧 header + ✨ sign-off + at most 1 more. Don't overdo it

## 3. Show Nick the Drafts

Before sending, show all drafted messages grouped by person. Wait for approval or edits.
Format:

```
📢 Fleet Announcement Draft

🔧 Ali (ShantiMa): [included/skipped + reason]
> [draft message]

🔧 Thomas (Roxy): [included/skipped + reason]
> [draft message]

[etc.]

Send all? Or edit?
```

## 4. Send

Use `openclaw message send` via SSH from each machine:

```bash
ssh <host> "openclaw message send --channel telegram -t <telegram_id> -m '<message>'"
```

**Important:** Single quotes in the message must be escaped. Use the bot's Telegram
channel — the message should come FROM their bot, not from Nick.

## 5. Confirm

Report back with delivery status for each person.

</process>

<what-not-to-announce>
- Routine maintenance (version bumps, deps)
- Config tweaks that don't change user experience
- Bug fixes for issues they never hit
- Internal agent operations (librarian, memory maintenance, cron tuning)
</what-not-to-announce>

<examples>

**Nick:** "Announce the BOOT.md restart recovery to the fleet"

**Step 1 — Relevance:** BOOT.md is core behavior. Everyone gets it. ✅ all included.

**Step 2 — Drafts:**

For Ali (ShantiMa, warm/grounded):

```
🔧 AI Ecosystem Update

Nick improved how I handle restarts. Before, if we were mid-conversation and I restarted, I'd come back with no memory of what we were just talking about. Now I detect that and pick right back up.

You shouldn't notice anything unless it happens, and that's the point! ✨
```

For Thomas (Roxy, direct/organized):

```
🔧 AI Ecosystem Update

Nick improved restart behavior. If we're mid-conversation and I need to restart, I now pick up where we left off instead of losing the thread.

Less "wait, what were we talking about?" moments. ✨
```

---

**Nick:** "Let them know about the email steward improvements"

**Step 1 — Relevance:** Check fleet files.

- Ali: No email steward → **skip**
- Gil: No email steward → **skip**
- Julianna: Has email steward (2 accounts) → **include**
- Thomas: Check fleet file → include/skip based on config

</examples>
