# Migration Analysis: OpenClaw → Claude Code

Gap analysis, capability mapping, workarounds, and recommendations for migrating
OpenClaw functionality to Claude Code.

**Last updated:** 2026-04-09

**Context:** Anthropic discontinued the Max subscription that provided unlimited API
access for OpenClaw. With per-token pricing now the only option, the question is whether
Claude Code (included with Pro subscription) can absorb some or all of OpenClaw's
workload — both for Nick's personal instance (Cora) and for fleet users (Ali, Gil,
Julianna, Thomas).

---

## Executive Summary

Claude Code can absorb **a meaningful portion** of OpenClaw's functionality, but not all
of it. The viability depends heavily on which capabilities matter most:

- **Scheduling and automation** — Claude Code's remote triggers and `/loop` cover basic
  cron use cases. The gap is in stateful workflows that accumulate knowledge between
  runs.
- **Memory and identity** — CLAUDE.md hierarchy is a strong replacement for OpenClaw's
  template system. Auto-memory covers some of the tiered memory architecture. The gap is
  semantic search.
- **Messaging channels** — This is the biggest gap. Claude Code's channels feature is
  session-scoped and limited to Telegram/Discord. WhatsApp and iMessage require the
  gateway or a custom bridge.
- **Fleet management** — The fleet commands already run from Claude Code (this repo's
  `.claude/commands/`). Fleet management is portable.
- **Skills** — Most OpenClaw skills are API wrappers that work anywhere Python runs.
  Easily portable.

**The fundamental tension:** OpenClaw is a daemon (always on, accepts events). Claude
Code is a CLI (invoked, does work, exits). This isn't an absolute blocker — remote
triggers, channels, and process managers can bridge the gap — but it changes the
operational model significantly.

---

## Capability Mapping Matrix

| OpenClaw Capability              | Claude Code Equivalent              | Gap Level | Notes                                                            |
| -------------------------------- | ----------------------------------- | --------- | ---------------------------------------------------------------- |
| **Always-on gateway**            | No equivalent (CLI, session-based)  | High      | Can be partially bridged with remote triggers + process managers |
| **WhatsApp channel**             | No native support                   | High      | Requires custom bridge or keeping gateway for WhatsApp only      |
| **iMessage channel**             | Channels feature (research preview) | Medium    | Exists but session-scoped, requires active process               |
| **Telegram channel**             | Channels feature (research preview) | Medium    | Works but session-scoped, not daemon-managed                     |
| **Slack channel**                | Native Slack integration            | Low       | Claude Code's Slack support is solid                             |
| **Cron runner (basic)**          | Remote triggers                     | Low       | Standard cron expressions, cloud-hosted                          |
| **Cron runner (advanced)**       | No equivalent                       | High      | No fallback chains, cooldown tracking, error counting            |
| **Model fallback chains**        | No equivalent                       | High      | Claude Code uses one model per session                           |
| **Provider routing**             | No equivalent                       | High      | No Anthropic/OpenRouter/etc routing                              |
| **Memory (MEMORY.md)**           | CLAUDE.md + auto-memory             | Low       | Good functional equivalent                                       |
| **Memory (daily observations)**  | Auto-memory                         | Medium    | Different structure, no tiered promotion                         |
| **Memory (vector search)**       | No equivalent                       | High      | No embeddings, no semantic search                                |
| **Memory (SQLite)**              | No equivalent                       | High      | No structured query over memory                                  |
| **Workflow state (agent_notes)** | No equivalent between runs          | High      | Remote triggers are stateless per-run                            |
| **Workflow learning loop**       | No equivalent                       | High      | No correction → pattern → promotion pipeline                     |
| **Skills (Python scripts)**      | Bash tool / MCP servers             | Low       | Scripts run fine; invocation mechanism changes                   |
| **Identity templates**           | CLAUDE.md hierarchy                 | Low       | Direct mapping, different file structure                         |
| **SOUL.md personality**          | Global CLAUDE.md                    | Low       | Works well for single user                                       |
| **BOOT.md startup**              | SessionStart hook                   | Low       | Good equivalent                                                  |
| **HEARTBEAT.md**                 | /loop or remote triggers            | Medium    | Can approximate with scheduled checks                            |
| **Fleet management**             | Already runs from Claude Code       | None      | Fleet commands are in this repo                                  |
| **Health monitoring**            | Remote triggers (basic)             | Medium    | Can poll, but no auto-remediation framework                      |
| **Security audits**              | Remote triggers + SSH               | Medium    | Can run, but no baseline/drift system                            |
| **Dashboard (web UI)**           | No equivalent                       | Medium    | No real-time monitoring UI                                       |
| **Multi-agent coordination**     | Subagents within session            | Medium    | Different model — session-scoped, not cross-gateway              |
| **Notification routing**         | Hooks + external scripts            | Medium    | Can notify, but no two-lane routing framework                    |

### Gap Level Summary

- **None / Low:** 8 capabilities (easily portable or already working)
- **Medium:** 8 capabilities (partial coverage, workarounds needed)
- **High:** 8 capabilities (significant gaps, major workarounds or not possible)

---

## Deep Dive: What Maps Cleanly

### Fleet Management — Already Done

The fleet commands (`/fleet`, `/update-model`, `/fleet-announce`) already run from
Claude Code via this repo's `.claude/commands/`. Fleet management is SSH-based and
doesn't depend on the OpenClaw gateway. **This requires zero migration work.**

### Skills — Trivially Portable

OpenClaw skills are standalone scripts. They run via `uv run` with inline dependencies.
Claude Code can invoke them via the Bash tool or wrap them as MCP servers. The only
change is invocation context:

- OpenClaw: gateway invokes skill during conversation or cron job
- Claude Code: user or scheduled task invokes skill during session

**Migration path:** No changes to skill code. Just invoke differently.

### Identity and Personality — Good Mapping

OpenClaw's template system maps to Claude Code's CLAUDE.md hierarchy:

| OpenClaw  | Claude Code         | Migration                                   |
| --------- | ------------------- | ------------------------------------------- |
| AGENTS.md | CLAUDE.md (project) | Copy workspace instructions                 |
| SOUL.md   | CLAUDE.md (global)  | Merge personality into global instructions  |
| USER.md   | CLAUDE.md (global)  | Merge user profile into global instructions |
| BOOT.md   | SessionStart hook   | Convert startup routine to hook script      |
| TOOLS.md  | CLAUDE.local.md     | Copy machine-specific config                |

**Trade-off:** OpenClaw's separation (SOUL.md vs USER.md vs AGENTS.md) is cleaner for
fleet deployment where each instance needs different files. Claude Code's CLAUDE.md
collapses everything, which works for single-user but makes fleet per-user customization
harder.

### Basic Scheduling — Covered

For simple "run this prompt at this time" jobs, Claude Code's remote triggers work:

- Standard cron expressions
- Cloud-hosted (no machine to keep running)
- MCP servers available for tool access

Jobs like "daily briefing at 8 AM" or "check for updates at 9 AM" translate directly.

### Slack Integration — Better in Claude Code

Claude Code's native Slack integration is arguably superior to OpenClaw's for
development teams. It's designed for Slack, well-maintained, and included in the
subscription.

---

## Deep Dive: Partial Coverage

### Telegram and iMessage Channels

Claude Code's channels feature supports Telegram and iMessage, but:

- **Session-scoped** — requires an active Claude Code process
- **No built-in daemon mode** — you'd need to wrap it in tmux/screen + launchd/systemd
- **Research preview** — breaking changes expected

**Workaround:** Run `claude --channels` as a launchd service on the Mac Minis. This
approximates OpenClaw's always-on channel behavior but with more fragile process
management. You'd need:

1. A launchd plist that starts `claude --channels` on boot
2. Restart logic for crashes
3. CLAUDE.md configuration for the instance's personality/context
4. Monitoring to detect when the process dies

**Assessment:** Doable but more operational overhead than OpenClaw's built-in daemon.

### Health Monitoring

Remote triggers can run health check prompts on a schedule. But OpenClaw's health check
system includes:

- Auto-remediation (restart gateway, clear logs, fix stuck jobs)
- Consecutive error tracking with escalation thresholds
- Silent success model
- Integration with the gateway's internal state

**Workaround:** Write a health check script that remote triggers invoke. Use external
state storage (a file in a GitHub repo, or a simple API) to track consecutive errors.
Send notifications via hook scripts.

**Assessment:** The basic polling works. The auto-remediation and state tracking require
custom engineering.

### Workflow Approximation (Stateless)

Simple workflows that don't need state between runs can use remote triggers:

- Daily briefing (calendar-steward) — just runs a prompt with today's context
- LLM usage report — queries data and formats a report
- Update checker — checks for new versions

**What breaks:** Workflows that accumulate knowledge (`agent_notes.md`), learn from
corrections (learning-loop), or maintain processing state (email-steward tracking which
emails were already handled).

### Multi-Agent Coordination

OpenClaw supports cross-gateway agent coordination via Slack @-mentions. Claude Code has
subagents within a session but no cross-instance coordination.

**Workaround:** Use Slack as the coordination bus (same pattern as OpenClaw's
`multi-agent-slack-bus.json`). Each Claude Code instance monitors a Slack channel and
responds to @-mentions. This actually works similarly to the OpenClaw model.

---

## Deep Dive: Real Gaps

### WhatsApp

Claude Code has no WhatsApp support — not in channels, not in MCP, not in any official
integration. WhatsApp requires a linked device with persistent WebSocket connection,
which requires a daemon.

**Workarounds:**

1. **Keep OpenClaw running just for WhatsApp** — use Claude Code for everything else
2. **Build a WhatsApp bridge** — a small Node.js service that receives WhatsApp messages
   and forwards them to Claude Code via `claude --message` or the Agent SDK
3. **Use a third-party WhatsApp API** (Twilio, MessageBird) with an MCP server
4. **Accept the loss** — if WhatsApp isn't critical for fleet users

**Assessment:** None of these are great. Option 1 defeats the purpose of migrating.
Option 2 means building a mini-gateway. Options 3-4 depend on use case.

### Stateful Workflows (Learning Loop)

OpenClaw's most distinctive feature is workflows that get smarter over time:

- Corrections are captured in structured format
- Patterns are detected (2+ similar corrections)
- Validated patterns promote to MEMORY.md or agent_notes.md
- Old patterns decay and get pruned

Claude Code has no equivalent. Auto-memory captures some learnings, but there's no
systematic correction → pattern → promotion pipeline.

**Workaround:** Build a `learning-loop` equivalent as a Claude Code plugin that:

- Stores corrections in a file
- Runs pattern detection on a schedule (via remote trigger)
- Updates CLAUDE.md with validated learnings

**Assessment:** The architecture is possible but would require significant custom
development. And it wouldn't be as tightly integrated as OpenClaw's version.

### Model Routing and Fallback Chains

OpenClaw's provider routing is critical for cost optimization and reliability:

- Role-based aliases select models by capability tier
- Fallback chains try alternative providers on failure
- Cooldown tracking avoids hammering rate-limited providers
- Per-job model specification allows cost optimization

Claude Code uses one model per session (the one your subscription provides). There's no
fallback, no provider routing, no cost-tier selection.

**Workaround:** For remote triggers, you can specify which model to use. But there's no
automatic failover. If the model is down, the trigger fails.

**Assessment:** This is a real operational reliability gap. In production, provider
outages happen regularly. Without fallback chains, you'll see more failures.

### Persistent Memory with Semantic Search

OpenClaw's memory system includes vector search via embeddings (LM Studio locally,
OpenAI fallback). This enables semantic recall: "What did Nick say about the auth
migration?" finds relevant memories even without exact keyword matches.

Claude Code's memory is file-based with no semantic search. You can grep for keywords,
but can't do similarity search.

**Workaround:** Build an MCP server that provides vector search over a memory database.
This is technically feasible — MCP servers can wrap any API. But you'd need to maintain
the embedding infrastructure separately.

### Advanced Cron Features

OpenClaw's cron runner tracks per-job health:

- Consecutive error count (escalate after N failures)
- Timeout management (configurable per-job, kills long-running jobs)
- Last run time and duration
- Model/provider used for each run
- Admin notification on state changes

Remote triggers have none of this. A trigger runs or it doesn't. You don't get
consecutive error tracking, timeout configuration, or health dashboards.

**Workaround:** Build external monitoring. A webhook from remote triggers could post
results to a monitoring service. But this is building infrastructure.

---

## Workarounds and Hybrid Approaches

### Hybrid: OpenClaw for Channels, Claude Code for Everything Else

Keep a minimal OpenClaw gateway running **only** for WhatsApp and iMessage channels.
Move all scheduling, workflows, fleet management, and development work to Claude Code.

**Pros:** Preserves the hardest-to-replace capability (always-on messaging) **Cons:**
Still running the gateway, still paying for the API tokens it uses

### Hybrid: Claude Code + Custom Bridge Service

Build a lightweight bridge service (not a full gateway) that:

- Receives messages from WhatsApp/Telegram/iMessage
- Invokes Claude Code via `claude --message` or the Agent SDK
- Sends responses back to the originating channel

**Pros:** Much simpler than OpenClaw's full gateway; single-purpose **Cons:** Still
custom code to maintain; loses conversation threading; each message is a fresh context
(no memory of the conversation unless `--resume` is used)

### Hybrid: Agent SDK as the New Gateway

Use the Claude Agent SDK to build a purpose-built replacement for OpenClaw that:

- Runs as a daemon (you build the process management)
- Connects to messaging channels (you build the adapters)
- Uses Anthropic's session API for conversation persistence
- Leverages MCP servers for tool integration

**Pros:** Modern architecture, official SDK, maintained by Anthropic **Cons:** You're
building a new OpenClaw. This is months of work.

### Full Migration: Accept the Losses

Move entirely to Claude Code, accepting that:

- WhatsApp/iMessage require being at the keyboard (or a tmux wrapper)
- Workflows lose their learning loop
- No model fallback chains
- No health dashboard

**Pros:** Simplest operational model; one subscription covers everything **Cons:**
Significant capability regression for fleet users

---

## Fleet Implications

The migration calculus is different for Nick vs fleet users:

### For Nick (Cora)

Nick is a developer who's already running Claude Code. The integration is natural:

- He's at the keyboard most of the day (channels work during sessions)
- Fleet management already runs from Claude Code
- His skills and workflows can be invoked directly
- CLAUDE.md already has his personality and preferences

**What he loses:** Always-on WhatsApp/iMessage when AFK, background cron jobs running
while sleeping, auto-remediation of issues overnight.

### For Fleet Users (Ali, Gil, Julianna, Thomas)

Fleet users are NOT developers. They interact with their AI via messaging channels. They
don't open terminals. They don't run Claude Code.

**Running Claude Code "for them"** means:

- SSH into their machine, start a Claude Code session with `--channels`
- Configure CLAUDE.md with their personality and preferences
- Hope the process doesn't die (or build restart automation)
- No per-user customization UI — everything is file-based

**What they lose:** The seamless "text your AI anytime" experience. Instead, they'd have
a less reliable channel connection that depends on a tmux session staying alive. They
also lose the dashboard, health monitoring, and any workflow that needs state between
runs.

**Alternative for fleet users:** Run Claude Code remote triggers for their scheduled
tasks (briefings, reports, reminders) but keep a minimal OpenClaw gateway for messaging.
Or migrate them to Claude's Slack integration if they use Slack.

---

## Cost Analysis

### Current Model (OpenClaw + API)

- Per-token API pricing for all gateway usage
- Nick's fleet: ~6 machines, each running scheduled jobs + handling messages
- No subscription fees for the gateway itself (open source)
- Cost is proportional to usage (busy instances cost more)

### Claude Code Pro Model

- $20/month per Claude Pro subscription per user
- Includes interactive use and remote triggers within quota
- API usage beyond quota at standard per-token pricing
- For fleet: $20/month × N users (if each gets their own subscription)

### Hybrid Model

- Keep OpenClaw for channels (API costs for message handling)
- Use Claude Code subscription for development, fleet management, and some scheduling
- Potentially lower total cost if channel volume is low

### Agent SDK / Managed Agents Model

- Standard API per-token pricing for all usage
- Cloud hosting costs if using Managed Agents
- Development cost to build the replacement

**Bottom line on cost:** The Max subscription made OpenClaw essentially free to run
(unlimited tokens). Without it, both OpenClaw and Claude Code cost per-token for actual
AI work. Claude Code's Pro subscription adds value if you're already using it for
development. The incremental cost of running cron jobs through remote triggers (within
subscription quota) could be lower than running them through the API directly.

---

## Recommendation

### What to Migrate to Claude Code

1. **Fleet management** — Already there. No changes needed.
2. **Simple scheduled tasks** — Daily briefings, update checks, reports. Remote triggers
   handle these well.
3. **Development workflows** — Code review, debugging, implementation. Claude Code's
   strength.
4. **Slack interactions** — Claude Code's native Slack support is excellent.
5. **Identity and configuration** — Migrate templates to CLAUDE.md hierarchy.

### What to Keep on OpenClaw (or Build a Bridge For)

1. **WhatsApp and iMessage channels** — No viable Claude Code replacement. Keep the
   gateway running for these, or build a thin bridge service.
2. **Stateful workflows** — email-steward, contact-steward, learning-loop. These need
   state between runs that remote triggers can't provide.
3. **Model fallback chains** — Critical for reliability. Keep for production workloads.
4. **Health monitoring with auto-remediation** — The auto-fix capability can't be
   replicated with simple scheduled prompts.

### What to Build

1. **Channels wrapper** — If migrating Telegram, wrap `claude --channels` in a launchd
   service with restart logic and monitoring.
2. **State persistence layer** — If migrating stateful workflows, build an MCP server or
   file-based state system that remote triggers can read/write.
3. **Monitoring** — External health monitoring for Claude Code processes and remote
   triggers, since there's no built-in observability.

### What to Accept as Lost (or Defer)

1. **Semantic memory search** — Not available in Claude Code. Build an MCP server later
   if needed, or wait for Anthropic to add it.
2. **Learning loop** — The correction → pattern → promotion pipeline doesn't translate.
   Redesign it as a Claude Code plugin if it's valuable enough to justify the work.
3. **Dashboard** — No web UI for monitoring. Use logs and Slack notifications instead.
4. **Advanced cron health tracking** — Consecutive error counting, timeout management.
   Accept simpler monitoring or build external tooling.

---

## Open Questions

These need answers before committing to a migration path:

1. **How much does WhatsApp actually matter for fleet users?** If they primarily use
   Telegram or Slack, the gap narrows significantly.
2. **How stable are Claude Code channels in practice?** The research preview label is
   concerning — is it stable enough for fleet deployment?
3. **What's the actual token cost of OpenClaw's current workload?** This determines
   whether Claude Code's subscription quota covers the load or if it's API-priced
   anyway.
4. **Are fleet users willing to switch to Slack?** Claude Code's Slack integration is
   the strongest channel option.
5. **How much does the learning loop actually improve outcomes?** If corrections are
   rare, the loss of the learning loop may not matter in practice.
6. **What's Anthropic's roadmap for channels and daemon mode?** If always-on channels
   are coming soon, waiting may be the best strategy.
