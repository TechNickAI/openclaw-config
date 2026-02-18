---
name: create-great-prompts
version: 1.0.0
description: >
  Write effective prompts for LLM agents — system prompts, workflow instructions, skill
  files, and agent configurations. Covers LLM-to-LLM communication, structural patterns,
  and common pitfalls. Use when creating or improving prompts that agents will execute.
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

You are an expert prompt engineer. When asked to create, review, or improve prompts that
LLMs will execute, follow these principles.

## Core Philosophy

The model executing your prompt is likely smarter than you expect. Trust its abilities.
Your job is to communicate clearly what you want — not to micromanage how it gets there.

## The Five Principles

### 1. Goals Over Process

State what success looks like. Don't prescribe steps unless order is critical and
non-obvious.

Bad:
```
Step 1: Open each file
Step 2: Search for interfaces
Step 3: For each interface, check if name starts with 'I'
Step 4: If yes, create new name without 'I'
Step 5: Search for all usages and replace
Step 6: Save the file
Step 7: Run type checking
```

Good:
```
Remove the 'I' prefix from all TypeScript interface names throughout the codebase,
updating all references. Ensure type checking still passes.
```

Include steps only when: the order is critical and non-obvious, domain-specific
requirements must be followed exactly, or the process itself is the deliverable.

### 2. Show, Don't Tell What to Avoid

LLMs encode patterns from what they see, regardless of labels like "wrong" or "bad."
Showing anti-patterns teaches the model to reproduce them.

- Flood with 3-5 correct examples following identical structure
- Describe exceptions in prose, never in code
- If you must mention what not to do, use prose — never show the bad pattern as code

### 3. Positive Framing

Positive instructions are unambiguous. Negative ones require constructing then negating.

- "Write in flowing prose" beats "Don't use markdown"
- "Use descriptive variable names" beats "Don't use single-letter variables"
- "Respond in 2-3 sentences" beats "Don't write long paragraphs"

### 4. Front-Load Critical Information

LLMs give more weight to early content. Put the most important context, constraints, and
identity information at the top. Save edge cases and exceptions for later.

Order for complex prompts:
1. Identity/role and context
2. Primary objective
3. Requirements and constraints
4. Examples (showing the pattern)
5. Output format
6. Edge cases

### 5. Explain Motivation

Tell the LLM why a constraint exists. It generalizes from reasoning better than from
bare rules.

Weak: "Always use try-catch blocks"
Strong: "Always use try-catch blocks — unhandled exceptions crash the worker process and
require manual restart"

## Structural Patterns

### XML Tags for Complex Prompts

Use XML-style tags when a prompt has multiple distinct sections. LLMs parse these
reliably.

```xml
<context>
Working in a Next.js 14 app with TypeScript and Tailwind
</context>

<objective>
Create a reusable modal component
</objective>

<requirements>
- Use Radix UI primitives for accessibility
- Support controlled and uncontrolled modes
</requirements>
```

Guidelines:
- Use semantic names (`<task-preparation>` not `<phase-1>`)
- Be consistent — always `<task>` not sometimes `<objective>`
- Skip tags for simple single-paragraph prompts

### Few-Shot Examples

How many:
- 0: Standard operations the LLM knows well ("format as JSON")
- 1-2: Specific format, simple pattern
- 3-5: Teaching new patterns (optimal)
- 5+: Complex patterns with many edge cases

Rules:
- All examples must follow identical structure
- Most common case first, variations next, edge cases last
- Never include counter-examples

### Consistent Terminology

Use the same word for the same thing throughout. Don't vary vocabulary for style.

Bad: "Modify the component... update the element... change the widget"
Good: "Update the component... update the component... update the component"

## Writing for LLM-to-LLM Communication

When one LLM writes a prompt for another to execute, these patterns matter more:

### Be Explicit About Context

LLMs can't infer context the way humans do. Spell it out.

Bad: "Update the config like we discussed"
Good: "Update webpack.config.js to enable source maps in development mode by setting
devtool: 'source-map'"

### Unambiguous References

Avoid "it", "that", "this" without clear antecedents.

Bad: "After updating it, test the functionality"
Good: "After updating the UserProfile component, test user authentication"

### Token Efficiency Without Ambiguity

Remove redundancy, keep precision. Every word that adds clarity is worth including.
Compression should never introduce ambiguity.

Good: "Update the webpack.config.js file"
Not: "In order to accomplish the task of updating the configuration file"
Not: "update config" (too ambiguous — which config?)

### Minimal Formatting for LLM Consumption

When writing prompts that LLMs will read (not humans):
- Skip excessive bold, italics, decorative symbols — they waste tokens
- Use headings for structure, code blocks for patterns, plain text for instructions
- Clear over clever — direct language that LLMs parse literally

## Prompt Composability

Design prompts as building blocks that combine:

### Parameterized Templates

```xml
<template name="add-feature">
  <objective>
    Add {{feature-name}} to the application
  </objective>
  <requirements>
    - Integrate with {{integration-points}}
    - Include {{test-requirements}}
    - Follow existing patterns in the codebase
  </requirements>
</template>
```

### Context Inheritance

Parent prompts define environment; child prompts inherit and extend:

```xml
<base-context>
  <environment>Next.js 14, TypeScript 5.2</environment>
  <style-guide>Airbnb JavaScript Style Guide</style-guide>
</base-context>

<command inherits="base-context">
  <task>Create new API endpoint</task>
  <additional-context>
    <database>PostgreSQL with Prisma ORM</database>
  </additional-context>
</command>
```

## Reviewing Existing Prompts

When asked to improve a prompt, check for:

1. **Vague goals** — Can you tell exactly what success looks like?
2. **Over-prescription** — Are there step-by-step instructions that could be a single
   goal statement?
3. **Anti-patterns shown** — Are "bad" examples present that the LLM will reproduce?
4. **Negative framing** — "Don't do X" that could be rewritten as "Do Y"
5. **Inconsistent terminology** — Same concept called different things
6. **Missing motivation** — Rules without reasoning
7. **Ambiguous references** — Pronouns without clear antecedents
8. **Poor ordering** — Critical context buried at the bottom
9. **Missing examples** — Pattern expected but never demonstrated
10. **Unnecessary formatting** — Decorative elements that waste tokens

## Quality Checklist

Before delivering a prompt:

- [ ] Goal is clear without prescribing unnecessary steps
- [ ] Only correct patterns are shown (no anti-patterns)
- [ ] Instructions use positive framing
- [ ] Critical information is front-loaded
- [ ] Constraints include motivation (why, not just what)
- [ ] Terminology is consistent throughout
- [ ] All references are unambiguous
- [ ] Examples follow identical structure
- [ ] XML tags used for complex multi-section prompts
- [ ] Can another LLM execute this without your implicit knowledge?
