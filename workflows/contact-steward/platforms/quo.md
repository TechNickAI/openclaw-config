# Quo Platform Guide

## Tools

Quo (formerly OpenPhone) access is through the `quo` CLI at
`~/src/openclaw-config/skills/quo/quo`. Requires `QUO_API_KEY` environment variable
(injected by OpenClaw automatically).

### Listing Conversations

```bash
quo conversations --limit 20
```

Optional filters:

- `--phone <number-or-id>` — filter by Quo phone line
- `--updated-after ISO` / `--updated-before ISO` — date range
- `--include-inactive` — include snoozed/inactive conversations
- `--unknown` — only show conversations with numbers NOT in Quo contacts

Each conversation has: ID, participants (phone numbers), last activity, phone number ID.

### Searching Contacts by Phone

```bash
quo search-phone <+1XXXXXXXXXX> [--refresh]
```

Uses a local cache (5-min TTL at `/tmp/quo-contacts-cache.json`). Pass `--refresh` to
force a fresh pull from the API.

### Gathering Everything for a Number

```bash
quo gather <+1XXXXXXXXXX> [--since ISO] [--until ISO] [--limit N] [--refresh]
```

This is the power command — pulls contact info, all messages, all calls with inline
transcripts/summaries/voicemails for a phone number. Defaults to last 30 days. **Use
this when spawning the work tier** — it gives the classifier everything in one shot.

**Important:** The default 30-day window may miss older conversations. When the scanner
identifies a conversation older than 30 days, pass `--since` explicitly to cover the
full 90-day scan window:

```bash
quo gather <phone> --since <90-days-ago-ISO>
```

### Call Intelligence

```bash
quo summary <callId>       # AI-generated call summary
quo transcript <callId>    # Full dialogue transcript with speaker attribution
quo recordings <callId>    # Recording URLs (MP3)
quo voicemails <callId>    # Voicemail + transcript
```

Transcripts include speaker-attributed dialogue with timestamps. This is gold for
identifying unknown callers — people introduce themselves on calls.

### Adding Contacts

**Quo contacts are managed through the `quo` CLI** — this is the correct place to add
contacts for this platform. Do NOT add contacts to Apple Contacts or WhatsApp from here
— cross-referencing for lookup is fine, cross-writing is not.

```bash
quo raw POST "/contacts" '{"defaultFields":{"firstName":"<first>","lastName":"<last>","phoneNumbers":[{"name":"mobile","value":"+1XXXXXXXXXX"}]}}'
```

Optional fields: `company`, `role`, `emails` (array of `{name, value}`).

**PATCH replaces entire `defaultFields`** — always include ALL existing fields when
updating.

### Listing Contacts

```bash
quo contacts --limit 20
```

## Quo-Specific Behaviors

### Business Context

Quo is typically used as a business phone. Contacts tend to be professional — clients,
vendors, collaborators. The classifier should capture company and role when available.

Check `preferences.md` for whether this instance uses Quo as business, personal, or
mixed.

### Your Human's Quo Phone Number

Your human's Quo phone number and line ID are stored in `preferences.md`. You need this
to filter conversations — only process ones involving your human's line.

### Call Transcripts Are the Best Source

Unlike WhatsApp and iMessage where you're parsing text messages, Quo has full call
transcripts with speaker attribution. The `gather` command pulls everything including
transcripts inline. People introduce themselves on calls: "Hi, my name is Jane from Acme
Corp."

### Low Volume

Quo has fewer conversations than WhatsApp or iMessage. Scanner can run once daily.

### The `--unknown` Filter

`quo conversations --unknown` compares conversation participants against the Quo contact
database and only shows unrecognized numbers. This is your primary scan command — it
does the "is this a known contact?" check for you.

## Scanner Flow

1. `quo conversations --unknown --limit 50` — get conversations with unknown numbers
   (larger limit to reach up to 90 days back)
2. For each, check `processed.db` — skip if already processed with no new activity
3. `quo gather <phone> --since <90-days-ago-ISO>` — pull all messages, calls,
   transcripts (explicit `--since` required — default is 30 days which misses older
   conversations)
4. Check if your human participated (sent messages or took calls)
5. If your human didn't engage, skip
6. Cross-reference: `wacli contacts search "<number>"` + Apple Contacts
7. If known elsewhere -> spawn the work tier to verify and add to Quo
8. If unknown everywhere -> spawn the work tier with the gathered data for
   classification
