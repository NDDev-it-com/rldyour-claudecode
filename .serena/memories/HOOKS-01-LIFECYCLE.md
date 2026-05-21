<!-- Memory Metadata
Last updated: 2026-05-18
Last commit: 84c28c2 fix(bootstrap): resolve git paths in submodules
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
- `plugins/rldyour-flow/hooks/pre_tool_use_ci_advisory.sh`: PreToolUse CI advisory (9th hook script, added 0.5.1 commit `22dc9d9`).
- `scripts/smoke_serena_memory_taxonomy.sh`: stale Stop hook and loop-guard behavior test.

## Current Behavior

- Two plugins own hooks: `rldyour-serena-mcp` and `rldyour-flow`.
- Registered lifecycle rows at HEAD (9 hook scripts in 2 manifests, 19 handlers total):
  - `UserPromptSubmit`: `rldyour-serena-mcp/hooks/user_prompt_submit.sh` (1 handler). Skip: `RLDYOUR_SKIP_USER_PROMPT_HINT`.
  - `PreToolUse:Bash`: `rldyour-serena-mcp/hooks/prepare_auto_sync.sh` (5 handlers: `git commit*`, `git merge*`, `git cherry-pick*`, `git rebase*`, `git am*`). Architecture F-2 closure.
  - `PreToolUse:Bash`: `rldyour-flow/hooks/pre_tool_use_ci_advisory.sh` (3 handlers: `gh workflow*`, `gh run*`, `gh actions*`). Advisory, exits 0. Skip: `RLDYOUR_SKIP_CI_ADVISORY`.
  - `PostToolUse:Bash`: `rldyour-serena-mcp/hooks/mark_sync_required.sh` (5 handlers: `git commit*`, `git merge*`, `git cherry-pick*`, `git rebase*`, `git am*`).
  - `PostToolUse:Bash`: `rldyour-flow/hooks/post_tool_use_commit_advice.sh` (1 handler: `git commit*`).
  - `SessionStart`: `rldyour-flow/hooks/session_start_worktree_bootstrap.sh` (1 handler).
  - `SessionStart`: `rldyour-flow/hooks/session_start_context.sh` (1 handler).
  - `Stop`: `rldyour-serena-mcp/hooks/stop_memory_sync.sh` (1 handler).
  - `Stop`: `rldyour-flow/hooks/stop_post_task_sync.sh` (1 handler).
- Handler breakdown: rldyour-serena-mcp 1+5+5+1=12; rldyour-flow 2+3+1+1=7; total 19 handlers. Verified at both `hooks.json` files at HEAD.
- Stop hooks are advisory enforcement gates. They write guidance to stderr and block with `exit 2` when required work remains.
- SessionStart and PostToolUse advisory hooks emit JSON `hookSpecificOutput.additionalContext` when applicable.
- `session_start_worktree_bootstrap.sh` is the only bounded mutating hook; it runs `fullrepo_sync.py --restore`, never `--publish` and never touches origin.
- `mark_sync_required.sh` treats agent-instruction paths as sync-relevant and writes `.serena/.serena_sync_state.json` with `required=true` when those paths changed.
- `stop_memory_sync.sh` includes taxonomy guidance without shell backticks in the Bash string, avoiding command-substitution side effects in advisory messages.
- **P3 UserPromptSubmit surgical rewrite** (commit `d48944b refactor(hook)`): `plugins/rldyour-serena-mcp/hooks/user_prompt_submit.sh` rewritten. Strong triggers (code/class/function/refactor/architecture, EN+RU) inject directly. Weak triggers (project/directory/file, EN+RU) inject only when paired with an action verb implying actual code work. Single python3 parser/emitter (no pipe chain). Verified at `plugins/rldyour-serena-mcp/hooks/user_prompt_submit.sh` at HEAD (104 lines).
- All 9 hook scripts (`plugins/rldyour-{flow,serena-mcp}/hooks/*.sh`) use full strict mode: `set -euo pipefail` + `IFS=$'\n\t'` + `unset CDPATH`.
- **Defensive `PYTHON_BIN` resolver (0.5.2, commit `10c8f06`)**: all 9 hook scripts replaced bare `python3` invocations with `"${PYTHON_BIN}"` (49 replacements total). Canonical resolver block (first 4 lines after `set -euo pipefail` header):
  ```bash
  PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)}"
  if [ -z "${PYTHON_BIN}" ] || [ ! -x "${PYTHON_BIN}" ]; then
    exit 0
  fi
  ```
  Exit semantics preserved: Stop hooks still `exit 2` to block after their own gate logic; advisory hooks still `exit 0` when Python is unavailable. Canonical pattern from tw73/Mole, rsyslog, dmauser/opnazure. Rationale: sanitized subprocess PATH may omit `~/.local/bin`; uv-managed Python 3.14 symlinks can be transiently broken during interpreter upgrades. Verified at all 9 hook scripts at HEAD `da432c6` via `grep -n "PYTHON_BIN" plugins/rldyour-{serena-mcp,flow}/hooks/*.sh`.
- **P0 hooks canonical-form rewrite** (commit `614bdcf fix(hooks)`): both `hooks.json` files use exec-form `command: "/bin/bash"` (absolute path, PATH-independent) + `args: ["${CLAUDE_PLUGIN_ROOT}/hooks/X.sh"]` per CC v2.1.139+. The `if` filter lives inside each inner hook handler (sibling to `type`/`command`/`args`). Verified at both `hooks.json` files at HEAD.
- **0.5.1 hook changes** (commit `24d2290 perf(hooks)`): Serena `PreToolUse:Bash` and `PostToolUse:Bash` use 5 explicit handlers per event (`git commit*`, `git merge*`, `git cherry-pick*`, `git rebase*`, `git am*`). All handlers in both `hooks.json` files use `command: "/bin/bash"`. Handler totals: Serena 1+5+5+1=12 handlers; flow 2+3+1+1=7 handlers; total 19 handlers in 2 manifests.
- **New PreToolUse hook `pre_tool_use_ci_advisory.sh`** (commit `22dc9d9 feat(hook)`): 9th hook script at `plugins/rldyour-flow/hooks/pre_tool_use_ci_advisory.sh`. Three narrow handlers for `Bash(gh workflow*)`, `Bash(gh run*)`, `Bash(gh actions*)`. Advisory ONLY - exits 0. Skip flag: `RLDYOUR_SKIP_CI_ADVISORY=1`. Verified at `plugins/rldyour-flow/hooks/pre_tool_use_ci_advisory.sh` and `plugins/rldyour-flow/hooks/hooks.json` at HEAD.
- **`user_prompt_submit.sh` RLDYOUR_SKIP_USER_PROMPT_HINT** (commit `cea0d73 feat(hook)`): `plugins/rldyour-serena-mcp/hooks/user_prompt_submit.sh` line 25 checks `RLDYOUR_SKIP_USER_PROMPT_HINT`. Verified at HEAD.

## Coordination Sequence

1. Serena Stop hook checks `serena_memory_state.py`.
2. If memories are stale, Serena Stop blocks with instructions to run `flow-memory-sync` or the equivalent Serena memory workflow.
3. After memories are current, flow Stop derives `serena_current` by calling `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py` directly.
4. Flow Stop then checks git/docs/fullrepo/cleanup state through `flow_post_task_state.py` and points to `flow-post-task-sync` when needed.
5. Loop guard markers `.serena/.sync_marker` and `.serena/.flow_sync_marker` allow repeated Stop attempts for the same fingerprint without infinite loops. `.serena/.sync_marker` contains compound fingerprint `${HEAD_SHA}:${NEWEST_SHA:-none}` (D32, commit `23901c6`); `.serena/.flow_sync_marker` contains SHA-256 content-hash fingerprint of 10-field `fingerprint_payload` (D31, commit `23901c6`).

## Contracts And Data

- Skip flags: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT`, `RLDYOUR_SKIP_FLOW_COMMIT_ADVICE`, `RLDYOUR_SKIP_STOP_GATES`, `RLDYOUR_SKIP_FLOW_SYNC`, `RLDYOUR_SKIP_SERENA_SYNC`, `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP`, `RLDYOUR_SKIP_CI_ADVISORY`, `RLDYOUR_SKIP_USER_PROMPT_HINT`.
- Stop hook exit code `2` is intentional blocking guidance; other hook errors should avoid breaking normal work unless the gate is intentionally blocking.
- `stop_memory_sync.sh` includes analyzer context: risk profile, analysis source, changed file count, memory taxonomy, memory targets, and high-priority areas.
- `post_tool_use_commit_advice.sh` sanitizes user-controlled text through `sanitize_for_advisory()` helper (extracted at lines 104-122) before embedding in advisory output. Covers `INJECTION_MARKERS` (13+ families) plus `BIDI_CONTROLS` (U+202A-U+202E, U+2066-U+2069). Verified at `plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh` lines 69-185 at HEAD.
- The Stop hook prompt tells the orchestrator to keep memories in `AREA-01-SLUG.md` form and use `CORE-01-INDEX.md` as the map.
- PYTHON_BIN missing or not executable → all hooks exit 0 (non-blocking). This preserves the non-blocking invariant for advisory hooks. Stop hooks (which would normally exit 2) also exit 0 in this failure mode, so Python unavailability does not permanently block sessions.

## Invariants

- No hook performs push, merge, release tagging, branch deletion, fullrepo publish, or arbitrary memory writes.
- High-blast-radius work stays in orchestrated skills/subagents after model judgement.
- Worktree bootstrap must restore agent-only files from `origin/fullrepo` and must never publish from a new worktree.
- Hook changes must keep `scripts/smoke_hooks.sh` aligned with skip flags and expected behavior.
- Memory Stop advisory behavior must keep `scripts/smoke_serena_memory_taxonomy.sh` passing.
- All hook scripts must use the canonical `PYTHON_BIN` resolver block (pattern in [[PATTERNS-01-CANONICAL]] Hook Script Python Resolver section).

## Cross-References

- Memory freshness contract: [[SERENA-01-MEMORY-SYNC]] (analyzer, sync markers, writer flow, AGENT_INSTRUCTION_PATHS canon).
- Post-task SDLC workflow: [[FLOW-01-SDLC]] (flow-post-task-sync, fullrepo publish, cleanup).
- Hook implementation patterns: [[PATTERNS-01-CANONICAL]] Hook Script section and Hook Script Python Resolver section.
- Injection-marker sanitization (D18, D42, D43): [[TECHDEBT-01-NOW]] D18, D42, D43.
- Closed debt D16 (strict mode), D17 (utility scripts): [[TECHDEBT-01-NOW]].
- Closed debt D77 (defensive python3 resolver): [[TECHDEBT-01-NOW]] D77.
- Skip flags: documented here; RLDYOUR_SKIP_STOP_GATES disables both Stop gates.
- Agent tools allowlist (reviewer agents): [[CLAUDECODE-01-PLUGIN-CANON]] Subagent Matrix.
- Release validation gate: [[RELEASE-01-VALIDATION]].

## Verification

- `bash scripts/smoke_hooks.sh`: dry-runs Serena and flow hook scripts. The script has 5 steps: "hooks.json parse", "hook scripts exist + bash -n", "skip-flag exit 0", "outside-git defensive guard", and "runtime stdin payloads (parse safety + advisory routing)".
- `bash scripts/smoke_serena_memory_taxonomy.sh`: verifies stale Stop hook exit `2`, taxonomy text, target list, and loop guard. 0.5.2 version asserts the new invariant (`required=False` for agent-instruction-only wave) plus a companion negative case (product-code commit still requires sync).
- `bash -n plugins/rldyour-serena-mcp/hooks/*.sh plugins/rldyour-flow/hooks/*.sh`: syntax check.
- `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`: verifies Serena Stop dependency.
- `python3 plugins/rldyour-flow/scripts/flow_post_task_state.py`: verifies flow Stop dependency.
