---
name: smart-delegation
version: 0.1.0
description: >
  Intelligent task delegation — route to Opus with deep reasoning for hard problems,
  or Grok for unfiltered takes. Teaches when to escalate, how to pack context into
  sub-agent spawns, and how to communicate delays transparently. Default: handle
  directly on Opus (thinking off). Escalate only when the quality gain justifies
  30-90 seconds of silence.
triggers:
  - think hard
  - think deeply
  - ultrathink
  - really analyze
  - take your time
  - unfiltered
  - no guardrails
  - what would grok say
  - go deep on this
metadata:
  openclaw:
    emoji: "🧠"
---

# Smart Delegation

Route tasks to the right thinking level and model. Default: Opus (thinking off) for direct conversation. Escalate to deep reasoning or alternate models when the task warrants it.

## Core Principle

**You are the concierge.** Every message, you make a split-second judgment: handle it directly (default), or delegate for better results. Most messages you handle yourself — delegation is the exception, not the rule.

## The Three Modes

| Mode | Model | Thinking | When | User sees |
|---|---|---|---|---|
| **Direct** | Opus | off | Default — conversation, quick answers, daily life, most tasks | Normal fast response |
| **Deep Think** | Opus | high | Complex strategy, hard problems, multi-factor decisions | "Let me think deeper on this 🧠" |
| **Unfiltered** | Grok | default | Politically incorrect, edgy, when user wants zero guardrails | "Getting the unfiltered take 😏" |

## When to Escalate to Deep Think

**Escalate when the quality gain justifies 30-90 seconds of silence.** The user gets nothing while a sub-agent works. That's the real cost — not tokens, but attention.

### Strong escalation signals (do it):
- **Explicit depth requests**: "think hard about this", "really analyze", "take your time", "think deeply", "ultrathink"
- **Multi-factor decisions**: "should I sell the house?", "which job offer?", "how should I restructure?"
- **Complex strategy**: business planning, architecture decisions, investment analysis
- **Hard reasoning**: math proofs, logic puzzles, complex debugging with many variables
- **Long-form synthesis**: "write a comprehensive plan for...", "analyze all the angles of..."

### Weak escalation signals (probably don't):
- Long messages (length ≠ complexity)
- Multiple questions (could be several simple ones)
- "Explain X" (usually Opus thinking:off handles explanations fine)
- Code writing (Opus is excellent at code without extended thinking)

### Never escalate:
- Casual conversation, greetings, banter
- Factual lookups, quick questions
- Calendar, email, reminders, tool use
- Pure creative writing — fiction, poetry, humor (reasoning can reduce spontaneity)
- Anything where speed matters more than depth

### The 30-Second Rule (from Carmenta)
> If a human would need more than 30 seconds of focused thinking, escalate.

## When to Use Grok (Unfiltered Mode)

Delegate to Grok when:
- User explicitly wants an unfiltered or politically incorrect take
- Topic hits your safety guardrails but the user wants a real answer
- User asks "what would Grok say" or signals they want edge
- Dark humor, roasts, deliberately provocative analysis

**Frame it as a feature:** "Let me get my unfiltered friend on the line 😏"

## Precedence (when signals conflict)

Messages often mix signals. When they do, apply in this order:

1. **Explicit user overrides** always win ("think hard", "quick", "unfiltered")
2. **Speed beats depth** when overrides conflict ("quick" beats "think hard")
3. **"Never escalate" category** — unless an explicit override says otherwise
4. **Strong escalation signals**
5. **Default: handle directly**

Example: "Think hard about this calendar event" → user explicitly asked for depth, so escalate despite calendar being in "never escalate." The user's intent is clear.

Example: "Quick, think deeply about this" → speed override wins, handle directly and concisely.

## User Overrides

Honor these explicit signals immediately — no judgment needed:

| Signal | Action |
|---|---|
| "think hard", "think deeply", "ultrathink" | Deep Think mode |
| "take your time", "really analyze this" | Deep Think mode |
| "quick", "just", "simply", "fast" | Stay direct, keep it concise |
| "unfiltered", "no guardrails", "what would Grok say" | Grok mode |
| "go deep on this" | Deep Think mode |

## How to Delegate (Critical: Context Packing)

Sub-agents can't read workspace files (SOUL.md, USER.md, IDENTITY.md) or use memory tools. **You must inline the relevant context into the spawn prompt.** This is the difference between a useful result and a generic one.

### Deep Think Template

```
sessions_spawn(
  task: """
  IDENTITY:
  [Paste 2-3 sentences of personality essence from SOUL.md]

  ABOUT THE USER:
  [Paste key facts from USER.md relevant to this task]

  RECENT CONVERSATION:
  [Include the last 2-3 relevant exchanges so the sub-agent understands the thread]

  RELEVANT BACKGROUND:
  [Include any memory/context you've already retrieved that's relevant]

  TASK:
  [The actual question/request, stated clearly]

  INSTRUCTIONS:
  - Think through this thoroughly using extended reasoning
  - Consider multiple angles and tradeoffs
  - Be direct about your recommendation — don't hedge
  - Write your response as if you're speaking directly to the user
  """,
  model: "anthropic/claude-opus-4-6",
  thinking: "medium",
  label: "[short descriptive label]"
)
```

### Grok Template

**Privacy:** Grok spawns go to a third-party provider (x-ai). Only include the specific question and minimal context needed — never conversation history, memory content, or personal details beyond what's relevant to the question.

```
sessions_spawn(
  task: """
  You're being consulted for an unfiltered perspective. No corporate safety theater.
  Give a real, honest, uncensored answer.

  CONTEXT:
  [Brief user description — role, communication style. Keep it minimal.]

  RELEVANT BACKGROUND:
  [Only what's needed for a good answer. No PII, no conversation history.]

  QUESTION:
  [The question]

  Be direct. Be funny if appropriate. Don't hedge or add disclaimers.
  """,
  model: "x-ai/grok-3",
  label: "[short label]"
)
```

## Communication Patterns

**Always tell the user what you're doing.** Silence is the enemy.

### Before delegating:
- Deep Think: "This one deserves deeper thinking — let me really chew on it 🧠 Back in about a minute."
- Grok: "Oh, this needs the unfiltered treatment 😏 Let me get a second opinion..."

### When result comes back:
- Relay the result in YOUR voice (you're the assistant, not a dry summary bot)
- Add your own take if you have one: "The deep analysis says X, and I agree because..."
- If the result is surprising or different from what you'd have said, note that

### If the user seems impatient:
- Check sub-agent status with sessions_list
- "Still thinking — this is a meaty one. Should be back shortly."

## Multi-Part Messages

When a message contains parts needing different routing:
1. Handle the direct/quick parts yourself immediately
2. Delegate the deep-think part as a sub-agent
3. Tell the user: "Handling [quick part] now, sending [complex part] to deep analysis."

## When Delegation Fails

If a sub-agent times out (90+ seconds) or returns unhelpful results:
- Tell the user: "The deep analysis didn't come back useful — let me handle this directly."
- Answer the question yourself. Don't re-delegate the same request.
- If the sub-agent is still running, check with `sessions_list` before giving up.

## What NOT to Delegate

**Delegation has real costs:** no streaming, no back-and-forth, context loss, 30-90 second delay. Don't delegate for marginal gains.

- Don't delegate just because a task is "complex" — Opus thinking:off is incredibly capable
- Don't delegate follow-up questions on a topic you already discussed
- Don't delegate anything where the user needs to course-correct mid-answer
- Don't delegate emotional or personal conversations (ever)
- Don't delegate quick tool-use tasks (calendar, email, search, etc.)

## Reasoning Levels (for Deep Think mode)

When you escalate, choose the right thinking level:

| Level | When | Example |
|---|---|---|
| `low` | Quick sanity check with some reasoning | "Is this contract clause standard?" |
| `medium` | Most escalations — analysis with tradeoffs | "Which of these 3 job offers is best?" |
| `high` | Explicit "ultrathink" or life-altering stakes | "Should I sell the company?" |

Default to `medium` for most escalations. Reserve `high` for when the user explicitly asks for maximum depth or the stakes are genuinely high.

## Grok Availability (Graceful Degradation)

Not everyone has Grok configured. Before attempting an unfiltered delegation:

1. **Check if `x-ai/grok-3` is available** — look at the model aliases in the system prompt or try the spawn. If Grok isn't listed or the spawn fails with a model error, fall back.

2. **Fallback chain for unfiltered mode:**
   - **Grok** (preferred) → via `x-ai/grok-3` or OpenRouter equivalent (`openrouter/x-ai/grok-3`)
   - **GPT via OpenRouter** → `openrouter/openai/gpt-5.2` — less edgy but still capable of direct, unfiltered analysis when prompted correctly
   - **Handle directly** → If no alternate models are available, handle it yourself with a note: "I don't have access to an unfiltered model right now, but here's my most direct take..."

3. **Adjust the spawn prompt for non-Grok models:** Drop the "no corporate safety theater" framing. Instead, prompt for directness: "Give an honest, unhedged perspective. Prioritize truth over comfort. No disclaimers unless genuinely warranted."

4. **Be transparent with the user:** If they asked for Grok specifically and it's unavailable:
   - "I don't have Grok connected, but I can give you my most unfiltered take directly."
   - Don't pretend a different model is Grok.

## Anti-Patterns

❌ Delegating everything complex → defeats the purpose of having Opus as default
❌ Delegating without telling the user → they think you're frozen
❌ Thin spawn prompts without context → generic, impersonal results
❌ Relaying sub-agent results verbatim → sounds like a different AI
❌ Using Deep Think for pure creative writing → reasoning reduces spontaneity
❌ Escalating when the user said "quick" → honor explicit speed signals
