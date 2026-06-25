#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
unset CDPATH

if [ "${RLDYOUR_SKIP_FLOW_SESSION_CONTEXT:-0}" = "1" ]; then
  exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

HOOK_INPUT_FILE=$(mktemp "${TMPDIR:-/tmp}/rldyour-session-context-input.XXXXXX")
trap 'rm -f "$HOOK_INPUT_FILE"' EXIT
cat > "$HOOK_INPUT_FILE"

python3 - "$ROOT" "$HOOK_INPUT_FILE" "$PLUGIN_DIR/scripts/project_flow_policy.py" <<'PY'
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
HOOK_INPUT = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace")
POLICY_SCRIPT = Path(sys.argv[3])
GIT_TIMEOUT = 0.8
DOC_FILES = ("AGENTS.md", ".claude/CLAUDE.md", "CLAUDE.md", "REVIEW.md")


def parse_source(raw: str) -> str:
    try:
        payload = json.loads(raw)
    except Exception:
        return "unknown"
    source = payload.get("source", "unknown")
    return source if isinstance(source, str) else "unknown"


def git(args: list[str], timeout: float = GIT_TIMEOUT) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return 124, ""
    return proc.returncode, proc.stdout.rstrip("\n")


def git_stdout(args: list[str], default: str = "") -> str:
    status, output = git(args)
    return output if status == 0 and output else default


def split_porcelain_path(line: str) -> str:
    path = line[3:] if len(line) > 3 else line
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.strip()


def dirty_paths() -> tuple[list[str], bool]:
    status, output = git(["status", "--porcelain=v1", "--untracked-files=no"], timeout=1.2)
    if status == 124:
        return [], True
    if status != 0 or not output:
        return [], False
    return [split_porcelain_path(line) for line in output.splitlines() if line.strip()], False


def ahead_behind(upstream: str) -> tuple[int, int, bool]:
    if not upstream:
        return 0, 0, False
    status, output = git(["rev-list", "--left-right", "--count", f"HEAD...{upstream}"])
    if status == 124:
        return 0, 0, True
    if status != 0 or not output:
        return 0, 0, False
    parts = output.split()
    if len(parts) != 2:
        return 0, 0, False
    try:
        return int(parts[0]), int(parts[1]), False
    except ValueError:
        return 0, 0, False


def worktree_count() -> tuple[int, bool]:
    status, output = git(["worktree", "list", "--porcelain"])
    if status == 124:
        return 0, True
    if status != 0 or not output:
        return 1, False
    return max(1, sum(1 for line in output.splitlines() if line.startswith("worktree "))), False


def tracked_agent_count() -> tuple[int, bool]:
    status, output = git(["ls-files", "--", "AGENTS.md", ".claude/CLAUDE.md", "CLAUDE.md", "REVIEW.md", ".serena"])
    if status == 124:
        return 0, True
    if status != 0 or not output:
        return 0, False
    return len([line for line in output.splitlines() if line.strip()]), False


def memory_count() -> int | None:
    memories = ROOT / ".serena" / "memories"
    if not memories.is_dir():
        return None
    try:
        return sum(1 for path in memories.rglob("*.md") if path.is_file())
    except OSError:
        return None


def project_policy() -> dict:
    if not POLICY_SCRIPT.is_file():
        return {}
    try:
        proc = subprocess.run(
            ["python3", str(POLICY_SCRIPT), "--json"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=1.2,
        )
    except subprocess.TimeoutExpired:
        return {}
    if proc.returncode != 0 and not proc.stdout.strip():
        return {}
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def main() -> int:
    source = parse_source(HOOK_INPUT)
    branch = git_stdout(["branch", "--show-current"], "detached")
    head = git_stdout(["rev-parse", "--short=7", "HEAD"], "unknown")
    upstream = git_stdout(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"], "none")
    if upstream == "none":
        ahead, behind, ahead_timeout = 0, 0, False
    else:
        ahead, behind, ahead_timeout = ahead_behind(upstream)
    dirty, dirty_timeout = dirty_paths()
    shown_dirty = dirty[:12]
    remaining_dirty = max(len(dirty) - len(shown_dirty), 0)
    wt_count, wt_timeout = worktree_count()
    tracked_agents, tracked_timeout = tracked_agent_count()
    policy = project_policy()
    effective_policy = policy.get("effective", {}) if isinstance(policy.get("effective"), dict) else {}
    normal_policy = (
        effective_policy.get("normal_branch_policy", {})
        if isinstance(effective_policy.get("normal_branch_policy"), dict)
        else {}
    )
    branch_cleanup_policy = (
        effective_policy.get("branch_cleanup", {})
        if isinstance(effective_policy.get("branch_cleanup"), dict)
        else {}
    )
    execution_policy = (
        effective_policy.get("execution", {})
        if isinstance(effective_policy.get("execution"), dict)
        else {}
    )
    cmux_policy = (
        effective_policy.get("cmux", {})
        if isinstance(effective_policy.get("cmux"), dict)
        else {}
    )
    instruction_docs_policy = (
        effective_policy.get("instruction_docs", {})
        if isinstance(effective_policy.get("instruction_docs"), dict)
        else {}
    )
    docs_present = [path for path in DOC_FILES if (ROOT / path).is_file()]
    mem_count = memory_count()
    serena_sync_marker = (ROOT / ".serena" / ".serena_sync_state.json").is_file()
    flow_marker = (ROOT / ".serena" / ".flow_sync_marker").is_file() or (
        ROOT / ".serena" / ".flow_post_task_state.json"
    ).is_file()
    needs_attention = bool(dirty or ahead or behind or serena_sync_marker or flow_marker)

    lines = [
        "rldyour-flow session context (fast, offline, read-only):",
        f"- Session source: {source}.",
        f"- Repository: {ROOT}.",
        (
            "- Git: "
            f"branch {branch}, HEAD {head}, upstream {upstream}, "
            f"ahead {ahead}, behind {behind}."
        ),
        f"- Worktrees detected: {'unknown' if wt_timeout else wt_count}.",
        (
            "- Serena memories: "
            f"{'sync marker pending' if serena_sync_marker else 'no sync marker'}, "
            f"memory_count {mem_count if mem_count is not None else 'unknown'}."
        ),
        (
            "- Agent context: tracked normally on main "
            f"(tracked agent-context paths {'unknown' if tracked_timeout else tracked_agents})."
        ),
        (
            "- Project policy: "
            f"source {policy.get('source', 'built-in defaults')}, "
            f"agent_files {normal_policy.get('agent_files', 'allowed')}, "
            f"instruction_docs.mode {instruction_docs_policy.get('mode', 'tracked-main')}, "
            f"branch_cleanup.mode {branch_cleanup_policy.get('mode', 'advisory')}."
        ),
        (
            "- Execution policy: "
            f"mode {os.environ.get('RLDYOUR_EXECUTION_MODE') or execution_policy.get('mode', 'standard')}, "
            f"agent_role {os.environ.get('RLDYOUR_AGENT_ROLE') or execution_policy.get('agent_role', 'auto')}, "
            f"cmux.enabled {cmux_policy.get('enabled', False)}, "
            f"workspace {os.environ.get('CMUX_WORKSPACE_ID') or 'none'}, "
            f"surface {os.environ.get('CMUX_SURFACE_ID') or 'none'}."
        ),
        "- Branch cleanup: not evaluated during SessionStart; run flow-post-task-sync before final delivery.",
    ]

    if ahead_timeout:
        lines.append("- Git upstream drift check timed out; treat ahead/behind as unknown until ry-init.")
    if dirty_timeout:
        lines.append("- Dirty file check timed out; inspect git status during ry-init.")
    elif dirty:
        lines.append(f"- Tracked dirty files ({len(dirty)}):")
        lines.extend(f"  - {path}" for path in shown_dirty)
        if remaining_dirty:
            lines.append(f"  - ... plus {remaining_dirty} more")
    else:
        lines.append("- Tracked dirty files: none.")

    if docs_present:
        lines.append("- Project instruction docs present: " + ", ".join(docs_present) + ".")

    if needs_attention:
        lines.append("- Flow sync signal: maybe pending. Before final delivery, run flow-post-task-sync after Serena memories are current and follow the effective project policy.")
    else:
        lines.append("- Flow sync signal: no startup marker or tracked dirty signal detected.")

    lines.extend(
        [
            "- If a task starts with insufficient context, trigger scoped ry-init before editing.",
            "- Agent context (.serena/, AGENTS.md, .claude/) is tracked normally on main; read it directly from the checked-out tree.",
            "- Before edits, pass the context sufficiency gate: code paths, symbols, data contracts, integration points, existing patterns, checks, and research evidence must be known or explicitly marked as unknown.",
            "- This context is advisory only. Do not block execution only because this hook emitted warnings.",
        ]
    )

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": "\n".join(lines),
                }
            }
        )
    )
    return 0


raise SystemExit(main())
PY
