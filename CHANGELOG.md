# Changelog

All notable changes to openclaw-config will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-01

### Added

- **Semantic memory search** with vector embeddings
  - LM Studio integration (local, free, recommended)
  - OpenAI API option for those who prefer cloud
  - EmbeddingGemma 300M model for 768-dim vectors
  - Verification test to ensure search works before completing setup
- **Skill versioning** — Each skill now has a version in frontmatter
- **Nightly auto-update** via heartbeat system
- Better install instructions (prompt-style, guides OpenClaw step by step)

### Changed

- **Consolidated setup into openclaw skill** — SETUP.md and SYNC.md absorbed into
  skills/openclaw/SKILL.md
- README Quick Start now has thorough copy-paste instructions
- openclaw skill now handles: setup, status, update, update --force
- VERSION bumped to 0.2.0

### Removed

- SETUP.md (now in openclaw skill)
- SYNC.md (now in openclaw skill)

## [0.1.0] - 2026-02-01

### Added

- Initial release
- Three-tier memory architecture (MEMORY.md, daily logs, deep knowledge)
- Task management system with GitHub-style checkboxes
- Decision-making framework (Bezos doors, certainty thresholds)
- Group chat behavior guidelines
- Heartbeat system for proactive checks
- **Templates:**
  - AGENTS.md — Full operating instructions
  - SOUL.md — AI personality template
  - USER.md — Human profile template
  - TOOLS.md — Local environment notes
  - HEARTBEAT.md — Periodic check config
  - IDENTITY.md — Quick reference card
- **Skills:**
  - limitless — Limitless Pendant lifelogs
  - fireflies — Fireflies.ai meeting transcripts
  - quo — Quo business phone integration
  - openclaw — Meta-skill for config management
- **Scripts:**
  - bootstrap.sh — Initial setup
  - sync.sh — Smart update with conflict handling
  - version-check.sh — Check for updates
- Memory directory structure (people/, projects/, topics/, decisions/)
- 4 criteria for memory extraction (Durability, Uniqueness, Retrievability, Authority)
- Progressive elaboration rules for knowledge evolution
