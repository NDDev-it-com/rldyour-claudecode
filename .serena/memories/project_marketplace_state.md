# rldyour-claude marketplace state

Last commit: a851d99 (refactor/restore-advisory-hooks, 2026-05-08, awaiting merge to main).
Four May-2026 best-practice waves applied:
- optimize/may-2026-best-practices: 6 commits 3fe9005..2e22652 (merged to main)
- docs/canonical-may2026: 1 commit ca13470 (merged to main)
- polish/deferred-findings: 3 commits 3ce7970..f23765d (merged to main)
- feat/memory-sync-subagent: 1 commit 772f6e8 (current branch, NOT YET merged)
First three feature branches deleted after fast-forward merge.
Marketplace name: `rldyour-claude`. Repo: github.com/rldyourmnd/rldyour-claude (private).

## Layered architecture (verified)

1. Transport — `rldyour-mcps` (single owner of `.mcp.json`, 13 pinned servers).
2. Semantic code — `rldyour-serena-mcp` (depends on `rldyour-mcps`).
3. SDLC orchestrator — `rldyour-flow` (depends on `rldyour-mcps`, `rldyour-serena-mcp`).
4. Domain — `rldyour-explore`, `rldyour-security`, `rldyour-browser`, `rldyour-design`,
   `rldyour-lsps` (each depends on `rldyour-mcps`).
5. Engineering rules — `rldyour-rules` (depends on `rldyour-mcps`).

Cross-plugin `dependencies` declared in plugin.json `dependencies: [...]` array.

## Hard boundaries

- Only `rldyour-mcps` declares `.mcp.json`.
- Only `rldyour-flow` and `rldyour-serena-mcp` declare `hooks.json`.
- One domain per plugin; cross-plugin overlap forbidden.
- `rldyour-browser`/`rldyour-design` are skills-only consumers of transport.

## Hooks lifecycle (coordination contract)

| Event | Owner | Script |
|---|---|---|
| UserPromptSubmit | rldyour-serena-mcp | hooks/user_prompt_submit.sh |
| PreToolUse:Bash | rldyour-serena-mcp | hooks/prepare_auto_sync.sh |
| PostToolUse:Bash | rldyour-serena-mcp | hooks/mark_sync_required.sh |
| PostToolUse:Bash | rldyour-flow | hooks/post_tool_use_commit_advice.sh |
| SessionStart | rldyour-flow | hooks/session_start_context.sh |
| Stop | rldyour-serena-mcp | hooks/stop_memory_sync.sh |
| Stop | rldyour-flow | hooks/stop_post_task_sync.sh |

`flow.stop_post_task_sync.sh` waits for `serena_current=true` from the Serena Stop hook
before running. Loop guard: `.serena/.flow_sync_marker` fingerprint of (HEAD, dirty,
ahead/behind, branch, Serena freshness). If `stop_hook_active=true` and same fingerprint,
hook allows stop.

All hooks advisory: emit `hookSpecificOutput.additionalContext`, exit 0 on errors.
Skip flags: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT`, `RLDYOUR_SKIP_STOP_GATES`,
`RLDYOUR_SKIP_FLOW_SYNC`.

## Subagent matrix (8 total)

Reviewer (rldyour-flow/agents/flow-*-review.md): `model: sonnet`, `effort: high`,
`maxTurns: 36` (security: `42`), `disallowedTools: [Edit, Write, NotebookEdit]`.
6 agents with distinct colors:

| Agent | maxTurns | color |
|---|---|---|
| flow-architecture-review | 36 | blue |
| flow-quality-review | 36 | green |
| flow-consistency-review | 36 | purple |
| flow-integration-review | 36 | orange |
| flow-verification-review | 36 | pink |
| flow-security-review | 42 | red |

`maxTurns` was raised from 12-14 to 36/42 (×3) after observing that MCP-rich
toolsets (Serena+Context7+DeepWiki+Grep) consume turns on tool plumbing.
Tight 12-14 limits effectively gave only 4-7 reasoning turns.

Research (rldyour-explore/agents/ry-explore.md): `model: opus[1m]`, `effort: max`,
`maxTurns: 90` (was 30), `disallowedTools: [Edit, Write, NotebookEdit]`, `color: cyan`.
Triggered via `/rldyour-explore:ry-explore` slash command (`context: fork`).

Memory sync (rldyour-serena-mcp/agents/flow-memory-sync.md, added 772f6e8): `model: sonnet`,
`effort: high`, `maxTurns: 36`, `disallowedTools: [Edit, Write, NotebookEdit]`, `color: yellow`.
Plugin-shipped subagent invoked from main session via Agent tool (subagent_type
`rldyour-serena-mcp:flow-memory-sync`). Narrow tool access — Serena memory tools
(write_memory, edit_memory, etc.) + read-only Bash/Read/Grep/Glob; cannot mutate
arbitrary files. Anti-hallucination guards in body: source-of-truth hierarchy
(code > tests > git diff > existing memories), citation requirement per claim,
removal-first principle for unverifiable claims. Receives diff context as Agent
prompt and runs commit_serena_knowledge.sh internally. Plugin agents on Claude
Code v2.1.x are loaded at session start — after creating/updating an agent file,
restart the session for the agent to appear in `Agent` tool subagent_type list.

## MCP transport (rldyour-mcps/.mcp.json)

13 pinned servers; all dead `startup_timeout_sec`/`tool_timeout_sec` keys removed
(commit 0d78443).

- serena: `serena-agent==1.2.0`, `--context=agent`, web dashboard disabled,
  `alwaysLoad: true` (v2.1.121+) — eager startup since Serena drives every
  UserPromptSubmit hook.
- sequential-thinking: `@modelcontextprotocol/server-sequential-thinking@2025.12.18`.
- playwright: `@playwright/mcp@0.0.74` headless.
- chrome-devtools: `chrome-devtools-mcp@0.25.0` headless isolated.
- context7: `@upstash/context7-mcp@2.2.4`. Requires `CONTEXT7_API_KEY`.
- deepwiki: HTTP `mcp.deepwiki.com/mcp`.
- grep: HTTP `mcp.grep.app`.
- semgrep: `semgrep==1.161.0`.
- shadcn: `shadcn@4.7.0`.
- dart-flutter: `dart mcp-server --force-roots-fallback`.
- figma: HTTP `mcp.figma.com/mcp`.
- openai-docs: HTTP `developers.openai.com/mcp`.
- github: `github-mcp-server stdio`. Requires `GITHUB_PERSONAL_ACCESS_TOKEN`.

Timeouts via env: `MCP_TIMEOUT`, `MCP_TOOL_TIMEOUT`, `MAX_MCP_OUTPUT_TOKENS`,
`MCP_CONNECTION_NONBLOCKING`.

## Serena MCP context

`--context=agent` is canonical for Claude Code in Serena 1.2.0 (set in commit 482c421).
Exposes 45 of 46 Serena tools (only excludes the redundant `initial_instructions`
tool that Claude Code loads via ToolSearch).

Serena 1.2.0 has no `claude-code` context. The `serena prompts print-cc-system-prompt-override`
command prints a Claude Code-specific system prompt that maps Read/Edit/Glob/Grep
to Serena's symbolic tools as PRIMARY — used when running Claude Code with
`--system-prompt` flag.

Serena memory location: project-level via `.serena/memories/` (managed by
`rldyour-serena-mcp`).

## Fullrepo branch policy

Agent-only files live on `fullrepo` only. `AGENT_ONLY_PATTERNS` in
`plugins/rldyour-flow/scripts/fullrepo_sync.py`:

- root: AGENTS.md, CLAUDE.md, REVIEW.md, GEMINI.md, QWEN.md, .cursorrules,
  .windsurfrules, .aider*
- directories: .claude/**, .cursor/rules/**, .gemini/**, .roo/**, .windsurf/**,
  .openhands/**, .agents/{skills,commands,hooks}/**
- .github: copilot-instructions.md, instructions/**, prompts/**
- .serena: project.yml, memories/**, plans/**, research/**, newproj/**, deploy/**

All other-CLI agent-only directory globs were trimmed in commit 5feae39; this
marketplace targets Claude Code only.

`fullrepo_sync.py` subcommands: `--bootstrap-init`, `--restore`, `--migrate-main`,
`--publish` (uses `--force-with-lease`), `--status-json`.

## CI

`.github/workflows/validate.yml` (commit bbb934b) runs on push, pull_request, and
workflow_dispatch:
1. `claude plugin validate .` + per-plugin validation via `npm install -g @anthropic-ai/claude-code`.
2. Syntax checks: JSON manifests, Python AST, bash -n, frontmatter presence.

## Conventions

- User-facing Russian; English repo artifacts.
- Skill `description` Russian-leading.
- Conventional Commits, ≤72 chars, single scope `(scope):`.
- Atomic commits; secrets/runtime/browser artifacts never committed.
- All MCP server versions pinned (stdio `==X.Y.Z`; HTTP by URL).
- Min Claude Code: **v2.1.111+** for `model: opus[1m]` bracket syntax in agents.

## Skill-listing optimizations (2026-05-08)

- 10 skills declare explicit `allowed-tools`: serena-code-workflow, serena-memory-sync,
  tech-research, web-research, browser-validation, browser-debug, lsp-routing,
  lsp-health-check, lsp-setup, serena-lsp-integration. MCP wildcard form
  `mcp__plugin_rldyour-mcps_<server>__*` validated via `claude plugin validate`.
- 2 skills marked `disable-model-invocation: true` (slash-only): ry-deploy, ry-newp.
- User-side fix in `~/.claude/settings.json`: `skillListingBudgetFraction: 0.03`
  (v2.1.129+) — default 1% truncated 37/70 skill descriptions.
- Plugin.json `$schema` URL switched to `json.schemastore.org/claude-code-plugin-manifest.json`
  (canonical per docs).

## Recent commit history (a115b86..HEAD)

main (a115b86..bbb934b):
- 482c421 feat(mcps): switch Serena MCP --context to agent
- 5feae39 refactor(flow,serena-mcp): trim other-CLI globs and rename agents-doc constant
- 131c57b docs: reframe AGENTS.md as cross-tool root file
- 0d78443 chore(mcps): drop unsupported timeout fields from .mcp.json
- bcfa726 feat: declare cross-plugin dependencies in plugin.json
- bbb934b ci: add claude plugin validate workflow

May-2026 best-practices wave (bbb934b..2e22652, merged 2026-05-08):
- 3fe9005 refactor(agents): unify reviewer effort/maxTurns/colors and triple ry-explore turns
- 2631322 chore(plugins): switch plugin.json $schema to schemastore canonical
- db18b8a feat(mcps): mark serena MCP server alwaysLoad
- 0f7362b feat(skills): add allowed-tools to skills with explicit toolset
- 652a49d feat(flow): mark ry-deploy and ry-newp as slash-only
- 2e22652 docs(flow): align reviewer-protocol with new effort/maxTurns/color matrix

Canonical docs wave (2e22652..ca13470, merged 2026-05-08, agent-only files
not in git history but published to fullrepo):
- AGENTS.md trimmed: removed Skill Listing Budget section (Claude Code-specific),
  added cross-ref + maintainer/living-doc HTML comments. 150 → 152 lines.
- .claude/CLAUDE.md aggressively rewritten: removed Slash Commands table,
  MCP Transport, Architecture Layers, Fullrepo Branch Policy (full duplicates
  with AGENTS.md). Kept Plugins And Components, Subagent Frontmatter Matrix,
  Hooks Lifecycle (with Timeout column), Skill Listing Budget, Hook Events Canon,
  Engineering Conventions, Don't, Done Criteria. 206 → 123 lines (-40%).
- ca13470 fix(explore): align ry-explore body maxTurns:90 with frontmatter
  (caught by flow-integration-review).
- All 5 RLDYOUR_SKIP_* flags now documented (was 3).

Polish wave (ca13470..f23765d, merged 2026-05-08):
- 3ce7970 feat(design): allowed-tools added to 4 of 5 design skills
  (figma-to-code, design-system-implementation, design-validation, ry-design).
  fsd-frontend-architecture intentionally without — pure reference skill.
- 7e32688 feat(audit): disable-model-invocation:true on ry-rules-review and
  ry-sec-review (audit operations are deliberate). Now 4 skills are slash-only:
  ry-deploy, ry-newp, ry-rules-review, ry-sec-review. ry-init/ry-start/ry-review/
  ry-design intentionally retain auto-trigger as orchestrators.
- f23765d docs(flow): documented maxTurns:36/42 rationale in reviewer-protocol.md
  (security gets +6 turns for variant-hunt sweep).
- .claude/CLAUDE.md grew by 1 line (124 total) documenting the validated pattern
  of mixing built-in tools and MCP wildcards in allowed-tools.

Memory-sync subagent wave (f23765d..772f6e8, merged 2026-05-08):
- 772f6e8 feat(serena-mcp): add flow-memory-sync subagent for fact-only sync.
  NEW plugins/rldyour-serena-mcp/agents/flow-memory-sync.md (sonnet/high/36/yellow,
  anti-hallucination contract in body — citation per claim, source-of-truth
  hierarchy code > tests > git diff > existing memories, removal-first principle).

Restored Codex-style advisory enforcement (refactor/restore-advisory-hooks):
- Stop hooks are advisory enforcement gates, not executors. Hooks compute
  machine-readable state via serena_memory_state.py / flow_post_task_state.py,
  block Stop with exit 2 when work remains, never perform high-blast-radius
  operations themselves.
- stop_memory_sync.sh: advisory exit 2 when memories stale, points orchestrator
  at flow-memory-sync subagent (preferred) or fallback Serena workflow.
- stop_post_task_sync.sh: advisory exit 2 when needs_flow_sync=true after
  Serena is current. Emits 9-step plan summary referencing flow-post-task-sync
  skill which handles: checks → atomic commits → push → ff-merge into default →
  push default → fullrepo publish → cleanup merged branches/worktrees.
- Orchestrator (ry-start, flow-post-task-sync skill, main session) is the
  executor of merge/push/publish/cleanup under model judgement.
- Loop guard preserved: same fingerprint + stop_hook_active=true → exit 0.
- Flow lifecycle when ry-start finishes a task wave:
    1. Task work commits land on feature branch.
    2. Stop fires.
    3. Serena hook checks memory freshness; blocks Stop if stale.
    4. Orchestrator invokes flow-memory-sync subagent (or fallback workflow).
    5. After Serena is current, Flow hook checks git/docs/fullrepo/cleanup
       state; blocks Stop if needs_flow_sync=true.
    6. Orchestrator runs flow-post-task-sync skill which executes the full
       pipeline.
    7. needs_flow_sync=false, Stop allowed.
