# WhatsApp Platform Guide

## Tools

All WhatsApp access is through `wacli`.

### Listing Conversations

```bash
wacli chats list --limit 100 --json
```

Returns recent chats sorted by last activity. Each chat has:

- `JID` — unique identifier (`<number>@s.whatsapp.net` for DMs, `@g.us` for groups,
  `@lid` for linked device contacts)
- `Kind` — "dm", "group", or "unknown" (LID contacts show as "unknown")
- `Name` — display name (from WhatsApp profile or phone contacts)
- `LastMessageTS` — when last message was sent/received

### Reading Messages

```bash
wacli messages list --chat "<JID>" --limit 20 --json
```

Messages are nested under `data.messages` (not `data` directly). Each message has:

- `FromMe: true/false` — whether your human sent it
- `Text` — message content
- `DisplayText` — fallback if Text is empty (reactions, etc.)
- `MediaType` — "Audio" for voice messages, "image", etc.
- `PushName` — sender's WhatsApp profile name
- `Timestamp` — when sent
- `ChatName` — resolved name for the chat

### Voice Messages

WhatsApp voice messages show as `MediaType: "Audio"` in message listings. These are
valuable for the Opus classifier when trying to identify someone — people often
introduce themselves or provide context in voice notes. Flag these for Opus but note
that transcription (via Whisper) will be needed.

### Groups

For v1, focus on DM conversations only. Group chats are noisy and the "human replied"
trigger doesn't map cleanly to a specific person. Future enhancement.

---

## Determining "Saved Contact" (Critical)

**Do NOT use `wacli contacts search` to determine if someone is a saved contact.** It
returns results for anyone WhatsApp knows about — including people who just have a
WhatsApp profile name (`push_name`). Nearly everyone has a push_name, so this check
gives false positives for almost everyone.

### Two Databases

There are two databases with contact info. Use the RIGHT one:

| Database                   | Path                  | What it is                                                                          |
| -------------------------- | --------------------- | ----------------------------------------------------------------------------------- |
| **session.db** (whatsmeow) | `~/.wacli/session.db` | **Source of truth.** Synced directly from WhatsApp servers.                         |
| **wacli.db**               | `~/.wacli/wacli.db`   | Local copy, imported via `wacli contacts refresh`. May be stale — can miss entries. |

**Always use `whatsmeow_contacts` in session.db** for the "is this a saved contact?"
check. wacli.db can lag behind (observed: saved contacts present in whatsmeow but
missing from wacli.db entirely).

### The Schema (whatsmeow_contacts in session.db)

```sql
CREATE TABLE whatsmeow_contacts (
    our_jid        TEXT,    -- your device JID
    their_jid      TEXT,    -- the contact's JID
    first_name     TEXT,    -- from phone address book
    full_name      TEXT,    -- from phone address book
    push_name      TEXT,    -- from WhatsApp profile (person chose this)
    business_name  TEXT,    -- from WhatsApp Business profile
    redacted_phone TEXT,
    PRIMARY KEY (our_jid, their_jid)
);
```

| Column          | Source             | Meaning                              |
| --------------- | ------------------ | ------------------------------------ |
| `push_name`     | WhatsApp profile   | Name the person chose for themselves |
| `full_name`     | Phone address book | Name saved in phone contacts         |
| `first_name`    | Phone address book | First name from phone contacts       |
| `business_name` | WhatsApp Business  | Business profile name                |

### The Rule

**A contact is "saved" if and only if `full_name` is non-empty on their
`@s.whatsapp.net` JID in `whatsmeow_contacts`.** Everything else is just WhatsApp
metadata.

```sql
-- Check if a phone-number JID is a saved contact (use session.db)
SELECT full_name, push_name, first_name, business_name
FROM whatsmeow_contacts
WHERE their_jid = '<number>@s.whatsapp.net';
-- full_name non-empty -> saved
-- full_name empty, business_name non-empty -> unsaved business
-- full_name empty, push_name only -> unsaved person
-- no row at all -> completely unknown
```

### LID Resolution

LID (Linked Device Identifier) JIDs like `265218726821991@lid` are opaque — no phone
number is extractable from the JID itself. But the `whatsmeow_lid_map` table in
`~/.wacli/session.db` maps LIDs to phone numbers:

```sql
-- Resolve a LID to a phone number (same database: session.db)
SELECT pn FROM whatsmeow_lid_map WHERE lid = '<lid_number>';
-- Returns the phone number (e.g., '50683545181')
```

**Always resolve LID -> phone number -> check `full_name` on the phone JID.**

A LID contact will typically NOT have `full_name` even for saved contacts — only the
phone-number JID carries the address book data. Example:

- `265218726821991@lid` -> push_name "Kevin Sheehy", no full_name on LID entry
- LID map: `265218726821991` -> `50683545181`
- `50683545181@s.whatsapp.net` -> full_name "Kevin Sheehy" — saved

Without this resolution, you'd incorrectly flag saved contacts as unknown.

### Using wacli.db (secondary, for push_name lookups)

wacli.db is still useful for looking up `push_name` when whatsmeow_contacts doesn't have
one (e.g., for contacts where only the LID entry has a push_name). But never use it as
the authority for "saved or not."

---

## Name Resolution

When the steward needs to determine the "best name" for a contact (for display,
notifications, or suggesting contact additions), use this priority:

### For Saved Contacts (full_name exists)

1. **Default to `full_name`** — this is what your human chose to save
2. **BUT if `push_name` is more complete, prefer it:**
   - `full_name` is one word, `push_name` has two+ words with the same first name
   - Example: `full_name` = "Alex", `push_name` = "Alex Martinez" -> use "Alex Martinez"
   - This is an **enrichment opportunity** — suggest updating the contact
3. **If they differ significantly** (different names entirely), use `full_name` but note
   the discrepancy — your human may have intentionally named them differently

### For Unsaved Contacts (no full_name)

1. **Use `push_name`** — it's what the person wants to be known as
2. Strip decorative emoji for the contact name suggestion, but keep them in notes
   - `push_name` = "natalie adele" -> suggest contact name "Natalie Adele"
   - `push_name` = "ADAM JAMES" -> suggest contact name "Adam James"
3. If `push_name` is clearly a nickname or incomplete, note it for the classifier

### For Businesses (business_name exists)

1. Use `business_name` as the display name
2. Flag as business -> skip per workflow rules
3. Log in `processed.md` with any human contact name found in conversation

### "More Complete" Check

A name A is more complete than name B when:

- A has more name parts (first + last vs. first only)
- A's first name/word matches B (so it's the same person, just more detail)
- After stripping emoji and normalizing case

Example comparisons:

- "Alex Martinez" > "Alex" (more complete, same person) -> enrichment
- "Seth Gordon" vs "Seth" (more complete) -> use Seth Gordon
- "natalie adele" vs "Natalie" -> push_name is more complete
- "Brigitte" vs "Brigitte Huff" -> full_name is more complete (keep it)

---

## Adding/Updating Contacts

**WhatsApp contacts are managed through `wacli` — not Apple Contacts or the phone's
address book.** This workflow only updates WhatsApp's own contact database.

```bash
# Set a local alias (display name override — this is the primary way to "name" a contact)
wacli contacts alias set "<JID>" "<alias>"

# Add tags
wacli contacts tags add "<JID>" "<tag>"
```

Setting an alias effectively "saves" the contact in WhatsApp with the name you choose.
This is the correct action for unknown contacts — set their alias to the resolved name.

---

## Scanner Flow

1. `wacli chats list --limit 200 --json` — get conversations (use a large limit to reach
   threads up to 90 days back)
2. Filter to `Kind: "dm"` or `Kind: "unknown"` (LID contacts), skip groups
3. For each, check `processed.md` — skip if already processed with no new messages
4. `wacli messages list --chat "<JID>" --limit 20 --json` — read recent messages
   (remember: messages are under `data.messages`)
5. Check if your human replied (`FromMe: true`) — if not, skip
6. **Determine if saved contact (all queries against session.db):** a. If JID is
   `@s.whatsapp.net`: query `full_name` from `whatsmeow_contacts` b. If JID is `@lid`:
   resolve via `whatsmeow_lid_map` -> get phone -> query `full_name` from
   `whatsmeow_contacts` on the `<phone>@s.whatsapp.net` JID c. `full_name` non-empty ->
   saved contact. Check for enrichment (name completeness). d. `full_name` empty,
   `business_name` non-empty -> business, skip + log e. `full_name` empty, `push_name`
   only -> **unsaved contact, process it** f. No entry at all -> **unknown contact,
   process it**
7. If saved + no enrichment: skip
8. If saved + enrichment (push_name more complete than full_name): flag for update
9. If unsaved: cross-reference on other platforms, then spawn Opus if still unresolved

### Batch SQL for Efficiency

**Input validation:** Before inserting any JID into a SQL query, verify it matches the
expected format: digits only for phone numbers (e.g. `1234567890`), digits + `@lid` for
LID JIDs, digits + `@s.whatsapp.net` for phone JIDs. Reject any value containing quotes,
semicolons, or SQL keywords. JIDs come from WhatsApp's protocol and should always be
numeric — if one isn't, skip it and log the anomaly.

Rather than querying one-by-one, batch the check. Both tables are in session.db:

```sql
-- Resolve LIDs to phone numbers (session.db)
SELECT lid, pn FROM whatsmeow_lid_map
WHERE lid IN ('lid1', 'lid2', ...);

-- Check saved status for phone JIDs (session.db)
SELECT their_jid, full_name, push_name, first_name, business_name
FROM whatsmeow_contacts
WHERE their_jid IN ('number1@s.whatsapp.net', 'number2@s.whatsapp.net', ...);
```

For push_name on LID-only entries (when whatsmeow doesn't have it), fall back to
wacli.db:

```sql
-- Get push_name for LID entries (wacli.db, secondary)
SELECT jid, push_name, business_name
FROM contacts
WHERE jid IN ('lid1@lid', 'lid2@lid', ...)
  AND jid NOT LIKE '%:_%@%';
```
