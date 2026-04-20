---
name: hubspot
version: 0.1.0
description:
  Query HubSpot CRM contacts, deals, and deal stages via the HubSpot REST API. Use when
  you need to look up contacts, inspect deals, search the CRM, or review deal stage
  definitions in HubSpot.
triggers:
  - hubspot
  - hub spot
  - crm
  - contacts
  - deals
  - pipeline
  - deal stages
  - look up in hubspot
  - search hubspot
metadata:
  openclaw:
    emoji: "🟠"
    apiKey:
      env: HUBSPOT_API_KEY
      getFrom: https://app.hubspot.com/private-apps
---

# HubSpot 🟠

Read HubSpot CRM data from the REST API.

## Setup

Create or use a HubSpot private app token, then configure it as `HUBSPOT_API_KEY` in
OpenClaw.

Recommended minimum scopes for this skill:

- `crm.objects.contacts.read`
- `crm.objects.deals.read`
- `crm.schemas.deals.read`

## What Users Ask

- "Look up this person in HubSpot"
- "Search HubSpot for [name or email]"
- "Show me recent deals"
- "What stage is this deal in?"
- "List the HubSpot deal stages"
- "Open this contact or deal by ID"

## Commands

- `hubspot contacts [query] [--limit N]`
- `hubspot contact <contact_id>`
- `hubspot deals [query] [--limit N]`
- `hubspot deal <deal_id>`
- `hubspot stages`

## Capabilities

- Search contacts by free text
- Fetch a contact by HubSpot ID
- Search deals by free text
- Fetch a deal by HubSpot ID
- Resolve deal stage IDs to readable labels
- List all configured deal pipelines and stages

## Notes

- This version is read-only.
- Owner lookup is not included because many HubSpot tokens do not have the extra scopes
  required for the owners API.
- Deal stage labels come from the pipelines API, so stage output stays readable instead
  of showing only internal IDs.
