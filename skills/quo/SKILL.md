---
name: quo
version: 0.4.0
description:
  Quo (formerly OpenPhone) business phone system — check calls, texts, voicemails,
  missed calls, send SMS/texts, manage contacts, read call transcripts and summaries,
  get recordings. Use for anything related to the work phone or business line.
triggers:
  - quo
  - openphone
  - business phone
  - work calls
  - call transcript
  - call summary
  - text
  - SMS
  - send text
  - missed calls
  - voicemail
  - phone messages
  - work phone
  - business messages
  - who called
  - who texted
metadata: { "openclaw": { "emoji": "📞", "primaryEnv": "QUO_API_KEY" } }
---

# Quo 📞

Query your Quo (formerly OpenPhone) business phone — calls, texts, contacts,
transcripts.

## Setup

API key from my.quo.com → Settings → API. Configure via gateway under
`skills.entries.quo.apiKey`. OpenClaw injects it as `QUO_API_KEY` automatically.

## What Users Ask

- "What's my Quo number?"
- "Show recent conversations"
- "Get the transcript from that call"
- "What was the summary of my call with [person]?"
- "List my business contacts"
- "Send a text to [number]"
- "Show my recent calls with [number]"
- "Any missed calls today?"
- "Who called the office?"
- "Text [person] from my work number"
- "Check my voicemails"
- "What messages came in on the business line?"

## CLI Reference

```
{baseDir}/quo numbers                    List phone numbers
{baseDir}/quo conversations [filters]    List conversations
{baseDir}/quo contacts [--limit N]       List contacts
{baseDir}/quo custom-fields              List contact custom fields
{baseDir}/quo users                      List workspace users
{baseDir}/quo summary <callId>           Get AI call summary
{baseDir}/quo transcript <callId>        Get full dialogue transcript
{baseDir}/quo recordings <callId>        Get recording URLs
{baseDir}/quo voicemails <callId>        Get voicemail + transcript
{baseDir}/quo send --from <num> --to <num> <message>
{baseDir}/quo messages --number-id <id> --participant <phone> [--limit N]
{baseDir}/quo calls --number-id <id> --participant <phone> [--limit N] [--created-after ISO] [--created-before ISO]
{baseDir}/quo raw [METHOD] <endpoint> [json-body]
```

### Conversation Filters

```
--phone <number-or-id>    Filter by Quo phone line (repeatable)
--updated-after ISO       Conversations updated after date
--updated-before ISO      Conversations updated before date
--created-after ISO       Conversations created after date
--created-before ISO      Conversations created before date
--include-inactive        Include inactive/snoozed conversations
--limit N                 Max results (default 10)
```

## API Endpoints

Full OpenAPI spec:
https://openphone-public-api-prod.s3.us-west-2.amazonaws.com/public/openphone-public-api-v1-prod.json

| Endpoint                       | Method  | Description                                                    |
| ------------------------------ | ------- | -------------------------------------------------------------- |
| `/v1/phone-numbers`            | GET     | List phone numbers                                             |
| `/v1/conversations`            | GET     | List conversations (filterable)                                |
| `/v1/messages`                 | GET     | List messages for a conversation                               |
| `/v1/messages`                 | POST    | Send a text message                                            |
| `/v1/messages/{id}`            | GET     | Get message by ID                                              |
| `/v1/calls`                    | GET     | List calls (with date filters)                                 |
| `/v1/calls/{callId}`           | GET     | Get call by ID                                                 |
| `/v1/call-summaries/{callId}`  | GET     | AI-generated call summary                                      |
| `/v1/call-transcripts/{id}`    | GET     | Full dialogue transcript with speaker attribution              |
| `/v1/call-recordings/{callId}` | GET     | Recording URLs (MP3)                                           |
| `/v1/call-voicemails/{callId}` | GET     | Voicemail + transcript                                         |
| `/v1/contacts`                 | GET     | List contacts (paginated)                                      |
| `/v1/contacts`                 | POST    | Create a contact                                               |
| `/v1/contacts/{id}`            | GET     | Get contact by ID                                              |
| `/v1/contacts/{id}`            | PATCH   | Update contact (**replaces entire defaultFields!**)            |
| `/v1/contacts/{id}`            | DELETE  | Delete a contact                                               |
| `/v1/contact-custom-fields`    | GET     | List custom contact fields                                     |
| `/v1/users`                    | GET     | List workspace users                                           |
| `/v1/webhooks/*`               | Various | Webhook management for messages, calls, summaries, transcripts |

## Key Data Formats

### Transcript Response

Returns `dialogue[]` array with speaker-attributed entries:

```json
{
  "data": {
    "callId": "AC...",
    "dialogue": [
      {
        "content": "Hello",
        "start": 0.16,
        "end": 0.48,
        "identifier": "+15551234567",
        "userId": "US..."
      },
      {
        "content": "Hi, my name is Jane",
        "start": 1.0,
        "end": 2.5,
        "identifier": "+15559876543",
        "userId": null
      }
    ]
  }
}
```

### Contact Fields

- `defaultFields`: firstName, lastName, company, role, emails[], phoneNumbers[]
- `customFields`: Array of {key, value} pairs (keys from `/contact-custom-fields`)
- ⚠️ PATCH replaces entire `defaultFields` — always include ALL existing fields

### Custom Fields (Julianna's workspace)

- `Property Associated` (key: `1712532493777`, type: string)
- `Address` (key: `1700067557182`, type: address)

## Notes

- Transcripts require call recording enabled in Quo settings
- Phone numbers in E.164 format (+1XXXXXXXXXX)
- Contacts API has no phone number search — must page through or use externalIds
- Voicemail endpoint returns single object (not array)
