# Vapi Phone Call Skill

Status: brainstormed, not started Date: Feb 4, 2026

## Motivation

OpenClaw hits a dead end when a task requires a phone call — e.g., cancelling a
restaurant reservation that can't be done online. Vapi (vapi.ai) provides an API for
AI-powered outbound phone calls. This skill lets OpenClaw call businesses to complete
tasks on Nick's behalf.

## Design

**Directory:** `skills/vapi/`

**Commands:**

- `vapi call <phone> "<task>"` — outbound call, blocks until complete
- `vapi call --async <phone> "<task>"` — fire and forget, returns call ID
- `vapi status <call_id>` — check status/results of async call
- `vapi help`

**How it works:**

1. Receives phone number + natural language task description
2. Builds a transient Vapi assistant (no pre-saved template needed) with:
   - System prompt from the task description, augmented with caller identity
   - A `firstMessage` derived from the task context
   - `analysisPlan` to extract structured success/failure outcome
   - Voice config (ElevenLabs, natural-sounding voice)
3. Initiates outbound call via Vapi `POST /call`
4. Blocking mode: polls every 5s until `status == "ended"`, returns transcript +
   analysis
5. Async mode: returns call ID immediately

**Environment variables:**

- `VAPI_API_KEY` — from dashboard.vapi.ai
- `VAPI_PHONE_NUMBER_ID` — provisioned phone number ID
- `VAPI_CALLER_NAME` — name to give when asked (e.g., "Nick Sullivan")
- `VAPI_CALLBACK_NUMBER` — number to leave if asked for callback

**Output (blocking mode):**

```markdown
## Call Complete

**Status:** Succeeded / Failed **Duration:** 2m 15s **Outcome:** Reservation cancelled
for Nick Sullivan, party of 2, tonight at 7:30pm

### Transcript

[Full conversation]

### Recording

[URL]
```

## Vapi API Details

**Python SDK:** `vapi_server_sdk` (pip: `vapi_server_sdk`)

```python
from vapi import Vapi

client = Vapi(token="YOUR_API_KEY")

call = client.calls.create(
    phone_number_id="your-phone-number-id",
    customer={"number": "+14155559876"},
    assistant={
        "name": "Task Assistant",
        "firstMessage": "Hi, I'm calling to cancel a dinner reservation please.",
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [{"role": "system", "content": "...task prompt..."}]
        },
        "voice": {
            "provider": "11labs",
            "voiceId": "cgSgspJ2msm6clMCkdW9"
        },
        "analysisPlan": {
            "structuredDataSchema": {
                "type": "object",
                "properties": {
                    "taskCompleted": {"type": "boolean"},
                    "outcome": {"type": "string"},
                    "notes": {"type": "string"}
                },
                "required": ["taskCompleted"]
            },
            "successEvaluationRubric": "PassFail"
        }
    }
)
```

**Polling for results:**

```python
result = client.calls.get(call_id)
# result.status, result.artifact.transcript, result.artifact.recording_url
# result.analysis.structured_data, result.analysis.success_evaluation
```

**Pricing:** ~$0.07-0.30/min depending on model. A 2-3 min call costs ~$0.15-0.60.

**Phone numbers:** Free tier gives up to 10 US numbers. For production, import from
Twilio/Vonage/Telnyx. STIR/SHAKEN + CNAM registration recommended to avoid spam flags.

## Prerequisites

- [ ] Create Vapi account at vapi.ai
- [ ] Get API key from dashboard.vapi.ai
- [ ] Provision a phone number (free tier or import existing)
- [ ] Choose a voice (ElevenLabs voices available through Vapi)

## Open Questions

- Which LLM provider to use for the call agent? OpenAI gpt-4o is the default but
  Anthropic is also supported. Cost vs quality tradeoff.
- Voice selection — should test a few to find one that sounds natural for business calls
- Should the skill support Anthropic models through Vapi? Would keep everything in the
  Claude family.
