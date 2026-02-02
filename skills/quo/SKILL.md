---
name: quo
description: Query Quo (formerly OpenPhone) business phone - calls, texts, conversations, contacts, and call transcripts/summaries.
triggers:
  - quo
  - openphone
  - business phone
  - work calls
  - call transcript
  - call summary
metadata:
  openclaw:
    emoji: "📞"
    apiKey:
      env: QUO_API_KEY
      getFrom: https://my.quo.com → Settings → API
    requires:
      bins:
        - curl
        - jq
---

# Quo Integration 📞

Query your Quo (formerly OpenPhone) business phone system - calls, texts, conversations, contacts, and AI-generated call transcripts/summaries.

## Setup

**If not configured:** Ask the user for their API key. They can get it from:
https://my.quo.com → Settings → API

Then configure via `gateway config.patch` with `env.QUO_API_KEY`.

## Quick Commands

```bash
# List your phone numbers
quo numbers

# Recent conversations (calls + texts)
quo conversations
quo conversations 20

# List contacts
quo contacts

# List workspace users
quo users

# Get call summary by call ID
quo summary AC123abc

# Get call transcript by call ID
quo transcript AC123abc

# Get call recording URLs
quo recordings AC123abc
```

## When to Use

- "What's my Quo number?"
- "Show recent conversations"
- "Get the transcript from call AC123..."
- "What was the summary of that call?"
- "List my business contacts"

## Response Format

**Conversations include:**
- `id` - Conversation ID
- `name` - Contact name if known
- `participants` - Phone numbers
- `lastActivityAt` - Most recent activity

**Call summaries/transcripts include:**
- AI-generated summary
- Full transcript with timestamps
- Speaker attribution when available

## Notes

- Call transcripts require call recording to be enabled in Quo settings
- Phone numbers are in E.164 format (+1XXXXXXXXXX)
