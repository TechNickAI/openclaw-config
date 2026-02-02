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

API key from platform.parallel.ai. Configure via gateway.

## What Users Ask

- "Search the web for recent developments in quantum computing"
- "What's the latest on the OpenAI drama?"
- "Extract the main content from this article"
- "Pull the text from this PDF URL"
- "Research competitor pricing for X"

## Capabilities

- Web search with AI-optimized excerpts
- Content extraction from any URL (handles JS, PDFs)
- Multi-query research for comprehensive coverage

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

## Notes

- Search API returns contextual excerpts, not just links
- Extract handles JavaScript-rendered pages (SPAs, dynamic content)
- PDFs automatically converted to text
- Rate limits apply — check docs.parallel.ai
