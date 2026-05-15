<!-- Memory Metadata
Last updated: 2026-05-15
Last commit: bf54d02 chore(release): cut 0.1.6 with agent + shell + docs changes
Scope: Serena memory sync, hook gates, fullrepo lifecycle, MCP pins, validation harness, current implementation risks
Area: TECHDEBT
-->

# TECHDEBT-01-NOW

## Purpose

Open technical debt, implementation mistakes already fixed, and anti-regression patterns that future agents must know before modifying this marketplace.

## Open Risks

### R1. Runtime-version drift outside pinned baseline

- Symptom: MCP package or host-binary drift breaks startup expectations or capability smoke.
- Impact: broken MCP onboarding, false-positive smoke baselines, or session-start failures.
- Mitigation in place: `scripts/check_mcp_runtime_versions.py`, `scripts/smoke_mcp_runtime.sh`, and `scripts/smoke_mcp_capabilities.sh`.
- Prevention: update `.mcp.json`, `config/mcp-runtime-versions.env`, docs/changelog, and validation evidence in one change.

### R2. Memory writes still require explicit verified sync pass

- Symptom: hooks compute impact and block Stop, but do not write durable facts.
- Impact: `.serena/memories` can become stale if the orchestrator skips `flow-memory-sync` or equivalent `serena-memory-sync` workflow.
- Risk class: process hygiene and operation completeness.
- Mitigation in place: `stop_memory_sync.sh` exits `2` with scoped analyzer context; `flow-memory-sync` is the canonical writer.
- Prevention: do not finish durable work until `serena_memory_state.py` is current or an explicit blocker is reported.

### R3. Analyzer targets are heuristic, not source of truth

- Symptom: `analysis.memory_targets` can miss a conceptual dependency or include an overly broad candidate.
- Impact: incomplete or noisy memory updates if a writer follows targets blindly.
- Mitigation in place: `flow-memory-sync` contract requires verifying claims against source files, tests, git history, and diff before writing; `scripts/smoke_serena_memory_taxonomy.sh` now asserts the high-value target families.
- Prevention: treat analyzer output as first-pass scope only; code/config/tests at HEAD remain the source of truth.

## Closed Debt And Anti-Regressions

- D1. GitHub MCP entitlement trap: Copilot HTTP endpoint produced 403 in non-Copilot account class. Fixed by stdio `github-mcp-server` transport in `plugins/rldyour-mcps/.mcp.json`; keep HTTP 403 as failure in capability smoke.
- D2. Capability smoke false positives: older HTTP smoke accepted 401/403 too broadly. Fixed by real JSON-RPC initialize + tools/list validation in `scripts/smoke_mcp_capabilities.sh`.
- D3. Serena tool-surface drift: `serena-agent 1.3.0` changed available tools under `--context=agent`. Fixed by pinning `serena-agent==1.3.0`, `alwaysLoad: true`, and verifying workflow tools.
- D4. Stop-hook loop hazard: repeated Stop attempts could loop. Fixed with `.serena/.sync_marker` and `.serena/.flow_sync_marker` fingerprints.
- D5. Manual broad memory sync drift: fixed with `analyze_sync_scope.py`, persisted `analysis`, and scoped Stop guidance.
- D6. Memory-state schema ambiguity: fixed with `analysis_source` and synchronized Stop hook formatting.
- D7. Empty-diff memory target noise: fixed so `HEAD..HEAD` yields no memory targets.
- D8. Large analysis payload shell limit: fixed by temp-file/stdin JSON handling instead of argv/env blobs.
- D9. Broad dated memories: fixed in `aaaa0dd` by numbered taxonomy (`AREA-01-SLUG.md`), `CORE-01-INDEX.md`, and analyzer schema v2 `memory_taxonomy`.
- D10. Agent-instruction-only sync bypass: fixed in `70c8d91` by limiting knowledge-only exemptions to Serena knowledge/runtime paths; `AGENTS.md`, `.claude/**`, `.agents/**`, and similar instruction files now require memory sync when changed.
- D11. Missing CLAUDECODE target mapping: fixed in `70c8d91`; plugin component and Claude Code instruction changes target `CLAUDECODE-01-PLUGIN-CANON.md`.
- D12. Docs-only Serena contract drift: fixed in `70c8d91`; `rldyour-serena-mcp` docs/references target `SERENA-01-MEMORY-SYNC.md`, `HOOKS-01-LIFECYCLE.md`, and `CORE-02-MARKETPLACE.md`.
- D13. Untested taxonomy edge cases: fixed in `70c8d91` with `scripts/smoke_serena_memory_taxonomy.sh`, wired into `scripts/validate_marketplace.sh`.
- D14. Fullrepo-managed stale memory acknowledgement: fixed in `70c8d91`; `commit_serena_knowledge.sh` refuses stale ignored memories and uses `git status --porcelain -uall` so runtime-marker filtering sees individual files instead of collapsed directories.
- D15. Serena MCP wildcard granted write tools to read-only reviewer/research agents: fixed in `cf781aa`; `mcp__plugin_rldyour-mcps_serena__*` wildcard in 7 agent `tools:` allowlists (6 reviewer agents + `ry-explore`) previously included `create_text_file`, `replace_content`, `replace_symbol_body`, `insert_after_symbol`, `insert_before_symbol`, `rename_symbol`, `safe_delete_symbol`, `write_memory`, `edit_memory`, `delete_memory`, `rename_memory`. Replaced with explicit 14-tool read-only subset (`find_symbol`, `find_referencing_symbols`, `find_implementations`, `find_declaration`, `get_symbols_overview`, `search_for_pattern`, `read_file`, `list_dir`, `find_file`, `list_memories`, `read_memory`, `get_current_config`, `get_diagnostics_for_file`, `check_onboarding_performed`). Eliminates confused-deputy / prompt-injection risk.
- D16. Shell strict mode inconsistency: fixed in `56c616f`; gold-standard pattern (`set -euo pipefail` + `IFS=$'\n\t'` + `unset CDPATH`) was only present in `scripts/install-rldyour-marketplace.sh`. Now applied uniformly to 8 hook scripts in `plugins/rldyour-{flow,serena-mcp}/hooks/*.sh` + 3 helper scripts (`scripts/worktree_add.sh`, `scripts/bootstrap_check.sh`, `plugins/rldyour-flow/scripts/deploy_readiness.sh`). Verified by `bash -n` + `scripts/smoke_hooks.sh`; no functional change.

## Error Patterns To Avoid

- Pattern: updating hook/skill/agent memory contracts without updating analyzer targets.
  - Prevention: keep `analyze_sync_scope.py`, `stop_memory_sync.sh`, `serena-memory-sync/SKILL.md`, `flow-memory-sync.md`, and this memory in one change wave.
- Pattern: treating agent-only instruction files as memory no-ops.
  - Prevention: only Serena knowledge/runtime paths are knowledge-only for freshness; instruction docs are durable sync targets.
- Pattern: committing agent-only files to `main`.
  - Prevention: check `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json` and keep `tracked_agent_paths: []`.
- Pattern: documenting desired behavior as fact.
  - Prevention: store desired future work in `.serena/plans/` only when useful; memories contain verified facts or explicit Known Gaps.
- Pattern: running `smoke_fullrepo_sync.sh` after editing agent-only docs/memories.
  - Prevention: run it before agent-only edits or be prepared to restore/reapply; it can restore agent-only files from `origin/fullrepo`.
- Pattern: mixing memory edits with unrelated tracked code changes and expecting `commit_serena_knowledge.sh` to commit them.
  - Prevention: commit tracked implementation first, then run memory sync against the new HEAD, then fullrepo publish.

## Change Rules

- Add new risks here when they are current and actionable.
- Move closed risks to the closed section only after code/config/tests/docs include a concrete mitigation.
- Keep debt entries concise and source-path anchored. Do not use this file as a backlog.

## Verification

- `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`: verifies memories mention current HEAD.
- `bash scripts/smoke_serena_memory_taxonomy.sh`: verifies the memory taxonomy edge cases that caused D10-D14.
- `bash scripts/validate_marketplace.sh`: catches many cross-plugin regressions and runs the taxonomy smoke.
- `bash scripts/smoke_hooks.sh`: catches hook registration and skip-flag drift.
- `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json`: verifies agent-only tracking state.
