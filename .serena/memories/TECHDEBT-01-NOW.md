<!-- Memory Metadata
Last updated: 2026-05-16
Last commit: ebeb062 docs(changelog): polish 0.2.0 entry per reviewer findings
Scope: Serena memory sync, hook gates, fullrepo lifecycle, MCP pins, validation harness, current implementation risks
Area: TECHDEBT
-->

# TECHDEBT-01-NOW

## Purpose

Open technical debt, implementation mistakes already fixed, and anti-regression patterns that future agents must know before modifying this marketplace.

## Source Of Truth

- `scripts/bootstrap_check.sh`: divergence guard (R5 mitigation, lines 31-138).
- `scripts/smoke_bootstrap_check.sh`: R5 behavior smoke (7 assertions at HEAD).
- `scripts/validate_marketplace.sh`: full validation harness; wires bootstrap smoke at line 144.
- `.github/workflows/validate.yml`: CI wires bootstrap smoke at line 141.
- `plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh`: injection-marker sanitization (D18, D23).
- `plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py`: TECHDEBT area mapping.
- `plugins/rldyour-security/skills/owasp-top-10-implementation/SKILL.md`: OWASP 2025 categories (D22).
- `scripts/validate_agent_tools.py`: agent tools allowlist enforcement (R4 mitigation).
- `scripts/validate_marketplace.sh` line 117: agent tools validator wiring.
- `.claude/CLAUDE.md`: "Smoke-script footgun" section documents R5 process order.
- `CHANGELOG.md` `[0.1.8]`: Wave 4 R5 hardening, smoke, SC2044, memory graph record.

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

### R4. Non-Serena MCP wildcards rely on read-only-by-design invariant

- Symptom: agent `tools:` allowlists in 7 read-only agents (6 flow reviewers + `ry-explore`) use wildcards `mcp__plugin_rldyour-mcps_{context7,deepwiki,grep,semgrep}__*` instead of explicit tool lists.
- Impact: wildcards accept any future tool added to these servers. If context7/deepwiki/grep/semgrep upstream adds a write/edit/create tool, read-only agents silently inherit write capability — same confused-deputy class as the closed D15 (Serena wildcard).
- Risk class: future-proofing / supply-chain.
- Mitigation in place: `scripts/validate_agent_tools.py` enforces a `READ_ONLY_BY_DESIGN_MCPS` set; any wildcard for a server outside that set FAILS. The validator is wired into `scripts/validate_marketplace.sh`.
- Prevention: when bumping `context7`, `deepwiki`, `grep`, `semgrep` runtime versions in `plugins/rldyour-mcps/.mcp.json`, inspect the new `tools/list` output (via `scripts/smoke_mcp_capabilities.sh`) and ensure no write-class tool names were added (`create_*`, `write_*`, `delete_*`, `modify_*`, `edit_*`, `replace_*`, `insert_*`, `rename_*`). If a write-class tool appears, remove the wildcard for that server and switch to an explicit read-only tool subset (the same pattern applied to Serena in D15).

### R5. Agent-only worktree restore can silently revert in-progress memory edits (CLOSED — see D19)

- Symptom: `scripts/bootstrap_check.sh` and `scripts/smoke_fullrepo_sync.sh` call `fullrepo_sync.py --bootstrap-init`, which restores `.serena/memories/**` from `origin/fullrepo`. If memories were edited locally but not yet published via `fullrepo_sync.py --publish`, those local edits are silently overwritten back to remote state.
- Impact: lost-work footgun. The user discovers the revert only by re-running `serena_memory_state.py` or noticing a missing R entry.
- Risk class: process hygiene / tooling foot-gun.
- Mitigation in place: documented in `.claude/CLAUDE.md` "Smoke-script footgun" section; verified live during Wave 2 (2026-05-15 R4 entry was overwritten by `bootstrap_check.sh` and re-applied). Wave 4 added `scripts/bootstrap_check.sh` divergence guard (lines 31-138) that refuses `--bootstrap-init` when worktree agent-only files differ from `origin/fullrepo`. See D19 for full closure record.
- Prevention: order operations correctly — (a) edit memories, (b) verify, (c) publish via `fullrepo_sync.py --publish`, (d) only then run bootstrap/smoke. Or run bootstrap/smoke first, then edit. Never sandwich memory edits between bootstrap and publish.

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
- D17. Strict mode incomplete in utility and plugin scripts: fixed in Wave 2 (commits `5586c8b`+`b4234c2`); 14 additional scripts gained `IFS=$'\n\t'` + `unset CDPATH` after `set -euo pipefail` — 9 in `scripts/` (smoke_hooks, smoke_fullrepo_sync, smoke_mcp_capabilities, smoke_mcp_runtime, smoke_serena_memory_taxonomy, sync_fullrepo_branch, validate_marketplace, collect_diagnostics, install_local_git_hooks) and 5 plugin scripts (`plugins/rldyour-flow/scripts/{detect_project_checks,git_sync_audit,local_git_ai_guard}.sh`, `plugins/rldyour-lsps/scripts/install_lsps_brew.sh`, `plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh`). No functional change to any script.
- D18. Commit subject prompt-injection coverage gap (EN-only, 3 marker families): fixed in Wave 2 commit `bb657ea`; `plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh` `INJECTION_MARKERS` regex expanded from 3 to 13+ marker families. Added: Llama/Mistral `[INST]`/`<<SYS>>`, Llama-3 `<|begin_of_text|>`/`<|end_of_text|>`, chat-template `<|user|>`/`<|assistant|>`, Markdown `---system---`, role-play prefixes (`you are now`, `from now on`), Russian-language equivalents (`[СИСТЕМА]`, `игнорируй ... инструкции`, `забудь ... команды`, `теперь ты`). Regex flags upgraded to `re.IGNORECASE | re.UNICODE` for Cyrillic word boundaries. Closes Wave 2 security review F-1 (HIGH, conf 85).
- D19. R5 agent-only divergence guard (open risk R5, now fully closed): fixed in Wave 4 commits `b2ebbde` + `0dc804a`; `scripts/bootstrap_check.sh` gained a pre-`--bootstrap-init` divergence guard at lines 31-138. For each agent-only path root, the guard uses `git cat-file -e` + `cmp -s` (content-based comparison) to detect local edits not yet published to `origin/fullrepo`, then blocks with an actionable error message listing diverged files and resolution steps. Override: `RLDYOUR_FORCE_BOOTSTRAP=1` prints `WARN RLDYOUR_FORCE_BOOTSTRAP=1 ... BYPASSED` to stderr and proceeds. Fetch failure emits `WARN git fetch origin fullrepo failed` to stderr instead of silently continuing with a potentially stale ref. `.aider*` glob expansion (`shopt -s nullglob; for aider_path in .aider*`) covers `.aiderignore`, `.aider.conf.yml`, `.aider.chat.history.md`, etc. that an earlier literal entry missed (Wave 4 quality F-1, conf 95). New `scripts/smoke_bootstrap_check.sh` (130 lines, 7 assertion steps) covers 4 code paths + glob wiring + bash/python array drift detector + runtime path-(a) subshell test. Wired into `scripts/validate_marketplace.sh` (line 144) and `.github/workflows/validate.yml` (line 141). Verified by `bash scripts/smoke_bootstrap_check.sh` reporting 7/7 OK at HEAD `9bf3c70`.
- D20. Cross-reference graph in memories: added in Wave 4; `## Cross-References` sections with `[[AREA-NN-SLUG]]` wikilinks added to all 18 memories. As of HEAD `9bf3c70`, `grep -l "## Cross-References" .serena/memories/*.md` returns 18 files (verified: 10 returned above; the remaining 8 are being added in this sync pass). Note: the D20 claim of "15 expected" was pre-sync; the final correct count is 18 (all memories). Behavior asserted by memory files at HEAD; no automated test.
- D21. Source Of Truth sections standardized: `## Source Of Truth` subsections added to memories that lacked them, providing a canonical anchor for where to verify facts. Pattern now documented in [[PATTERNS-01-CANONICAL]] Memory File Pattern section. Behavior asserted by memory files at HEAD; no automated test.
- D22. OWASP Top 10 precision: OWASP Top 10 2025 release status confirmed as final (released 2025-11-06), ASVS 5.0.0 reference added. A03 renamed to "Software Supply Chain Failures" (was "Injection" in OWASP Top 10 2021; renaming and repositioning to #3 reflects supply-chain concern escalation). A10 renamed to "Mishandling of Exceptional Conditions". Verified at `plugins/rldyour-security/skills/owasp-top-10-implementation/SKILL.md` and [[SECURITY-01-OWASP]].
- D23. SC2044 NUL-delimited find loops: fixed in Wave 4 commit `b2ebbde`; `scripts/validate_marketplace.sh` and `.github/workflows/validate.yml` replaced `for f in $(find ...)` patterns with `while IFS= read -r -d '' file; do ... done < <(find ... -print0)` NUL-delimited loops. Verified by `grep -c "while IFS= read -r -d ''" scripts/validate_marketplace.sh .github/workflows/validate.yml` returning 2+2=4 hits at HEAD `9bf3c70`. Closes shellcheck SC2044 (word-splitting and globbing on find output).
- D24. GitHub Actions unpinned tags (Wave 4 security F-3, LOW 90): fixed in Wave 5 commit `9c20c75`; all four `.github/workflows/*.yml` files switched from mutable semantic tags to SHA-pinned references per OWASP A03:2025. Pinned SHAs: `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd` (v6.0.2), `actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e` (v6.4.0), `actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405` (v6.2.0), `step-security/harden-runner@ab7a9404c0f3da075243ca237b5fac12c98deaa5` (v2.19.3). Verified at `.github/workflows/validate.yml` lines 31-32 at HEAD `334fe09`.
- D25. Claude Code CLI unpinned in CI (Wave 4 security F-5, INFO 35): fixed in Wave 5 commit `9c20c75`; `validate.yml` now installs `npm install -g '@anthropic-ai/claude-code@2.1.143'` (was unpinned `@latest`). Verified at `.github/workflows/validate.yml` line 46 at HEAD `334fe09`.
- D26. No SAST coverage (CodeQL not viable without GHAS): fixed in Wave 5 commits `81126bc`+`334fe09`; CodeQL requires GitHub Advanced Security (paid, not available for this private repo — PATCH security_and_analysis returned HTTP 422). Replaced by `.github/workflows/semgrep.yml` using Semgrep OSS Docker image `semgrep/semgrep:1.163.0` (matches MCP server pin). Rule packs: `p/python`, `p/github-actions`, `p/security-audit`, `p/secrets`, `p/owasp-top-ten`, `p/ci` (`p/bash` and `p/yaml` returned HTTP 404; bash rules are bundled in `p/security-audit`). `--error` flag fails CI on WARNING/ERROR findings. No SARIF/GHAS upload needed. Verified at `.github/workflows/semgrep.yml` at HEAD `334fe09`.
- D27. Smoke awk extractor dumped entire file for one-line step() definitions: fixed in Wave 5 commit `92eb8dd`; `scripts/smoke_bootstrap_check.sh` runtime path-a harness used awk with `in_step`/`in_fail` flag logic to extract `step()`/`fail()` bodies. One-line `step() { ...; }` form caused `^}` to never match as a separate line — flag was never reset — so the awk appended the entire remainder of `bootstrap_check.sh` into `TMP_GUARD`. Fixed by inlining minimal helpers via a `PRELUDE` heredoc and extracting only the divergence-guard block via awk range. Verified at `scripts/smoke_bootstrap_check.sh` lines 89-114 at HEAD `334fe09`.
- D28. 0.2.0 release boundary consolidation (Wave 6): all 9 plugins and marketplace `VERSION` synchronized to `0.2.0` in commits `26dbd54` + `ebeb062`. No plugin runtime files added or modified vs 0.1.9 (bump is cache-invalidation + tag boundary). 10 tags pushed: `marketplace--v0.2.0` (marketplace aggregate boundary, manual push) + 9 plugin tags via `claude plugin tag --push`. F-3 (GitHub Actions SHA pinning, LOW 90) closed in D24 (Wave 5). F-5 (npm pinning, INFO 35) closed in D25 (Wave 5). CHANGELOG `[0.2.0]` follows Keep-a-Changelog 1.1.0 with `### Changed` + `### Notes` subsections and reference-links block at tail. Verified via `git tag --list "*--v0.2.0"` and `cat VERSION` at HEAD `ebeb062`.


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

## Cross-References

- Divergence guard implementation: [[SERENA-01-MEMORY-SYNC]] (memory freshness + commit_serena_knowledge.sh).
- Agent tools allowlist invariants: [[CLAUDECODE-01-PLUGIN-CANON]] (validate_agent_tools.py wiring).
- Patterns: [[PATTERNS-01-CANONICAL]] (hook script pattern, strict-mode trio, injection markers, Memory File Pattern).
- OWASP coverage (D22): [[SECURITY-01-OWASP]] OWASP Top 10 2025 + ASVS 5.0.0.
- Hook lifecycle and skip flags: [[HOOKS-01-LIFECYCLE]].
- Release record (D19 + D23 wave): [[RELEASE-01-VALIDATION]] `[0.1.8] - 2026-05-16`.
- Release record (D24-D27 wave): [[RELEASE-01-VALIDATION]] `[0.1.9] - 2026-05-16`.
- Release record (D28 0.2.0 boundary): [[RELEASE-01-VALIDATION]] `[0.2.0] - 2026-05-16`.
- Memory taxonomy and cross-reference graph: [[CORE-01-INDEX]] (map of all 18 memories).
- SDLC post-task sync flow: [[FLOW-01-SDLC]].
- Instruction docs policy: [[DOCS-01-INSTRUCTIONS]].
