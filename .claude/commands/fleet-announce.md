---
# prettier-ignore
description: "Announce a fleet update to users — send a personalized message from each person's bot explaining what changed and why they should care"
version: 1.0.0
---

# Fleet Announcement 📢

<objective>
Send a personalized notification to fleet users about a change that was rolled out. Each
message comes from that person's own bot, in the bot's voice, explaining the update in
terms that matter to them.
</objective>

<fleet-data>
Fleet files live at `~/openclaw-fleet/*.md` — one per remote server. These contain each
machine's installed skills, workflows, cron jobs, and feature usage. **Read these before
drafting to determine relevance.**

Each fleet file includes SSH host, bot identity, notification channel, and Telegram ID
for the user. Use that data at runtime — do not hardcode it here. </fleet-data>

<process>

## 1. Determine Relevance

Not every update applies to everyone. Check `~/openclaw-fleet/<name>.md` for what each
person actually uses.

**Include when:**

- Update affects core behavior everyone gets (BOOT.md, AGENTS.md, gateway, session
  handling)
- Update is about a feature/workflow they actively use
- The fleet owner explicitly says to include them

**Skip when:**

- Update is about a feature they don't have (e.g., email steward but no email steward
  configured)
- Update is purely infrastructure and invisible to them
- They're not actively using their bot

## 2. Draft Messages

**Consistent format:**

```
🔧 AI Ecosystem Update

[1-2 sentences: what changed, plain language, no jargon]

What this means for you: [1-2 sentences: what they'll notice differently]

[Fleet owner's name] built this one. ✨
```

**Rules:**

- **Header:** Always `🔧 AI Ecosystem Update`
- **Voice:** Write as the person's bot (SSH to the machine and read their IDENTITY.md to
  match personality)
- **Tone:** Warm, brief, non-technical. These are regular people, not engineers
- **Credit the fleet owner:** Always. These people know who maintains their AI
- **Empathy first:** What they'll experience, not what changed under the hood
- **No jargon:** "gateway" → "I need to restart". "Compaction" → never say this
- **Length:** 3-5 sentences max. Notification, not changelog
- **Emoji:** 🔧 header + ✨ sign-off + at most 1 more. Don't overdo it

## 3. Show Drafts for Approval

Before sending, show all drafted messages grouped by person. Wait for approval or edits.

Format:

```
📢 Fleet Announcement Draft

🔧 [Person] ([Bot Name]): [included/skipped + reason]
> [draft message]

[etc.]

Send all? Or edit?
```

## 4. Send

Look up the notification channel and recipient ID from each person's fleet file, then
send via SSH:

```bash
ssh <host> "openclaw message send --channel <channel> -t <recipient_id> -m '<message>'"
```

**Important:** Single quotes in the message must be escaped. Messages come FROM their
bot, not from the fleet owner.

## 5. Confirm

Report back with delivery status for each person.

</process>

<examples>

**Example 1:** "Announce the restart recovery improvement to the fleet"

Step 1 — Relevance: Core behavior (BOOT.md). Everyone gets it. ✅ all included.

Step 2 — Drafts adapt to each bot's voice. A warm/grounded bot might say:

```
🔧 AI Ecosystem Update

[Owner] improved how I handle restarts. Before, if we were mid-conversation and I
restarted, I'd come back with no memory of what we were just talking about. Now I
detect that and pick right back up.

You shouldn't notice anything unless it happens, and that's the point! ✨
```

A direct/organized bot might say:

```
🔧 AI Ecosystem Update

[Owner] improved restart behavior. If we're mid-conversation and I need to restart,
I now pick up where we left off instead of losing the thread.

Less "wait, what were we talking about?" moments. ✨
```

---

**Example 2:** "Let them know about the email steward improvements"

Step 1 — Relevance: Check fleet files. Only include people who have the email steward
configured. Skip everyone else.

</examples>
