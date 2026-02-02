---
name: fireflies
description: Query Fireflies.ai meeting transcripts - recorded meetings, AI summaries, action items, and searchable conversation history.
triggers:
  - fireflies
  - meetings
  - transcripts
  - what was discussed
  - meeting notes
metadata:
  clawdbot:
    emoji: "🔥"
    requires:
      env:
        - FIREFLIES_API_KEY
      bins:
        - curl
        - jq
---

# Fireflies.ai Integration 🔥

Query meeting transcripts from Fireflies.ai - the AI notetaker that records, transcribes, and summarizes your Zoom, Google Meet, and Teams calls.

## Setup

1. Get your API key from [app.fireflies.ai](https://app.fireflies.ai) → Integrations → Fireflies API
2. Set environment variable: `export FIREFLIES_API_KEY=your-key`
3. Or configure in moltbot.json under `env.FIREFLIES_API_KEY`

## Quick Commands

```bash
# Recent transcripts (default: 5)
fireflies recent
fireflies recent 10

# Search for topics across all meetings
fireflies search "product roadmap"
fireflies search "budget discussion"

# Get today's meetings
fireflies today

# Get meetings from a specific date
fireflies date 2026-01-28

# Get full transcript by ID
fireflies get abc123xyz

# Check your account info
fireflies me
```

## When to Use

- "What meetings did I have today/this week?"
- "What was discussed in the [project] meeting?"
- "Find meetings about [topic]"
- "What were the action items from yesterday's call?"
- "Get the transcript from my call with [person]"
- Building context about professional discussions

## Response Format

**List view includes:**
- `id` - Transcript ID (use with `get` command)
- `title` - Meeting title from calendar
- `duration` - Length in minutes
- `participants` - Attendee emails
- `summary` - AI-generated overview and action items

**Full transcript includes:**
- All list fields plus:
- `sentences` - Full transcript with speaker names and timestamps
- `keywords`, `topics_discussed`, `outline`
- `action_items` - Extracted tasks

## Query Filters (for advanced use)

| Filter | Description |
|--------|-------------|
| `limit` | Max results (1-50) |
| `keyword` | Search in title + transcript |
| `fromDate`/`toDate` | Date range (ISO 8601) |
| `mine` | Only meetings you participated in |
| `host_email` | Filter by meeting host |

## Notes

- Speaker names come from calendar invites (Zoom/Meet integration)
- Summaries are AI-generated and include action items automatically
- Works with Zoom, Google Meet, Microsoft Teams, and other platforms
- API documentation: [docs.fireflies.ai](https://docs.fireflies.ai)
