---
name: limitless
version: 0.3.0
description:
  Query Limitless Pendant lifelogs - conversations, meetings, and ambient recordings
triggers:
  - limitless
  - pendant
  - lifelogs
  - what did I say
  - what was discussed
metadata:
  openclaw:
    emoji: "🎙️"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/limitless
    category: integrations
    apiKey:
      env: LIMITLESS_API_KEY
      getFrom: https://app.limitless.ai → Settings → Developer
---

# Limitless Pendant 🎙️

Query your Limitless wearable's lifelogs — conversations and ambient recordings.

## Setup

API key from app.limitless.ai → Settings → Developer. Configure via gateway.

## What Users Ask

- "What did I talk about with [person]?"
- "What happened in my meeting today?"
- "Show me my recent conversations"
- "Search my lifelogs for [topic]"
- "What was that thing someone mentioned about [subject]?"

## Capabilities

- Recent lifelogs (configurable count, max 10)
- Semantic + keyword search
- Filter by date or date range
- Filter starred entries
- Get specific lifelog by ID with full content
- Delete lifelogs
- Download audio (Ogg Opus, max 2h)
- List Ask AI chats

## Response Data

- `title` — AI-generated summary
- `markdown` — Full transcript with timestamps
- `startTime`/`endTime` — When it happened
- `contents` — Segments with speaker attribution

## Notes

- Speaker attribution shows "Unknown" unless voice profiles trained
- Rate limit: 180 requests/minute
- Requires Limitless Pendant hardware
