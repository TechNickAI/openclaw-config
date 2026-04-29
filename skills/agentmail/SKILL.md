---
name: agentmail
version: 0.2.0
description:
  Email inboxes for AI agents - create addresses, send and receive email, manage threads
triggers:
  - agentmail
  - email
  - inbox
  - send email
  - check email
  - email agent
  - create inbox
  - webhook
  - incoming email
  - email notification
metadata:
  openclaw:
    emoji: "\U0001F4EC"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/agentmail
    category: integrations
    apiKey:
      env: AGENTMAIL_API_KEY
      getFrom: https://agentmail.to → Dashboard → API Keys
---

# AgentMail

Email infrastructure for AI agents — create inboxes, send/receive messages, manage
threads.

## Setup

API key from agentmail.to → Dashboard → API Keys. Configure via gateway.

## What Users Ask

- "Create an email inbox for the support agent"
- "Send an email to user@example.com"
- "Check the inbox for new messages"
- "What emails came in today?"
- "Reply to that email"
- "Show me the thread with the customer"

## Capabilities

- Create and manage email inboxes (each gets a unique address)
- Send emails from any inbox
- List and read incoming messages
- Reply to messages within threads
- Thread-based conversation tracking
- Webhooks for real-time email notifications (push-based)
- Delete inboxes when done

## Response Data

**Inbox:**

- `id` — Inbox ID
- `email` — The inbox's email address
- `display_name` — Friendly name
- `created_at` — Creation timestamp

**Message:**

- `id` — Message ID
- `thread_id` — Thread this message belongs to
- `from` — Sender address
- `to` — Recipient addresses
- `subject` — Email subject
- `text` — Plain text body
- `created_at` — Timestamp

**Thread:**

- `id` — Thread ID
- `subject` — Thread subject
- `message_count` — Number of messages
- `messages` — Messages in the thread (when fetched individually)

## Webhooks

AgentMail can push events to your endpoint in real-time via webhooks (powered by Svix).

**Event types:** `message.received`, `message.sent`, `message.delivered`,
`message.bounced`, `message.complained`, `message.rejected`, `message.received.spam`,
`message.received.blocked`, `domain.verified`

**Signature verification:** Each webhook POST includes Svix headers (`svix-id`,
`svix-signature`, `svix-timestamp`). The `secret` returned at creation time is used with
Svix libraries to verify authenticity.

**Filtering:** Webhooks can be scoped to specific inboxes (max 10 per webhook).

### Serving the webhook endpoint

The webhook URL must be reachable from the internet. Two approaches:

**Tailscale Funnel (preferred if already on Tailscale):**

```bash
# Expose a local port to the internet via your Tailscale domain
tailscale funnel 8080
# Your URL: https://<machine-name>.<tailnet>.ts.net/hook
```

No config changes, no DNS, no certs — Tailscale handles it all. Works on any fleet
machine that already runs Tailscale.

**Cloudflare Tunnel (alternative):**

```bash
# One-time setup, then:
cloudflared tunnel run --url http://localhost:8080
```

Gives you a stable `*.cfargotunnel.com` URL or custom domain.

### Connecting to OpenClaw

OpenClaw is pull-based today (cron polling). To handle incoming webhooks, the instance
needs a lightweight HTTP listener that:

1. Receives the webhook POST from AgentMail
2. Verifies the Svix signature
3. Writes the event to a file (e.g., `events/incoming-email.md`)
4. OpenClaw picks it up on next cron cycle, or a reactive workflow triggers

This is OpenClaw's first push-based integration pattern. The webhook receiver is
intentionally minimal — a thin HTTP server that authenticates and persists events for
OpenClaw to process.

## Notes

- Free tier: 3 inboxes, 3,000 emails/month, 3 GB storage, 2 webhook endpoints
- Inboxes get addresses on agentmail.to domain by default
- Custom domains available on paid plans
- Webhook management requires org-level API key (not inbox-scoped)
- API docs: https://docs.agentmail.to
