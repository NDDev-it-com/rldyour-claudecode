<!-- Memory Metadata
Last updated: 2026-05-17
Last commit: 6b59af7 fix(security): explicit https/http scheme guard in fetch_json
Scope: VERSION, CHANGELOG.md, README.md, .claude-plugin/marketplace.json, plugins/*/.claude-plugin/plugin.json, .github/workflows/validate.yml, .github/workflows/dependency-check.yml, .github/workflows/semgrep.yml, .github/workflows/actionlint.yml, .github/dependabot.yml, scripts/validate_marketplace.sh, scripts/validate_plugin_versions.py, scripts/smoke_serena_memory_taxonomy.sh, docs/release-process.md
Area: RELEASE
-->

# RELEASE-01-VALIDATION

## Purpose

Versioning, changelog, validation, tagging, and release evidence contracts for this marketplace.

## Source Of Truth

- `VERSION`: marketplace/release boundary version.
- `CHANGELOG.md`: Keep-a-Changelog release notes.
- `.claude-plugin/marketplace.json`: marketplace plugin versions.
- `plugins/<plugin>/.claude-plugin/plugin.json`: per-plugin behavior/cache-refresh versions.
- `README.md`: owner-facing catalog, version summary, smoke/check commands.
- `docs/release-process.md`: release process reference.
- `scripts/validate_marketplace.sh`: full validation harness.
- `scripts/validate_plugin_versions.py`: marketplace/manifest version consistency.
- `scripts/smoke_serena_memory_taxonomy.sh`: focused Serena memory taxonomy regression smoke.
- `scripts/validate_reviewer_contracts.sh`: reviewer output transport contract drift detector; asserts 9 invariant types across 6 reviewer agents + `reviewer-protocol.md`. Wired into `scripts/validate_marketplace.sh` after the "Agent tools allowlist validation" step.

## Current Behavior

- Current release boundary at HEAD: `VERSION` is `0.2.3` (verified at `VERSION` file, HEAD `5bd57ae`).
- Per-plugin versions (verified from `python3 scripts/validate_plugin_versions.py` at HEAD `5bd57ae`):
  - `rldyour-mcps`: `0.2.1`
  - `rldyour-serena-mcp`: `0.2.1`
  - `rldyour-flow`: `0.2.3` (wave-2 reviewer transport hardening + wave-3 em-dash normalization)
  - `rldyour-explore`: `0.2.1`
  - `rldyour-browser`: `0.2.1`
  - `rldyour-design`: `0.2.1`
  - `rldyour-lsps`: `0.2.1`
  - `rldyour-rules`: `0.2.1`
  - `rldyour-security`: `0.2.1`
- **0.2.1 release** (`e3d146b`): `rldyour-flow` bumped to `0.2.1` for the D29 reviewer output transport contract (file-first output, `.serena/reviews/` runtime dir, run_id coordination, `RLDYOUR_REPORT_EOF` precursor pattern). Tags pushed: `marketplace--v0.2.1`, `rldyour-flow--v0.2.1`. All other 8 plugins remained at `0.2.0`.
- **0.2.2 release** (`0ff613d`): `rldyour-flow` bumped to `0.2.2` for wave-2 reviewer transport hardening after self-bootstrap review wave `2026-05-16T1433Z-e3d146b`. Changes: `RLDYOUR_REPORT_EOF` heredoc EOF marker replacing short tokens (`MD`, `EOF`) that could cause early termination; explicit Bash write boundary `<report_dir>/<reviewer-name>.md`; mandatory orchestrator `Read` of each `critical`/`high` report file before disposition; `run_id` canonicalized to `<UTC-ISO-compact>-<git-short-sha>`; `info` severity added to enum in `reviewer-protocol.md` line 24; `.serena/diagnostics/**` and `.serena/reviews/**` added to `RUNTIME_EXCLUDE_PATTERNS` in `fullrepo_sync.py` lines 50-53. Tags pushed: `marketplace--v0.2.2`, `rldyour-flow--v0.2.2`. Verified via `git tag --list "*--v0.2.2"` at HEAD `0ff613d`.
- **HEAD `61b913d` (no version bump)**: `scripts/validate_reviewer_contracts.sh` added (173 lines); wired into `scripts/validate_marketplace.sh`. This is a repo-level script addition only - no plugin runtime files changed, no `rldyour-flow` version bump, no new release tag. Wave-3 audit (`2026-05-16T1538Z-0ff613d`) F-3 verification info finding (confidence 85: "no automatic check for heredoc marker drift") closed via this script. All per-plugin versions remain at 0.2.0 / `rldyour-flow` at 0.2.2.
- **All 4 new tags in this wave** (verified via `git tag --list "*--v0.2.1" "*--v0.2.2"`): `rldyour-flow--v0.2.1`, `marketplace--v0.2.1` (backfilled at `e3d146b`), `rldyour-flow--v0.2.2`, `marketplace--v0.2.2` (at `0ff613d`).
- **HEAD `557bc00` (no version bump)**: 4 commits close 5 audit findings D31-D35 from review wave `2026-05-16T1859Z-61b913d`. Changes: loop guard fingerprint field parity in `flow_post_task_state.py` (D31, `23901c6`); compound `.sync_marker` in `stop_memory_sync.sh` (D32, `23901c6`); non-dict payload stderr surface in `serena_memory_state.py` (D33, `d563ea5`); CI steps `validate_reviewer_contracts.sh` + `smoke_mcp_runtime.sh` added to `.github/workflows/validate.yml` (D34, `dcbc7cc`); semgrep container digest-pinned in `.github/workflows/semgrep.yml` (D35, `dcbc7cc`); `CHANGELOG.md` `[Unreleased]` section updated (`557bc00`). No `plugins/*/plugin.json` version bumps - all changes are script body / hook script / CI workflow files. VERSION remains `0.2.2`.
- **HEAD `00d3f82` (no version bump)**: 3 doc-fix commits close wave-3 audit findings D36-D38. Changes: `validate_reviewer_contracts.sh` header corrected to list all 9 invariants with concrete PASS breakdown (`6f0c70d`); `rldyour-rules` cross-plugin path to `fullrepo_sync.py` canonicalized from `${CLAUDE_PLUGIN_ROOT}/../rldyour-flow/scripts/...` to `python3 "$(git rev-parse --show-toplevel)"/plugins/rldyour-flow/scripts/...` (`9a49121`, PATTERNS-01-CANONICAL F-2 closure); `config/REVIEW.md.template` added (68 lines, all 6+ sections, `00d3f82`, verification F-4 closure). No `plugins/*/plugin.json` version bumps. VERSION remains `0.2.2`.
- **0.2.3 release** (`d58f4ce` + `c041fac` + `5bd57ae`, wave-5/6/7, 2026-05-17): marketplace `VERSION` bumped to `0.2.3`. `rldyour-flow` bumped `0.2.2 -> 0.2.3`. All 8 other plugins bumped `0.2.0 -> 0.2.1` (em-dash normalization touched `plugin.json` description and skill bodies). 603 em-dash occurrences replaced codebase-wide. Security wave D39-D41 (`c041fac`): egress-policy block in all 4 CI workflows, fullrepo false-positive fix in `local_git_ai_guard.sh`, `RLDYOUR_FORCE_BOOTSTRAP=1` audit trail in `bootstrap_check.sh`. Security/verification wave D42-D46 (`5bd57ae`): INJECTION_MARKERS + BiDi BIDI_CONTROLS, `sanitize_for_advisory()` helper, `openai-docs` in READ_ONLY_BY_DESIGN_MCPS, `smoke_serena_memory_taxonomy.sh` D20+D21 completeness step, `validate_marketplace.sh` inline R5 rationale. Tag planned: `marketplace--v0.2.3`. Cache namespace: `~/.claude/plugins/cache/rldyour-claudecode/rldyour-flow/0.2.3/`; all other 8 plugins at `0.2.1/`. Verified via `cat VERSION` and `python3 scripts/validate_plugin_versions.py` at HEAD `5bd57ae`.
- `CHANGELOG.md` `[0.2.2] - 2026-05-16` follows Keep-a-Changelog 1.1.0 with `### Changed` and `### Notes` subsections. `[Unreleased]` compare base updated to `marketplace--v0.2.2...HEAD`. `[0.2.2]` reference-link points to `https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.2.2`. Verified at `CHANGELOG.md` lines 742-743 at HEAD `0ff613d`.
- `CHANGELOG.md` `[0.2.1] - 2026-05-16` preserved: D29 reviewer output transport contract, file-first output, `.serena/reviews/` runtime artifact policy, `marketplace--v0.2.1` release boundary. Verified at HEAD `0ff613d`.
- `scripts/validate_marketplace.sh` is the broad local gate. CI workflows: `validate.yml` (SHA-pinned actions, harden-runner, `claude-code@2.1.143`, top-level `permissions: {}`), `dependency-check.yml` (same hardening), `semgrep.yml` (Semgrep OSS SAST), `actionlint.yml` (workflow YAML linter). Verified at HEAD `0ff613d`.

## Contracts And Data

- Plugin cache refresh depends on per-plugin `plugin.json` version strings. Content-only plugin changes under the same version can be missed by the runtime cache.
- **Post-change bump policy (project rule, owner-set 2026-05-17)**: after any change touching marketplace or plugin files - including documentation, memories, agent-only context, scripts, hooks, references, or skill bodies - bump BOTH the affected plugin versions AND the marketplace `VERSION`. This is stronger than the AGENTS.md cache-refresh rule (which limits bumps to `SKILL.md/agent.md/hooks.json/.mcp.json` runtime-cache-relevant changes). Rationale (owner): "после изменений версии всего маркетплейса и плагинов должны подниматься, чтобы все точно обновлялось". Concrete: every wave that modifies any tracked or agent-only file produces a new `VERSION` and at least one plugin version bump. Memories MUST also be updated and actualized in the same wave.
- If a plugin's runtime behavior changes, bump that plugin version and align the marketplace entry.
- If a change affects the overall release boundary, update `VERSION` and `CHANGELOG.md`.
- Tag convention for plugins: `<plugin-name>--v<version>` via `claude plugin tag --push`.
- Tag convention for marketplace boundary: `marketplace--v<version>` (introduced in 0.2.0; pushed manually alongside plugin tags). This is NOT a plugin tag - it marks the aggregate release boundary in the CHANGELOG reference-links block.
- Tags should be created only after the worktree is clean for tracked files and validation passes.
- Cache namespace: `~/.claude/plugins/cache/rldyour-claudecode/<plugin>/<version>/`; for this wave `rldyour-flow` is `~/.claude/plugins/cache/rldyour-claudecode/rldyour-flow/0.2.3/` and all other 8 plugins are at `0.2.1/`.

## Change Rules

- For manifest or version changes, run `python3 scripts/validate_plugin_versions.py` and `bash scripts/validate_marketplace.sh`.
- For MCP runtime changes, also run `python3 scripts/check_mcp_runtime_versions.py` and relevant MCP smoke checks.
- For hook or memory-sync behavior changes, run shell syntax checks, analyzer/state script checks, `bash scripts/smoke_hooks.sh`, and `bash scripts/smoke_serena_memory_taxonomy.sh`.
- Avoid `scripts/smoke_fullrepo_sync.sh` after editing agent-only files unless prepared to restore/reapply them; it runs `--bootstrap-init` and can restore agent-only files from `origin/fullrepo`.

## Cross-References

- Open and closed debt record: [[TECHDEBT-01-NOW]] (D28 0.2.0 boundary, D24-D27 Wave 5 closures, D19 R5 closure, D29 reviewer output transport 0.2.1/0.2.2, D31-D35 wave-3 audit closures, D36-D38 doc fixes, D39-D46 wave-3 security/verification 0.2.3).
- Validation harness patterns: [[PATTERNS-01-CANONICAL]] (commit message, memory file pattern, tag conventions).
- Plugin manifest and Claude Code version facts: [[CLAUDECODE-01-PLUGIN-CANON]].
- Marketplace architecture and plugin version map: [[CORE-02-MARKETPLACE]].
- Hook lifecycle and smoke gates: [[HOOKS-01-LIFECYCLE]].
- Post-task SDLC sync workflow: [[FLOW-01-SDLC]].
- Memory taxonomy and index: [[CORE-01-INDEX]].
- MCP transport version pins: [[MCP-01-TRANSPORT]].
- OWASP security precision (D22): [[SECURITY-01-OWASP]].

## Verification

- `python3 scripts/validate_plugin_versions.py`: version consistency.
- `bash scripts/validate_marketplace.sh`: full marketplace validation including Serena taxonomy smoke.
- `git diff --check`: whitespace sanity.
- `python3 plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py --from-ref HEAD --to-ref HEAD`: no-op analyzer sanity.
- `bash scripts/smoke_serena_memory_taxonomy.sh`: targeted memory taxonomy gate.
- `bash scripts/smoke_hooks.sh`: hook smoke.
- `bash scripts/smoke_mcp_runtime.sh`: MCP runtime smoke.
- `bash scripts/smoke_mcp_capabilities.sh`: MCP capability smoke; `figma` can be skipped when auth/session env is absent.
- `bash scripts/validate_reviewer_contracts.sh`: proves reviewer output transport contract (9 invariant types, 6 agents + protocol) is drift-free; wired into `bash scripts/validate_marketplace.sh`.
