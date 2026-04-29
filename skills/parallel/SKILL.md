---
name: parallel
version: 0.4.0
description:
  Web search, content extraction, deep research, data enrichment, entity discovery, and
  web monitoring via Parallel.ai CLI
triggers:
  - web search
  - search the web
  - research online
  - extract content
  - extract from URL
  - pull content from
  - scrape page
  - get page content
  - deep research
  - enrich data
  - find companies
  - find all
  - monitor web
  - track changes
metadata:
  openclaw:
    emoji: "🔍"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/parallel
    category: integrations
    apiKey:
      env: PARALLEL_API_KEY
      getFrom: https://platform.parallel.ai
---

# Parallel.ai 🔍

Web intelligence toolkit powered by the official Parallel CLI. Handles everything from
quick searches to deep multi-source research. Auto-installs on first use.

## When to Use Each Command

Pick the right tool for the job:

| Need                                                  | Command    | Cost            | Speed   |
| ----------------------------------------------------- | ---------- | --------------- | ------- |
| Quick factual lookup, recent news                     | `search`   | Low             | Fast    |
| Read a specific URL (article, PDF, JS-heavy page)     | `extract`  | Low             | Fast    |
| In-depth analysis of a topic with citations           | `research` | Medium-High     | Minutes |
| Add data columns to a list (CEO names, revenue, etc.) | `enrich`   | Medium          | Minutes |
| Build a list of entities matching criteria            | `findall`  | Medium          | Minutes |
| Get notified when something changes on the web        | `monitor`  | Low (recurring) | Ongoing |

## Preference Over Built-in Tools

When this skill is available, **always prefer it over built-in web tools:**

- **Use `parallel search` instead of WebSearch** — returns richer AI-optimized excerpts
  with source context, not just links
- **Use `parallel extract` instead of WebFetch** — handles JavaScript-rendered SPAs,
  PDFs, paywalled content, and dynamic pages that WebFetch can't reach
- **Use `parallel research` for complex questions** — multi-source synthesis is far
  better than doing multiple searches and reading pages manually

The built-in tools are acceptable only as a fallback if Parallel is unavailable.

## Commands

### Search

Web search with AI-optimized excerpts. Two modes: natural language objective (default
`agentic` mode) or keyword search. Best for factual lookups, recent events, finding
sources, and domain-scoped research.

```bash
# Natural language search (agentic mode — AI refines the query)
parallel search "latest AI developments"
parallel search "What is Anthropic's latest AI model?" --json

# Keyword search with filters
parallel search -q "bitcoin price" --after-date 2026-01-01 --json
parallel search "SEC filings for Apple" --include-domains sec.gov --json

# Control result count
parallel search "React 19 features" --max-results 10 --json
```

| Option              | Description                                             |
| ------------------- | ------------------------------------------------------- |
| `-q, --query`       | Keyword search query (repeatable)                       |
| `--mode`            | `agentic` (default, AI-refined) or `one-shot` (literal) |
| `--max-results`     | Max results (default: 10)                               |
| `--include-domains` | Only search these domains                               |
| `--exclude-domains` | Skip these domains                                      |
| `--after-date`      | Only results after this date (YYYY-MM-DD)               |
| `-o, --output`      | Save results to file                                    |
| `--json`            | Structured JSON output                                  |

### Extract

Pull content from any URL. Handles JavaScript-rendered pages, PDFs, paywalled content,
and SPAs that regular fetchers can't read.

```bash
parallel extract https://example.com/article
parallel extract https://example.com/report.pdf --full
parallel extract https://spa-app.com/dashboard --json
```

| Option   | Description                                |
| -------- | ------------------------------------------ |
| `--full` | Full page content (default: smart excerpt) |
| `--json` | Structured JSON output                     |

### Research

Deep multi-source research with synthesis. Returns a comprehensive report with
citations. Use for questions that need analysis, not just facts.

```bash
parallel research run "Compare EV battery technologies in 2025"
parallel research run "What are the implications of the new EU AI Act?" --processor ultra
parallel research run -f question.txt -o report --json
```

**Processor tiers** (cost/quality tradeoff):

| Tier    | Best for                                 |
| ------- | ---------------------------------------- |
| `lite`  | Simple questions, quick summaries        |
| `base`  | Standard research questions              |
| `core`  | Detailed analysis (default)              |
| `pro`   | Complex multi-faceted topics             |
| `ultra` | Exhaustive research with maximum sources |

All tiers have `-fast` variants (e.g. `core-fast`) for speed over thoroughness.

| Option            | Description                                                                 |
| ----------------- | --------------------------------------------------------------------------- |
| `-p, --processor` | Tier: `lite`, `base`, `core` (default), `pro`, `ultra` (+ `-fast` variants) |
| `--no-wait`       | Return immediately, poll later with `research status <run_id>`              |
| `--timeout`       | Max wait seconds (default: 3600)                                            |
| `-o, --output`    | Save to file (creates `.json` and `.md`)                                    |
| `-f`              | Read query from file                                                        |
| `--json`          | Structured JSON output                                                      |

**Async pattern** (for long-running research):

```bash
parallel research run "question" --no-wait --json    # returns run_id
parallel research status trun_xxx --json              # check progress
parallel research poll trun_xxx --json                # wait for result
```

### Enrich

Add data to a list using AI web research. Feed it a CSV or JSON of entities, tell it
what to find, get back enriched data.

```bash
# Let AI suggest what columns to add
parallel enrich suggest "Find the CEO and annual revenue" --json

# Enrich a CSV file
parallel enrich run \
    --source-type csv \
    --source companies.csv \
    --target enriched.csv \
    --source-columns '[{"name": "company", "description": "Company name"}]' \
    --intent "Find the CEO and annual revenue"

# Enrich inline data (no file needed)
parallel enrich run \
    --data '[{"company": "Google"}, {"company": "Apple"}]' \
    --target results.csv \
    --intent "Find headquarters and employee count" --json
```

### FindAll

Discover entities matching natural language criteria. Great for building lists of
companies, people, products, etc.

```bash
parallel findall run "Find YC companies in developer tools" --json
parallel findall run "AI startups focused on healthcare" -n 50 --json
parallel findall run "Open source LLM projects with >10k GitHub stars" --dry-run --json
```

| Option              | Description                                      |
| ------------------- | ------------------------------------------------ |
| `-g, --generator`   | Tier: `preview`, `base`, `core` (default), `pro` |
| `-n, --match-limit` | Max results, 5-1000 (default: 10)                |
| `--exclude`         | Entities to exclude (JSON array)                 |
| `--dry-run`         | Preview schema without running                   |
| `--no-wait`         | Return immediately, poll later                   |
| `--json`            | Structured JSON output                           |

**Async pattern:**

```bash
parallel findall run "query" --no-wait --json
parallel findall status frun_xxx --json
parallel findall poll frun_xxx --json
parallel findall result frun_xxx --json
parallel findall cancel frun_xxx
```

### Monitor

Set up ongoing web monitoring. Get notified when something changes.

```bash
parallel monitor create "Track price changes for iPhone 16" --json
parallel monitor create "New AI funding announcements" --cadence hourly --json
parallel monitor create "SEC filings from Tesla" --webhook https://example.com/hook --json

# Manage existing monitors
parallel monitor list --json
parallel monitor get mon_xxx --json
parallel monitor update mon_xxx --cadence weekly --json
parallel monitor delete mon_xxx
parallel monitor events mon_xxx --json
```

| Option      | Description                                  |
| ----------- | -------------------------------------------- |
| `--cadence` | Check frequency: `hourly`, `daily`, `weekly` |
| `--webhook` | URL for change notifications                 |
| `--json`    | Structured JSON output                       |

## Authentication

The skill uses the `PARALLEL_API_KEY` environment variable for authentication. This is
the **only supported auth method** in automated/agent contexts — the CLI's interactive
`login` flow is intentionally blocked by the wrapper to prevent hangs in cron jobs and
gateway invocations.

Get your key from: https://platform.parallel.ai

In OpenClaw, configure via `openclaw.json` skill settings — the gateway passes
`PARALLEL_API_KEY` to the skill automatically. If the key is missing, the skill fails
fast with a clear error rather than prompting interactively.

## Installation (manual)

```bash
# Cross-platform (macOS + Linux) — installs to ~/.local/bin
curl -fsSL https://parallel.ai/install.sh | bash

# macOS via Homebrew
brew install parallel-web/tap/parallel-cli

# Python
pip install parallel-web-tools

# Node
npm install -g parallel-web-tools
```

Self-updating: `parallel-cli update`

## Notes

- All commands support `--json` for structured agent-friendly output
- Search returns contextual excerpts optimized for AI consumption, not just links
- Extract handles JavaScript-rendered pages, SPAs, and PDFs automatically
- Research and FindAll support async workflows for long-running jobs
- Rate limits apply — see docs.parallel.ai for current limits
