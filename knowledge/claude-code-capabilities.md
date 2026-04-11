# Claude Code Capabilities

Complete inventory of Claude Code features relevant to replacing or supplementing a
persistent AI assistant service. Written to support migration analysis from OpenClaw.

**Last updated:** 2026-04-09

**Important caveat:** Claude Code is evolving rapidly. Some features described here are
in research preview or recently launched. Verify current status before making
architectural decisions.

---

## Architecture

Claude Code is an **interactive CLI tool** — you invoke it, it does work, it exits. It
is not a daemon or persistent service.

- Runs in a terminal session (or IDE extension, desktop app, web app)
- Session-scoped: state exists during the conversation, cleared on exit
- Powered by Claude models (Opus, Sonnet, Haiku) via Anthropic API or subscription
- Available as: CLI (`claude`), VS Code extension, JetBrains plugin, desktop app
  (Mac/Windows), web app (claude.ai/code)

**Key architectural property:** Claude Code is designed for software engineering tasks.
It's a coding assistant, not a general-purpose AI gateway. Features like scheduling and
channels extend it beyond coding, but the core design assumes a developer at the
keyboard.

---

## Scheduled Tasks and Remote Triggers

Claude Code offers three scheduling mechanisms:

### Remote Triggers (Cloud-Hosted)

- Created via web UI (`claude.ai/code/scheduled`) or `/schedule` CLI skill
- Run on **Anthropic's cloud infrastructure** — not on your local machine
- Standard cron expressions for scheduling
- Each run is a fresh session (no state carried between runs)
- Can access MCP servers configured for the task
- Tied to a GitHub repository for context
- Auto-expire after 7 days of inactivity (configurable)

**Strengths:** No machine to keep running, Anthropic manages infrastructure, survives
your laptop being off.

**Limitations:** Cannot access local files, local APIs, or SSH into machines. No model
fallback chains. No consecutive error tracking. No timeout management beyond the
platform default. State between runs requires external storage (GitHub, API calls).

### Desktop App Scheduled Tasks

- Visual scheduling in the Claude Code desktop app
- Runs locally on your machine
- Persists while the app is running — **lost if the app closes or machine restarts**
- More like a fancy cron UI than a service

### /loop Skill (Session-Scoped)

- Runs a prompt on a repeating interval within the current session
- `claude --loop 10m "your prompt"` — repeats every 10 minutes
- Dies when the session ends
- Useful for watching deployments, polling CI, monitoring builds
- Not a cron replacement — it's a temporary polling tool
- Auto-expires after 3 days

---

## Channels

Claude Code can receive messages from external platforms:

### Native Slack Integration

- Claude appears as a bot in Slack workspaces
- Responds to @mentions and DMs
- Coding-focused — designed for development team collaboration
- Runs within the Claude Code subscription (no additional API cost)

### Channels Feature (Research Preview)

- Supported platforms: **Telegram, Discord, iMessage** (as of early 2026)
- Activated via `--channels` flag when starting Claude Code
- **Session-scoped** — channels only work while the Claude Code process is running
- No built-in daemon mode — requires wrapping in `tmux`/`screen` or a process manager
  for persistence
- WhatsApp is NOT natively supported (community MCP connectors exist)
- Still in research preview — breaking API changes expected

### Community/Third-Party Bridges

- Various community projects bridge Claude Code to additional platforms
- MCP servers exist for some messaging platforms
- These are not officially supported and may break with updates

**Key gap vs OpenClaw:** Claude Code channels require an active process. There's no
"start and walk away" mode. You either keep a terminal open or wrap it in a process
manager yourself. OpenClaw's channels are built into a daemon that the OS keeps alive.

---

## Hooks

Event-driven automation that fires during Claude Code sessions:

### Hook Types

| Hook         | When It Fires                  | Can Modify Behavior                        |
| ------------ | ------------------------------ | ------------------------------------------ |
| PreToolUse   | Before Claude executes a tool  | Yes — block, modify inputs, inject context |
| PostToolUse  | After a tool executes          | Yes — validate, transform, notify          |
| SessionStart | When session begins or resumes | Yes — inject environment, load context     |

### Configuration

Hooks live in settings files (project or global):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "your-script.sh" }]
      }
    ]
  }
}
```

### Key Properties

- **Persistent across sessions** — configured once, apply to all future sessions
- **Synchronous execution** — shell commands that block until complete
- **Can trigger external actions** — send notifications, call APIs, run scripts
- Hook commands receive tool inputs via environment variables
- Exit codes control behavior: 0 = success, 2 = block with error

### Relevance for Migration

Hooks are powerful for local automation but only fire during active sessions. They can't
replace OpenClaw's always-on event processing. However, combined with scheduled tasks,
hooks could automate some workflow-like behaviors.

---

## Memory and Persistence

Claude Code persists information across sessions through several mechanisms:

### CLAUDE.md Hierarchy

- `~/.claude/CLAUDE.md` — global instructions (all projects)
- `<project>/CLAUDE.md` — project-level instructions (checked into git)
- `<project>/CLAUDE.local.md` — local overrides (gitignored)
- Loaded automatically at session start
- This is the primary mechanism for persistent identity and instructions

### Auto-Memory

- Claude saves notes to `~/.claude/projects/<project>/memory/` automatically
- Triggered by learning something important about the user, project, or preferences
- Persists across sessions within the same project
- Memory index (MEMORY.md) loaded into every conversation
- Individual memory files loaded on relevance

### Session Summaries

- Claude auto-compresses conversation history as context fills up
- Previous conversation context is available when starting a new session
- Not perfect recall — lossy compression

### What's Missing vs OpenClaw

- **No vector search** — Claude Code memory is file-based, not semantically searchable
- **No SQLite backend** — no structured queries over memory
- **No tiered architecture** — no automatic promotion from observations to durable
  knowledge
- **No shared memory across projects** — each project has its own memory silo (though
  global CLAUDE.md spans all)
- **No embeddings infrastructure** — no LM Studio integration, no semantic recall

---

## Skills and Plugins

### Skills

- Reusable knowledge bundles that extend Claude Code's capabilities
- Invoked via `/skill-name` syntax
- Can be defined per-project or globally
- Contain prompts, instructions, and tool patterns
- Lightweight — typically 30-50 tokens of instruction

### Plugins

- Shareable bundles of skills + hooks + MCP servers + commands
- Installable from a marketplace or local paths
- Can add new capabilities to Claude Code (e.g., the `ai-coding-config` plugin)
- Plugins define hooks that fire automatically

### Relevance for Migration

OpenClaw skills (standalone Python scripts) are structurally different from Claude Code
skills (prompt/instruction bundles). However, Claude Code can invoke Python scripts via
Bash, and MCP servers can wrap external tools. The skill _content_ is portable; the
_invocation mechanism_ changes.

---

## MCP Servers (Model Context Protocol)

MCP extends Claude Code with external tool access:

- **Protocol:** Standardized interface for tools, resources, and prompts
- **Available servers:** GitHub, Slack, Sentry, Postgres, Figma, Playwright, filesystem,
  and many more
- **Configuration:** Per-project or global in settings files
- **Lazy loading:** Tools are loaded on-demand to save context
- **Custom servers:** You can build your own MCP server for any API or tool

### Relevance for Migration

MCP servers could replace some OpenClaw skills (e.g., an MCP server wrapping the
Parallel API, or Fireflies API). The difference: OpenClaw skills are invoked by the
gateway daemon; MCP servers are invoked during Claude Code sessions. For scheduled
tasks, remote triggers can use MCP servers configured for the task.

---

## CLI Automation

Claude Code can be invoked programmatically:

| Command                      | Purpose                                |
| ---------------------------- | -------------------------------------- |
| `claude --message "prompt"`  | Send a single message, get response    |
| `claude --print "prompt"`    | Non-interactive mode, prints response  |
| `claude --loop 10m "prompt"` | Repeat prompt on interval              |
| `claude --channels`          | Start with messaging channel listeners |
| `claude --resume`            | Resume previous session                |

These commands enable scripting Claude Code into cron jobs, shell scripts, or other
automation. A cron job could run `claude --message "check the inbox"` on a schedule —
but each invocation starts a fresh session without memory of the previous run (unless
`--resume` is used).

---

## Agent SDK

Anthropic provides SDKs for building custom agents:

### SDK Capabilities

- Available in Python and TypeScript
- Wraps the Anthropic API with agent-specific features (tool calling, sessions, loops)
- Sessions can be persisted to disk and resumed later
- Supports custom tools and MCP server integration
- Open-source, self-hosted

### Managed Agents API

- Cloud-hosted agent infrastructure via `/v1/agents` and `/v1/sessions`
- Long-running conversation threads that persist across API calls
- Sessions resumable indefinitely via `session_id`
- Webhook support for receiving external events
- Anthropic manages infrastructure

### Relevance for Migration

The Agent SDK is the most viable path to building an "OpenClaw-like" service on top of
Anthropic's infrastructure. You could build a custom gateway using the SDK that handles
messaging channels, scheduling, and memory. But this means building a new gateway, not
using Claude Code directly.

---

## Background Agents and Worktrees

### Subagents

- Claude Code can dispatch work to subagents within a session
- Each subagent runs with its own context, returns results
- Useful for parallel research, code review, implementation

### Git Worktrees

- Agents can work in isolated git worktrees
- Changes are committed to separate branches
- Worktree is auto-cleaned if no changes are made

### Relevance for Migration

These are development features, not personal-assistant features. They're valuable for
the coding use case but don't map to OpenClaw's workflow system.

---

## Identity and Configuration

Claude Code's identity system maps partially to OpenClaw's:

| OpenClaw     | Claude Code         | Notes                                      |
| ------------ | ------------------- | ------------------------------------------ |
| AGENTS.md    | CLAUDE.md (project) | Direct equivalent — workspace instructions |
| SOUL.md      | CLAUDE.md (global)  | Personality goes in global instructions    |
| USER.md      | CLAUDE.md (global)  | User profile in global instructions        |
| BOOT.md      | SessionStart hook   | Can inject context on session start        |
| HEARTBEAT.md | No equivalent       | No periodic check system                   |
| TOOLS.md     | CLAUDE.local.md     | Machine-specific config                    |
| IDENTITY.md  | No equivalent       | No quick-reference card mechanism          |

**Key difference:** OpenClaw's identity templates are separate files with distinct
purposes. Claude Code collapses everything into the CLAUDE.md hierarchy. This works for
a single user on a single machine, but doesn't scale to fleet deployment where each
instance needs different personality/identity files.

---

## Multi-User / Fleet Considerations

Claude Code is designed as a **single-user tool:**

- One Claude Code instance per user account
- No built-in multi-tenant support
- No fleet management or remote deployment features
- `CLAUDE_CONFIG_DIR` can point to different config directories (workaround for per-user
  isolation, not an official multi-user feature)

**For fleet use cases,** the options are:

1. Run separate Claude Code instances per user on separate machines (same topology as
   OpenClaw fleet, but more manual management)
2. Use the Agent SDK to build a multi-tenant service (effectively building a new
   OpenClaw)
3. Use Claude Managed Agents API for cloud-hosted multi-user agents (offloads
   infrastructure to Anthropic)

---

## Cost Model

- **Claude Code Pro subscription:** Included with Claude Pro ($20/month) — covers
  interactive use and some scheduled tasks
- **API usage beyond subscription:** Per-token pricing applies
- **Remote triggers:** Run within subscription quota
- **Agent SDK / Managed Agents:** Standard API pricing (per-token)

**vs OpenClaw:** OpenClaw uses API keys directly (pay per token). The Max subscription
previously provided unlimited tokens — now that it's gone, OpenClaw and Claude Code are
on similar pricing (per-token), but Claude Code's subscription covers interactive use
that would otherwise be API-billed.
