---
name: librarian
version: 0.5.1
description: >
  DEPRECATED — Use the `cortex` skill instead. Cortex v2 absorbs all librarian
  functionality (memory maintenance, knowledge organization, learning analysis) into a
  unified knowledge compiler. This skill is kept for backwards compatibility but all
  triggers now route to Cortex.
triggers:
  - organize memories
  - clean up knowledge base
  - tidy up memory
  - run the librarian
  - memory maintenance
  - organize my notes
  - review daily files
metadata:
  openclaw:
    emoji: "\U0001F4DA"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/librarian
    category: knowledge
    deprecated: true
    replacement: cortex
---

# Librarian — DEPRECATED

**This skill has been replaced by [Cortex](../cortex/SKILL.md).**

Cortex v2 absorbs all librarian functionality:

- Memory maintenance → Cortex MEMORY.md routing table
- Knowledge organization → Cortex category indexes + entity pages
- Learning analysis → Cortex `learning/` directory (corrections → patterns → how-to)
- Progressive elaboration → Cortex handles organically as sources accumulate
- Daily journals → Cortex `daily/` directory

If you're seeing this, invoke Cortex instead:

```
cortex lint          # Health-check and organize
cortex status        # See current state
```

Or tell the AI: "organize my knowledge base" — Cortex will handle it.
