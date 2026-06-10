# Claude Code Project Memory - rldyour-claude

Personal Claude Code plugin marketplace by `rldyourmnd`. Cross-tool overview, source-of-truth manifests, plugin layers, CLI commands, and `config/rldyour-contract.json` / `docs/contract-matrix.md` live in `./AGENTS.md`. This file (`./.claude/CLAUDE.md`) is the Claude Code-native deep memory: subagent matrix, hook canon, skill-listing budget, frontmatter conventions, and Don't/Done rules. Both files are agent-only, live on the `fullrepo` branch, and are excluded from `main` via `.git/info/exclude`.

<!-- sync_contract:
claims:
  mcp_owner: rldyour-mcps
  hook_owners: [rldyour-flow, rldyour-serena-mcp]
  lsp_owner: rldyour-lsps
  reviewer_transport_marker: RLDYOUR_REPORT_EOF
  reviewer_report_dir_template: ".serena/reviews/<run_id>/"
  reviewer_run_id_format: "<UTC-ISO-compact>-<git-short-sha>"
  claude_code_runtime_pin: "2.1.170"
  claude_code_feature_floor: "2.1.146"
  skill_listing_budget_fraction: 0.04
  max_skill_description_chars: 1536
  fullrepo_branch: fullrepo
  plugin_count: 10
  skill_count: 38
  command_count: 11
  subagent_count: 8
-->

<!-- Maintainer notes (HTML comments are stripped from Claude's context per CC v2.1.72): keep this file under 200 lines per Anthropic official guidance (code.claude.com/docs/en/memory). Project CLAUDE.md re-injects after /compact and is inherited by every subagent - every line is a recurring token cost. Update only when discovering durable Claude Code-specific facts; cross-tool facts belong in AGENTS.md. -->

## Plugins And Components

```
rldyour-mcps         transport     0 skills • 0 cmds • 0 agents • 0 hooks  • .mcp.json (11 pinned servers)
rldyour-serena-mcp   semantic      2 skills • 0 cmds • 1 agent  • 4 hooks
rldyour-flow         SDLC          8 skills • 7 cmds • 6 agents • 4 hooks  • 7 scripts • 7 references
rldyour-orchestrator cmux macOS   2 skills • 0 cmds • 0 agents • 0 hooks  • macOS-only
rldyour-explore      research      2 skills • 1 cmd  • 1 agent  • 0 hooks
rldyour-security     security      2 skills • 1 cmd  • 0 agents • 0 hooks
rldyour-browser      browser       6 skills • 0 cmds • 0 agents • 0 hooks
rldyour-design       design        5 skills • 1 cmd  • 0 agents • 0 hooks
rldyour-lsps         lsp           4 skills • 0 cmds • 0 agents • 0 hooks  • 2 scripts • 3 references
rldyour-rules        rules         7 skills • 1 cmd  • 0 agents • 0 hooks  • 6 references
```
Total: 38 skills, 11 slash commands, 8 subagents. Slash commands (SDLC + tool-routing), plugin dependency graph, MCP transport detail, and fullrepo branch policy are listed in `./AGENTS.md`.

## Subagent Frontmatter Matrix

Required fields for plugin-shipped subagents: `name`, `description`. Plugin-shipped subagents silently ignore `hooks`, `mcpServers`, and `permissionMode` - copy to `.claude/agents/` if those are needed.

| Agent | model | effort | maxTurns | color | role |
|---|---|---|---|---|---|
| flow-architecture-review | sonnet | high | 90 | blue | boundaries, dependency direction, public API |
| flow-quality-review | sonnet | high | 90 | green | correctness, edge cases, lifecycle |
| flow-consistency-review | sonnet | high | 90 | purple | naming, style, project conventions |
| flow-integration-review | sonnet | high | 90 | orange | cross-module sync, contracts |
| flow-verification-review | sonnet | high | 90 | pink | tests, LSP, browser/server evidence |
| flow-security-review | sonnet | high | 100 | red | defensive auth/authz/secrets/injection |
| ry-explore | opus[1m] | max | 90 | cyan | deep multi-source research, `context: fork` |

All reviewer agents declare explicit `tools:` allowlist (`Read`, `Grep`, `Glob`, `Bash`, plus `mcp__plugin_rldyour-mcps_serena__*`, `mcp__plugin_rldyour-mcps_context7__*`, `mcp__plugin_rldyour-mcps_deepwiki__*`, `mcp__plugin_rldyour-mcps_grep__*`) for future-proof read-only enforcement. `flow-security-review` additionally allows `WebFetch` and `WebSearch` for CVE lookups; SAST evidence comes from project security scripts and CI artifacts. `ry-explore` uses the same allowlist pattern. Pattern follows canonical `anthropics/claude-plugins-official/plugins/pr-review-toolkit/agents/code-reviewer` (explicit allowlist), not the older `disallowedTools` denylist - explicit positive intent isolates reviewers from future tool additions. `maxTurns` raised to 90 (security: 100) in 0.3.0 release after the 0.3.0 self-review wave found that 36/42 was insufficient: 3 of 6 reviewers hit limit during investigation and never reached the report-write step. MCP-rich toolsets (Serena + Context7 + DeepWiki + Grep + WebFetch + WebSearch) eat 8-15 turns on tool plumbing before useful work begins, plus the file-first write contract itself costs 2-3 turns; 90 gives ~70 turns of effective reasoning + writing budget.

Reviewer output transport is **file-first** since rldyour-flow `0.2.2`: each reviewer writes the full long-form report to `.serena/reviews/<run_id>/<reviewer-name>.md` via `Bash` using the unique heredoc marker `<<'RLDYOUR_REPORT_EOF'` (multi-char marker prevents early termination on short tokens like `MD`/`EOF`) and returns only a ≤ 4 KB compact summary (Report path + severity counts + one-liner findings, cap 30 entries). The orchestrator (`ry-start` / `ry-review` skill body) generates one `run_id = <UTC-ISO-compact>-<git-short-sha>` per wave (minute-precision UTC), injects `report_dir` into every reviewer prompt, MUST `Read` per-reviewer report files for every critical and high finding before disposition, and writes `<report_dir>/_summary.md` as the consolidated wave artefact. Full contract in `plugins/rldyour-flow/references/reviewer-protocol.md` "Output Transport". Rationale: Claude Code 2.0.77+ regression (Anthropic [`#16789`](https://github.com/anthropics/claude-code/issues/16789), [`#20531`](https://github.com/anthropics/claude-code/issues/20531), [`#23463`](https://github.com/anthropics/claude-code/issues/23463), all closed as "not planned") can deliver 200-500 KB JSONL transcript per subagent and overflow parent context; 6 reviewers × ≤ 4 KB = ≤ 24 KB structurally prevents the failure class. Read-only invariant preserved (`Edit`/`Write`/`NotebookEdit` still absent; `Bash` writes are bounded to `<report_dir>/<reviewer-name>.md` only).

| flow-memory-sync (rldyour-serena-mcp) | sonnet | high | 36 | yellow | fact-only Serena memory sync, invoked by orchestrator when Stop hook advisory triggers |

`flow-memory-sync` is a plugin-shipped subagent with narrow tool access (Serena memory tools - `write_memory`/`edit_memory`/`delete_memory`/`rename_memory` - plus read-only `Read`/`Grep`/`Glob`/`Bash`; `disallowedTools: [Edit, Write, NotebookEdit]`). Anti-hallucination contract enforced via body: source-of-truth hierarchy code > tests > git diff > existing memories; citation required per claim; removal-first principle for unverifiable claims; `Last commit: <HEAD_SHA>` line mandatory in every touched memory; `commit_serena_knowledge.sh` runs internally; final JSON report. Memory files are a numbered knowledge base: `CORE-01-INDEX.md` is the map and topics use `AREA-01-SLUG.md` (`SERENA-01-MEMORY-SYNC.md`, `TECHDEBT-01-NOW.md`). Invocation pattern: when the dispatcher Serena memory child gate emits its advisory, the orchestrator (model in main session, or `flow-post-task-sync` skill workflow step 1) calls `Agent({subagent_type: 'rldyour-serena-mcp:flow-memory-sync', prompt: ...})` with HEAD context - keeping high-blast-radius operations under workflow control rather than letting hooks fire them silently.

## Hooks Lifecycle

Two plugins coordinate hooks. `rldyour-flow` owns the single registered Claude Stop hook through `hooks/stop_lifecycle_dispatcher.sh`; the dispatcher runs the Serena memory child check before the Flow post-task child check. `flow.stop_post_task_sync.sh` derives `serena_current` by calling `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py` before running its own gate. Loop guard: `.serena/.flow_sync_marker` writes a fingerprint of (HEAD, dirty files, ahead/behind, branch, Serena freshness). If `stop_hook_active=true` and the fingerprint matches, the hook emits a compact system message and allows Stop. Flow Stop state runs with `RLDYOUR_FLOW_STATE_LOCAL_ONLY=1` / `RLDYOUR_FULLREPO_STATUS_LOCAL_ONLY=1` so the hook hot path never depends on remote fetch status; `flow_post_task_state.py` resolves installed sibling plugin scripts from `__file__` before repo-relative fallbacks, keeping direct diagnostics and real hook execution consistent. The dispatcher also writes `.serena/.stop_lifecycle_timeout_marker` so repeated identical child timeouts are allowed on the second `stop_hook_active=true` pass instead of looping.

| Event | Owner | Script | Timeout |
|---|---|---|---|
| UserPromptSubmit | rldyour-serena-mcp | `hooks/user_prompt_submit.sh` | 5s |
| PreToolUse:Bash | rldyour-serena-mcp | `hooks/prepare_auto_sync.sh` | 5s |
| PostToolUse:Bash | rldyour-serena-mcp | `hooks/mark_sync_required.sh` | 5s |
| PostToolUse:Bash | rldyour-flow | `hooks/post_tool_use_commit_advice.sh` | 5s |
| SessionStart | rldyour-flow | `hooks/session_start_worktree_bootstrap.sh` | 30s |
| SessionStart | rldyour-flow | `hooks/session_start_context.sh` | 5s |
| Stop | rldyour-flow | `hooks/stop_lifecycle_dispatcher.sh` | 45s |

Stop hooks are **advisory enforcement gates**, not executors. Pattern: hooks compute machine-readable state, block Stop (`exit 2`) until the orchestrator (`ry-start`, `flow-post-task-sync` skill, model in main session) brings the project to a clean final state. Hooks themselves do **not** push, merge, publish, or delete branches - those are high-blast-radius operations and live in the workflow executor under model judgement.

Stop sequence: dispatcher child check `stop_memory_sync.sh` checks `serena_memory_state.py` first and blocks stale memories with `flow-memory-sync` guidance; dispatcher child check `stop_post_task_sync.sh` then checks git/docs/fullrepo/cleanup state through `flow_post_task_state.py`; `.serena/.sync_marker`, `.serena/.flow_sync_marker`, and `.serena/.stop_lifecycle_timeout_marker` carry loop-guard fingerprints so repeated identical Stop gates do not loop forever. `tests/test_flow_stop_state.py` is the regression suite for direct installed-state invocation, local-only fullrepo status, dispatcher timeout escape, and Stop hook loop-guard behavior from a subdirectory.

The orchestrator (skill / model in main session) does the actual work: invoke `flow-memory-sync` subagent for memories, then run the `flow-post-task-sync` skill which handles checks → atomic commits → push → ff-merge into default branch → push default → fullrepo publish (`--force-with-lease`, only on `fullrepo`) → cleanup merged branches and worktrees.

Skip flags during local debugging: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT=1` (SessionStart context), `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1` (SessionStart worktree bootstrap), `RLDYOUR_SKIP_FLOW_COMMIT_ADVICE=1` (PostToolUse:Bash flow), `RLDYOUR_SKIP_STOP_GATES=1` (registered dispatcher and all child Stop gates), `RLDYOUR_SKIP_FLOW_SYNC=1` (Flow child gate only), `RLDYOUR_SKIP_SERENA_SYNC=1` (Serena memory child gate only).

## Skill Listing Budget

Per-entry combined `description` + `when_to_use` cap: **1,536 chars** (raised from 250 in CC v2.1.128). Aggregate budget defaults to **1% of context window** with 8,000-char fallback. With 38+ skills the default budget truncates tail-end descriptions and Claude can no longer auto-trigger them.

User-side fix in `~/.claude/settings.json`:

```json
{
  "skillListingBudgetFraction": 0.04,
  "maxSkillDescriptionChars": 1536
}
```

`maxSkillDescriptionChars` and `skillListingBudgetFraction` were added in CC **v2.1.105+**. `skillListingBudgetFraction` is a decimal fraction in `(0, 1]`. Runtime override: `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var (raw chars). The separate `skillOverrides` map (`"on" | "name-only" | "user-invocable-only" | "off"`) was added in **v2.1.129+** and does **not** affect plugin-shipped skills - manage those through `/plugin` instead. The `0.04` (4%) value is bumped above the claudekit-cli baseline `0.03` (verified 2026-05-15) because our bilingual Russian-leading + English-triggers description format averages ~400 chars per entry vs ~250 for pure-English plugins; at 38 skills our total skill-listing token cost is ~15.2K chars and `0.03` of 200K-token Sonnet sessions truncates tail-end auto-trigger descriptions. `opus[1m]` 1M-token sessions have room at 0.03 too, but 0.04 covers both cases.

Plugin-side levers used in this repo:
- `disable-model-invocation: true` on **4 skills** (`skills/ry-deploy/SKILL.md`, `skills/ry-newp/SKILL.md`, `skills/ry-rules-review/SKILL.md`, `skills/ry-sec-review/SKILL.md`) - slash-only, freeing budget for auto-triggered skills.
- `allowed-tools` on **15 skills** with explicit toolsets - eliminates per-call permission prompts during work without touching listing budget.

## Hook Events Canon

Claude Code v2.1.x publishes **29 canonical hook events** (per `code.claude.com/docs/en/hooks`). Five handler types: `command`, `http`, `mcp_tool` (v2.1.118+), `prompt`, `agent`. Prompt/agent handlers spawn LLM evaluation or full subagent verification - used for runtime validation when shell hooks aren't expressive enough. `InstructionsLoaded` event (CC v2.1.69+) fires when CLAUDE.md or `.claude/rules/*.md` files are loaded into context.

Hierarchy precedence (highest → lowest): managed policy → plugin hooks (force-enabled exempt from `allowManagedHooksOnly`) → `.claude/settings.json` → `.claude/settings.local.json` → `~/.claude/settings.json` → skill/agent frontmatter.

Per Anthropic guidance: put guardrails in hooks, not in CLAUDE.md prose. CLAUDE.md is delivered as a user message after the system prompt - it is context, not enforced configuration.

## Anthropic Precedent Confirmations

Patterns verified against `anthropics/claude-plugins-official` snapshot `1a2f18b05cf5652fd25403e8d229fc884fb84103` and `code.claude.com/docs` v2.1.142 (audit 2026-05-15):

- **Parallel reviewer subagents** - direct precedent in `pr-review-toolkit/agents/` (6 specialized review agents: `code-reviewer`, `code-simplifier`, `comment-analyzer`, `pr-test-analyzer`, `silent-failure-hunter`, `type-design-analyzer`). README explicitly endorses parallel dispatch: *"Parallel (faster): 'Run pr-test-analyzer and comment-analyzer in parallel'"*. Our 6-track + security matrix (7 reviewers total) is on the deep end of this pattern.
- **`tools:` explicit allowlist for read-only agents** - canonical in `pr-review-toolkit/code-reviewer.md` (`tools: Glob, Grep, LS, Read, NotebookRead, WebFetch, TodoWrite, WebSearch, KillShell, BashOutput`) and all 4 examples in `plugin-dev/skills/agent-development/examples/complete-agent-examples.md`. Migration `disallowedTools` → `tools` allowlist isolates from future Claude Code additions.
- **Stop hook `stop_hook_active` loop guard** - dictated verbatim by `code.claude.com/docs/en/hooks-guide`. Our `stop_post_task_sync.sh` and `stop_memory_sync.sh` implement it + add fingerprint marker for sub-fingerprint precision.
- **Exec-form `command: "bash"` + `args: ["${CLAUDE_PLUGIN_ROOT}/hooks/X.sh"]`** - v2.1.139+ canonical form for path-placeholder hooks per `code.claude.com/docs/en/hooks` (May 2026). Adopted across all 8 hooks in v0.5.0 (commit `614bdcf`). Reasoning: exec-form passes each `args` element verbatim (no shell tokenization), so paths with spaces/special chars never need quoting. Anthropic's own plugins-official marketplace still uses shell-form at the snapshot above; we adopted exec-form because the docs recommend it for placeholder-bearing commands.
- **Stop hook advisory-gate pattern** - production-grade pattern in `bitwarden/server`, `MemPalace/mempalace`, `mem0ai/mem0`, `iamfakeguru/agent-md`, `yohey-w/multi-agent-shogun`. Our `flow_post_task_state.py` + structured fingerprint is the cleaner variant.
- **`alwaysLoad: true` for critical-path MCP servers** - community pattern in `tractorjuice/arc-kit`, `OMARVII/claude-alloy`, `darkroomengineering/cc-settings`. Our restraint (only `serena`) is appropriate scoping.
- **Tag convention `<plugin-name>--v<version>`** - Anthropic-canonical via `claude plugin tag --push` (docs `code.claude.com/docs/en/plugin-dependencies`). Anthropic's own plugins-official marketplace doesn't apply tags yet, but the documented convention is the canonical one.

## Changelog Adoption (v2.1.133 -> v2.1.170)

Verified against `code.claude.com/docs/en/changelog`, `code.claude.com/docs/en/model-config`, `references/claude-baseline.json`, `package.json`, and npm package metadata on 2026-06-09. Runtime pin: **v2.1.170**. Feature compatibility floor: **v2.1.146+**.

Adopted:
- v2.1.105 - `maxSkillDescriptionChars` and `skillListingBudgetFraction` user settings (Anthropic + claudekit-cli baseline is `0.03`; this repo recommends `0.04` - see Skill Listing Budget section above for the bilingual-description rationale). Per-entry skill description cap `1,536` chars, used by all 38 skills.
- v2.1.121 - `alwaysLoad: true` on `serena` MCP server.
- v2.1.118 - `claude plugin tag --push` for release tagging (canonical, `<plugin>--v<version>`).
- v2.1.129 - `skillOverrides` map (`"on" | "name-only" | "user-invocable-only" | "off"`); does NOT apply to plugin skills - manage those through `/plugin`. `experimental.{themes,monitors}` wrapper available (we declare neither).
- v2.1.x - `SessionStart` + `WorktreeRemove`/`WorktreeCreate` worktree workflow (added 2026-05-12): `hooks/session_start_worktree_bootstrap.sh` auto-restores agent-only files into a fresh worktree via `fullrepo_sync.py --restore`. `WorktreeCreate` is intentionally NOT used because the worktree path does not yet exist on disk when that event fires - `SessionStart` in the new worktree session is the correct injection point. `scripts/worktree_add.sh` covers the manual `git worktree add` flow with bootstrap baked in.

Available, not adopted:
- v2.1.133 `worktree.baseRef: "head"` - user-side setting (`~/.claude/settings.json`); recommendation documented in AGENTS.md Worktree Workflow but not forced. `ry-explore` uses `context: fork`, not `isolation: worktree`.
- v2.1.133 hook input `effort.level` + `$CLAUDE_EFFORT` env var in Bash - could enrich hook telemetry; not yet wired into `flow_post_task_state.py` or `serena_memory_state.py`.
- v2.1.142-2.1.146 refreshed the operational floor: agent CLI flags, HTTP `MCP_TOOL_TIMEOUT` fix, plugin dependency enforcement, `/plugin` context-cost/component previews, background/worktree/MCP pagination fixes, stricter `claude plugin validate`, and Auto mode `AskUserQuestion` behavior needed by decision gates. This repo keeps the feature compatibility floor at v2.1.146+ and the runtime pin at v2.1.170.
- v2.1.152 - `disallowed-tools` frontmatter for skills and slash commands, `/reload-skills`, `SessionStart.reloadSkills`, and `MessageDisplay` hook event are tracked in `references/claude-surface-adoption.md`.
- v2.1.153 - `skipLfs` marketplace-source option, npm update diagnostics in `/doctor`, status-line `COLUMNS`/`LINES`, and `claude agents` native command/bundled skill autocomplete are tracked in `references/claude-surface-adoption.md`.
- v2.1.154 - Opus 4.8 support, dynamic workflows, Opus 4.8 fast mode, default streaming tool execution, `defaultEnabled: false` plugin metadata, and safer piped MCP pending-approval reporting are tracked in `references/claude-surface-adoption.md`.
- v2.1.156 - Opus 4.8 thinking-block API error hotfix remains required for release readiness.
- v2.1.157-2.1.169 - Direct `.claude/skills` loading, package latest drift, agent JSON `waitingFor`, native `Grep`/`Glob` tool listing, read-only config fallback behavior, `fallbackModel` / `--fallback-model`, deny-rule glob support including `"*"`, relayed `SendMessage` permission hardening, explicit thinking-disable controls, managed MCP `${VAR}` predicates, the 2.1.168 reliability rollup, and the 2.1.169 package/runtime rollup are recorded; marketplace plugins remain the first-party release surface.
- v2.1.141 `claude agents --cwd <path>` and `terminalSequence` hook field were added; hook and daemon regressions were fixed.
- v2.1.139 hook `args: string[]` exec-form **adopted** in v0.5.0 (commit `614bdcf`): all 8 hooks switched from shell-form `command: "bash ${CLAUDE_PLUGIN_ROOT}/..."` to exec-form `command: "bash", args: ["${CLAUDE_PLUGIN_ROOT}/hooks/X.sh"]`. Verified 2026-05-17 against `code.claude.com/docs/en/hooks` which explicitly recommends exec-form for any hook with path placeholders.
- v2.1.139 `PostToolUse` `continueOnBlock: true` - our PostToolUse hooks are advisory-only (`exit 0` always), nothing to "block on".
- v2.1.139 stdio MCP env receives `${CLAUDE_PROJECT_DIR}` - no current server needs project-root context.
- v2.1.139 `claude plugin details <name>` - diagnostic only (see AGENTS.md Validation And Setup).

GitHub MCP transport (changed in v0.1.2, 2026-05-13): switched from HTTP `api.githubcopilot.com/mcp/` (Copilot-entitlement-gated; non-Copilot accounts get `HTTP 403 "unauthorized: not authorized to use this Copilot feature"` on `initialize`) to local stdio `github-mcp-server stdio --toolsets=repos,issues,pull_requests,users,context`. Host binary is the Homebrew bottle `github-mcp-server` pinned at v1.2.0 in `config/mcp-runtime-versions.env`; PAT scopes `repo` + `read:org` are sufficient, no Copilot subscription required. `scripts/check_mcp_runtime_versions.py` enforces version parity by probing `github-mcp-server --version` rather than parsing `.mcp.json` args. `anthropics/claude-plugins-official` keeps the HTTP endpoint as their canonical pattern for Copilot users - we cannot mirror that without an allowlist.

Smoke-script footgun (documented for future maintainers): `scripts/smoke_fullrepo_sync.sh` calls `fullrepo_sync.py --bootstrap-init`, which restores agent-only worktree files (AGENTS.md, .claude/CLAUDE.md, .serena/**) from `origin/fullrepo`. Run smoke **before** editing agent-only files in a session, or re-apply edits after smoke completes; otherwise in-progress changes are silently reverted.

Capability-smoke hardening (added 2026-05-13, v0.1.2): `scripts/smoke_mcp_capabilities.sh` no longer treats HTTP 401/403 as blanket PASS for `HTTP_AUTH_GATED` servers - that shortcut hid the GitHub Copilot entitlement failure. Now performs real MCP `initialize` JSON-RPC handshake over HTTP, parses both `application/json` and `text/event-stream` bodies, requires `result.serverInfo.name`. Classification: 401 without auth → SKIP, 401 with auth → FAIL ("token rejected"), 403 → FAIL with explicit remediation hint, 200 without `serverInfo` → FAIL ("silent-misconfig catch"). `figma` is the only remaining `HTTP_AUTH_GATED` entry (accepts 200 without `serverInfo` pre-session).

Capability smoke (added 2026-05-12): `scripts/smoke_mcp_capabilities.sh` performs JSON-RPC `initialize` + `tools/list` per server (stdio spawn or HTTP POST) and asserts a non-empty tool set. Historical focused smoke evidence from 2026-05-20 used older MCP pins; current source of truth is `config/mcp-runtime-versions.env` plus the root `config/mcp-version-policy.json`, and `scripts/check_mcp_runtime_versions.py` verifies the active Serena, Chrome DevTools, GitHub MCP, and related MCP pins before release.

## Engineering Conventions

- Russian user-facing communication; English repository artifacts. User-facing invocation metadata is Russian-leading with English compatibility: skill `description`, slash-command `description`, and reviewer-agent `description` fields.
- Skill frontmatter: `name`, `description` (recommended). Optional: `when_to_use`, `argument-hint`, `allowed-tools`, `disable-model-invocation`, `user-invocable`, `model`, `effort`, `paths`, `context: fork`, `agent`.
- Agent frontmatter: `name`, `description`, `model`, `effort`, `maxTurns`, `color`. Tool access: prefer explicit `tools:` allowlist (canonical Anthropic pattern, used by all 6 flow reviewer agents + ry-explore for future-proof read-only enforcement); `disallowedTools:` denylist is legacy and still works (used by `flow-memory-sync` which has narrow Serena memory MCP needs). Optional: `skills`, `memory`, `background`, `isolation`, `initialPrompt`.
- `model: opus[1m]` is the canonical bracketed alias for the latest Opus 1M context on Claude Code. On Anthropic API it resolves to Opus 4.8 and requires CC **v2.1.154+**; `[1m]` availability remains account/plan-dependent.
- `model: sonnet` is the canonical short form for reviewer subagents.
- Slash command frontmatter: `description`, `argument-hint`, optional `context: fork` and `agent: <name>`. Bare `model:` on a slash command is silently ignored without `context: fork` - pair them or delegate via `agent:`.
- Conventional Commits, ≤72 char subjects, atomic commits per logical unit.
- Separate source, tests/validators, docs/instructions, license/metadata, generated artifacts, and Serena/fullrepo sync commits when it improves history clarity. Do not rewrite already-pushed history without explicit owner approval.
- All MCP server versions are pinned (stdio with `==X.Y.Z`; HTTP servers by URL).
- `allowed-tools` may mix built-in tool names (`Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash`, `WebSearch`, `WebFetch`) and MCP wildcards (`mcp__plugin_rldyour-mcps_<server>__*`) in the same skill - pattern is validated by `claude plugin validate` and used by `serena-code-workflow`, `serena-memory-sync`, `lsp-routing`, `serena-lsp-integration`, `figma-to-code`, `ry-design`, `design-system-implementation`.

## Claude Code-specific Diagnostics

Beyond `claude plugin validate` and bootstrap commands documented in `./AGENTS.md`:

- `/mcp` - transport status. `/doctor` - env health (skill-listing truncation warnings appear here). `/status` - session state. `/context` - token-budget breakdown by category. `/hooks` - active hooks. `/memory` - CLAUDE.md, CLAUDE.local.md, and rules files loaded.
- `python3 plugins/rldyour-flow/scripts/instruction_docs_state.py --json` - whether AGENTS.md and `.claude/CLAUDE.md` need review.
- `python3 plugins/rldyour-flow/scripts/flow_post_task_state.py` - fingerprint of dirty state, Serena freshness, branch cleanup candidates.
- `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py` - Serena memory match-vs-HEAD state.

## Don't

- Don't reduce this file to `@AGENTS.md` import - `@imports` don't reduce token cost (Anthropic memory docs); content loads at launch either way. Keep separation: AGENTS.md cross-tool, CLAUDE.md Claude Code-deep.
- Don't grow either file past 200 lines - Anthropic empirical evidence: adherence drops, instructions get lost.
- Don't put hard guardrails in CLAUDE.md prose ("ALWAYS X", "NEVER Y") - they are advisory user-message context. Use hooks for enforcement.
- Don't add `.mcp.json` outside `rldyour-mcps`. Don't add `hooks.json` outside `rldyour-flow` or `rldyour-serena-mcp`. Don't add a new plugin without confirming domain boundary.
- Don't commit `AGENTS.md`, `.claude/**`, `.serena/project.yml`, `.serena/memories/**` to `main` - fullrepo only.
- Don't write Serena memories from `ry-init` unless explicitly requested or a Stop/stale-memory hook required it.
- Don't force-push `main`; `--force-with-lease` is allowed only for `fullrepo`.
- Don't auto-generate this file or AGENTS.md from code analysis - ETH Zurich research (cited in Augment 2026 guide) shows LLM-generated context files reduce task success 0.5-2% with 20-23% token overhead.

## Done Criteria

- All touched manifests pass `claude plugin validate`.
- `git status` clean of non-agent files; agent-only paths excluded via the `# >>> rldyour fullrepo agent-only files >>>` block in `.git/info/exclude`.
- `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json` shows `tracked_agent_paths: []` on `main`.
- `fullrepo` republished after any agent-only change.
- Plugin component cross-references (skills referencing scripts/agents/references) actually exist on disk.
- Reviewer subagents (when invoked) produce read-only findings, never edit files.
- This file stays under 200 lines.
