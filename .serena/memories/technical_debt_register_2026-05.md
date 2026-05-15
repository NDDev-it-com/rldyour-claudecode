<!-- Memory Metadata
Last updated: 2026-05-15
Last commit: f4510fb feat(serena-mcp): add scoped memory sync analysis
Scope: Serena memory sync, workflow hooks, fullrepo lifecycle, MCP pins, error patterns, technical debt
Area: CORE
-->

# Technical Debt And Error Register — 2026-05

## Open and Active Risks

### R1. Runtime-version drift outside pinned baseline
- **Symptom:** Any MCP pin drift (binary or package) breaks startup expectations and capability smoke.
- **Impact:** Broken MCP onboarding, false-positive smoke baselines, or hook failures at session start.
- **Mitigation in place:** `scripts/check_mcp_runtime_versions.py` + `scripts/smoke_mcp_runtime.sh` + `scripts/smoke_mcp_capabilities.sh`.
- **Prevention:** periodic upstream pin check against NPM/PyPI/GitHub release pages before bumping `config/mcp-runtime-versions.env`.

### R2. Memory update execution still requires explicit subagent pass
- **Symptom:** automatic hook detection can only compute diff impact and block `Stop`; it does not write durable facts.
- **Impact:** stale `.serena/memories` can persist if `flow-memory-sync` is skipped.
- **Risk class:** process hygiene / operation completeness.
- **Mitigation in place:** `stop_memory_sync.sh` emits scoped instructions and `flow-memory-sync` is the required follow-up writer.
- **Prevention:** never end a task without either successful `flow-memory-sync` (subagent) run or explicit confirmation that memory updates are not required by scope.

## Closed Debt (with anti-regressions)

- **D1. GitHub MCP entitlement trap**
  - **Issue:** Copilot HTTP endpoint returned `403 "not authorized to use this Copilot feature"` in non-Copilot environments.
  - **Fix:** switched to local stdio transport `github-mcp-server stdio --toolsets=repos,issues,pull_requests,users,context`, pinned to `1.0.4`, added in plugin manifests and capability checks.
  - **Prevention:** smoke harness validates real JSON-RPC initialize path; auth-gated HTTP blanket-pass for 401/403 removed.

- **D2. Capability smoke false-positive masking auth and protocol regressions**
  - **Issue:** legacy smoke treated HTTP 401/403 as acceptable in some paths, hiding failures.
  - **Fix:** per-server `initialize` + `tools/list` handshake, `result.serverInfo.name` validation, typed classification of 401 vs 403 outcomes.
  - **Prevention:** keep `scripts/smoke_mcp_capabilities.sh` as blocker for meaningful MCP runtime changes.

- **D3. Serena version drift and tool-surface confusion**
  - **Issue:** upgrade to `serena-agent 1.3.0` changed tool surface from 45 to 28 under `agent` context.
  - **Fix:** hard-verified workflow toolset under `--context=agent`; hooks only call supported commands.
  - **Prevention:** keep `.mcp.json` with `alwaysLoad: true` and pin to exact `uvx` version.

- **D4. rldyour-flow orchestration loop hazard**
  - **Issue:** repeated Stop hooks could loop indefinitely.
  - **Fix:** loop-guard markers `.serena/.sync_marker` and `.serena/.flow_sync_marker` introduced using `(HEAD, dirty state, branch, serena state)`.
  - **Prevention:** advisory stop hooks only, high-blast-radius operations remain in orchestrator workflows.

- **D5. Serena scope drift from manual-only updates**
  - **Issue:** earlier memory updates depended on broad full-repo diffs and could miss newly touched contract files.
  - **Fix:** introduced deterministic analyzer (`analyze_sync_scope.py`) + persisted analysis fields in
    `.serena/.serena_sync_state.json`, so `mark_sync_required.sh` and `flow-memory-sync` target durable
    contract seams directly.
  - **Prevention:** never update hook/skill/agent contracts without updating analyzer targets in lockstep.

- **D6. Memory-state command parsing mismatch risk during schema changes**
  - **Issue:** previous versions had no stable contract for analysis metadata source and stop advisory interpretation.
  - **Fix:** added `analysis_source` in `serena_memory_state.py` and aligned stop-message formatting to explicit fields.
  - **Prevention:** all schema changes now require synchronized edits to analyzer, state script, stop hook, and subagent instructions in one change wave.

- **D7. Empty-diff memory target noise**
  - **Issue:** an initial analyzer draft emitted baseline memory targets for an empty `HEAD..HEAD` range.
  - **Fix:** `analyze_sync_scope.py` now returns empty `memory_targets` and `candidate_memory_focus` when no paths changed.
  - **Prevention:** keep `python3 plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py --from-ref HEAD --to-ref HEAD` in verification for analyzer edits.

- **D8. Large analysis payload shell limit risk**
  - **Issue:** passing analysis JSON through argv/env can break on large commit ranges.
  - **Fix:** `mark_sync_required.sh` writes analyzer output to a temp file for the embedded Python writer, and `stop_memory_sync.sh` reads state JSON through stdin.
  - **Prevention:** do not pass `.serena/.serena_sync_state.json` or analyzer JSON as a shell argument in future hook changes.

## Error and fix pattern ledger (for new code paths)

- **Pattern:** Memory edits plus unrelated non-memory docs in one working session.
  - **Avoided by:** `commit_serena_knowledge.sh` refusing to auto-commit when non-knowledge changes are present.
  - **Preferred sequence:** stabilize docs + implementation first; run Serena sync; then run flow post-task sync.

- **Pattern:** Full-repo-sensitive files ending up committed in `main`.
  - **Avoided by:** `flow/serena scripts --status-json` should keep `tracked_agent_paths: []` on `main`.
  - **Preferred sequence:** modify agent-only files in worktree with fullrepo restore and publish, never manually keep them on main index.

- **Pattern:** MCP env-file and `.mcp.json` divergence.
  - **Avoided by:** `scripts/check_mcp_runtime_versions.py` and manifest validation script in `scripts/validate_marketplace.sh`.
  - **Preferred sequence:** when a MCP pin changes, update env/version checks + manifest + docs/changelog/CHANGELOG as a single unit.

- **Pattern:** Auto-sync scope contract drift between analysis + hooks + sync skill.
  - **Avoided by:** updating analyzer output keys, hook readers, and `flow-memory-sync` scope logic in one code change.
  - **Preferred sequence:** run analyzer script and stale-state command after edits before closing to verify required fields remain parseable.

- **Pattern:** Current dirty docs recorded as durable memory.
  - **Avoided by:** treating `dirty_files`/`needs_flow_sync` output as final report material unless the condition reveals a stable contract.
  - **Preferred sequence:** commit or restore durable docs, then record only the underlying process rule in this register.

## Knowledge for GPT operation
- Always treat this file as part of **first-priority operational context** together with
  `project_marketplace_state.md`, `claude_code_plugin_canon_2026-05.md`,
  `serena_memory_sync_protocol_2026-05.md`.
- For every workflow change, update:
  1. code/docs,
  2. dependency/runtime checks,
  3. Serena memory entries,
  4. AGENTS/.CLAUDE only when Claude Code-specific behavior changes.
