---
name: create-great-prompts
version: 2.0.0
description: >
  Write effective prompts for LLM agents — system prompts, workflow instructions, skill
  files, and agent configurations. Use when creating or improving prompts that agents
  will execute.
triggers:
  - write a prompt
  - create a system prompt
  - improve this prompt
  - prompt engineering
  - write agent instructions
  - create a skill
  - optimize this prompt
  - make this prompt better
metadata:
  openclaw:
    emoji: "✍️"
---

# Create Great Prompts

You write prompts that LLMs execute — system prompts, agent instructions, workflow
definitions, skill files. The model running your prompt is likely more capable than you
expect. Communicate what you want clearly and trust it to figure out how.

## The Principles

### Goals Over Process

State what success looks like. Trust the executing model to determine the approach.

```
Remove the 'I' prefix from all TypeScript interface names throughout the codebase,
updating all references. Ensure type checking still passes.
```

Include specific steps only when order is critical and non-obvious, or when the process
itself is the deliverable (like a deployment checklist).

### Positive Framing

Positive instructions are unambiguous. "Write in flowing prose" gives the model a clear
target. State what you want, not what you want to avoid — the model executes toward a
destination, not away from one.

### Show Correct Patterns Only

LLMs encode patterns from what they see, regardless of labels. When teaching through
examples, flood with 3-5 correct examples following identical structure. Describe
exceptions and edge cases in prose.

### Front-Load What Matters

LLMs weight early content more heavily. Lead with identity, context, and the primary
objective. Save edge cases for later.

For complex prompts: identity/role → objective → constraints → examples → output format.

### Explain Why

Constraints with reasoning generalize better than bare rules.

```
Use try-catch blocks in all API handlers — unhandled exceptions crash the worker
process and require manual restart.
```

## Structure

Use XML-style tags when a prompt has multiple distinct sections that need clear
boundaries. Use semantic tag names (`<task-preparation>` not `<phase-1>`), keep them
consistent throughout, and skip them entirely for simple prompts.

```xml
<context>
Working in a Next.js 14 app with TypeScript and Tailwind
</context>

<objective>
Create a reusable modal component with Radix UI primitives
</objective>

<requirements>
- Accessible keyboard navigation
- Support controlled and uncontrolled modes
</requirements>
```

## LLM-to-LLM Communication

When writing prompts that another LLM will execute (not a human reading):

**Be explicit.** Spell out context that a human would infer. "Update webpack.config.js
to enable source maps in development mode by setting devtool: 'source-map'" — not
"update the config."

**Use consistent terminology.** Same word for the same concept throughout. Varying
vocabulary for style introduces ambiguity that humans resolve but LLMs may not.

**Name your references.** "After updating the UserProfile component, test user
authentication" — pronouns without clear antecedents create parsing ambiguity.

**Keep formatting functional.** Headings for structure, code blocks for patterns, plain
text for instructions. Every formatting choice should aid parsing, not decoration.

## Creating a Prompt

When someone asks you to write a prompt:

1. **Understand the goal.** What will the executing model produce? What does success
   look like? Ask if it's unclear.

2. **Understand the context.** What model runs this? What tools does it have? What does
   it already know? What's the input format?

3. **Write the prompt.** Apply the principles above. Start with the simplest version
   that could work — you can always add specificity.

4. **Stress-test mentally.** Could a different model interpret this differently than you
   intend? Are there ambiguities? Would this work without your implicit knowledge of
   the project?

## Improving an Existing Prompt

Apply the principles as a lens. The single most important question: **can another LLM
execute this without your implicit knowledge?**
