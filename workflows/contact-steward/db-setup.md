# Contact Steward — Database Setup & Migration

Only read this file when AGENT.md directs you here — during first-time setup, legacy
migration, or schema upgrade. Do not read on normal runs.

## Prerequisites

Verify sqlite3 is available:

```bash
which sqlite3
```

If not found:

- **macOS:** Already installed at `/usr/bin/sqlite3`. If missing: `brew install sqlite`
- **Ubuntu/Debian:** `sudo apt install sqlite3`

## Schema Version History

| Version | Changes                                                                                    | Date       |
| ------- | ------------------------------------------------------------------------------------------ | ---------- |
| 1       | Initial schema — processed table with platform, contact_id, status, last_checked, metadata | 2026-03-29 |

## Target Schema (Current: Version 1)

```sql
CREATE TABLE IF NOT EXISTS schema_meta (
  id INTEGER PRIMARY KEY CHECK(id = 1),
  version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS processed (
  platform TEXT NOT NULL,
  contact_id TEXT NOT NULL,
  status TEXT NOT NULL,
  last_checked INTEGER NOT NULL,
  metadata TEXT,
  PRIMARY KEY (platform, contact_id)
);

CREATE INDEX IF NOT EXISTS idx_status ON processed(status);
CREATE INDEX IF NOT EXISTS idx_last_checked ON processed(last_checked);
```

### Column Reference

| Column       | Type    | Description                                                           |
| ------------ | ------- | --------------------------------------------------------------------- |
| platform     | TEXT    | `whatsapp`, `imessage`, or `quo`                                      |
| contact_id   | TEXT    | Phone number, JID, or platform-specific identifier                    |
| status       | TEXT    | One of: `classified`, `asked_human`, `skipped`, `enriched`, `error`   |
| last_checked | INTEGER | Unix timestamp of last processing                                     |
| metadata     | TEXT    | Brief notes (e.g., "enriched from WhatsApp", "spam — pizza delivery") |

### Status Values

- **classified** — Identity resolved, contact added to platform
- **asked_human** — Couldn't resolve, asked human, awaiting response
- **skipped** — Spam, business, automated, or human didn't reply
- **enriched** — Existing contact updated with new details
- **error** — Processing failed, will retry next run

## Scenario: New Installation (No Database)

Run the initialization SQL from AGENT.md. It's inline there and fully idempotent. You
don't need this file for new installations — AGENT.md has everything.

## Scenario: Legacy Migration (processed.md exists)

If `processed.md` exists from a previous version, migrate its entries to SQLite.

**Step 1:** Run the initialization SQL from AGENT.md to create the database.

**Step 2:** Read `processed.md`. It's natural language grouped by platform. Each entry
has an identifier, optional name, date, and status. For each entry, insert:

```bash
sqlite3 workflows/contact-steward/processed.db \
  "INSERT OR IGNORE INTO processed (platform, contact_id, status, last_checked, metadata) \
   VALUES ('<platform>', '<contact_id>', '<status>', <unix_timestamp>, '<notes>')"
```

Use `INSERT OR IGNORE` to skip duplicates safely. Map the natural language statuses to
the standard values: classified, asked_human, skipped, enriched, error.

**Step 3:** Verify by comparing counts:

```bash
sqlite3 workflows/contact-steward/processed.db \
  "SELECT platform, COUNT(*) FROM processed GROUP BY platform"
```

**Step 4:** Archive the old file:

```bash
mv workflows/contact-steward/processed.md workflows/contact-steward/processed.md.migrated
```

Keep `.migrated` for a few weeks as a safety net, then delete it.

## Scenario: Schema Upgrade (Version Mismatch)

When AGENT.md's `schema_version` is higher than the database's version, apply migrations
in order. Each migration block is idempotent — safe to re-run.

### Migrating from Version 0 → 1 (No schema_meta table)

If `SELECT version FROM schema_meta` errors (table doesn't exist), the database was
created before version tracking. The processed table likely already exists with the
correct columns. Run:

```bash
sqlite3 workflows/contact-steward/processed.db <<'SQL'
CREATE TABLE IF NOT EXISTS schema_meta (
  id INTEGER PRIMARY KEY CHECK(id = 1),
  version INTEGER NOT NULL
);
INSERT OR REPLACE INTO schema_meta (id, version) VALUES (1, 1);
CREATE INDEX IF NOT EXISTS idx_status ON processed(status);
CREATE INDEX IF NOT EXISTS idx_last_checked ON processed(last_checked);
SQL
```

<!-- Future migrations go here, labeled clearly:
### Migrating from Version 1 → 2
Description of what changed and why.
```sql
ALTER TABLE processed ADD COLUMN new_column TEXT;
UPDATE schema_meta SET version = 2;
```
-->
