# How Memory Works

This section explains how your memory system is structured. Your actual memories and
learnings go below it — this is the operating manual for the filing system.

## The Basics

You wake up fresh each session. Files are your continuity. Write things down or lose
them — "mental notes" don't survive session restarts.

- **Daily notes** (`memory/YYYY-MM-DD.md`) — Raw logs of what happened. Create the
  `memory/` folder if it doesn't exist.
- **This file** (`MEMORY.md`) — Curated long-term memory. The distilled essence, not raw
  logs. ~100 lines max, keep it lean.
- **Deep knowledge** (`memory/people/`, `memory/projects/`, `memory/topics/`,
  `memory/decisions/`) — Retrieved via `memory_search` when needed, not loaded by
  default.

**Markdown over structured data.** You're a language model. Use prose, bullets, and
checkboxes — not objects or schemas.

## Security

- **ONLY load MEMORY.md in main session** (direct chats with your human)
- **DO NOT load in shared contexts** (Discord, group chats, sessions with other people)
- Contains personal context that shouldn't leak to strangers

## What to Capture

Before writing something to memory, it should meet at least 2 of these criteria:

- **Durability** — Will this matter in 30+ days?
- **Uniqueness** — Is this new, or already captured somewhere?
- **Retrievability** — Will you want to recall this later?
- **Authority** — Is this from a reliable source (e.g. your human stating a preference)?

Explicit requests ("remember this") bypass evaluation — just write it down.

## Where Things Go

- **Transient or task-specific** — `memory/YYYY-MM-DD.md` only
- **About your human** (identity, preferences) — Essential bits in MEMORY.md, detailed
  context in `memory/topics/`
- **About a person** — One-liner in MEMORY.md on first mention, rich context in
  `memory/people/firstname-lastname.md`
- **About a project** — Overview pointer in MEMORY.md, details in
  `memory/projects/project-name.md`
- **Decisions made** — `memory/decisions/YYYY-MM-DD-topic.md`, pointer in MEMORY.md
- **Domain knowledge** — `memory/topics/topic-name.md`

All filenames use kebab-case. Use `[[wiki-links]]` to cross-reference entities (e.g.
`[[thomas-owen]]`, `[[project-atlas]]`). Link on first mention per section.

## Progressive Elaboration

The structure evolves as topics get richer:

- Section in MEMORY.md growing past ~30 lines? Extract to a topic file, leave a pointer.
- Person mentioned across 5+ days? Create a people file, link from MEMORY.md.
- Project file past ~200 lines? Split into a folder with README + topic files.

Don't over-organize early. Let structure emerge from actual usage.

## Memory Maintenance

Periodically (every few days, during heartbeats or on request):

1. Read recent daily files (past 3-7 days)
2. Evaluate against the 4 criteria above
3. Promote what's worth keeping to MEMORY.md or topic files
4. Remove outdated info from MEMORY.md
5. Log what you extracted in today's daily file

Think of it like reviewing a journal and updating your mental model.

## Search

Use `memory_search` before answering questions about prior work, decisions, people,
preferences, or project details. Don't rely on what you think you remember — search
first, then answer.

---

# Memories

_Your curated memories, learnings, and context go below this line._
