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
    requires:
      env:
        - LIMITLESS_API_KEY
      bins:
        - curl
        - jq
---

# Limitless Pendant Integration 🎙️

Query your Limitless wearable's lifelogs - the AI device that captures conversations and creates searchable transcripts of your life.

## Setup

1. Get your API key from [app.limitless.ai](https://app.limitless.ai) → Settings → Developer
2. Set environment variable: `export LIMITLESS_API_KEY=your-key`
3. Or configure in openclaw.json under `env.LIMITLESS_API_KEY`

## Quick Commands

```bash
# Recent lifelogs (default: 5)
limitless recent
limitless recent 10

# Search for something specific
limitless search "meeting with john"
limitless search "that restaurant recommendation"

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

## API Parameters

| Param | Description |
|-------|-------------|
| `limit` | Max results (1-10, default 5) |
| `search` | Semantic + keyword hybrid search |
| `date` | YYYY-MM-DD for specific day |
| `start`/`end` | Date range (YYYY-MM-DD) |
| `timezone` | Timezone for date filtering |
| `isStarred` | Filter starred entries only |

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
- API documentation: [docs.limitless.ai](https://docs.limitless.ai)
