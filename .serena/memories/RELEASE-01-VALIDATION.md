<!-- Memory Metadata
Last updated: 2026-05-16
Last commit: 91cc276 docs: sync marketplace plugin versions to 0.2.0
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

## Current Behavior

- Current release boundary at HEAD: `VERSION` is `0.2.0` (verified at `VERSION` file, HEAD `91cc276`).
- All 9 plugins at `0.2.0` (verified from `.claude-plugin/marketplace.json` at HEAD `ebeb062`):
  - `rldyour-mcps`: `0.2.0` (was `0.1.3`)
  - `rldyour-serena-mcp`: `0.2.0` (was `0.1.5`)
  - `rldyour-flow`: `0.2.0` (was `0.1.4`)
  - `rldyour-explore`: `0.2.0` (was `0.1.3`)
  - `rldyour-browser`: `0.2.0` (was `0.1.2`)
  - `rldyour-design`: `0.2.0` (was `0.1.2`)
  - `rldyour-lsps`: `0.2.0` (was `0.1.2`)
  - `rldyour-rules`: `0.2.0` (was `0.1.2`)
  - `rldyour-security`: `0.2.0` (was `0.1.2`)
- **0.2.0 tag set** (10 tags, all pushed): `marketplace--v0.2.0`, `rldyour-browser--v0.2.0`, `rldyour-design--v0.2.0`, `rldyour-explore--v0.2.0`, `rldyour-flow--v0.2.0`, `rldyour-lsps--v0.2.0`, `rldyour-mcps--v0.2.0`, `rldyour-rules--v0.2.0`, `rldyour-security--v0.2.0`, `rldyour-serena-mcp--v0.2.0`. Verified via `git tag --list "*--v0.2.0"` at HEAD `ebeb062`.
- `CHANGELOG.md` `[0.2.0] - 2026-05-16` follows Keep-a-Changelog 1.1.0: two subsections `### Changed` and `### Notes`. `### Changed` documents Wave 1-5 consolidation summary, plugin version transitions (old → 0.2.0 per plugin), and `marketplace--v0.2.0` aggregate tag. `### Notes` records: no plugin runtime files added or modified vs 0.1.9; cache namespace `~/.claude/plugins/cache/rldyour-claudecode/<plugin>/0.2.0/`; done criteria. Reference-links block at CHANGELOG tail: `[0.2.0]` points to `https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.2.0`. Verified at `CHANGELOG.md` lines 9-68 at HEAD `ebeb062`.
- `CHANGELOG.md` `[0.1.9] - 2026-05-16` documents Wave 5 CI hardening + org transfer: SHA-pinned GitHub Actions (`actions/checkout@de0fac2e`, `actions/setup-node@48b55a01`, `actions/setup-python@a309ff8b`, `step-security/harden-runner@ab7a9404`) per OWASP A03:2025; top-level `permissions: {}` deny-all + per-job `contents: read` grants; concurrency cancel-in-progress across all four workflows; harden-runner egress audit in every job; Claude Code CLI pinned to `@2.1.143` in `validate.yml`; new `.github/workflows/semgrep.yml` (SAST, Semgrep OSS `semgrep/semgrep:1.163.0` Docker image, rule packs `p/python p/github-actions p/security-audit p/secrets p/owasp-top-ten p/ci`; replaces CodeQL which required GHAS not available on private repo); new `.github/workflows/actionlint.yml` (workflow YAML linter, `rhysd/actionlint` v1.7.12 binary, SHA256 `8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8`); new `.github/dependabot.yml` (monthly `github-actions` updates, grouped minor+patch, max 5 PRs); marketplace slug `rldyour-claude` → `rldyour-claudecode`; 9 plugin `plugin.json` `homepage` + `repository` URLs updated to `nddev-it-com/rldyour-claudecode`; smoke awk extractor fix. VERSION `0.1.8` → `0.1.9`.
- `scripts/validate_marketplace.sh` is the broad local gate and includes `claude plugin validate`, JSON parse, Python AST, shell syntax, frontmatter checks, version consistency, instruction docs, routing policy, MCP runtime drift checks, "Agent tools allowlist validation" (via `scripts/validate_agent_tools.py`, unconditional), `scripts/smoke_serena_memory_taxonomy.sh`, `scripts/smoke_hooks.sh`, and `scripts/smoke_bootstrap_check.sh`. CI workflows at HEAD `ebeb062`: `validate.yml` (SHA-pinned actions, harden-runner, `claude-code@2.1.143`, top-level `permissions: {}`), `dependency-check.yml` (same hardening), `semgrep.yml` (Semgrep OSS SAST), `actionlint.yml` (workflow YAML linter). CodeQL workflow removed (GHAS required for private repo).

## Contracts And Data

- Plugin cache refresh depends on per-plugin `plugin.json` version strings. Content-only plugin changes under the same version can be missed by the runtime cache.
- If a plugin's runtime behavior changes, bump that plugin version and align the marketplace entry.
- If a change affects the overall release boundary, update `VERSION` and `CHANGELOG.md`.
- Tag convention for plugins: `<plugin-name>--v<version>` via `claude plugin tag --push`.
- Tag convention for marketplace boundary: `marketplace--v<version>` (introduced in 0.2.0; pushed manually alongside plugin tags). This is NOT a plugin tag — it marks the aggregate release boundary in the CHANGELOG reference-links block.
- Tags should be created only after the worktree is clean for tracked files and validation passes.
- Cache namespace for 0.2.0: `~/.claude/plugins/cache/rldyour-claudecode/<plugin>/0.2.0/`.

## Change Rules

- For manifest or version changes, run `python3 scripts/validate_plugin_versions.py` and `bash scripts/validate_marketplace.sh`.
- For MCP runtime changes, also run `python3 scripts/check_mcp_runtime_versions.py` and relevant MCP smoke checks.
- For hook or memory-sync behavior changes, run shell syntax checks, analyzer/state script checks, `bash scripts/smoke_hooks.sh`, and `bash scripts/smoke_serena_memory_taxonomy.sh`.
- Avoid `scripts/smoke_fullrepo_sync.sh` after editing agent-only files unless prepared to restore/reapply them; it runs `--bootstrap-init` and can restore agent-only files from `origin/fullrepo`.

## Cross-References

- Open and closed debt record: [[TECHDEBT-01-NOW]] (D28 0.2.0 boundary, D24-D27 Wave 5 closures, D19 R5 closure).
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
