# Cortex: Personal Knowledge Compiler

Status: reviewed (deep multi-review complete) Date: April 11, 2026

## Motivation

A full digital life spread across Dropbox and Google Drive — documents, notes, captures,
transcripts, media, code artifacts. None of it is structured for AI agent consumption.
Inspired by Andrej Karpathy's LLM Wiki architecture: an LLM acts as a knowledge compiler
that ingests raw sources into a structured, interlinked knowledge base that agents can
navigate and reason over.

The name: Latin _cortex_ = the brain's outer integration layer where diverse inputs
become coherent understanding. Raw sources are sensory input; Cortex compiles them into
structured, navigable knowledge. Not a wiki — a compiler.

The key insight: humans explore ideas, LLMs handle bookkeeping. Cortex compounds
knowledge over time — cross-references, entity pages, synthesis — without manual
maintenance.

## Design Principles

- **Agent-first, Obsidian-compatible.** Structured frontmatter, consistent linking,
  tiered indexes sized for context windows. The directory structure happens to be a
  valid Obsidian vault, but Obsidian is a viewer, not a dependency.
- **Cloud storage as transport.** All machines have either Dropbox or Google Drive.
  Cortex lives in cloud storage and gets symlinked into OpenClaw's memory path. No
  servers, no databases, no vector stores at initial scale.
- **Three-layer architecture.** Raw sources (immutable), compiled knowledge (LLM-owned),
  schema (rules). Adapted from Karpathy for agent-first consumption.
- **Three operations.** Ingest (compile raw -> knowledge), query (search -> synthesize),
  lint (self-heal contradictions and gaps).
- **Local-first, graduated infrastructure.** Plain markdown on disk. Grep at <500 pages,
  add qmd (BM25 hybrid search) at 500-2000, consider embeddings only beyond that.
- **Single-writer architecture.** Only one machine runs ingest/lint operations at a
  time. All other machines are read-only consumers. Cloud storage is eventually
  consistent, not transactional — respect that.
- **Schema as droppable prompt.** `schema.md` is designed to be copy-pasted into any LLM
  agent session, turning it into a disciplined knowledge maintainer. Not just
  documentation — an executable instruction set (per Karpathy's "idea file" framing).

## Architecture

### Store Location

Cortex lives in cloud storage on whichever service is available:

```
Primary:   ~/Dropbox/cortex/
Fallback:  ~/Library/CloudStorage/GoogleDrive-<email>/My Drive/cortex/   (macOS)
Fallback:  ~/google-drive/cortex/                                         (Linux rclone)
```

A setup script detects which path exists and stores it in a local config file
(`~/.config/cortex/config`) so other tools know where to find the store.

**Obsidian compatibility:** The directory is a valid Obsidian vault. Point Obsidian at
it to get graph view, search, and Web Clipper delivery. But nothing in Cortex requires
Obsidian — it's plain markdown files in folders.

### Store Structure (Three Layers)

```
cortex/                                <- Knowledge store root (in cloud storage)
|
+-- .obsidian/                         <- Optional: Obsidian config if viewer is used
+-- .git/                              <- Git tracking for versioning/rollback
|
+-- raw/                               <- LAYER 1: Immutable source material
|   +-- documents/                     <- PDFs, exports, manuals
|   +-- notes/                         <- Apple Notes exports, journal entries, ideas
|   +-- captures/                      <- Web Clipper output, saved articles, bookmarks
|   +-- transcripts/                   <- Fireflies, Limitless meeting transcripts
|   +-- media/                         <- Screenshots, design assets, images
|   +-- code/                          <- Architecture docs, READMEs, config snapshots
|   +-- conversations/                 <- Notable AI conversation exports
|   +-- reference/                     <- API docs, specs, standards
|
+-- knowledge/                         <- LAYER 2: LLM-compiled knowledge (symlinked)
|   +-- index.md                       <- Meta-index: category summaries + pointers
|   +-- log.md                         <- Append-only operation log
|   +-- .ingest-state.md               <- Tracks ingest progress (path -> status + hash)
|   +-- .lock                          <- Advisory write lock (machine ID + timestamp)
|   +-- entities/                      <- People, companies, projects, tools, services
|   |   +-- _index.md                  <- Entity sub-index
|   +-- concepts/                      <- Ideas, patterns, principles, domains
|   |   +-- _index.md                  <- Concept sub-index
|   +-- summaries/                     <- 1:1 with raw files, source-level digests
|   |   +-- _index.md                  <- Summary sub-index
|   +-- synthesis/                     <- Cross-cutting analysis and comparisons
|   |   +-- _index.md                  <- Synthesis sub-index
|   +-- decisions/                     <- Architectural decisions, trade-off records
|   |   +-- _index.md                  <- Decision sub-index
|   +-- how-to/                        <- Procedural knowledge extracted from sources
|       +-- _index.md                  <- How-to sub-index
|
+-- schema.md                          <- LAYER 3: Rules for LLM knowledge maintenance
```

### Layer 1: Raw Sources

Immutable. The LLM reads but never modifies. Files dropped here by the human (via
Obsidian Web Clipper, manual copy, script import, etc.). Each raw file is the source of
truth — Cortex summarizes and cross-references it.

Subdirectory choice is a hint, not a rule. A PDF about trading architecture goes in
`documents/`, a screenshot of a UI goes in `media/`. The LLM uses the subdirectory as
context during ingest but doesn't depend on perfect categorization.

**Media handling:** Use vision models (Claude, Gemini) for screenshots, diagrams, and
images. Extract text from PDFs via standard tooling. Media files get summary pages like
any other source — Cortex describes what's in them so agents can find relevant visuals
without loading images.

### Layer 2: Knowledge (LLM-Compiled)

Every file in `knowledge/` is generated and maintained by the LLM. Humans can read but
should not edit (edits get overwritten on next lint/ingest cycle).

**Write access:** Only the `cortex` skill writes to `knowledge/`. The symlink into
OpenClaw memory is read-only for consuming agents (enforced by directory permissions:
755 for the skill user, read-only for others, or by convention when permissions aren't
enforceable).

**Page constraints:**

- Maximum page size: ~2000 words. Pages exceeding this get split into focused sub-pages
  with a parent page linking them.
- Each page must have valid YAML frontmatter (validated on write).
- All internal links must reference existing pages (validated on write, broken links
  logged for lint repair).

**Page frontmatter (agent-first):**

```yaml
---
title: Event-Driven Architecture
type: concept # entity | concept | summary | synthesis | decision | how-to
sources:
  - raw/documents/trading-arch.pdf
  - raw/code/alpaca-readme.md
related:
  - entities/alpaca.md
  - concepts/message-queues.md
  - decisions/chose-redis-streams.md
tags: [architecture, trading, patterns]
source_count: 2 # number of raw sources citing this topic
created: 2026-04-11
last_compiled: 2026-04-11
confidence: high # see confidence scoring rules below
supersedes: # pages this replaces (for evolving knowledge)
---
```

**Confidence scoring rules:**

- **high** — primary source (official docs, firsthand experience, authored content) OR
  3+ corroborating sources
- **medium** — secondhand source (blog post, summary, single reference) OR 1-2 sources
- **low** — informal/unverified (conversation snippet, speculation, undated content)
- **contradicted** — conflicts with another source; both claims preserved with
  citations, contradiction noted explicitly in page body

Confidence upgrades when new corroborating sources are ingested. Confidence downgrades
when source age exceeds 1 year without reconfirmation.

**Tiered index design:**

The root `index.md` is a meta-index — category summaries and pointers to sub-indexes.
This stays small regardless of total page count.

```markdown
# Cortex Index

Last updated: 2026-04-11 Total pages: 247 | Sources ingested: 523

## Categories

| Category  | Pages | Sub-index                                   |
| --------- | ----- | ------------------------------------------- |
| Entities  | 42    | [entities/\_index.md](entities/_index.md)   |
| Concepts  | 65    | [concepts/\_index.md](concepts/_index.md)   |
| Summaries | 89    | [summaries/\_index.md](summaries/_index.md) |
| Synthesis | 23    | [synthesis/\_index.md](synthesis/_index.md) |
| Decisions | 15    | [decisions/\_index.md](decisions/_index.md) |
| How-to    | 13    | [how-to/\_index.md](how-to/_index.md)       |

## Recent Activity (last 10)

- 2026-04-11: Ingested `raw/documents/trading-arch.pdf` -> 3 new, 7 updated
- 2026-04-10: Lint pass -> fixed 2 contradictions, added 5 cross-references
```

Each sub-index (`entities/_index.md`, etc.) contains one-line entries for its category.
At 100 entries per category, each sub-index is ~8K chars (~2K tokens) — comfortably
within any context budget.

**Query workflow for agents:** Read `index.md` (tiny) -> identify relevant category ->
read that category's `_index.md` -> read specific pages. Two hops, bounded cost.

**log.md structure:**

```markdown
# Operation Log

## 2026-04-11T14:32:00Z — INGEST [complete]

Source: raw/documents/trading-arch.pdf Content hash: a3f8c2... Pages created:
concepts/event-driven-arch.md, entities/alpaca.md, how-to/set-up-alpaca.md Pages
updated: entities/redis.md, concepts/message-queues.md Token usage: ~45K input, ~8K
output Summary: Technical architecture document covering trading system design
patterns...

## 2026-04-11T10:00:00Z — LINT [complete]

Scope: entities/ (32 pages scanned) Issues found: 2 Fixed: concepts/rest-api.md
contradicted concepts/graphql.md on "preferred API style" Fixed: entities/vercel.md had
stale deployment limits
```

### Layer 3: Schema

`schema.md` is designed as a **droppable prompt** — copy-paste it into any LLM agent and
it becomes a knowledge maintainer. It contains:

- Frontmatter specification (required fields, valid types, confidence scoring rules)
- Page size limits and splitting strategy
- Naming conventions (kebab-case filenames, title-case titles)
- Cross-referencing rules (when to create links, when to create new pages vs update)
- **Redaction rules** (strip API keys, tokens, passwords, account numbers, SSNs, and
  third-party PII before writing knowledge pages — raw sources may contain sensitive
  data)
- Ingest workflow (step-by-step with validation gates)
- Query workflow (tiered index navigation -> page reads -> synthesis)
- Lint workflow (scoped contradiction detection, not global pairwise)
- Merge rules (what to do when two sources contradict)
- Confidence scoring criteria and upgrade/downgrade triggers
- Supersession rules (new claims explicitly replacing old ones)

This file is handed to the LLM at the start of any Cortex operation.

### Relationship to OpenClaw Librarian Memory

The existing librarian skill manages **conversation-derived memories** — things learned
during chat sessions, organized into `memory/decisions/`, `memory/learning/`, etc.

Cortex manages **compiled knowledge from all sources** — documents, transcripts, notes,
captures, etc.

**Ownership boundary:**

- `memory/*.md` (top-level) — owned by librarian, conversation-derived
- `memory/cortex/` (symlink) — owned by cortex skill, source-compiled
- No overlap. The librarian never writes into `cortex/`. Cortex never writes outside it.
- An agent reading memory sees both: recent conversation context (librarian) and deep
  compiled knowledge (cortex). They complement, not compete.

### OpenClaw Integration

Each OpenClaw instance symlinks Cortex's knowledge layer into its memory path:

```
~/openclaw/memory/
  cortex/ -> <cloud-storage-path>/cortex/knowledge/    <- symlink (read-only)
  MEMORY.md                                             <- add pointer to cortex/index.md
```

One line added to each instance's `MEMORY.md`:

```markdown
- [Cortex](cortex/index.md) — compiled knowledge base from all personal sources
```

The agent discovers Cortex through the existing memory path. No new tooling needed for
reads — agents already know how to navigate memory files.

**Symlink validation:** Every cortex operation checks that the symlink target exists and
is readable before proceeding. If broken: "Cortex symlink target
`<path>/cortex/knowledge/` does not exist. Run `cortex setup` to reconfigure, or check
that cloud storage is running."

### Setup Per Machine

A setup script (`skills/cortex/cortex setup`) handles:

1. **Detect cloud storage** — scan for Dropbox path, then Google Drive paths. If
   multiple found, prompt for selection. If none found, error with actionable message.
2. **Validate permissions** — check detected path is writable.
3. **Initialize store** — create directory structure if first machine.
4. **Handle existing symlink** — if `memory/cortex` already exists, warn and confirm
   before overwriting. If it points to the correct target, skip.
5. **Create symlink** — `ln -s <cloud-path>/cortex/knowledge/ ~/openclaw/memory/cortex`
6. **Update MEMORY.md** — add cortex index pointer if not present. Create MEMORY.md if
   absent.
7. **Store config** — write `~/.config/cortex/config` with resolved paths.
8. **Init git** — `git init` the store if not already tracked.

```bash
# Example config file (~/.config/cortex/config)
CORTEX_STORE_PATH=~/Dropbox/cortex
CORTEX_RAW_PATH=~/Dropbox/cortex/raw
CORTEX_KNOWLEDGE_PATH=~/Dropbox/cortex/knowledge
CORTEX_SCHEMA_PATH=~/Dropbox/cortex/schema.md
CLOUD_PROVIDER=dropbox
WRITER_MACHINE=true                    # false for read-only machines
```

**API key:** Sourced exclusively from `ANTHROPIC_API_KEY` environment variable. Never
stored in config files. The skill errors with "Set ANTHROPIC_API_KEY environment
variable to use ingest/query/lint operations" if missing.

## Operations

### Ingest

Triggered when new raw files are added. Single-writer: only the designated writer
machine runs ingest.

```
cortex ingest [path]              # Ingest specific file or all new files in raw/
cortex ingest --bulk raw/notes/   # Bulk ingest an entire directory
```

**Write lock protocol:**

1. Check `knowledge/.lock` — if exists and less than 30 minutes old, abort with message
   showing which machine holds the lock.
2. Create `knowledge/.lock` with machine hostname + timestamp.
3. Perform ingest.
4. Remove `knowledge/.lock` on completion (or on error).

**Ingest workflow:**

1. Acquire write lock
2. Read `schema.md` for conventions (including redaction rules)
3. Read the raw source file; compute content hash
4. Check `.ingest-state.md` — skip if this hash was already ingested
5. Write "pending" entry to `.ingest-state.md`
6. **Pass 1 — Extract:** Identify entities, concepts, and topics from source
7. **Pass 2 — Targeted update:** Read only the relevant sub-index and matched existing
   pages (bounded context load)
8. Write/update knowledge pages with frontmatter validation after each write
9. Update relevant `_index.md` sub-indexes
10. Update `knowledge/index.md` category counts
11. Mark entry "complete" in `.ingest-state.md` with hash and timestamp
12. Append to `knowledge/log.md` with token usage
13. Release write lock
14. Git commit changes (auto-commit per ingest for rollback capability)

**Token budget per ingest:** Schema (~2K) + source (variable) + relevant sub-index (~2K)

- matched pages (~10-20K) = target <50K input tokens per ingest. Large sources (>20K
  tokens) get chunked.

**Idempotency:** Every step is create-or-update. If ingest crashes and reruns, the
content hash check (step 4) catches completed ingests. Pending entries with no
corresponding pages get cleaned up by lint.

**Sensitive file exclusion:** Bulk ingest skips files matching: `.env`, `.ssh/`,
`.aws/`, `credentials*`, `*.pem`, `*.key`, `*.p12`, `secret*`. Configurable via
`~/.config/cortex/config`.

### Query

Any agent with Cortex symlinked can query by reading files. For a dedicated query:

```
cortex query "What trading APIs have I evaluated?"
```

**Query workflow:**

1. Validate symlink target exists
2. Read `knowledge/index.md` (meta-index) to identify relevant categories
3. Read relevant `_index.md` sub-indexes
4. Read matched pages (cap at 10 pages per query to bound context)
5. Synthesize answer with citations to raw sources
6. If the answer reveals a useful new synthesis, file it as a new knowledge page

### Lint

Self-healing health check. Run weekly or after bulk ingests.

```
cortex lint                    # Incremental (pages modified since last lint)
cortex lint --full             # Full scan (expensive, with cost warning)
cortex lint --section entities # Check just entities
```

**Lint workflow (incremental by default):**

1. Acquire write lock
2. Scan modification timestamps — select pages changed since last lint + their direct
   neighbors (pages sharing `related` links)
3. Check for contradictions **within the scoped set** (not global O(n^2))
4. Check for stale dates (source mtime > summary compile date)
5. Find orphan pages (no incoming links from any \_index.md)
6. Find missing cross-references (shared tags/entities not linked)
7. Verify source references still exist in `raw/`
8. Detect and resolve cloud sync conflict files (`*conflict*`, `*(1)*`)
9. Validate all frontmatter YAML in scoped pages
10. Update confidence scores based on source count and freshness
11. Fix all found issues
12. Append results to `knowledge/log.md`
13. Release write lock
14. Git commit changes

**Full lint** scans all pages. Displays estimated token cost before proceeding and
requires confirmation.

**Rebuild index:** `cortex rebuild-index` regenerates all `_index.md` files and
`index.md` from scanning knowledge pages and their frontmatter. Recovery path for
corrupted indexes.

### Bulk Import (Initial Setup)

For the first run, existing cloud storage files need bulk ingestion:

```
cortex ingest --bulk ~/Dropbox/Documents/ --estimate  # Show cost estimate only
cortex ingest --bulk ~/Dropbox/Documents/              # Run with confirmation
cortex ingest --bulk ~/Dropbox/Documents/ --budget 5   # Stop after $5 spent
```

The bulk import:

- Enumerates all files, filters to supported types (md, txt, pdf, html, json, png, jpg)
- Skips sensitive file patterns (see exclusion list above)
- Computes content hashes, skips already-ingested files via `.ingest-state.md`
- **Estimates cost** before starting (file count x average tokens x API pricing)
- Requires confirmation above $1 estimated cost
- Respects `--budget` cap, pausing when reached
- Processes in batches with exponential backoff on rate limits
- Isolates per-file errors (log failure, continue to next file)
- Shows progress: `[47/523] Ingesting trading-arch.pdf... 3 new pages, 7 updated`
- Fully resumable via `.ingest-state.md` hash tracking
- Git commits after each batch (not each file) for manageable history

## Skill Design

**Directory:** `skills/cortex/`

**Files:**

- `SKILL.md` — metadata, triggers, documentation
- `cortex` — Python UV script implementing all operations

**Commands:**

- `cortex setup` — detect cloud storage, init store, create symlinks
- `cortex ingest [path]` — compile raw sources into knowledge
- `cortex ingest --bulk <dir>` — bulk import with cost estimation
- `cortex query "<question>"` — search and synthesize from knowledge
- `cortex lint` — incremental self-healing health check
- `cortex lint --full` — full scan with cost confirmation
- `cortex rebuild-index` — regenerate all indexes from page frontmatter
- `cortex status` — show store stats (page counts, last ingest, last lint)

**Implementation:** Standalone UV script (Python 3.11+, inline dependencies). The script
handles setup/status/bulk orchestration/locking/validation. The actual ingest/query/lint
operations delegate to the LLM (Claude) via the Anthropic API — the script provides the
schema and file contents, the LLM decides what knowledge pages to create/update.

**API key:** `ANTHROPIC_API_KEY` env var only. Never stored in config or script.

## Graduated Search Strategy

The system starts simple and adds search infrastructure only when needed:

| Scale          | Search method                       | Infrastructure           |
| -------------- | ----------------------------------- | ------------------------ |
| <500 pages     | Tiered indexes + grep               | None (built-in)          |
| 500-2000 pages | Add qmd (BM25 hybrid search)        | Single binary, no server |
| 2000+ pages    | Consider embeddings + vector search | Evaluate Khoj or similar |

The threshold to upgrade is: **when agents consistently fail to find relevant pages via
index navigation + grep.** Don't pre-optimize.

## Cross-Storage Sync

Cortex lives in ONE cloud storage provider per machine.

**Recommended approach:** Pick one canonical storage (Dropbox preferred). Machines with
only Google Drive either:

- Install Dropbox free tier (simplest)
- Use rclone to mount the Dropbox folder
- Use rclone bisync to mirror just the `cortex/` folder between providers

The setup script detects what's available. The system works with any path — only the
symlink target changes per machine.

**Write safety:** Single-writer architecture means only one machine is configured with
`WRITER_MACHINE=true`. Other machines consume knowledge read-only. This eliminates cloud
sync conflict risk for knowledge pages. (Raw sources can be added from any machine —
they're immutable, so conflicts are impossible.)

## Versioning and Rollback

The store is git-tracked. The cortex skill auto-commits after each operation:

```
git commit -m "ingest: trading-arch.pdf -> 3 new, 7 updated"
git commit -m "lint: fixed 2 contradictions in entities/"
```

This provides:

- Full history of knowledge evolution
- Rollback for bad LLM compilations (`git revert`)
- Diffable changes (see exactly what an ingest or lint changed)
- Independent of cloud storage version history (which varies by provider)

Raw sources in `raw/` are gitignored (large, binary). Only `knowledge/` and `schema.md`
are tracked.

## Automation

**Recommended: fswatch with debounce** for automatic ingest when new files appear in
`raw/`:

```bash
fswatch -0 --event Created raw/ | xargs -0 -I {} cortex ingest {}
```

With a debounce window (5 seconds) to batch rapid file additions. Only on the writer
machine. This supports the natural workflow: drop a file via Web Clipper, ask about it 2
minutes later.

Manual ingest remains available for bulk operations or when automation is paused.

## What This Enables

Once running, any OpenClaw instance (or Claude Code session) with the symlink can:

- **Answer questions from compiled knowledge** — "What did I learn about X?" navigates
  the tiered index, finds relevant pages, synthesizes with citations
- **Pull context for tasks** — "Build a trading dashboard" finds design inspiration,
  past architecture decisions, preferred tools from Cortex
- **Self-improve over time** — each ingest adds knowledge, each lint pass fixes gaps,
  knowledge compounds
- **Share context across agents** — all instances see the same knowledge, so a meeting
  transcript on one machine is available to a coding agent on another

## Resolved Design Decisions

These were open questions, now resolved based on review:

1. **Media handling:** Use vision models for images/screenshots/diagrams. Extract text
   from PDFs. Every media file gets a summary page so agents can find it without loading
   the binary.
2. **Deduplication:** Content hash on ingest. Same file re-dropped is skipped. Same
   _topic_ from different sources gets merged into the existing page with the new source
   added to the `sources` list and confidence potentially upgraded.
3. **Privacy/redaction:** Schema includes mandatory redaction rules. The LLM strips
   credentials, tokens, account numbers, and third-party PII during compilation. Raw
   sources stay as-is (they're the source of truth), but knowledge pages are sanitized.
4. **Obsidian:** Optional viewer. Web Clipper is useful for dropping captures into
   `raw/`. Graph view is nice for occasional human exploration. But Cortex is
   agent-first — it works identically without Obsidian installed.
5. **Automation:** fswatch with debounce on the writer machine. Not cron (misses the
   "drop and ask" workflow).
