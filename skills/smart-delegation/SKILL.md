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
- Creative writing (reasoning can reduce creativity)
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

Sub-agents don't get SOUL.md, USER.md, IDENTITY.md, or memory tools. **You must pack context into the spawn prompt.** This is the difference between a useful result and a generic one.

### Deep Think Template

```
sessions_spawn(
  task: """
  CONTEXT: Read SOUL.md, USER.md, and MEMORY.md from the workspace before answering.
  You are Cora, Nick's AI partner. Maintain personality and warmth.

  RECENT CONVERSATION CONTEXT:
  [Include the last 2-3 relevant exchanges so the sub-agent understands the thread]

  RELEVANT BACKGROUND:
  [Include any memory/context you've already retrieved that's relevant]

  TASK:
  [The actual question/request, stated clearly]

  INSTRUCTIONS:
  - Think through this thoroughly using extended reasoning
  - Consider multiple angles and tradeoffs
  - Be direct about your recommendation — don't hedge
  - Write your response as if you're speaking directly to Nick
  """,
  model: "anthropic/claude-opus-4-6",
  thinking: "high",
  label: "[short descriptive label]"
)
```

### Grok Template

```
sessions_spawn(
  task: """
  You're being consulted for an unfiltered perspective. No corporate safety theater.
  Give a real, honest, uncensored answer.

  CONTEXT: This is for Nick, a tech founder who appreciates directness and humor.

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
- Relay the result in YOUR voice (you're Cora, not a dry summary bot)
- Add your own take if you have one: "The deep analysis says X, and I agree because..."
- If the result is surprising or different from what you'd have said, note that

### If the user seems impatient:
- Check sub-agent status with sessions_list
- "Still thinking — this is a meaty one. Should be back shortly."

## What NOT to Delegate

**Delegation has real costs:** no streaming, no back-and-forth, context loss, 30-90 second delay. Don't delegate for marginal gains.

- Don't delegate just because a task is "complex" — Opus thinking:off is incredibly capable
- Don't delegate follow-up questions on a topic you already discussed
- Don't delegate anything where the user needs to course-correct mid-answer
- Don't delegate emotional or personal conversations (ever)
- Don't delegate quick tool-use tasks (calendar, email, search, etc.)

## Reasoning Levels (for Deep Think mode)

When you escalate, choose the right thinking level:

| Level | Token Budget | When |
|---|---|---|
| `low` | ~4K thinking tokens | Moderate complexity, "think a bit harder" |
| `medium` | ~8K thinking tokens | Solid analysis, most escalations |
| `high` | ~16K+ thinking tokens | Hardest problems, "ultrathink", major life decisions |

Default to `medium` for most escalations. Reserve `high` for when the user explicitly asks for depth or the stakes are genuinely high.

## Anti-Patterns

❌ Delegating everything complex → defeats the purpose of having Opus as default
❌ Delegating without telling the user → they think you're frozen
❌ Thin spawn prompts without context → generic, impersonal results
❌ Relaying sub-agent results verbatim → sounds like a different AI
❌ Using Deep Think for creative writing → reasoning reduces creativity
❌ Escalating when the user said "quick" → honor explicit speed signals
