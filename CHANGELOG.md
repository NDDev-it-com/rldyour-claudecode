# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and marketplace/plugin versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.4] - 2026-05-15

### Changed

- `plugins/rldyour-serena-mcp`:
  - Added `scripts/analyze_sync_scope.py` impact analysis and persisted analysis payload in
    `.serena/.serena_sync_state.json` for deterministic, low-noise memory-sync targeting.
  - Updated hook pipeline so `mark_sync_required.sh` stores `non_knowledge_changed_files`,
    `analysis.areas`, and `analysis.memory_targets`; `stop_memory_sync.sh` prints analysis context
    (risk profile/high-priority areas/memory targets) when stale.
  - Expanded analyzer coverage for agent-only instruction paths, plugin commands, MCP transport,
    MCP runtime config, release/version files, and repository docs.
  - Ensured empty commit ranges produce empty memory targets to avoid no-op sync noise.
  - Bumped plugin version to `0.1.4` in plugin manifest and marketplace entry.
- Refined `.serena/memories/serena_memory_sync_protocol_2026-05.md` as a durable protocol memory for
  Serena lifecycle, marker payload contracts, and memory-sync execution rules.
- Synchronized `AGENTS.md` and `.claude/CLAUDE.md` with current hook/flow dependency contracts and
  Claude Code v2.1.142 documentation facts.

## [0.1.3] - 2026-05-15

### Changed

- `plugins/rldyour-mcps/.mcp.json` updated MCP runtime pins to latest verified:
  - `chrome-devtools-mcp` `0.25.0` → `0.26.0`
  - `semgrep` `1.162.0` → `1.163.0`
- `config/mcp-runtime-versions.env` aligned with MCP pin updates.
- `plugins/rldyour-mcps/README.md` updated transport documentation for GitHub MCP stdio transport and current CC context behavior note.
- `AGENTS.md` and `.claude/CLAUDE.md` synchronized with local Claude Code `v2.1.142` and verified MCP pin set.
- `plugins/rldyour-mcps` version bumped to `0.1.3` in both `plugin.json` and marketplace manifest to ensure cache refresh on `claude plugin update`.

## [0.1.2] - 2026-05-13

Hotfix for GitHub MCP server: the previous `https://api.githubcopilot.com/mcp/` HTTP endpoint is entitlement-gated and returns `HTTP 403 "unauthorized: not authorized to use this Copilot feature"` for accounts without an active GitHub Copilot allowlist, even when the bearer PAT is otherwise valid. Switched to the canonical local stdio transport via the Homebrew-installed `github-mcp-server` binary (v1.0.4, released 2026-05-11), which works with a standard `gho_*`/`github_pat_*` PAT and exposes 39 tools by default (`repos,issues,pull_requests,users,context` toolset). Cache-bump release so users get the new `.mcp.json` on `claude plugin update`.

### Fixed

- `plugins/rldyour-mcps/.mcp.json` `github` entry rewritten from HTTP transport (`api.githubcopilot.com/mcp/`, Copilot-gated) to local stdio `github-mcp-server stdio --toolsets=repos,issues,pull_requests,users,context` with `GITHUB_PERSONAL_ACCESS_TOKEN` env. Requires `brew install github-mcp-server` (or equivalent) on PATH; minimum version v1.0.4. PAT scopes: `repo` + `read:org` (Copilot subscription not required).
- `scripts/smoke_mcp_capabilities.sh` no longer blanket-passes HTTP 401/403 for `HTTP_AUTH_GATED` servers — that shortcut hid the exact 403 entitlement-denial above. Now performs a real MCP `initialize` JSON-RPC handshake against HTTP endpoints, parses both `application/json` and `text/event-stream` response bodies, checks `result.serverInfo.name`, and classifies failures: 401 without auth → SKIP (reachable, no creds), 401 with auth → FAIL (token rejected), 403 → FAIL with explicit "switch to stdio github-mcp-server" hint, 200 without `serverInfo` → FAIL (silent-misconfig catch). Sends canonical `MCP-Protocol-Version` header. `figma` remains in `HTTP_AUTH_GATED` (accepts 200 without `serverInfo` until session id is established); `github` removed because it is now stdio.

### Changed

- `scripts/check_mcp_runtime_versions.py` gained a `SYSTEM_BINARY_TO_ENV` track that probes host binaries via `<binary> --version` and enforces parity with the env pin. Used for `github-mcp-server`. Missing binary on PATH reports `INFO` (not `FAIL`) so CI without Homebrew does not regress. Drift between local binary and env pin reports `FAIL` with a `brew upgrade` hint.
- `config/mcp-runtime-versions.env`: added `GITHUB_MCP_SERVER_VERSION=1.0.4`; removed `GITHUB_MCP_URL` (no longer HTTP). Comment block expanded to document system-binary servers (github, dart-flutter).

### Removed

- `GITHUB_MCP_URL` env entry and the corresponding `github → HTTP_TO_ENV` row in `check_mcp_runtime_versions.py`. The HTTP-transport pattern for github MCP is preserved in `anthropics/claude-plugins-official` for Copilot users; we cannot use it without an allowlist.

## [0.1.1] - 2026-05-12

Release boundary cut after the 2026-05-08..2026-05-12 wave of best-practice, MCP-runtime, capability-smoke, serena-bump, audit and worktree-workflow commits accumulated in the `[Unreleased]` block. Bumps every plugin from `0.1.0` to `0.1.1` so that the Claude Code plugin cache at `~/.claude/plugins/cache/rldyour-claude/<plugin>/<version>/` actually refreshes on next `claude plugin update` (cache compares plugin.json `version` strings, so content-only changes under the same version are silently ignored by the user-facing runtime).

### Changed

- Bumped pinned MCP runtime versions after manual launcher smoke
  (release notes verified via GitHub Releases on 2026-05-12):
  - `@playwright/mcp` `0.0.74` → `0.0.75` (bug fixes: serialize shared browser
    launch in `--isolated`, forward browser-level CDP commands in extension
    mode; we use neither, low risk).
  - `@upstash/context7-mcp` `2.2.4` → `2.2.5` (accept hallucinated arg names
    on `tools/call` requests; backwards-compatible quality fix).
  - `semgrep` `1.161.0` → `1.162.0` (taint tracking through nested functions,
    ~5x faster JSON rule parsing; backwards-compatible).
- `scripts/check_mcp_runtime_versions.py` now also enforces URL parity for
  the `github` HTTP MCP server (added `GITHUB_MCP_URL` to env file and to
  `HTTP_TO_ENV`). Closes a tracking gap left by 47387ee when github moved
  from stdio to HTTP transport.

- `serena-agent` `1.2.0` → `1.3.0` (released 2026-05-11). The 81-commit
  delta includes new LSP tools (`find_declaration`, `find_implementations`,
  `get_diagnostics_for_file`, `get_diagnostics_for_symbol`), Ada/SPARK and
  Angular/HTML/SCSS experimental language support, the "Revamp mode
  selection" mode-system refactor, and BSL/Lombok improvements. Breaking
  change for `project.yml`: `base_modes` override is replaced by
  `added_modes`. We do not override `base_modes` in `.serena/project.yml`,
  so the bump is non-breaking for this marketplace. CLI flag `--context=agent`
  is preserved; `mcp__plugin_rldyour-mcps_serena__*` tool surface narrows
  from 45 to 28 tools under `agent` context (the mode refactor scopes tool
  exposure more tightly per context). `scripts/smoke_mcp_capabilities.sh`
  passed 13/13 servers post-bump on 2026-05-12.
- Stop hooks restored to advisory enforcement gates: hooks compute
  machine-readable state and block Stop with `exit 2` when work remains, but
  do not perform high-blast-radius git operations (push, merge, force-with-lease,
  branch deletion). Those operations belong to the `flow-post-task-sync` skill
  executor under model judgement.
- `reviewer-protocol.md` documents the canonical effort/maxTurns/color matrix
  for reviewer subagents and the `+6 turns` security-track variant-hunt rule.

### Added

- Worktree workflow:
  - `plugins/rldyour-flow/hooks/session_start_worktree_bootstrap.sh` —
    `SessionStart` hook (timeout 30s) that detects a fresh worktree
    (missing AGENTS.md / .claude/CLAUDE.md / .serena/project.yml marker)
    and auto-runs `fullrepo_sync.py --restore` to install the
    per-worktree `.git/info/exclude` block and check out agent-only
    paths from `origin/fullrepo`. Skip via
    `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1`. The hook never publishes,
    never mutates origin.
  - `scripts/worktree_add.sh` — one-step helper for the manual
    `git worktree add` flow: detects whether the branch is local /
    remote / new, runs `git worktree add` with the right ref, then
    bootstraps agent-only context. Supports `RLDYOUR_DRY_RUN=1` and
    `WORKTREE_BASE_REF=HEAD` to mirror Claude Code's
    `worktree.baseRef: "head"` setting.
  - AGENTS.md "Worktree Workflow" section documenting the manual + auto
    flow, the Claude Code v2.1.139 `worktree.{baseRef,symlinkDirectories,
    sparsePaths}` settings, and the maintenance contract (per-worktree
    `.serena/memories/`, reconciled via `flow-post-task-sync` publish).
- `scripts/smoke_mcp_capabilities.sh` — capability-level smoke harness.
  Spawns each pinned MCP server (stdio) or POSTs to its endpoint (HTTP),
  performs the JSON-RPC `initialize` + `tools/list` handshake, and asserts
  a non-empty tool set. Supports `--server <name>` for targeted probes,
  `--timeout <s>` for slow cold-starts, and `--skip-uvx` for fast CI
  subsets. Servers requiring credentials (`CONTEXT7_API_KEY`,
  `GITHUB_PERSONAL_ACCESS_TOKEN`) are SKIPped when env is absent rather
  than FAILing. Auth-gated HTTP endpoints (figma, github) accept 401/403
  as a passing handshake.
- Root-level public files: `README.md`, `CHANGELOG.md`, `VERSION`, `LICENSE`.
- Operations harness adapted to Claude Code conventions: marketplace
  validation script (`scripts/validate_marketplace.sh`), smoke tests for
  hooks / MCP runtime / fullrepo / branch-cleanup, scheduled MCP runtime
  pin freshness CI (`.github/workflows/dependency-check.yml`), plugin-version
  validator, instruction-docs validator, skill-routing policy tests, release
  manifest, runtime-version drift check, diagnostics collection, local git
  pre-push guard installer.
- `docs/` reference set for release process, rollback/restore, dependency updates,
  observability.
- `config/` directory: `mcp-runtime-versions.env` (canonical pinned launcher versions
  outside `.mcp.json`), `skill-routing-policy.json` (deterministic Russian/English
  prompt routing tests).
- Per-plugin `README.md` for the nine first-party plugins.
- `statusMessage` field on Stop/PostToolUse/SessionStart hook handlers for
  user-visible runtime indicators while hooks fire.
- `flow-memory-sync` plugin-shipped subagent with anti-hallucination contract
  (source-of-truth hierarchy code > tests > git diff > existing memories;
  citation per claim; removal-first principle; narrow tools — Serena memory
  MCP plus read-only Bash/Read/Grep/Glob; `disallowedTools: [Edit, Write,
  NotebookEdit]`). Invoked by orchestrator from Stop hook advisory.

### May-2026 best-practice waves (2026-05-08, applied incrementally on `main`)

- `optimize/may-2026-best-practices` (3fe9005..2e22652, 6 commits): unified
  reviewer subagent frontmatter, ×3 maxTurns increase to compensate MCP-rich
  toolsets, distinct colors per reviewer, `$schema` switched to SchemaStore
  canonical URL, serena MCP `alwaysLoad: true`, explicit `allowed-tools` on
  10 skills, `disable-model-invocation: true` on `ry-deploy` and `ry-newp`,
  reviewer-protocol aligned.
- `docs/canonical-may2026` (ca13470, 1 commit): aggressive `.claude/CLAUDE.md`
  rewrite (206 → 124 lines, removed duplicates with `AGENTS.md`), Skill Listing
  Budget section moved exclusively to CLAUDE.md (Claude Code-specific concern),
  HTML maintainer comments added (stripped from agent context per CC v2.1.72).
  Body fix `ry-explore.md` `maxTurns: 30 → 90` to match frontmatter.
- `polish/deferred-findings` (3ce7970..f23765d, 3 commits): `allowed-tools`
  on 4 of 5 design skills, `disable-model-invocation` on audit skills
  `ry-rules-review` and `ry-sec-review`, documented `maxTurns: 36/42` rationale
  in `reviewer-protocol.md`.
- `feat/memory-sync-subagent` (772f6e8, 1 commit): `flow-memory-sync` subagent
  introduced.

## [0.1.0] - 2026-05-07

### Added

- Initial controlled Claude Code marketplace with nine first-party plugins —
  `rldyour-mcps` (MCP transport, 13 pinned servers), `rldyour-serena-mcp`
  (semantic code workflow + memory sync + 4 lifecycle hooks), `rldyour-flow`
  (SDLC orchestrator: ry-init/start/newp/review/deploy + 6 reviewer subagents
  + 3 hooks + 7 scripts + 7 references), `rldyour-explore` (deep research via
  ry-explore agent, model `opus[1m]`), `rldyour-security` (OWASP Top 10 + ry-sec-review),
  `rldyour-browser` (Playwright + Chrome DevTools MCP), `rldyour-design`
  (Figma → code, FSD, shadcn/ui, ReactBits, browser validation),
  `rldyour-lsps` (LSP routing + brew-first install + Serena LSP integration),
  `rldyour-rules` (quality-first engineering + architecture/dependency policy +
  AGENTS.md/CLAUDE.md/MADR 4.0.0 conventions).
- Cross-plugin `dependencies` declared in each `plugin.json`; `rldyour-mcps`
  is the single owner of `.mcp.json`; only `rldyour-flow` and
  `rldyour-serena-mcp` declare `hooks.json`.
- `fullrepo` branch policy for portable agent-only files, with
  `fullrepo_sync.py` covering `--bootstrap-init`, `--restore`, `--migrate-main`,
  `--publish` (safe `--force-with-lease`), `--status-json`.
- GitHub Actions `validate.yml` workflow running `claude plugin validate` for
  marketplace and per-plugin manifests, JSON manifest parse, Python AST and
  shell syntax checks, frontmatter presence verification on all skills,
  agents, and commands.
