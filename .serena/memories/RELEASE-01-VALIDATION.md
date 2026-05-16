<!-- Memory Metadata
Last updated: 2026-05-16
Last commit: 9bf3c70 chore(release): cut 0.1.8 (Wave 4 R5 hardening + smoke + memory graph)
Scope: VERSION, CHANGELOG.md, README.md, .claude-plugin/marketplace.json, plugins/*/.claude-plugin/plugin.json, scripts/validate_marketplace.sh, scripts/validate_plugin_versions.py, scripts/smoke_serena_memory_taxonomy.sh, docs/release-process.md
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
- `README.md`: active catalog version summary and smoke/check commands.
- `docs/release-process.md`: release process reference.
- `scripts/validate_marketplace.sh`: full validation harness.
- `scripts/validate_plugin_versions.py`: marketplace/manifest version consistency.
- `scripts/smoke_serena_memory_taxonomy.sh`: focused Serena memory taxonomy regression smoke.

## Current Behavior

- Current release boundary at HEAD: `VERSION` is `0.1.8` (verified at `VERSION` file, HEAD `9bf3c70`).
- `rldyour-serena-mcp` is `0.1.5`; `rldyour-mcps` is `0.1.3`; `rldyour-flow` is `0.1.4`; `rldyour-explore` is `0.1.3`; `rldyour-security`, `rldyour-browser`, `rldyour-design`, `rldyour-lsps`, `rldyour-rules` are `0.1.2`. All verified from `.claude-plugin/marketplace.json` at HEAD.
- `CHANGELOG.md` `[0.1.7] - 2026-05-16` documents Wave 2 polish: (1) Tier 1 — `flow-post-task-sync` SKILL.md step 1 path replaced with `$(git rev-parse --show-toplevel)` (cwd-independent); new `scripts/validate_agent_tools.py` enforces agent `tools:` allowlist invariants (built-in names, MCP wildcard discipline, `READ_ONLY_BY_DESIGN_MCPS` set); TECHDEBT R4 and R5 added; (2) Tier 2 — 14 utility/plugin scripts gained `IFS=$'\n\t'` + `unset CDPATH`; `.github/workflows/validate.yml` extended with 3 new CI steps (Agent tools allowlist validation, Hook lifecycle smoke, Serena memory taxonomy smoke), no `fetch-depth: 0`; (3) Tier 3 — `scripts/worktree_add.sh` adds `git check-ref-format --branch` as second gate; `post_tool_use_commit_advice.sh` expands injection markers to 13+ families including Russian-language patterns, flags upgraded to `re.IGNORECASE | re.UNICODE`; (4) Tier 4 — `scripts/smoke_hooks.sh` new "runtime stdin payloads" step with 6 test cases; `scripts/bootstrap_check.sh` new "git pre-push hook (advisory)" step. Security: prompt-injection coverage gap closed (HIGH, conf 85); branch validation second gate (MEDIUM, conf 70). `rldyour-flow` bumped `0.1.3` → `0.1.4`; VERSION `0.1.6` → `0.1.7`.
- `CHANGELOG.md` `[0.1.8] - 2026-05-16` documents Wave 4 R5 hardening + smoke + memory graph: R5 divergence guard in `scripts/bootstrap_check.sh` (lines 31-138) refuses `--bootstrap-init` when worktree agent-only files diverge from `origin/fullrepo`; `.aider*` glob expansion via `shopt -s nullglob`; WARN bypass to stderr; WARN on fetch failure; new `scripts/smoke_bootstrap_check.sh` (130 lines, 7 steps) wired into `scripts/validate_marketplace.sh` (line 144) and `.github/workflows/validate.yml` (line 141); SC2044 NUL-delimited find loops in `scripts/validate_marketplace.sh` and `.github/workflows/validate.yml` (2+2 hits); `## Cross-References` sections added to all 18 memories; OWASP precision (A03 supply-chain #3, A10 Mishandling of Exceptional Conditions, ASVS 5.0.0). VERSION `0.1.7` → `0.1.8`.
- `scripts/validate_marketplace.sh` is the broad local gate and includes `claude plugin validate`, JSON parse, Python AST, shell syntax, frontmatter checks, version consistency, instruction docs, routing policy, MCP runtime drift checks, "Agent tools allowlist validation" (via `scripts/validate_agent_tools.py`, unconditional), `scripts/smoke_serena_memory_taxonomy.sh`, `scripts/smoke_hooks.sh`, and `scripts/smoke_bootstrap_check.sh`. Verified at `scripts/validate_marketplace.sh` lines 117, 130-147 at HEAD `9bf3c70`.

## Contracts And Data

- Plugin cache refresh depends on per-plugin `plugin.json` version strings. Content-only plugin changes under the same version can be missed by the runtime cache.
- If a plugin's runtime behavior changes, bump that plugin version and align the marketplace entry.
- If a change affects the overall release boundary, update `VERSION` and `CHANGELOG.md`.
- Tag convention is `<plugin-name>--v<version>` through `claude plugin tag --push`.
- Tags should be created only after the worktree is clean for tracked files and validation passes.

## Change Rules

- For manifest or version changes, run `python3 scripts/validate_plugin_versions.py` and `bash scripts/validate_marketplace.sh`.
- For MCP runtime changes, also run `python3 scripts/check_mcp_runtime_versions.py` and relevant MCP smoke checks.
- For hook or memory-sync behavior changes, run shell syntax checks, analyzer/state script checks, `bash scripts/smoke_hooks.sh`, and `bash scripts/smoke_serena_memory_taxonomy.sh`.
- Avoid `scripts/smoke_fullrepo_sync.sh` after editing agent-only files unless prepared to restore/reapply them; it runs `--bootstrap-init` and can restore agent-only files from `origin/fullrepo`.

## Cross-References

- Open and closed debt record: [[TECHDEBT-01-NOW]] (R5 D19 closure, D23 SC2044, version bump history).
- Validation harness patterns: [[PATTERNS-01-CANONICAL]] (commit message, memory file pattern).
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
