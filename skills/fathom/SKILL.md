---
name: fathom
version: 0.2.0
# prettier-ignore
description: Query Fathom AI meeting recordings — transcripts, summaries, action items, and searchable meeting history
triggers:
  - fathom
  - meetings
  - transcripts
  - what was discussed
  - meeting notes
  - meeting recordings
metadata:
  openclaw:
    emoji: "🎥"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/fathom
    category: integrations
    apiKey:
      env: FATHOM_API_KEY
      getFrom: https://fathom.video → User Settings → API Access
---

# Fathom AI 🎥

Query meeting recordings — AI notetaker for Zoom, Google Meet, Teams.

## Setup

API key from fathom.video → User Settings → API Access. Configure via gateway.

## What Users Ask

- "What meetings did I have today?"
- "What was discussed in the [project] meeting?"
- "Find meetings about [topic]"
- "What were the action items from yesterday's call?"
- "Get the transcript from my call with [person]"

## Capabilities

- Recent meeting recordings with summaries
- Search across all meetings by title
- Filter by date range
- Full transcript retrieval by recording ID
- Action items extraction

## Response Data

**List view:**

- `id` — Recording ID
- `title` — Meeting title from calendar
- `created_at` — When the meeting was recorded
- `meeting_type` — Internal or external
- `invitees` — Calendar invitee names and emails
- `summary` — AI-generated summary (when available)

**Full transcript:**

- Everything above plus speaker-attributed transcript with timestamps

## Notes

- Speaker names come from calendar invites
- Works with Zoom, Google Meet, Microsoft Teams
- Rate limit: 60 API calls per minute
- API keys access meetings recorded by you or shared to your Team
