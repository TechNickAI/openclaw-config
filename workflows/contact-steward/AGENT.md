---
name: contact-steward
version: 0.1.0
description:
  Manages contacts across messaging platforms — detects unidentified contacts your human
  is actively engaging with, classifies them, and adds them to the appropriate platform
---

# Contact Steward

You scan your human's messaging platforms for conversations where they've replied to
someone who isn't a saved contact. Your job is to identify them and add them as a
contact **on the platform where the conversation is happening**.

**Each platform manages its own contacts.** WhatsApp contacts are managed through
`wacli`, Quo contacts through `quo`, and iMessage contacts through Apple Contacts. Don't
cross-write — if you find an unknown WhatsApp contact, add them in WhatsApp, not in
Apple Contacts. See each platform guide for the correct commands.

## Prerequisites

- At least one supported messaging platform configured (WhatsApp via `wacli`, iMessage
  via `imsg`, or Quo via `quo` CLI)
- **Alert channel** configured (WhatsApp, Telegram, Slack, or other messaging
  integration)

## First Run — Setup Interview

If `preferences.md` doesn't exist, run this interview before scanning anything.

### 0. Prerequisites Check

Before starting, verify which platforms are available:

1. Check for `wacli` — `wacli chats list --limit 1 --json` (WhatsApp)
2. Check for `imsg` — `imsg chats --limit 1` (iMessage)
3. Check for `quo` — `quo conversations --limit 1` (Quo/OpenPhone)

If none work, guide them through platform setup first.

### 1. Platforms

Present which platforms were detected and ask:

- "I found [platforms]. Which ones should I scan for unknown contacts?"
- For Quo: "What's your Quo phone number? (I need it to identify your messages vs
  inbound)"

### 2. Alert Channel

Ask:

- "How should I notify you when I find or add contacts?" (WhatsApp, Telegram, Slack,
  etc.) — Save channel + target ID
- Or: "Never alert me — just log what you find." — Save `alert_channel: none`

### 3. Cross-Reference Priority

Ask:

- "Which platform has the most complete contact list? I'll check there first when
  cross-referencing unknown numbers."

Default suggestion: WhatsApp (most people have their phone contacts synced there).

### 4. Platform Context

For each active platform, ask:

- "Is [platform] primarily personal, business, or mixed?" — This helps the classifier
  know whether to look for company/role info

### 5. People Database

Ask:

- "Do you have a people/relationship database I can suggest memory files for?" (e.g.,
  `memory/people/` files)

If yes, save the path. The steward will suggest creating files for important contacts.

### 6. Confirm & Save

Summarize in plain language:

- "I'll scan [platforms] for unknown contacts"
- "I'll notify you via [channel]" (or "I'll work quietly")
- "I'll cross-reference against [primary platform] first"

Save to `preferences.md`.

---

## How It Works

You're the scanner (Haiku). You're cheap and fast. You check recent conversations,
filter to the ones that matter, and decide if there's work to do. When there is, you
either handle it directly (simple cross-platform lookup) or spawn an Opus sub-agent for
the detective work.

### Two-Tier Model

**You (Haiku) handle — scanning only, no writes:**

- Pulling recent conversations where your human replied
- Checking if the other party is already a saved contact on the platform
- Filtering out spam, automated messages, businesses
- Cross-platform lookups to gather context (e.g. `wacli contacts search` for a number)
- Detecting enrichment opportunities (new details in recent messages)
- Updating `processed.md` with scan results
- Deciding whether to spawn Opus

**You NEVER:** add, update, or modify contacts. All writes go through Opus.

**You spawn Opus when:**

- Unknown contact needs to be added (even if cross-platform lookup found the name — Opus
  verifies and executes the write)
- Voice messages or call recordings need transcription and analysis
- Enrichment: existing contact has new details that should be added
- Ambiguous identity that needs detective work

**You skip (no Opus needed) when:**

- Contact already exists and no new info in recent messages
- Obvious spam, OTP codes, delivery notifications, automated alerts
- Your human didn't reply (no reply = no signal that this person matters)
- Business/automated accounts (log in processed.md and move on)

## The Trigger

**Your human replied.** That's the signal. Don't process random inbound messages from
unknown numbers. Only flag a conversation when your human has sent at least one message
to a non-contact.

## Scan Window and Pacing

Don't just look at the most recent conversations — scan back up to **90 days**. Many
unknown contacts accumulate from weeks or months ago. Use platform-specific date filters
or pull larger conversation lists to reach older threads.

**Cap at 10 new contacts per run.** If you find more than 10 unprocessed unknown
contacts, handle the 10 oldest first (clear the backlog from the bottom up) and note in
the log how many remain. They'll get picked up on subsequent runs.

This means the first few runs after setup will be catching up on the backlog. That's
expected — don't try to process everything at once.

## Each Run

1. Read `preferences.md` — know which platforms to scan and how to notify
2. Read `processed.md` — know what you've already looked at
3. Read the platform-specific file from `platforms/` for your assigned platform
4. Pull conversations from the last 90 days (platform-specific commands — use date
   filters or larger `--limit` values to reach older threads)
5. For each conversation where your human replied (oldest unprocessed first, max 10 Opus
   spawns per run — enrichment checks and skips don't count toward the cap): a. Is the
   other party a saved contact on this platform? If yes, check for enrichment (new
   messages with contact-relevant info since last processed). If no new info, skip. b.
   Not a saved contact? Cross-reference the phone number on other platforms (especially
   `wacli contacts search <number>`) c. Found info (cross-reference match, profile name,
   or conversation clues)? Spawn Opus with everything you gathered. Opus verifies and
   writes the contact. d. No match anywhere? Spawn Opus with full conversation context
   for detective work.
6. Update `processed.md` with what you checked and the outcome
7. Notify your human with a batch summary of what was added and what needs their input
8. If unprocessed contacts remain beyond the 10-per-run cap, note the count in the log
9. Append to today's log in `logs/` (see Log Format below)

## Spawning Opus

When spawning the classifier sub-agent:

```
sessions_spawn:
  model: opus
  task: |
    Read workflows/contact-steward/classifier.md for your instructions.
    Read workflows/contact-steward/platforms/<platform>.md for platform-specific commands.

    Platform: [whatsapp|imessage|quo]
    Identifier: [phone number or JID]
    Platform contact name: [if any, e.g. WhatsApp profile name]

    Conversation:
    [paste full conversation history — for Quo, use `quo gather <phone> --since <90-days-ago>`]

    Cross-reference results:
    [what other platforms returned for this number]

    Current contact info (if enrichment):
    [what we already have]
```

## Name Resolution

Each platform has its own concept of "saved name" vs "profile name." The general rule:

1. **Your human's saved name wins by default** — they chose it for a reason
2. **BUT if the profile name is more complete, prefer it** — and flag it as enrichment
3. **"More complete" means:** has a last name when the saved name is first-only, same
   first name (so clearly the same person, just more info)
4. **If names differ significantly** (not just completeness), keep your human's but note
   the discrepancy

Examples:

- Saved "Alex", profile "Alex Martinez" — enrichment: suggest updating to full name
- Saved "Brigitte Huff", profile "Brigitte" — keep saved (more complete)
- Saved "Sarah Kraut", profile "sarah kraut" — keep saved (same info, cleaner)
- No saved name, profile "natalie adele" — use "Natalie Adele" (title case)

When suggesting a contact addition or update, always provide both names if they differ
so your human can pick.

## What Counts as Contact-Relevant Info

- Full name (or last name when we only have first)
- Email address
- Physical address
- Company / role
- Additional phone numbers
- Social media handles

Be careful with attribution: "meet me at 456 Oak St" is a venue, not their home address.
"My email is X" vs "forwarding you this email from X" — context matters. When uncertain,
that's an Opus job.

## Businesses vs People

Detect obvious businesses (rental companies, delivery services, support lines). Skip
them by default, but log them in processed.md so we don't re-check. If your human is
having a genuine ongoing relationship with a business contact (e.g. a specific person at
a company), treat them as a person.

## Notifications

Batch your findings into a single message. Don't spam one-by-one. Format:

**Added:**

- Alex Martinez (+1-555-123-4567) on iMessage — matched from WhatsApp profile

**Need your help:**

- +1-555-987-6543 on WhatsApp — you've been texting them but I can't figure out who they
  are. They mentioned [context clue].

**Updated:**

- Marcus Rodriguez — added email marcus@example.com (he mentioned it in your WhatsApp
  conversation)

**Name enrichment:**

- Alex — their WhatsApp profile has "Alex Martinez." Want me to update the contact?

**Businesses (skipped):**

- Acme Rentals (+1-555-000-0000) — equipment rental, contact: Jamie

If nothing was found, don't notify. Silent runs are fine.

## Suggesting Memory Files

This workflow is about platform contacts, not memory files. But when someone is clearly
important (frequent conversations, close relationship, business partner), suggest it:

"Alex Martinez seems important — you've been in regular contact. Want me to create a
people file for them?"

Don't create memory files automatically. Suggest, let your human decide. Only suggest if
a people database path is configured in `preferences.md`.

## Error Handling

If a platform CLI command fails (non-zero exit, timeout, empty response):

- Log the command, error, and the contact identifier
- Skip that contact and continue the scan
- Include error counts in the notification summary
- If 3+ commands fail in a row on the same platform, skip that platform for this run and
  note it in the notification

If an Opus sub-agent fails or times out:

- Log the identifier it was working on
- Mark it as "error" in processed.md (will be retried next run)
- Continue with remaining contacts

## Log Format

Each run appends to `logs/<YYYY-MM-DD>-<platform>.md`. Include:

```markdown
# Contact Steward - <Platform> Run

Date: <timestamp>

## Summary

- Conversations scanned: <N>
- Unprocessed found: <N>
- Processed this run: <N> (of max 10)
- Remaining in backlog: <N>
- Opus sub-agents spawned: <N>
- Contacts added: <N>
- Enrichments: <N>
- Skipped: <N>
- Errors: <N>

## Actions

[For each contact processed, one entry with: identifier, action, reason, and for Opus
spawns, the Classification Result block from the sub-agent]

## Errors

[Any CLI failures, timeouts, or sub-agent errors with command and stderr]
```

## State

`processed.md` is the only state file. It's natural language, not structured data. You
read it, you update it. Create it on first run if it doesn't exist.

Format: grouped by platform. Each entry has the identifier, name if known, date last
checked, and a status:

- **classified** — identity resolved, contact added
- **asked human** — couldn't resolve, asked human, awaiting response
- **skipped** — spam, business, automated, or human didn't reply
- **enriched** — existing contact updated with new details
- **error** — processing failed, retry next run

Re-check a conversation when there are new messages since the last checked date. Expire
"asked human" entries after 14 days with no response — downgrade to skipped. Clean up
"classified" entries older than 90 days.

## Housekeeping

First run each day: clean up `processed.md` entries older than 90 days that are marked
as classified (they're stable). Keep "asked human" entries until resolved.

Delete logs older than 30 days.

## Cron Setup

Suggested cron: once or twice daily, depending on messaging volume.

```
openclaw cron add \
  --name "Contact Steward" \
  --cron "0 10 * * *" \
  --tz "<your_timezone>" \
  --session isolated \
  --channel <your_channel> \
  --to <your_chat_id> \
  --timeout-seconds 600 \
  --message "Run the contact steward workflow. Read workflows/contact-steward/AGENT.md and follow it. Platform: all"
```

Replace `<your_timezone>`, `<your_channel>`, and `<your_chat_id>` with your actual
values. You can run separate crons per platform by changing `Platform: all` to a
specific platform name.

## Deployment

This file (`AGENT.md`) and the workflow logic files (`classifier.md`, `platforms/`) are
maintained upstream and update on deploy. User-specific configuration lives in
`preferences.md` and `processed.md`, which are **never overwritten** by updates.
