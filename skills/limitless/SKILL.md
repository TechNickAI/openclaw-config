---
name: limitless
description: Query Limitless Pendant lifelogs - conversations, meetings, and ambient recordings from your wearable AI device.
triggers:
  - limitless
  - pendant
  - lifelogs
  - what did I say
  - what was discussed
metadata:
  openclaw:
    emoji: "🎙️"
    apiKey:
      env: LIMITLESS_API_KEY
      getFrom: https://app.limitless.ai → Settings → Developer
    requires:
      bins:
        - curl
        - jq
---

# Limitless Pendant Integration 🎙️

Query your Limitless wearable's lifelogs - the AI device that captures conversations and creates searchable transcripts of your life.

## Setup

**If not configured:** Ask the user for their API key. They can get it from:
https://app.limitless.ai → Settings → Developer

Then configure via `gateway config.patch` with `env.LIMITLESS_API_KEY`.

## Quick Commands

```bash
# Recent lifelogs (default: 5)
limitless recent
limitless recent 10

# Search for something specific
limitless search "meeting with john"

# Get today's conversations
limitless today

# Get a specific date
limitless date 2026-01-28

# Raw API call with custom params
limitless raw "limit=5&isStarred=true"
```

## When to Use

- "What did I talk about with [person]?"
- "What happened in my meeting today/yesterday?"
- "What was that thing someone mentioned?"
- "Summarize my conversations this week"
- Recalling ambient conversations captured throughout the day

## Response Format

Lifelogs contain:
- `title` - AI-generated summary title
- `markdown` - Full transcript with timestamps
- `startTime`/`endTime` - When recording happened
- `contents` - Structured segments with speaker attribution

## Notes

- Speaker attribution may show as "Unknown" unless voice profiles are trained
- Rate limit: 180 requests/minute
- Requires Limitless Pendant hardware device
