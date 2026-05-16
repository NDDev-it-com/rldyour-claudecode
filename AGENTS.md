# AGENTS.md — rldyour-claude

Personal Claude Code plugin marketplace by `rldyourmnd`. The repository ships nine plugins that compose an opinionated SDLC, semantic-code, MCP transport, security, browser, design, LSP, and rules layer for Claude Code. There is no runtime application code — every artifact in this repo is plugin metadata, skills, slash commands, agents, hooks, scripts, and references.

This `AGENTS.md` is the concise root project-instruction file for any AI agent working in this repository — cross-tool standard governed by the Linux Foundation Agentic AI Foundation (AAIF) since 2025-12-09 (see https://agents.md/). The deep Claude Code-native memory lives in `./.claude/CLAUDE.md` and contains subagent matrix, hook canon, skill-listing budget, frontmatter conventions, and Don't/Done rules that other AI tools don't need.

<!-- Maintainer note (HTML comments are not parsed by most AI tools): Anthropic's claude-plugins-official marketplace ships `.claude-plugin/marketplace.json` + 8+ first-party plugins (pr-review-toolkit, feature-dev, hookify, ralph-loop, security-guidance, plugin-dev, etc.) but no root AGENTS.md or CLAUDE.md (verified 2026-05-15). Our two-file split is justified by cross-tool ambition (AGENTS.md is read by 30+ tools / 60k+ repos per agents.md spec, May 2026) plus Claude Code-deep specifics. Both files dual-purpose: full information for each agent class, no `@import` redirection. Keep this file under 200 lines. -->


## Source Of Truth

- `./.claude-plugin/marketplace.json` — marketplace manifest, `pluginRoot: ./plugins`, source form `./plugins/<name>`.
- `./plugins/<name>/.claude-plugin/plugin.json` — per-plugin manifest. Required: `$schema`, `name`, `version` (per-plugin values can differ), `description`, `author`, `license`, `homepage`, `repository`, `keywords`.
- `./plugins/rldyour-mcps/.mcp.json` — single-owner MCP transport for the whole marketplace.
- `./plugins/rldyour-flow/hooks/hooks.json` and `./plugins/rldyour-serena-mcp/hooks/hooks.json` — only two plugins ever own hooks.
- `./plugins/rldyour-flow/references/*.md` — durable contracts for `ry-init`, `ry-start`, `ry-newp`, `ry-review`, `ry-deploy`, post-task sync, reviewer protocol, and source citations.
- `./plugins/rldyour-rules/references/*.md` — engineering rules: architecture, dependency, quality gates, project instructions and ADRs.
- `./.serena/memories/CORE-01-INDEX.md` — numbered Serena memory map for future GPT/Claude/Codex sessions.

## Repository Layout

```
.claude-plugin/marketplace.json
plugins/
  rldyour-mcps/        # transport — 13 pinned MCP servers (.mcp.json)
  rldyour-serena-mcp/  # Serena workflow + memory sync + 4 lifecycle hooks
  rldyour-flow/        # ry-init/start/newp/review/deploy + 6 reviewer agents + 4 hooks + 7 scripts
  rldyour-explore/     # ry-explore agent (opus[1m], max effort) + tech/web research skills
  rldyour-security/    # owasp-top-10-implementation + ry-sec-review
  rldyour-browser/     # browser-validation/debug/tool-routing (skills-only)
  rldyour-design/      # ry-design + figma-to-code + design-system + fsd + design-validation
  rldyour-lsps/        # lsp-routing/health-check/setup + serena-lsp-integration
  rldyour-rules/       # quality-first + architecture/dependency/implementation/verification + ry-rules-review
.serena/               # agent-only Serena project state (fullrepo-managed)
.gitignore             # blocks secrets, runtime markers, browser artifacts
```

## Plugin Boundaries (hard rules)

- `rldyour-mcps` is the single owner of any `.mcp.json`. Other plugins consume MCP transport from it; they never declare MCP servers themselves.
- Only `rldyour-flow` and `rldyour-serena-mcp` declare `hooks.json`. No other plugin attaches Claude Code lifecycle hooks.
- One domain per plugin. No catch-all plugins. Cross-plugin overlap is forbidden.
- `rldyour-design` and `rldyour-browser` are skills-only and use Figma/shadcn/Playwright/Chrome DevTools transport from `rldyour-mcps`; `rldyour-design` also depends on `rldyour-browser` for validation routing.

## Codex CLI Compatibility

OpenAI Codex CLI reads this `AGENTS.md` before starting work. Codex layers configuration: global `~/.codex/AGENTS.md` plus repository-level files concatenated from root down — files closer to the active directory override earlier guidance. Codex is trained to run any test/quality commands explicitly listed in `AGENTS.md` before finishing a task; the **Validation And Setup** section below is the deterministic command set Codex (and Claude Code, and any other AI agent) should run to verify a change. This repo has no nested `AGENTS.md` files. Spec source: `https://agents.md/` — Linux Foundation Agentic AI Foundation since 2025-12-09. Codex-specific source: `https://developers.openai.com/codex/guides/agents-md`.

## Validation And Setup

- Validate manifests: `claude plugin validate <path>` from repo root after editing any `marketplace.json` or `plugin.json`. CI runs this on every PR via `.github/workflows/validate.yml`.
- Tag releases: `claude plugin tag --push` (v2.1.119+) validates that `plugin.json` and marketplace entry agree on version, refuses dirty worktrees and pre-existing tags. Tag convention: `<plugin-name>--v<version>`.
- Prune orphaned dependencies: `claude plugin prune` (v2.1.121+); `claude plugin uninstall <plugin> --prune` cascades.
- Inspect a plugin's component inventory and projected per-session token cost: `claude plugin details <name>` (v2.1.139+; v2.1.142 added LSP server visibility to details output).
- Minimum Claude Code version: **v2.1.111+** as this repository's compatibility floor for bracketed extended-context model syntax used by the `ry-explore` agent. `[1m]` model availability remains account/plan-dependent. Current local: **v2.1.143** (verification range v2.1.111-v2.1.143, May 2026).
- Bootstrap a fresh checkout: `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --bootstrap-init` — installs `.git/info/exclude` block for agent-only files and restores or publishes `fullrepo`.
- Audit git/branch/worktree state: `bash plugins/rldyour-flow/scripts/git_sync_audit.sh`.
- Quality checks for product repositories that consume this marketplace: `bash plugins/rldyour-flow/scripts/detect_project_checks.sh`. This repository has no runtime test suite by design.
- LSP health for consumer projects: `bash plugins/rldyour-lsps/scripts/check_lsps.sh`.

## SDLC Workflow

Five orchestrated lifecycle skills live in `rldyour-flow`. Each has a Russian-leading skill description.

- `/rldyour-flow:ry-init` — read-only scope discovery and context pack, mandatory before non-trivial work.
- `/rldyour-flow:ry-start` — full task lifecycle: init → research → plan → implement → quality gates → reviewer subagents → post-task sync.
- `/rldyour-flow:ry-newp` — design new project: skeptical questions → research → architecture docs → optional scaffold.
- `/rldyour-flow:ry-review` — report-only deep review with reviewer tracks (architecture/quality/consistency/integration/verification/security).
- `/rldyour-flow:ry-deploy` — deploy with local↔GitHub↔server sync, log checks, fix-forward, docs/git finalization.

Reviewer subagents live in `plugins/rldyour-flow/agents/flow-*-review.md`. All run on `model: sonnet`, `effort: high`, `maxTurns: 36` (security: `42`), with explicit `tools` allowlist (`Read`, `Grep`, `Glob`, `Bash` + Serena/Context7/DeepWiki/Grep MCP wildcards; `flow-security-review` adds `WebFetch`, `WebSearch`, Semgrep MCP for CVE lookups and SAST) and distinct colors (architecture: blue, quality: green, consistency: purple, integration: orange, verification: pink, security: red). They are read-only and self-contained — explicit allowlist isolates them from any future edit-like tool Claude Code might add. Generous `maxTurns` is intentional — MCP-heavy toolsets consume turns on tool plumbing.

Reviewer output uses a **file-first transport contract** (full text in `plugins/rldyour-flow/references/reviewer-protocol.md`, section "Output Transport") to work around the Claude Code 2.0.77+ `task.output` regression (Anthropic issues [`#16789`](https://github.com/anthropics/claude-code/issues/16789), [`#20531`](https://github.com/anthropics/claude-code/issues/20531), [`#23463`](https://github.com/anthropics/claude-code/issues/23463), closed as "not planned"). Orchestrator (`ry-start` / `ry-review`) generates `run_id = <UTC-ISO-compact>-<git-short-sha>` (minute-precision UTC timestamp), computes `report_dir = .serena/reviews/<run_id>/` (gitignored runtime artefact alongside `.serena/cache/` and `.serena/diagnostics/`), and injects both into every reviewer prompt. Each reviewer writes the full long-form report to `<report_dir>/<reviewer-name>.md` via `Bash` using `<<'RLDYOUR_REPORT_EOF'` heredoc (unique multi-char marker prevents accidental early termination on short tokens) and returns a compact summary ≤ 4 KB (Report path, severity counts, all findings as one-liners capped at 30 entries). 6 tracks × ≤ 4 KB = ≤ 24 KB injected into parent context, structurally preventing the overflow class. Orchestrator MUST `Read` the per-reviewer report file for every `critical` and `high` finding before disposition.

## Hooks Lifecycle

Two plugins coordinate hooks. `flow.stop_post_task_sync.sh` derives `serena_current` by calling `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`; it does not consume output from the Serena Stop hook.

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

Most hooks are advisory and exit `0`; Stop hooks are advisory enforcement gates that write guidance to stderr and block with `exit 2` when memory or post-task sync is required. The single hook that performs a bounded worktree mutation is `session_start_worktree_bootstrap.sh` — it runs `fullrepo_sync.py --restore` (never `--publish`, never touches origin) only when an agent-only marker is missing in the active worktree. Skip flags: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT`, `RLDYOUR_SKIP_FLOW_COMMIT_ADVICE`, `RLDYOUR_SKIP_STOP_GATES`, `RLDYOUR_SKIP_FLOW_SYNC`, `RLDYOUR_SKIP_SERENA_SYNC`, `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP`.

## Worktree Workflow

Multiple git worktrees can run in parallel — one worktree per feature, each driving its own Claude Code session. All worktrees share the main `.git` database but each gets its own working tree, its own per-worktree `.git/info/exclude` block, and its own copy of agent-only files. Per-worktree `.serena/memories/` prevents concurrent sessions from stomping on each other; reconciliation happens via `flow-post-task-sync` publishing to `fullrepo`.

```bash
scripts/worktree_add.sh <branch> [path]                          # create worktree + bootstrap agent-only context
RLDYOUR_DRY_RUN=1 scripts/worktree_add.sh <branch>               # preview
RLDYOUR_WORKTREE_BASE_REF=HEAD scripts/worktree_add.sh <branch>  # branch from local HEAD instead of origin/main
git worktree remove <path>                                       # tear down
```

The helper invokes `fullrepo_sync.py --restore` (never `--publish`) and aborts with a clear error if `origin/fullrepo` does not yet exist — publishing is reserved for the orchestrator (`flow-post-task-sync` skill or explicit `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --publish` from the main worktree).

Automatic bootstrap on `claude` startup: `hooks/session_start_worktree_bootstrap.sh` runs `fullrepo_sync.py --restore` (never `--publish`) when an agent-only marker is missing. Skip flag: `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1`.

Relevant Claude Code settings (in `~/.claude/settings.json`): `worktree.baseRef` (`"fresh"` default, or `"head"` to preserve unpushed commits), `worktree.symlinkDirectories` (keep `.serena/` and `.claude/` OUT), `worktree.sparsePaths` (large monorepos only).

Trust model: agent-only files restored into a fresh worktree come from `origin/fullrepo`. A compromised origin (lost GitHub credentials, force-pushed fullrepo, MITM on unsigned git transport) would inject the attacker's `AGENTS.md` / `.claude/CLAUDE.md` / `.serena/memories/**` into every new worktree on next `claude` startup. Mitigations already in place: 2FA on GitHub, branch protection on `fullrepo`, and the optional disable switch `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1` for paranoid sessions. This is the same trust boundary as the existing manual `fullrepo_sync.py --bootstrap-init`; the new SessionStart hook automates it, it does not expand the attack surface.

## Fullrepo Branch Policy

Agent-only files live on the `fullrepo` branch only. Patterns are defined in `plugins/rldyour-flow/scripts/fullrepo_sync.py` (`AGENT_ONLY_PATTERNS`) and include: root `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, `GEMINI.md`, `QWEN.md`, `.cursorrules`, `.windsurfrules`, `.claude/**`, `.cursor/rules/**`, `.gemini/**`, `.roo/**`, `.windsurf/**`, `.openhands/**`, `.aider*`, `.agents/skills/**`, `.agents/commands/**`, `.agents/hooks/**`, `.github/copilot-instructions.md`, `.github/instructions/**`, `.github/prompts/**`, `.serena/project.yml`, `.serena/memories/**`, `.serena/plans/**`, `.serena/research/**`, `.serena/newproj/**`, `.serena/deploy/**`.

Subcommands:

- `--bootstrap-init` — install excludes, restore remote `fullrepo`, publish first snapshot when missing, migrate tracked agent-only files out of the index.
- `--restore` — fetch and restore agent-only files from `origin/fullrepo` and install excludes.
- `--migrate-main` — `git rm --cached` tracked agent-only files; worktree files survive.
- `--publish` — push snapshot tree to `fullrepo` with `--force-with-lease`.
- `--status-json` — machine-readable state.

`main` must never carry agent-only files. `fullrepo` is regenerated on every meaningful change.

## MCP Transport (`rldyour-mcps/.mcp.json`)

13 pinned servers: `serena-agent==1.3.0` (with `--context=agent` for generic CLI agents like Claude Code, **`alwaysLoad: true`** since v2.1.121+ — eager startup because Serena drives every UserPromptSubmit hook; 1.3.0 mode-selection refactor scopes the tool surface to 28 tools under `agent` context, all workflow tools we use present), `@modelcontextprotocol/server-sequential-thinking@2025.12.18`, `@playwright/mcp@0.0.75`, `chrome-devtools-mcp@0.26.0`, `@upstash/context7-mcp@2.2.5`, `deepwiki` (HTTP `mcp.deepwiki.com`), `grep` (HTTP `mcp.grep.app`), `semgrep==1.163.0`, `shadcn@4.7.0`, `dart mcp-server`, `figma` (HTTP `mcp.figma.com`), `openai-docs` (HTTP), `github` (local stdio `github-mcp-server stdio` — Homebrew bottle v1.0.4 pinned in `config/mcp-runtime-versions.env`; defaults to toolset `repos,issues,pull_requests,users,context`; **not** the Copilot-gated `api.githubcopilot.com/mcp/` HTTP endpoint). Required env: `CONTEXT7_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`. Required host binaries: `github-mcp-server` (via `brew install github-mcp-server`), `dart`.

MCP timeouts are controlled by Claude Code env vars: `MCP_TIMEOUT` for server startup (documented in MCP/env-var docs) and `MCP_TOOL_TIMEOUT` for per-tool-call timeout (confirmed in the v2.1.142 changelog for HTTP/SSE MCP requests). Per-server `startup_timeout_sec`/`tool_timeout_sec` keys in `.mcp.json` are NOT documented and silently ignored — do not add them.

## Cross-Plugin Dependencies

Each consumer plugin declares its dependency on `rldyour-mcps` (and `rldyour-serena-mcp` for `rldyour-flow`) in `plugin.json` under `"dependencies": ["..."]`. This array of plugin names lets `claude plugin install` resolve transitive installs and surface conflicts. Schema source: https://code.claude.com/docs/en/plugins-reference#metadata-fields.

Current dependency graph:

| Plugin | Depends on |
|---|---|
| rldyour-mcps | (none) |
| rldyour-serena-mcp | rldyour-mcps |
| rldyour-flow | rldyour-mcps, rldyour-serena-mcp |
| rldyour-explore | rldyour-mcps |
| rldyour-security | rldyour-mcps |
| rldyour-browser | rldyour-mcps |
| rldyour-design | rldyour-mcps, rldyour-browser |
| rldyour-lsps | rldyour-mcps |
| rldyour-rules | rldyour-mcps |

## Tool Routing

- Code understanding: prefer Serena MCP tools (`get_symbols_overview`, `find_symbol`, `find_referencing_symbols`, `search_for_pattern`) over raw text reads. See `plugins/rldyour-serena-mcp/skills/serena-code-workflow/SKILL.md`.
- Memory writes: use `flow-memory-sync` subagent when Stop/post-task sync requires it; use the `serena-memory-sync` skill as the manual/fallback workflow. Memories are fact-only, use `CORE-01-INDEX.md` as the map, new topics use `AREA-01-SLUG.md`, and broad files must be split instead of expanded indefinitely.
- LSP / diagnostics / refactoring: route through `plugins/rldyour-lsps/skills/lsp-routing/SKILL.md`.
- Browser validation, debugging, performance: `plugins/rldyour-browser/skills/*`.
- Figma → code: `plugins/rldyour-design/skills/figma-to-code/SKILL.md`.
- Deep research: `/rldyour-explore:ry-explore` slash command runs `agents/ry-explore.md` (opus[1m], max effort, isolated context).
- Defensive security review: `/rldyour-security:ry-sec-review`.
- Architecture/quality/consistency/integration/verification/security review for an existing diff: `/rldyour-flow:ry-review`.

## Engineering Constraints

- Russian user-facing language; English repository artifacts (skill descriptions are Russian-leading with `EN triggers:` appended for cross-language LLM routing).
- Bilingual skill description pattern is a personal-marketplace UX innovation, not Anthropic canon (verified unique in production via 2026-05-15 audit). Token cost is ~1.5-2× pure-English; budget set via `skillListingBudgetFraction: 0.04` recommendation in `./.claude/CLAUDE.md`.
- Quality-first: no hacks, no fake checks, no swallowed errors. See `plugins/rldyour-rules/skills/quality-first-engineering/SKILL.md`.
- Plugin boundary discipline: see `plugins/rldyour-rules/skills/architecture-boundaries/SKILL.md`.
- Dependency policy: latest-compatible, source-backed, SLSA Level 2, SBOM and lockfile discipline. See `plugins/rldyour-rules/references/dependency-policy.md`.
- Conventional Commits for all changes. Atomic commits per logical unit.
- Never commit secrets, runtime markers, browser artifacts, local env files.
- All MCP server versions are pinned (stdio servers with `==X.Y.Z`; HTTP servers by URL).

## Done Criteria

- All touched manifests pass `claude plugin validate`.
- `git status` is clean of non-agent files; `.serena/` and other agent-only paths are excluded via `.git/info/exclude`.
- `fullrepo_sync.py --status-json` shows `tracked_agent_paths: []` on `main`.
- `fullrepo` is republished after any agent-only change.
- Conventional commits for source/docs/Serena knowledge are kept separate when it improves history clarity.
- Pre-existing reviewer subagents and skills referenced by new components actually exist on disk.

## Cross-Tool Support

`AGENTS.md` is the cross-tool agent-instruction standard (Linux Foundation AAIF, 60k+ adopting repos, 30+ supported tools per `https://agents.md/` as of May 2026): Claude Code, OpenAI Codex CLI, GitHub Copilot, Cursor, Aider, Devin, VS Code agents, JetBrains AI, Continue, Windsurf, Roo, OpenHands, Gemini Code Assist, Qwen Code, and others. This file contains every cross-tool fact needed to work on this marketplace: source-of-truth manifests, plugin boundaries, validation commands, SDLC workflow, hook lifecycle, worktree contract, fullrepo policy, MCP transport, cross-plugin dependencies, tool routing, engineering constraints, and done criteria.

Claude Code-specific deep memory (subagent matrix, hook canon details, skill-listing budget tuning, Claude Code changelog adoption, `/mcp`/`/hooks`/`/memory`/`/doctor` diagnostics, Claude-specific Don't/Done rules) lives in `./.claude/CLAUDE.md`. Both files are intentionally dual-source — no `@import` redirection — so each agent class loads only the relevant context without indirection. The split is verified consistent on every meaningful change wave through `python3 plugins/rldyour-flow/scripts/instruction_docs_state.py --json` and the `instruction-docs-sync` skill.

<!-- Living-doc note: when discovering a non-obvious project fact during work that another AI tool would also need (cross-tool concern), propose an AGENTS.md edit in the same change. Don't auto-generate. Claude Code-specific facts (skill listing, hook canon, subagent matrix) belong in ./.claude/CLAUDE.md instead. -->
