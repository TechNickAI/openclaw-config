---
name: vapi-calls
version: 0.2.0
description:
  Make outbound phone calls via Vapi voice AI. Use when the agent needs to call someone
  on the phone for any reason (reminders, notifications, requests to businesses, or any
  task that benefits from a real voice conversation). Requires VAPI_API_KEY, a
  provisioned phone number, and an assistant configured in Vapi.
triggers:
  - vapi
  - make a call
  - place a call
  - call someone
  - phone call
  - outbound call
  - voice agent
  - voice call
metadata:
  openclaw:
    emoji: "☎️"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/vapi-calls
    category: integrations
    apiKey:
      env: VAPI_API_KEY
      getFrom: https://dashboard.vapi.ai → API Keys
---

# Vapi Voice Calls

Make real outbound phone calls through Vapi's voice AI platform.

## Prerequisites

Check that these are set in your environment:

- `VAPI_API_KEY`
- `VAPI_ASSISTANT_ID`
- `VAPI_PHONE_NUMBER_ID`

If any are missing, read [references/setup.md](references/setup.md) and complete
first-time setup before proceeding.

## Making a Call

Use the Vapi `POST /call` endpoint with:

- `phoneNumberId` and `assistantId` from your config
- `customer.number` — the phone number to call (E.164 format)
- `assistantOverrides.model.systemPrompt` — the full system prompt including
  task-specific instructions for this call
- `assistantOverrides.firstMessage` — a contextual opening line for this specific call

The base assistant defines voice, transcriber, and personality defaults. The override
injects what THIS call is about.

### System Prompt Structure for Each Call

1. The base prompt (heart-centered foundation + agent personality + "You are on a live
   phone call")
2. A `TASK:` section with specific instructions for this call

Everything the voice agent needs to know goes in the override. The voice agent has no
memory between calls.

### After the Call

Poll `GET /call/{id}` to check status and `endedReason`. Key values:

- `assistant-ended-call` — completed normally
- `customer-did-not-answer` — no pickup, consider retrying or texting first
- `pipeline-error-*` — voice provider issue, check configuration

## Notes

- Vapi built-in voices are free. ElevenLabs voices require a paid ElevenLabs plan.
- Cost is ~$0.05-0.07/min, pay-as-you-go.
- Template variables (`{{var}}`) can be used in prompts, resolved from call metadata.
