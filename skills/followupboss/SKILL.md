---
name: followupboss
version: 0.2.0
description:
  Query and manage Follow Up Boss CRM — contacts, notes, tasks, deals, and pipeline
  stages
triggers:
  - follow up boss
  - fub
  - crm
  - contacts
  - leads
  - deals
  - pipeline
metadata:
  openclaw:
    emoji: "🏠"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/followupboss
    category: integrations
    apiKey:
      env: FUB_API_KEY
      getFrom: https://app.followupboss.com → Admin → API
---

# Follow Up Boss CRM 🏠

Query and manage your Follow Up Boss real estate CRM — contacts, notes, tasks, deals.

## Setup

API key from app.followupboss.com → Admin → API. Configure via gateway.

## What Users Ask

- "Look up [client name] in Follow Up Boss"
- "What notes do we have on [person]?"
- "Add a note to [person]'s record"
- "What tasks are due today?"
- "Show me our active deals"
- "Who are our recent leads?"

## Capabilities

- Search contacts by name, email, phone, stage, source, or tags
- View full contact details including activity history
- Read and create notes on contacts
- List and create tasks
- View deals and pipeline stages
- List team members and their assignments

## Response Data

- `people` — Contact records with name, stage, source, phones, emails, tags
- `notes` — Notes attached to contacts with subject and body
- `tasks` — Tasks with assignee, due date, and completion status
- `deals` — Deals with pipeline stage, price, and assigned agents
- `stages` — Pipeline stages for deal tracking
- `users` — Team members with roles and contact info

## Notes

- Rate limit: 250 requests per 10-second window (global)
- Notes endpoint limited to 10 requests per 10-second window
- PUT /people limited to 25 per 10-second window
- API key inherits the user's permission level (Owner, Admin, Agent, Lender)
