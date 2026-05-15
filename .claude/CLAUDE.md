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

| flow-memory-sync (rldyour-serena-mcp) | sonnet | high | 36 | yellow | fact-only Serena memory sync, invoked by orchestrator when Stop hook advisory triggers |

`flow-memory-sync` is a plugin-shipped subagent with narrow tool access (Serena memory tools — `write_memory`/`edit_memory`/`delete_memory`/`rename_memory` — plus read-only `Read`/`Grep`/`Glob`/`Bash`; `disallowedTools: [Edit, Write, NotebookEdit]`). Anti-hallucination contract enforced via body: source-of-truth hierarchy code > tests > git diff > existing memories; citation required per claim; removal-first principle for unverifiable claims; `Last commit: <HEAD_SHA>` line mandatory in every touched memory; `commit_serena_knowledge.sh` runs internally; final JSON report. Memory files are a numbered knowledge base: `CORE-01-INDEX.md` is the map and topics use `AREA-01-SLUG.md` (`SERENA-01-MEMORY-SYNC.md`, `TECHDEBT-01-NOW.md`). Invocation pattern: when the Serena Stop hook emits its advisory, the orchestrator (model in main session, or `flow-post-task-sync` skill workflow step 1) calls `Agent({subagent_type: 'rldyour-serena-mcp:flow-memory-sync', prompt: ...})` with HEAD context — keeping high-blast-radius operations under workflow control rather than letting hooks fire them silently.

## Hooks Lifecycle

Two plugins coordinate hooks. `flow.stop_post_task_sync.sh` derives `serena_current` by calling `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py` before running its own gate. Loop guard: `.serena/.flow_sync_marker` writes a fingerprint of (HEAD, dirty files, ahead/behind, branch, Serena freshness). If `stop_hook_active=true` and the fingerprint matches, the hook allows stop.

| Event | Owner | Script | Timeout |
|---|---|---|---|
| UserPromptSubmit | rldyour-serena-mcp | `hooks/user_prompt_submit.sh` | 5s |
| PreToolUse:Bash | rldyour-serena-mcp | `hooks/prepare_auto_sync.sh` | 5s |
| PostToolUse:Bash | rldyour-serena-mcp | `hooks/mark_sync_required.sh` | 5s |
| PostToolUse:Bash | rldyour-flow | `hooks/post_tool_use_commit_advice.sh` | 5s |
| SessionStart | rldyour-flow | `hooks/session_start_worktree_bootstrap.sh` | 30s |
| SessionStart | rldyour-flow | `hooks/session_start_context.sh` | 5s |
| Stop | rldyour-serena-mcp | `hooks/stop_memory_sync.sh` | 10s |
| Stop | rldyour-flow | `hooks/stop_post_task_sync.sh` | 10s |

Stop hooks are **advisory enforcement gates**, not executors. Pattern: hooks compute machine-readable state, block Stop (`exit 2`) until the orchestrator (`ry-start`, `flow-post-task-sync` skill, model in main session) brings the project to a clean final state. Hooks themselves do **not** push, merge, publish, or delete branches — those are high-blast-radius operations and live in the workflow executor under model judgement.

Sequence:
1. **Serena Stop hook** (`stop_memory_sync.sh`) checks `serena_memory_state.py`. If memories are stale for current HEAD, blocks Stop with an advisory pointing at the `flow-memory-sync` subagent (preferred) or the equivalent Serena workflow (fallback).
2. **Flow Stop hook** (`stop_post_task_sync.sh`) reads `serena_current` from `serena_memory_state.py`, then checks `flow_post_task_state.py`. If git/docs/fullrepo/cleanup state is dirty (uncommitted, ahead of upstream, fullrepo stale, instruction docs need review, merged branches/worktrees not cleaned), blocks Stop with an advisory pointing at the `flow-post-task-sync` skill.
3. Loop guard: `.serena/.sync_marker` and `.serena/.flow_sync_marker` carry fingerprints. If `stop_hook_active=true` and the fingerprint matches, the chain allows Stop without re-running — prevents infinite loops while still forcing real progress between Stops.

The orchestrator (skill / model in main session) does the actual work: invoke `flow-memory-sync` subagent for memories, then run the `flow-post-task-sync` skill which handles checks → atomic commits → push → ff-merge into default branch → push default → fullrepo publish (`--force-with-lease`, only on `fullrepo`) → cleanup merged branches and worktrees.

Skip flags during local debugging: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT=1` (SessionStart context), `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1` (SessionStart worktree bootstrap), `RLDYOUR_SKIP_FLOW_COMMIT_ADVICE=1` (PostToolUse:Bash flow), `RLDYOUR_SKIP_STOP_GATES=1` (both Stop hooks), `RLDYOUR_SKIP_FLOW_SYNC=1` (flow Stop only), `RLDYOUR_SKIP_SERENA_SYNC=1` (Serena Stop only).

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

Claude Code v2.1.x publishes **29 canonical hook events** (per `code.claude.com/docs/en/hooks`). Five handler types: `command`, `http`, `mcp_tool` (v2.1.118+), `prompt`, `agent`. Prompt/agent handlers spawn LLM evaluation or full subagent verification — used for runtime validation when shell hooks aren't expressive enough. `InstructionsLoaded` event (CC v2.1.69+) fires when CLAUDE.md or `.claude/rules/*.md` files are loaded into context.

Hierarchy precedence (highest → lowest): managed policy → plugin hooks (force-enabled exempt from `allowManagedHooksOnly`) → `.claude/settings.json` → `.claude/settings.local.json` → `~/.claude/settings.json` → skill/agent frontmatter.

Per Anthropic guidance: put guardrails in hooks, not in CLAUDE.md prose. CLAUDE.md is delivered as a user message after the system prompt — it is context, not enforced configuration.

## Changelog Adoption (v2.1.133 → v2.1.142)

Verified against `code.claude.com/docs/en/changelog` for v2.1.133-v2.1.142 on 2026-05-15. Current local CC: **v2.1.142** (`$(which claude) --version`).

Adopted:
- v2.1.128 — per-entry skill description cap `1,536` chars, used by all 32 skills.
- v2.1.129 — `skillListingBudgetFraction: 0.03` in user settings; `experimental.{themes,monitors}` wrapper available (we declare neither).
- v2.1.121 — `alwaysLoad: true` on `serena` MCP server.
- v2.1.119 — `claude plugin tag --push` for release tagging (canonical, `<plugin>--v<version>`).
- v2.1.x — `SessionStart` + `WorktreeRemove`/`WorktreeCreate` worktree workflow (added 2026-05-12): `hooks/session_start_worktree_bootstrap.sh` auto-restores agent-only files into a fresh worktree via `fullrepo_sync.py --restore`. `WorktreeCreate` is intentionally NOT used because the worktree path does not yet exist on disk when that event fires — `SessionStart` in the new worktree session is the correct injection point. `scripts/worktree_add.sh` covers the manual `git worktree add` flow with bootstrap baked in.

Available, not adopted:
- v2.1.133 `worktree.baseRef: "head"` — user-side setting (`~/.claude/settings.json`); recommendation documented in AGENTS.md Worktree Workflow but not forced. `ry-explore` uses `context: fork`, not `isolation: worktree`.
- v2.1.133 hook input `effort.level` + `$CLAUDE_EFFORT` env var in Bash — could enrich hook telemetry; not yet wired into `flow_post_task_state.py` or `serena_memory_state.py`.
- v2.1.142 added `claude agents` flags (`--add-dir`, `--settings`, `--mcp-config`, `--plugin-dir`, `--permission-mode`, `--model`, `--effort`, `--dangerously-skip-permissions`) and made fast mode default to Opus 4.7.
- v2.1.142 fixed `MCP_TOOL_TIMEOUT` behavior for HTTP/SSE servers so per-request timeout applies to all MCP calls.
- v2.1.141 `claude agents --cwd <path>` and `terminalSequence` hook field were added; hook and daemon regressions were fixed.
- v2.1.139 hook `args: string[]` exec-form (spawns without shell) — all 8 hooks consistently use bare `command: bash ${CLAUDE_PLUGIN_ROOT}/...` form; migrating only one would diverge style without fixing any quoting bug.
- v2.1.139 `PostToolUse` `continueOnBlock: true` — our PostToolUse hooks are advisory-only (`exit 0` always), nothing to "block on".
- v2.1.139 stdio MCP env receives `${CLAUDE_PROJECT_DIR}` — no current server needs project-root context.
- v2.1.139 `claude plugin details <name>` — diagnostic only (see AGENTS.md Validation And Setup).

GitHub MCP transport (changed in v0.1.2, 2026-05-13): switched from HTTP `api.githubcopilot.com/mcp/` (Copilot-entitlement-gated; non-Copilot accounts get `HTTP 403 "unauthorized: not authorized to use this Copilot feature"` on `initialize`) to local stdio `github-mcp-server stdio --toolsets=repos,issues,pull_requests,users,context`. Host binary is the Homebrew bottle `github-mcp-server` pinned at v1.0.4 in `config/mcp-runtime-versions.env`; PAT scopes `repo` + `read:org` are sufficient, no Copilot subscription required. `scripts/check_mcp_runtime_versions.py` enforces version parity by probing `github-mcp-server --version` rather than parsing `.mcp.json` args. `anthropics/claude-plugins-official` keeps the HTTP endpoint as their canonical pattern for Copilot users — we cannot mirror that without an allowlist.

Smoke-script footgun (documented for future maintainers): `scripts/smoke_fullrepo_sync.sh` calls `fullrepo_sync.py --bootstrap-init`, which restores agent-only worktree files (AGENTS.md, .claude/CLAUDE.md, .serena/**) from `origin/fullrepo`. Run smoke **before** editing agent-only files in a session, or re-apply edits after smoke completes; otherwise in-progress changes are silently reverted.

Capability-smoke hardening (added 2026-05-13, v0.1.2): `scripts/smoke_mcp_capabilities.sh` no longer treats HTTP 401/403 as blanket PASS for `HTTP_AUTH_GATED` servers — that shortcut hid the GitHub Copilot entitlement failure. Now performs real MCP `initialize` JSON-RPC handshake over HTTP, parses both `application/json` and `text/event-stream` bodies, requires `result.serverInfo.name`. Classification: 401 without auth → SKIP, 401 with auth → FAIL ("token rejected"), 403 → FAIL with explicit remediation hint, 200 without `serverInfo` → FAIL ("silent-misconfig catch"). `figma` is the only remaining `HTTP_AUTH_GATED` entry (accepts 200 without `serverInfo` pre-session).

Capability smoke (added 2026-05-12): `scripts/smoke_mcp_capabilities.sh` performs JSON-RPC `initialize` + `tools/list` per server (stdio spawn or HTTP POST) and asserts a non-empty tool set. Used to validate `serena 1.2.0 → 1.3.0` bump — 13/13 servers pass on 2026-05-12. Serena under `--context=agent` reports 28 tools in 1.3.0 (was 45 in 1.2.0); the mode-selection refactor scopes the tool surface more tightly per context. All workflow tools we use are present.

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
