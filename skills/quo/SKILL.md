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
  clawdbot:
    emoji: "📞"
    requires:
      env:
        - QUO_API_KEY
      bins:
        - curl
        - jq
---

# Quo Integration 📞

Query your Quo (formerly OpenPhone) business phone system - calls, texts, conversations, contacts, and AI-generated call transcripts/summaries.

## Setup

1. Get your API key from [my.quo.com](https://my.quo.com) → Settings → API
2. Set environment variable: `export QUO_API_KEY=your-key`
3. Or configure in clawdbot.json under `env.QUO_API_KEY`

## Quick Commands

```bash
# List your phone numbers (needed for other queries)
quo numbers

# Recent conversations (calls + texts)
quo conversations
quo conversations 20

# List contacts
quo contacts
quo contacts 50

# List workspace users
quo users

# Get call summary by call ID
quo summary AC123abc

# Get call transcript by call ID
quo transcript AC123abc

# Get call recording URLs
quo recordings AC123abc

# Get voicemails for a call
quo voicemails AC123abc
```

## When to Use

- "What's my Quo number?"
- "Show recent conversations"
- "Get the transcript from call AC123..."
- "What was the summary of that call?"
- "List my business contacts"
- "Who's on our Quo workspace?"

## Response Format

**Conversations include:**
- `id` - Conversation ID (CN...)
- `name` - Contact name if known
- `participants` - Phone numbers in E.164 format
- `lastActivityAt` - Most recent activity
- `phoneNumberId` - Your Quo number used

**Call summaries/transcripts include:**
- AI-generated summary text
- Full transcript with timestamps
- Speaker attribution when available

## API Filters

| Filter | Description |
|--------|-------------|
| `maxResults` | Results per page (1-100) |
| `createdAfter` | Filter by date (ISO 8601) |
| `createdBefore` | Filter by date (ISO 8601) |
| `excludeInactive` | Hide inactive conversations |

## Notes

- API uses API key authentication via header
- Rate limits apply per Quo plan
- Call transcripts/summaries require call recording to be enabled
- Phone numbers are in E.164 format (+1XXXXXXXXXX)
- API documentation: [quo.com/docs](https://www.quo.com/docs)
