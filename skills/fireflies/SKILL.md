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
    apiKey:
      env: FIREFLIES_API_KEY
      getFrom: https://app.fireflies.ai → Integrations → Fireflies API
    requires:
      bins:
        - curl
        - jq
---

# Fireflies.ai Integration 🔥

Query meeting transcripts from Fireflies.ai - the AI notetaker that records, transcribes, and summarizes your Zoom, Google Meet, and Teams calls.

## Setup

**If not configured:** Ask the user for their API key. They can get it from:
https://app.fireflies.ai → Integrations → Fireflies API

Then configure via `gateway config.patch` with `env.FIREFLIES_API_KEY`.

## Quick Commands

```bash
# Recent transcripts (default: 5)
fireflies recent
fireflies recent 10

# Search for topics across all meetings
fireflies search "product roadmap"

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

## Response Format

**List view includes:**
- `id` - Transcript ID (use with `get` command)
- `title` - Meeting title from calendar
- `duration` - Length in minutes
- `participants` - Attendee emails
- `summary` - AI-generated overview and action items

**Full transcript includes:**
- All list fields plus full transcript with speaker names and timestamps

## Notes

- Speaker names come from calendar invites
- Works with Zoom, Google Meet, Microsoft Teams
