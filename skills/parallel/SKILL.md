---
name: parallel
version: 0.1.0
description: Web search and content extraction via Parallel.ai API
triggers:
  - web search
  - search the web
  - research online
  - extract content
  - extract from URL
  - pull content from
  - scrape page
  - get page content
metadata:
  openclaw:
    emoji: "🔍"
    apiKey:
      env: PARALLEL_API_KEY
      getFrom: https://platform.parallel.ai
---

# Parallel.ai 🔍

Web search and content extraction optimized for AI agents. Better than Brave/Perplexity
for research tasks. Handles JS-heavy pages, PDFs, and complex content.

## Setup

1. Create account at https://platform.parallel.ai
2. Generate API key from dashboard
3. Add to environment: `export PARALLEL_API_KEY="your-key"`

## What Users Ask

- "Search the web for recent developments in quantum computing"
- "What's the latest on the OpenAI drama?"
- "Extract the main content from this article"
- "Pull the text from this PDF URL"
- "Research competitor pricing for X"

## Capabilities

- **Web Search** — AI-optimized search returning relevant excerpts with sources
- **Content Extraction** — Clean text from any URL (handles JS rendering, PDFs, paywalls)
- **Research Queries** — Multi-query search for comprehensive coverage

## Commands

```bash
parallel search "query"              # Web search
parallel search "query" --limit N    # Limit results (default: 5)
parallel extract <url>               # Extract content from URL
parallel extract <url> --full        # Include full page content
parallel help                        # Usage info
```

## Response Data

### Search Results
- `title` — Page title
- `url` — Source URL
- `excerpt` — Relevant text snippet
- `domain` — Source domain

### Extracted Content
- `url` — Source URL
- `title` — Page title
- `content` — Extracted text (markdown formatted)
- `excerpt` — Key excerpts if requested

## Notes

- Search API is optimized for AI research — returns contextual excerpts, not just links
- Extract handles JavaScript-rendered pages (SPAs, dynamic content)
- PDFs are automatically converted to text
- Rate limits apply — check https://docs.parallel.ai for current limits
