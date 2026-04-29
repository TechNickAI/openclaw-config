---
name: apple-photos
version: 0.2.0
description:
  Query, inspect, and export photos from the macOS Apple Photos library using osxphotos.
  Find photos by person, album, keyword, or date range. Export candidates for curation
  workflows.
triggers:
  - apple photos
  - photos library
  - find photos
  - export photos
  - photo of me
  - photos of
  - face clusters
  - people in photos
  - profile pictures
metadata:
  openclaw:
    emoji: "\U0001F4F7"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/apple-photos
    category: integrations
    platform: macos
    os: [darwin]
    requires:
      bins: [osxphotos]
---

# Apple Photos

Query and export from the macOS Photos library. Three subcommands cover the typical
workflow: discover people, search with filters, export to a folder.

## Subcommands

### people

List face clusters with photo counts.

```bash
apple-photos people --limit 30
apple-photos people --include-unknown
```

### query

Search photos by person, album, keyword, and date range.

```bash
apple-photos query --person "<NAME>" --after 2026-01-01 --limit 20 --json
apple-photos query --album "Favorites" --newest-first --limit 10
apple-photos query --keyword "vacation" --before 2025-12-31
```

Filters: `--person`, `--album`, `--keyword`, `--after`, `--before`, `--favorite`,
`--edited`, `--movies`, `--newest-first`

### export

Copy matched photos to a destination folder. Never modifies the Photos library.

```bash
apple-photos export ~/Desktop/exports --person "<NAME>" --after 2026-01-01 --limit 30
apple-photos export ~/Desktop/exports --album "Favorites" --edited
apple-photos export ~/Desktop/exports --person "<NAME>" --dry-run
```

Add `--edited` to prefer edited versions. Use `--dry-run` to preview without copying.

## Workflow

1. Run `people` to confirm the face label exists.
2. Run `query` to search and preview matches.
3. Run `export` to copy a batch to a working folder.
4. Use vision or local tools to score, sort, crop, and retouch the exports.

## Guardrails

- Never modify the Photos library directly — export copies only.
- Face labels can be incomplete. Spot-check results.
- For large exports, start with `--dry-run` or a narrow date range.

## Fallbacks

- If face labels are incomplete, query by album/date and review manually.
- If a photo only exists in Google Photos or shared links, use browser retrieval.
- If the user wants deep retouching, export first, then use external editors.

## Requirements

- macOS with Photos.app
- `osxphotos` Python library (auto-installed via UV on first run)
