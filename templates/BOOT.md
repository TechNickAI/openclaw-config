# BOOT.md — Gateway Startup Routine

When the gateway starts (or restarts), run through this checklist before doing anything
else. This is your "waking up" moment — orient yourself, check what happened while you
were offline, and get ready.

## 1. Orient

- Read `SOUL.md` — remember who you are
- Read `USER.md` — remember who you're helping
- Read `memory/YYYY-MM-DD.md` (today) — what happened so far today?
- If today's file doesn't exist, read yesterday's — pick up where you left off

## 2. Conversation Recovery (Was I Mid-Conversation?)

Check if a restart interrupted an active conversation.

**How to check:**

1. Look at the session store: `~/.openclaw/agents/<agentId>/sessions/sessions.json` (use
   the `agent=<id>` value from the system prompt Runtime line for `<agentId>`)
2. Find the most recently updated session key that has `origin.provider` set to a chat
   channel (telegram, whatsapp, imessage, discord, slack, etc.) and `origin.chatType` =
   "direct"
3. Check `updatedAt` — convert from epoch ms to a timestamp
4. If the last direct conversation was **within the last 1 minute**, the restart
   interrupted an active exchange

**If interrupted (< 1 min ago):**

1. Read the last 20 lines of that session's JSONL transcript
2. Extract the last few user messages and your last response
3. Write a short summary of the interrupted conversation to a temp note: what was being
   discussed, what the user last asked, what you were working on
4. Send the user a message via the `message` tool on the channel where the conversation
   was happening:
   - Keep it brief: "Just restarted. We were working on [X]. Want to pick up where we
     left off?"
   - Include enough context that they can say "yes, continue" without re-explaining
5. Reply with NO_REPLY after sending the message

**If NOT interrupted (> 1 min ago or no recent direct conversation):**

- Skip to step 3 (check for unfinished work)

## 3. Check for Unfinished Work

- Does `state/active-work.json` exist? → Resume it
- Any tasks tagged as in-progress in your task system? → Note them
- Were you in the middle of something before the restart? Memory files will tell you

## 4. Silent Start

Don't message your human on routine restarts. Only reach out if:

- Step 2 detected an interrupted conversation (already handled above)
- You found unfinished urgent work that needs their attention
- Something is broken that was working before
- It's been >24h since any interaction (check-in is appropriate)

If everything is fine, start quietly and wait for the next heartbeat or message.

---

## Customization

Add your own startup checks below. Keep it lightweight — this runs on every gateway
restart, so don't do heavy processing here.

```markdown
## Custom Startup

- [ ] Check [service] connection
- [ ] Verify [integration] is authenticated
```
