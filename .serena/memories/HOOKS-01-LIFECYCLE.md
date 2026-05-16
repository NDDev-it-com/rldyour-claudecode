<!-- Memory Metadata
Last updated: 2026-05-16
Last commit: e5a7694 docs(flow): align reviewer-protocol terminology and flow-lifecycle
Scope: plugins/rldyour-serena-mcp/hooks/hooks.json, plugins/rldyour-serena-mcp/hooks/*.sh, plugins/rldyour-flow/hooks/hooks.json, plugins/rldyour-flow/hooks/*.sh, scripts/smoke_hooks.sh, scripts/smoke_serena_memory_taxonomy.sh, .claude/CLAUDE.md, AGENTS.md
Area: HOOKS
-->

# HOOKS-01-LIFECYCLE

## Purpose

Claude Code hook lifecycle and coordination contract between Serena freshness gates and flow post-task gates.

## Source Of Truth

- `plugins/rldyour-serena-mcp/hooks/hooks.json`: Serena hook registration.
- `plugins/rldyour-serena-mcp/hooks/user_prompt_submit.sh`: Serena-first context reminder.
- `plugins/rldyour-serena-mcp/hooks/prepare_auto_sync.sh`: commit-like Bash baseline capture.
- `plugins/rldyour-serena-mcp/hooks/mark_sync_required.sh`: post-commit sync marker writer.
- `plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh`: memory freshness Stop gate.
- `plugins/rldyour-flow/hooks/hooks.json`: flow hook registration.
- `plugins/rldyour-flow/hooks/session_start_worktree_bootstrap.sh`: agent-only context restore for new worktrees.
- `plugins/rldyour-flow/hooks/session_start_context.sh`: SessionStart context advisory.
- `plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh`: post-Bash git advice.
- `plugins/rldyour-flow/hooks/stop_post_task_sync.sh`: post-task flow Stop gate.
- `scripts/smoke_serena_memory_taxonomy.sh`: stale Stop hook and loop-guard behavior test.

## Current Behavior

- Two plugins own hooks: `rldyour-serena-mcp` and `rldyour-flow`.
- Registered lifecycle rows at HEAD:
  - `UserPromptSubmit`: `rldyour-serena-mcp/hooks/user_prompt_submit.sh`.
  - `PreToolUse:Bash`: `rldyour-serena-mcp/hooks/prepare_auto_sync.sh`.
  - `PostToolUse:Bash`: `rldyour-serena-mcp/hooks/mark_sync_required.sh`.
  - `PostToolUse:Bash`: `rldyour-flow/hooks/post_tool_use_commit_advice.sh`.
  - `SessionStart`: `rldyour-flow/hooks/session_start_worktree_bootstrap.sh`.
  - `SessionStart`: `rldyour-flow/hooks/session_start_context.sh`.
  - `Stop`: `rldyour-serena-mcp/hooks/stop_memory_sync.sh`.
  - `Stop`: `rldyour-flow/hooks/stop_post_task_sync.sh`.
- Stop hooks are advisory enforcement gates. They write guidance to stderr and block with `exit 2` when required work remains.
- SessionStart and PostToolUse advisory hooks emit JSON `hookSpecificOutput.additionalContext` when applicable.
- `session_start_worktree_bootstrap.sh` is the only bounded mutating hook; it runs `fullrepo_sync.py --restore`, never `--publish` and never touches origin.
- `mark_sync_required.sh` treats agent-instruction paths as sync-relevant and writes `.serena/.serena_sync_state.json` with `required=true` when those paths changed.
- `stop_memory_sync.sh` includes taxonomy guidance without shell backticks in the Bash string, avoiding command-substitution side effects in advisory messages.
- All 8 hook scripts (`plugins/rldyour-{flow,serena-mcp}/hooks/*.sh`) and 3 helper scripts (`scripts/worktree_add.sh`, `scripts/bootstrap_check.sh`, `plugins/rldyour-flow/scripts/deploy_readiness.sh`) use full strict mode: `set -euo pipefail` + `IFS=$'\n\t'` + `unset CDPATH`. Wave 2 additionally applied `IFS=$'\n\t'` + `unset CDPATH` to 14 more utility/plugin scripts: 9 in `scripts/` (smoke_hooks, smoke_fullrepo_sync, smoke_mcp_capabilities, smoke_mcp_runtime, smoke_serena_memory_taxonomy, sync_fullrepo_branch, validate_marketplace, collect_diagnostics, install_local_git_hooks) and 5 in plugins (`plugins/rldyour-flow/scripts/{detect_project_checks,git_sync_audit,local_git_ai_guard}.sh`, `plugins/rldyour-lsps/scripts/install_lsps_brew.sh`, `plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh`). Pattern matches gold-standard in `scripts/install-rldyour-marketplace.sh`. Verified by `bash -n` + `scripts/smoke_hooks.sh` at HEAD.
- Wave 5 fix (D27): `scripts/smoke_bootstrap_check.sh` runtime path-a harness awk extractor was broken for one-line `step() { ...; }` function form — `in_step` flag was never reset, causing the awk to dump the entire remainder of `bootstrap_check.sh` into `TMP_GUARD`. Fixed in commit `92eb8dd` by using an inline `PRELUDE` heredoc for step()/fail() helpers and an awk range for the divergence-guard block. Verified at `scripts/smoke_bootstrap_check.sh` lines 89-114 at HEAD `334fe09`.

## Coordination Sequence

1. Serena Stop hook checks `serena_memory_state.py`.
2. If memories are stale, Serena Stop blocks with instructions to run `flow-memory-sync` or the equivalent Serena memory workflow.
3. After memories are current, flow Stop derives `serena_current` by calling `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py` directly.
4. Flow Stop then checks git/docs/fullrepo/cleanup state through `flow_post_task_state.py` and points to `flow-post-task-sync` when needed.
5. Loop guard markers `.serena/.sync_marker` and `.serena/.flow_sync_marker` allow repeated Stop attempts for the same fingerprint without infinite loops.

## Contracts And Data

- Skip flags: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT`, `RLDYOUR_SKIP_FLOW_COMMIT_ADVICE`, `RLDYOUR_SKIP_STOP_GATES`, `RLDYOUR_SKIP_FLOW_SYNC`, `RLDYOUR_SKIP_SERENA_SYNC`, `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP`.
- Stop hook exit code `2` is intentional blocking guidance; other hook errors should avoid breaking normal work unless the gate is intentionally blocking.
- `stop_memory_sync.sh` includes analyzer context: risk profile, analysis source, changed file count, memory taxonomy, memory targets, and high-priority areas.
- `post_tool_use_commit_advice.sh` sanitizes commit subjects through `INJECTION_MARKERS` regex before echoing to LLM context. Wave 2 expanded coverage from 3 to 13+ families: bracket-style role tags (`[SYSTEM]`/`[INST]`/`[СИСТЕМА]`/etc.), XML role tags, `<<SYS>>`, Llama-3 special tokens (`<|begin_of_text|>` etc.), chat-template tags (`<|user|>`/`<|assistant|>` etc.), `---system---`, `BEGIN/END PROMPT`, English instruction-override phrases, and Russian-language equivalents (`игнорируй`, `забудь`, `теперь ты`). Flags: `re.IGNORECASE | re.UNICODE`. Verified at `plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh` lines 69-84 at HEAD.
- The Stop hook prompt tells the orchestrator to keep memories in `AREA-01-SLUG.md` form and use `CORE-01-INDEX.md` as the map.

## Invariants

- No hook performs push, merge, release tagging, branch deletion, fullrepo publish, or arbitrary memory writes.
- High-blast-radius work stays in orchestrated skills/subagents after model judgement.
- Worktree bootstrap must restore agent-only files from `origin/fullrepo` and must never publish from a new worktree.
- Hook changes must keep `scripts/smoke_hooks.sh` aligned with skip flags and expected behavior.
- Memory Stop advisory behavior must keep `scripts/smoke_serena_memory_taxonomy.sh` passing.

## Cross-References

- Memory freshness contract: [[SERENA-01-MEMORY-SYNC]] (analyzer, sync markers, writer flow).
- Post-task SDLC workflow: [[FLOW-01-SDLC]] (flow-post-task-sync, fullrepo publish, cleanup).
- Hook implementation patterns: [[PATTERNS-01-CANONICAL]] Hook Script section.
- Injection-marker sanitization (D18): [[TECHDEBT-01-NOW]] D18.
- Closed debt D16 (strict mode), D17 (utility scripts): [[TECHDEBT-01-NOW]].
- Skip flags: documented here; RLDYOUR_SKIP_STOP_GATES disables both Stop gates.
- Agent tools allowlist (reviewer agents): [[CLAUDECODE-01-PLUGIN-CANON]] Subagent Matrix.
- Release validation gate: [[RELEASE-01-VALIDATION]].

## Verification

- `bash scripts/smoke_hooks.sh`: dry-runs Serena and flow hook scripts. The script has 5 steps: "hooks.json parse", "hook scripts exist + bash -n", "skip-flag exit 0", "outside-git defensive guard", and "runtime stdin payloads (parse safety + advisory routing)" (added Wave 2). The stdin payloads step runs 6 test cases: empty prompt, non-trigger prompt, RU code-related prompt, EN code-related prompt (all against `user_prompt_submit.sh`), clean stop state (`stop_memory_sync.sh`), and non-git command (`post_tool_use_commit_advice.sh`). Verified at `scripts/smoke_hooks.sh` lines 127-195 at HEAD.
- `bash scripts/smoke_serena_memory_taxonomy.sh`: verifies stale Stop hook exit `2`, taxonomy text, target list, and loop guard.
- `bash -n plugins/rldyour-serena-mcp/hooks/*.sh plugins/rldyour-flow/hooks/*.sh`: syntax check.
- `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`: verifies Serena Stop dependency.
- `python3 plugins/rldyour-flow/scripts/flow_post_task_state.py`: verifies flow Stop dependency.
