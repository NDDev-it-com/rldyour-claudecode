# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and marketplace/plugin versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
