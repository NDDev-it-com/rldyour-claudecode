# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and marketplace/plugin versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Root-level public files: `README.md`, `CHANGELOG.md`, `VERSION`, `LICENSE`.
- Codex-parity operations harness ported under Claude Code conventions:
  marketplace validation script, smoke tests for hooks/MCP/fullrepo/branch-cleanup,
  scheduled MCP runtime pin freshness CI, plugin-version validator, instruction-docs
  validator, skill-routing policy tests, release manifest, runtime-version drift check,
  diagnostics collection, local git pre-push guard installer.
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

### Changed

- Stop hooks restored to advisory enforcement gates: hooks compute
  machine-readable state and block Stop with `exit 2` when work remains, but
  do not perform high-blast-radius git operations (push, merge, force-with-lease,
  branch deletion). Those operations belong to the `flow-post-task-sync` skill
  executor under model judgement.
- `reviewer-protocol.md` documents the canonical effort/maxTurns/color matrix
  for reviewer subagents and the `+6 turns` security-track variant-hunt rule.

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
