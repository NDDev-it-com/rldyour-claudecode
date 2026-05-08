# Claude Code Project Memory — rldyour-claude

Personal Claude Code plugin marketplace by `rldyourmnd`. Cross-tool overview, source-of-truth manifests, plugin layers, and CLI commands live in `./AGENTS.md`. This file (`./.claude/CLAUDE.md`) is the Claude Code-native deep memory: subagent matrix, hook canon, skill-listing budget, frontmatter conventions, and Don't/Done rules. Both files are agent-only, live on the `fullrepo` branch, and are excluded from `main` via `.git/info/exclude`.

<!-- Maintainer notes (HTML comments are stripped from Claude's context per CC v2.1.72): keep this file under 200 lines per Anthropic official guidance (code.claude.com/docs/en/memory). Project CLAUDE.md re-injects after /compact and is inherited by every subagent — every line is a recurring token cost. Update only when discovering durable Claude Code-specific facts; cross-tool facts belong in AGENTS.md. -->

## Plugins And Components

```
rldyour-mcps         transport     0 skills • 0 cmds • 0 agents • 0 hooks  • .mcp.json (13 pinned servers)
rldyour-serena-mcp   semantic      2 skills • 0 cmds • 1 agent  • 4 hooks
rldyour-flow         SDLC          7 skills • 5 cmds • 6 agents • 3 hooks  • 7 scripts • 7 references
rldyour-explore      research      2 skills • 1 cmd  • 1 agent  • 0 hooks
rldyour-security     security      2 skills • 1 cmd  • 0 agents • 0 hooks
rldyour-browser      browser       3 skills • 0 cmds • 0 agents • 0 hooks
rldyour-design       design        5 skills • 1 cmd  • 0 agents • 0 hooks
rldyour-lsps         lsp           4 skills • 0 cmds • 0 agents • 0 hooks  • 2 scripts • 3 references
rldyour-rules        rules         7 skills • 1 cmd  • 0 agents • 0 hooks  • 6 references
```

Total: 32 skills, 9 slash commands, 8 subagents. Slash commands (SDLC + tool-routing), plugin dependency graph, MCP transport detail, and fullrepo branch policy are listed in `./AGENTS.md`.

## Subagent Frontmatter Matrix

Required fields for plugin-shipped subagents: `name`, `description`. Plugin-shipped subagents silently ignore `hooks`, `mcpServers`, and `permissionMode` — copy to `.claude/agents/` if those are needed.

| Agent | model | effort | maxTurns | color | role |
|---|---|---|---|---|---|
| flow-architecture-review | sonnet | high | 36 | blue | boundaries, dependency direction, public API |
| flow-quality-review | sonnet | high | 36 | green | correctness, edge cases, lifecycle |
| flow-consistency-review | sonnet | high | 36 | purple | naming, style, project conventions |
| flow-integration-review | sonnet | high | 36 | orange | cross-module sync, contracts |
| flow-verification-review | sonnet | high | 36 | pink | tests, LSP, browser/server evidence |
| flow-security-review | sonnet | high | 42 | red | defensive auth/authz/secrets/injection |
| ry-explore | opus[1m] | max | 90 | cyan | deep multi-source research, `context: fork` |

All reviewer agents declare `disallowedTools: [Edit, Write, NotebookEdit]` (read-only). Generous `maxTurns` (×3 of naive limit) compensates MCP-rich toolsets that consume turns on tool plumbing — Serena + Context7 + DeepWiki + Grep eat 5-8 turns before useful work begins.

| flow-memory-sync (rldyour-serena-mcp) | sonnet | high | 36 | yellow | fact-only Serena memory sync — invoked from main session via Agent tool with diff payload |

`flow-memory-sync` is a plugin-shipped subagent with narrow tool access (Serena memory tools — `write_memory`/`edit_memory`/`delete_memory`/`rename_memory` — plus read-only `Read`/`Grep`/`Glob`/`Bash`; `disallowedTools: [Edit, Write, NotebookEdit]`). Anti-hallucination contract enforced via body: source-of-truth hierarchy code > tests > git diff > existing memories; citation required per claim; removal-first principle for unverifiable claims; `Last commit: <HEAD_SHA>` line mandatory in every touched memory; `commit_serena_knowledge.sh` runs internally; final JSON report. Stop hook advisory (`stop_memory_sync.sh`) points at this subagent rather than asking the main session to inline-edit memories. Plugin agents are loaded at session start — restart Claude Code after creating or editing the agent file before invoking via `subagent_type: "rldyour-serena-mcp:flow-memory-sync"`.

## Hooks Lifecycle

Two plugins coordinate hooks. `flow.stop_post_task_sync.sh` waits for `serena_current=true` from the Serena Stop hook before running. Loop guard: `.serena/.flow_sync_marker` writes a fingerprint of (HEAD, dirty files, ahead/behind, branch, Serena freshness). If `stop_hook_active=true` and the fingerprint matches, the hook allows stop.

| Event | Owner | Script | Timeout |
|---|---|---|---|
| UserPromptSubmit | rldyour-serena-mcp | `hooks/user_prompt_submit.sh` | 5s |
| PreToolUse:Bash | rldyour-serena-mcp | `hooks/prepare_auto_sync.sh` | 5s |
| PostToolUse:Bash | rldyour-serena-mcp | `hooks/mark_sync_required.sh` | 5s |
| PostToolUse:Bash | rldyour-flow | `hooks/post_tool_use_commit_advice.sh` | 5s |
| SessionStart | rldyour-flow | `hooks/session_start_context.sh` | 5s |
| Stop | rldyour-serena-mcp | `hooks/stop_memory_sync.sh` | 10s |
| Stop | rldyour-flow | `hooks/stop_post_task_sync.sh` | 10s |

All hooks are advisory — emit `hookSpecificOutput.additionalContext`, exit `0` on errors, never block tool use. Skip flags during local debugging: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT=1` (SessionStart), `RLDYOUR_SKIP_FLOW_COMMIT_ADVICE=1` (PostToolUse:Bash flow), `RLDYOUR_SKIP_STOP_GATES=1` (both Stop hooks), `RLDYOUR_SKIP_FLOW_SYNC=1` (flow Stop only), `RLDYOUR_SKIP_SERENA_SYNC=1` (Serena Stop only).

## Skill Listing Budget

Per-entry combined `description` + `when_to_use` cap: **1,536 chars** (raised from 250 in CC v2.1.128). Aggregate budget defaults to **1% of context window** with 8,000-char fallback. With 32+ skills the default budget truncates tail-end descriptions and Claude can no longer auto-trigger them.

User-side fix in `~/.claude/settings.json`:

```json
{
  "skillListingBudgetFraction": 0.03,
  "skillListingMaxDescChars": 1536
}
```

Both keys added in CC v2.1.129+. `skillListingBudgetFraction` is a decimal fraction in `(0, 1]`. Runtime override: `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var (raw chars). `skillOverrides` map (`"on" | "name-only" | "user-invocable-only" | "off"`) does **not** affect plugin-shipped skills — manage those through `/plugin`.

Plugin-side levers used in this repo:
- `disable-model-invocation: true` on `skills/ry-deploy/SKILL.md` and `skills/ry-newp/SKILL.md` — slash-only, freeing budget for auto-triggered skills.
- `allowed-tools` on 10 skills with explicit toolsets — eliminates per-call permission prompts during work without touching listing budget.

## Hook Events Canon

Claude Code v2.1.x publishes **30 canonical hook events** (per `code.claude.com/docs/en/hooks`). Five handler types: `command`, `http`, `mcp_tool` (v2.1.118+), `prompt`, `agent`. Prompt/agent handlers spawn LLM evaluation or full subagent verification — used for runtime validation when shell hooks aren't expressive enough. `InstructionsLoaded` event (CC v2.1.69+) fires when CLAUDE.md or `.claude/rules/*.md` files are loaded into context.

Hierarchy precedence (highest → lowest): managed policy → plugin hooks (force-enabled exempt from `allowManagedHooksOnly`) → `.claude/settings.json` → `.claude/settings.local.json` → `~/.claude/settings.json` → skill/agent frontmatter.

Per Anthropic guidance: put guardrails in hooks, not in CLAUDE.md prose. CLAUDE.md is delivered as a user message after the system prompt — it is context, not enforced configuration.

## Engineering Conventions

- Russian user-facing communication; English repository artifacts. Skill `description` fields are Russian-leading (English keywords appended).
- Skill frontmatter: `name`, `description` (recommended). Optional: `when_to_use`, `argument-hint`, `allowed-tools`, `disable-model-invocation`, `user-invocable`, `model`, `effort`, `paths`, `context: fork`, `agent`.
- Agent frontmatter: `name`, `description`, `model`, `effort`, `maxTurns`, `disallowedTools`, `color`. Optional: `tools`, `skills`, `memory`, `background`, `isolation`, `initialPrompt`.
- `model: opus[1m]` is the canonical bracketed form for Opus 4.7 1M context (used by `ry-explore`); requires CC **v2.1.111+**.
- `model: sonnet` is the canonical short form for reviewer subagents.
- Slash command frontmatter: `description`, `argument-hint`, optional `context: fork` and `agent: <name>`. Bare `model:` on a slash command is silently ignored without `context: fork` — pair them or delegate via `agent:`.
- Conventional Commits, ≤72 char subjects, atomic commits per logical unit. Separate commits for source / docs / Serena knowledge when it improves history clarity.
- All MCP server versions are pinned (stdio with `==X.Y.Z`; HTTP servers by URL).
- `allowed-tools` may mix built-in tool names (`Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash`, `WebSearch`, `WebFetch`) and MCP wildcards (`mcp__plugin_rldyour-mcps_<server>__*`) in the same skill — pattern is validated by `claude plugin validate` and used by `serena-code-workflow`, `serena-memory-sync`, `lsp-routing`, `serena-lsp-integration`, `figma-to-code`, `ry-design`, `design-system-implementation`.

## Claude Code-specific Diagnostics

Beyond `claude plugin validate` and bootstrap commands documented in `./AGENTS.md`:

- `/mcp` — transport status. `/doctor` — env health (skill-listing truncation warnings appear here). `/status` — session state. `/context` — token-budget breakdown by category. `/hooks` — active hooks. `/memory` — CLAUDE.md, CLAUDE.local.md, and rules files loaded.
- `python3 plugins/rldyour-flow/scripts/instruction_docs_state.py --json` — whether AGENTS.md and `.claude/CLAUDE.md` need review.
- `python3 plugins/rldyour-flow/scripts/flow_post_task_state.py` — fingerprint of dirty state, Serena freshness, branch cleanup candidates.
- `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py` — Serena memory match-vs-HEAD state.

## Don't

- Don't reduce this file to `@AGENTS.md` import — `@imports` don't reduce token cost (Anthropic memory docs); content loads at launch either way. Keep separation: AGENTS.md cross-tool, CLAUDE.md Claude Code-deep.
- Don't grow either file past 200 lines — Anthropic empirical evidence: adherence drops, instructions get lost.
- Don't put hard guardrails in CLAUDE.md prose ("ALWAYS X", "NEVER Y") — they are advisory user-message context. Use hooks for enforcement.
- Don't add `.mcp.json` outside `rldyour-mcps`. Don't add `hooks.json` outside `rldyour-flow` or `rldyour-serena-mcp`. Don't add a new plugin without confirming domain boundary.
- Don't commit `AGENTS.md`, `.claude/**`, `.serena/project.yml`, `.serena/memories/**` to `main` — fullrepo only.
- Don't write Serena memories from `ry-init` unless explicitly requested or a Stop/stale-memory hook required it.
- Don't force-push `main`; `--force-with-lease` is allowed only for `fullrepo`.
- Don't auto-generate this file or AGENTS.md from code analysis — ETH Zurich research (cited in Augment 2026 guide) shows LLM-generated context files reduce task success 0.5-2% with 20-23% token overhead.

## Done Criteria

- All touched manifests pass `claude plugin validate`.
- `git status` clean of non-agent files; agent-only paths excluded via the `# >>> rldyour fullrepo agent-only files >>>` block in `.git/info/exclude`.
- `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json` shows `tracked_agent_paths: []` on `main`.
- `fullrepo` republished after any agent-only change.
- Plugin component cross-references (skills referencing scripts/agents/references) actually exist on disk.
- Reviewer subagents (when invoked) produce read-only findings, never edit files.
- This file stays under 200 lines.

<!-- Living-doc note: when discovering a non-obvious Claude Code-specific fact during work, propose a CLAUDE.md edit in the same change. Treat CLAUDE.md like code — review when behavior drifts, prune regularly, test by observing whether Claude's behavior actually shifts. -->
