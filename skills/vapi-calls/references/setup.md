# Vapi First-Time Setup

Complete these steps to enable voice calling for your agent.

## 1. Create a Vapi Account

Sign up at https://dashboard.vapi.ai (Google, GitHub, or email). New accounts get $10 in
credits.

## 2. Store the API Key

Get the private API key from Dashboard > API Keys. Add it to the gateway as
`VAPI_API_KEY`.

## 3. Provision a Phone Number

Create a free US phone number through the Vapi `POST /phone-number` endpoint with
`provider: "vapi"`. Up to 10 free numbers per account.

The number starts in `activating` status and takes 1-2 minutes to become `active`. Do
not attempt calls until it's active.

Save the phone number ID as `VAPI_PHONE_NUMBER_ID` and the actual number as
`VAPI_PHONE_NUMBER` in your config.

## 4. Create an Assistant

Create an assistant via `POST /assistant` with:

- A base system prompt (keep it generic, task details come per-call)
- A voice selection
- A transcriber (Deepgram nova-2 is the default)

### System Prompt Design

The base prompt should be minimal:

1. Heart-centered foundation (terse version from `heart-centered-prompts` if available)
2. Agent personality in 2-3 sentences
3. "You are on a live phone call. Your task instructions will tell you who you are
   calling, why, and what to accomplish. Follow them."

No scenario-specific logic belongs in the base prompt. All call-specific instructions go
in `assistantOverrides` at call time.

### Voice Selection

Available free built-in voices:

| Voice    | Tags                     |
| -------- | ------------------------ |
| **Leah** | Warm, Gentle             |
| **Mia**  | Professional, Articulate |
| **Tara** | Conversational, Clear    |
| **Jess** | Energetic, Youthful      |
| **Zoe**  | Calm, Soothing           |

Also available: Clara, Kylie, Lily, Savannah, Hana, Neha, Paige, Emma, Naina (female);
Godfrey, Elliot, Rohan, Cole, Harry, Spencer, Nico, Kai, Sagar, Neil, Leo, Dan, Zac
(male)

No preview audio in the dashboard. To audition, use the "Talk" button in the assistant
editor for a live web call, or make test phone calls.

ElevenLabs voices can be added via the `/credential` endpoint (provider `11labs`) but
require a paid ElevenLabs plan. Free tier is blocked for real-time streaming.

Save the assistant ID as `VAPI_ASSISTANT_ID` in your config.

## 5. Verify

Make a test call to confirm everything works. If the call fails, check `endedReason` on
the call object for diagnostics.

## Fleet Deployment

One Vapi account with shared billing. Each agent gets its own assistant (personality +
voice) and phone number under the same org.
