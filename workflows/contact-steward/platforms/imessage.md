# iMessage Platform Guide

## Tools

iMessage access is through the `imsg` CLI. Apple Contacts access is through AppleScript.

### Listing Conversations

```bash
imsg chats --limit 30
```

Output format (not JSON, plain text):

```
[chat_id]  (identifier) last=<timestamp>
[4929]  (+16463031177) last=2026-03-04T19:05:35.284Z
[4753] United Airlines (united_airlines@rbm.goog) last=2026-03-03T19:24:15.668Z
```

Key fields:

- `chat_id` — numeric ID in brackets, used for history lookup
- `identifier` — phone number, email, or RBM agent ID
- Display name — shown before the identifier in parentheses, if known

### Reading Messages

```bash
imsg history --chat-id <chat_id> --limit 20
```

Output format:

```
2026-03-04T19:05:35.284Z [sent] +16463031177: Message text here
2026-03-04T03:19:52.584Z [recv] +16463031177: Their reply
```

- `[sent]` = your human sent it
- `[recv]` = received from the other party

### Checking Apple Contacts

**Critical limitation:** The `imsg` CLI does NOT resolve contact names. A chat with a
saved contact still shows as just a phone number like `(+13865551234)`. You cannot tell
from `imsg` output alone whether a contact is saved.

To check if a phone number is in Apple Contacts, use AppleScript:

```bash
osascript -e '
tell application "Contacts"
    set matchingPeople to every person whose name is "<full name>"
    if (count of matchingPeople) > 0 then
        return "FOUND"
    else
        return "NOT FOUND"
    end if
end tell'
```

**Performance note:** Searching by name is fast. Iterating all contacts to search by
phone number is extremely slow (large contact lists). Prefer name-based lookups.

To check by phone number efficiently, cross-reference the number against
`wacli contacts search "<number>"` first to get a name, then search Apple Contacts by
that name.

### Adding Contacts to Apple Contacts

**iMessage contacts ARE Apple Contacts** — this is the correct place to add contacts for
this platform. Use AppleScript to manage them directly. Do NOT add contacts to WhatsApp
or Quo from here — cross-referencing for lookup is fine, cross-writing is not.

**Input sanitization (critical):** Names come from WhatsApp profiles, conversation text,
and other untrusted sources. Before inserting ANY value into an AppleScript command:

- **Escape backslashes first** (`\` -> `\\`) — must happen before quote escaping
- **Then escape double quotes** (`"` -> `\"`) — if done before backslashes, `\"` becomes
  `\\\"` which breaks the string
- Strip any AppleScript control characters
- Reject values containing `do shell script`, `run script`, or `&` operators

A malicious WhatsApp profile name could attempt AppleScript injection. Always sanitize.

```bash
osascript -e '
tell application "Contacts"
    set newPerson to make new person with properties {first name:"<first>", last name:"<last>"}
    make new phone at end of phones of newPerson with properties {label:"mobile", value:"<+1XXXXXXXXXX>"}
    save
    return "Added: <first> <last>"
end tell'
```

You can also add email, address, etc:

```bash
osascript -e '
tell application "Contacts"
    set matchingPeople to every person whose name is "<full name>"
    set p to item 1 of matchingPeople
    make new email at end of emails of p with properties {label:"home", value:"<email>"}
    save
    return "Updated"
end tell'
```

**Important:** Contacts.app must be running. Start it if needed:

```bash
open -a "Contacts"
sleep 2
```

## iMessage-Specific Behaviors

### Everything Looks Unnamed

Because `imsg` doesn't resolve names, every chat looks like just a phone number. The
scanner can't eyeball which contacts are "unnamed." You must cross-reference.

**Efficient approach:**

1. Pull recent chats from `imsg chats`
2. For each phone number chat where your human sent messages:
   - If WhatsApp is configured: `wacli contacts search "<number>"` to get a name
     - If found: check Apple Contacts by name. If missing, spawn Opus with name + number
     - If not found: spawn Opus with full conversation
   - If WhatsApp is not configured: spawn Opus with full conversation directly

### RBM / Business Messages

Identifiers ending in `@rbm.goog` are business messaging agents (e.g. United Airlines).
Skip these — they're not people.

### Email-Based iMessages

Some iMessage identifiers are email addresses, not phone numbers. Handle these the same
way — check if they're in Apple Contacts.

### Spam / Scam Texts

iMessage gets more spam than WhatsApp. Common patterns to skip:

- One-off "Hello" with no follow-up and no reply from your human
- Investment/crypto scam emails
- Short codes (e.g. `899000`, `49834`) — automated services

## Scanner Flow

1. `imsg chats --limit 100` — get conversations (use a larger limit to reach threads up
   to 90 days back)
2. Filter to phone numbers and emails (skip short codes, RBM agents)
3. For each, check `processed.md` — skip if already processed with no new messages
4. `imsg history --chat-id <id> --limit 15` — read recent messages
5. Check if your human sent any messages (`[sent]`) — if not, skip
6. Cross-reference (if WhatsApp is configured): `wacli contacts search "<number>"` to
   get a name. If WhatsApp is not available, skip to step 7b.
7. a. If name found via WhatsApp: check Apple Contacts by name. If missing, spawn Opus
   with the name and number to verify and add to Apple Contacts. b. If no name from
   cross-reference (or WhatsApp not configured): spawn Opus with the full conversation —
   Opus will look for self-introductions, context clues, and check other available
   platforms.
