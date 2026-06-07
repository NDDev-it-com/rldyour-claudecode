#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_flow_policy import load_policy  # noqa: E402

RUNTIME_IGNORED = {
    ".serena/.sync_marker",
    ".serena/.serena_sync_state.json",
    ".serena/.auto_sync_head",
    ".serena/.active_workflow_intent.json",
    ".serena/.dirty_stop_ack",
    ".serena/.flow_sync_marker",
    ".serena/.flow_post_task_state.json",
    ".serena/.flow_blocker_ack.json",
    ".serena/.stop_lifecycle_timeout_marker",
}
UNTRACKED_BOOTSTRAP_IGNORED = {
    ".serena/.gitignore",
    ".serena/project.yml",
    ".serena/project.local.yml",
}

DOC_FILES = ("AGENTS.md", ".claude/CLAUDE.md", "CLAUDE.md")
PROTECTED_BRANCHES = {"main", "master", "dev", "develop", "development", "staging", "production", "prod", "fullrepo"}
WORKFLOW_BRANCH_PREFIXES = ("ai/", "claude/", "ry-", "rldyour/")


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True)


def _stdout(*args: str) -> str:
    return _git(*args).stdout.strip()


def _subprocess_timeout() -> float:
    raw = os.environ.get("RLDYOUR_FLOW_SUBPROCESS_TIMEOUT_SECONDS", "10")
    try:
        return max(0.1, float(raw))
    except ValueError:
        return 10.0


def _porcelain_paths() -> list[str]:
    raw = _git("status", "--porcelain").stdout.rstrip("\n")
    paths: list[str] = []
    for line in raw.splitlines():
        if not line:
            continue
        status = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if (
            path
            and path not in RUNTIME_IGNORED
            and not (status == "??" and path in UNTRACKED_BOOTSTRAP_IGNORED)
        ):
            paths.append(path)
    return sorted(paths)


def _ahead_behind() -> tuple[int, int, str]:
    upstream = _stdout("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if not upstream:
        return 0, 0, ""
    counts = _stdout("rev-list", "--left-right", "--count", f"{upstream}...HEAD")
    try:
        behind_s, ahead_s = counts.split()
        return int(ahead_s), int(behind_s), upstream
    except ValueError:
        return 0, 0, upstream


def _worktree_count() -> int:
    raw = _stdout("worktree", "list", "--porcelain")
    return sum(1 for line in raw.splitlines() if line.startswith("worktree "))


def _ref_exists(ref: str) -> bool:
    return _git("rev-parse", "--verify", "--quiet", ref).returncode == 0


def _default_cleanup_base() -> str:
    for candidate in ("origin/main", "main", "origin/master", "master"):
        if _ref_exists(candidate):
            return candidate
    return "HEAD"


def _local_merged_branches(base: str, current_branch: str, protected_branches: set[str]) -> list[str]:
    raw = _stdout("branch", "--format=%(refname:short)", "--merged", base)
    branches: list[str] = []
    for branch in raw.splitlines():
        branch = branch.strip()
        if not branch or branch == current_branch or branch in protected_branches:
            continue
        branches.append(branch)
    return sorted(set(branches))


def _remote_merged_branches(base: str, protected_branches: set[str]) -> list[str]:
    raw = _stdout("branch", "-r", "--format=%(refname:short)", "--merged", base)
    branches: list[str] = []
    for ref in raw.splitlines():
        ref = ref.strip()
        if not ref or ref.endswith("/HEAD") or " -> " in ref or "/" not in ref:
            continue
        branch = ref.split("/", 1)[1] if "/" in ref else ref
        if branch in protected_branches:
            continue
        branches.append(ref)
    return sorted(set(branches))


def _workflow_branch(branch: str, prefixes: tuple[str, ...]) -> bool:
    normalized = branch.split("/", 1)[1] if branch.startswith("origin/") else branch
    return normalized.startswith(prefixes)


def _worktree_cleanup_candidates(base: str, protected_branches: set[str]) -> list[dict[str, str]]:
    raw = _stdout("worktree", "list", "--porcelain")
    candidates: list[dict[str, str]] = []
    current_root = _stdout("rev-parse", "--show-toplevel")
    item: dict[str, str] = {}

    def flush() -> None:
        if not item:
            return
        path = item.get("worktree", "")
        branch_ref = item.get("branch", "")
        branch = branch_ref.removeprefix("refs/heads/")
        if not path or path == current_root or not branch or branch in protected_branches:
            return
        if _git("merge-base", "--is-ancestor", branch, base).returncode == 0:
            candidates.append({"path": path, "branch": branch})

    for line in raw.splitlines():
        if not line:
            flush()
            item = {}
            continue
        key, _, value = line.partition(" ")
        item[key] = value
    flush()
    return candidates


def _dict_section(value: object) -> dict[str, Any]:
    return cast(dict[str, Any], value) if isinstance(value, dict) else {}


def _effective_policy(policy: dict[str, Any]) -> dict[str, Any]:
    return _dict_section(policy.get("effective"))


def _runtime_execution(effective_policy: dict[str, Any]) -> dict[str, Any]:
    execution_policy = effective_policy.get("execution")
    if not isinstance(execution_policy, dict):
        execution_policy = {}
    mode = os.environ.get("RLDYOUR_EXECUTION_MODE") or str(execution_policy.get("mode", "standard"))
    if mode not in {"standard", "orchestrator"}:
        mode = "standard"

    role = os.environ.get("RLDYOUR_AGENT_ROLE") or str(execution_policy.get("agent_role", "auto"))
    if role not in {"auto", "standalone", "orchestrator", "worker"}:
        role = "auto"
    if role == "auto":
        if mode == "orchestrator" and os.environ.get("RLDYOUR_ORCHESTRATOR") == "1":
            role = "orchestrator"
        elif mode == "orchestrator" and (
            os.environ.get("RLDYOUR_WORKER") == "1" or os.environ.get("RLDYOUR_WORKER_ID")
        ):
            role = "worker"
        else:
            role = "standalone"

    return {
        "execution_mode": mode,
        "agent_role": role,
        "task_delegation": str(execution_policy.get("task_delegation", "direct")),
        "cmux_workspace_id": os.environ.get("CMUX_WORKSPACE_ID", ""),
        "cmux_surface_id": os.environ.get("CMUX_SURFACE_ID", ""),
        "worker_id": os.environ.get("RLDYOUR_WORKER_ID", ""),
        "worker_allowed_paths": _split_worker_paths(os.environ.get("RLDYOUR_WORKER_ALLOWED_PATHS", "")),
    }


def _split_worker_paths(raw: str) -> list[str]:
    if not raw:
        return []
    normalized = raw.replace("\n", ",").replace(os.pathsep, ",")
    return sorted({part.strip().strip("/") for part in normalized.split(",") if part.strip().strip("/")})


def _path_matches_scope(path: str, scopes: list[str]) -> bool:
    normalized = path.strip("/")
    for scope in scopes:
        if normalized == scope or normalized.startswith(scope.rstrip("/") + "/"):
            return True
    return False


def _policy_list(section: dict[str, Any], key: str, fallback: tuple[str, ...]) -> tuple[str, ...]:
    value = section.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        return fallback
    return tuple(value)


def _branch_cleanup_state(current_branch: str, policy: dict[str, Any]) -> dict[str, Any]:
    effective = _effective_policy(policy)
    branches_policy = _dict_section(effective.get("branches"))
    cleanup_policy = _dict_section(effective.get("branch_cleanup"))
    protected_branches = set(PROTECTED_BRANCHES)
    protected_branches.update(branches_policy.get("protected_branches", []) if isinstance(branches_policy, dict) else [])
    protected_branches.update(cleanup_policy.get("protected_branches", []) if isinstance(cleanup_policy, dict) else [])
    workflow_prefixes = _policy_list(cleanup_policy, "workflow_branch_prefixes", WORKFLOW_BRANCH_PREFIXES)
    blocking_prefixes = _policy_list(cleanup_policy, "blocking_prefixes", workflow_prefixes)
    cleanup_mode = str(cleanup_policy.get("mode", "advisory"))
    block_stop = bool(cleanup_policy.get("block_stop")) or cleanup_mode == "strict"

    base = _default_cleanup_base()
    local_merged = _local_merged_branches(base, current_branch, protected_branches)
    remote_merged = _remote_merged_branches(base, protected_branches)
    worktree_candidates = _worktree_cleanup_candidates(base, protected_branches)
    workflow_local = [branch for branch in local_merged if _workflow_branch(branch, workflow_prefixes)]
    workflow_remote = [branch for branch in remote_merged if _workflow_branch(branch, workflow_prefixes)]
    blocking_local: list[str] = []
    blocking_remote: list[str] = []
    blocking_worktrees: list[dict[str, str]] = []
    advisory_local: list[str] = []
    advisory_remote: list[str] = []
    advisory_worktrees: list[dict[str, str]] = []

    if cleanup_mode == "strict" and block_stop:
        blocking_local = [branch for branch in local_merged if _workflow_branch(branch, blocking_prefixes)]
        blocking_remote = [branch for branch in remote_merged if _workflow_branch(branch, blocking_prefixes)]
        blocking_worktrees = [
            item for item in worktree_candidates if _workflow_branch(item.get("branch", ""), blocking_prefixes)
        ]
        advisory_local = [branch for branch in local_merged if branch not in blocking_local]
        advisory_remote = [branch for branch in remote_merged if branch not in blocking_remote]
        advisory_worktrees = [item for item in worktree_candidates if item not in blocking_worktrees]
    elif cleanup_mode != "disabled":
        advisory_local = local_merged
        advisory_remote = remote_merged
        advisory_worktrees = worktree_candidates

    blocking_candidates: list[Any] = [*blocking_local, *blocking_remote, *blocking_worktrees]
    advisory_candidates: list[Any] = [*advisory_local, *advisory_remote, *advisory_worktrees]
    needs_cleanup = bool(blocking_candidates)
    return {
        "base": base,
        "mode": cleanup_mode,
        "block_stop": block_stop,
        "protected_branches": sorted(protected_branches),
        "local_merged_branches": local_merged,
        "remote_merged_branches": remote_merged,
        "merged_workflow_branches": sorted(set(workflow_local + workflow_remote)),
        "worktree_cleanup_candidates": worktree_candidates,
        "blocking_local_branches": blocking_local,
        "blocking_remote_branches": blocking_remote,
        "blocking_worktree_candidates": blocking_worktrees,
        "blocking_candidates": blocking_candidates,
        "advisory_local_branches": advisory_local,
        "advisory_remote_branches": advisory_remote,
        "advisory_worktree_candidates": advisory_worktrees,
        "advisory_candidates": advisory_candidates,
        "needs_cleanup": needs_cleanup,
    }


def _resolve_sibling_plugin_script(plugin: str, relative: str) -> Path | None:
    """Find a script in a sibling plugin via repo-relative or CLAUDE_PLUGIN_ROOT fallback.

    Co-location assumption (closure of architecture F-4, info 90, from review
    wave `2026-05-16T1859Z-61b913d`): `rldyour-flow` and the named sibling
    plugin are expected to live inside the same marketplace repo under
    per-entry relative sources (`./plugins/<name>`). Both lookup paths reflect this:

      1. `plugins/<plugin>/<relative>` - resolves when the script runs with
         cwd == repo root (the standard invocation pattern through
         `bash scripts/...` or hook scripts that `cd "$(git rev-parse
         --show-toplevel)"`).
      2. `${CLAUDE_PLUGIN_ROOT}/../<plugin>/<relative>` - fallback when
         Claude Code injects `CLAUDE_PLUGIN_ROOT` pointing at the calling
         plugin's root; `..` walks back to the shared `plugins/` parent.

    Neither path declares an explicit plugin dependency, which is intentional:
    the marketplace ships all nine plugins together. If `rldyour-flow` is
    ever installed without `rldyour-serena-mcp`, this returns `None` and
    `_serena_current` falls back to `(True, {})` rather than crashing.
    The canonical alternative path pattern is
    `"$(git rev-parse --show-toplevel)"/plugins/<plugin>/...` per
    PATTERNS-01-CANONICAL; that pattern is used in skill bodies but not
    here because this is a long-lived Python script with multiple call
    sites, not a one-shot shell expansion.
    """
    candidates = [
        Path(__file__).resolve().parents[1].parent / plugin / relative,
        Path(f"plugins/{plugin}/{relative}"),
    ]
    plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root_env:
        candidates.append((Path(plugin_root_env) / ".." / plugin / relative).resolve())
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _serena_current() -> tuple[bool, dict[str, Any]]:
    candidate = _resolve_sibling_plugin_script("rldyour-serena-mcp", "scripts/serena_memory_state.py")
    if candidate is None:
        return True, {}
    try:
        proc = subprocess.run(
            [sys.executable, str(candidate)],
            check=False,
            capture_output=True,
            text=True,
            timeout=_subprocess_timeout(),
        )
    except subprocess.TimeoutExpired:
        return True, {"not_proven": "serena memory state timed out"}
    if proc.returncode != 0 or not proc.stdout.strip():
        return True, {}
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return True, {}
    return bool(payload.get("is_current", True)), payload


def _self_plugin_script(relative: str) -> Path | None:
    """Find a script in this plugin (rldyour-flow) via repo-relative or CLAUDE_PLUGIN_ROOT."""
    candidates = [
        Path(__file__).resolve().parents[1] / relative,
        Path(f"plugins/rldyour-flow/{relative}"),
    ]
    plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root_env:
        candidates.append((Path(plugin_root_env) / relative).resolve())
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def _fullrepo_state() -> dict[str, Any]:
    candidate = _self_plugin_script("scripts/fullrepo_sync.py")
    if candidate is None:
        return {}
    args = [sys.executable, str(candidate), "--status-json"]
    if os.environ.get("RLDYOUR_FLOW_STATE_LOCAL_ONLY") == "1":
        args.append("--local-only")
    try:
        proc = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=_subprocess_timeout(),
        )
    except subprocess.TimeoutExpired:
        return {}
    if proc.returncode != 0 or not proc.stdout.strip():
        return {}
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _instruction_docs_state() -> dict[str, Any]:
    candidate = _self_plugin_script("scripts/instruction_docs_state.py")
    if candidate is None:
        return {}
    env = os.environ.copy()
    if os.environ.get("RLDYOUR_FLOW_STATE_LOCAL_ONLY") == "1":
        env["RLDYOUR_FULLREPO_STATUS_LOCAL_ONLY"] = "1"
    try:
        proc = subprocess.run(
            [sys.executable, str(candidate), "--json"],
            check=False,
            capture_output=True,
            text=True,
            env=env,
            timeout=_subprocess_timeout(),
        )
    except subprocess.TimeoutExpired:
        return {}
    if proc.returncode != 0 or not proc.stdout.strip():
        return {}
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def state() -> dict[str, Any]:
    if _git("rev-parse", "--is-inside-work-tree").returncode != 0:
        return {"is_git_repo": False, "needs_flow_sync": False, "serena_current": True}

    project_policy = load_policy(Path.cwd())
    effective_policy = _effective_policy(project_policy)
    fullrepo_policy = _dict_section(effective_policy.get("fullrepo"))
    stop_policy = _dict_section(effective_policy.get("stop_hook"))
    serena_policy = _dict_section(effective_policy.get("serena"))
    fullrepo_mode = str(fullrepo_policy.get("mode", "auto"))
    runtime_execution = _runtime_execution(effective_policy)
    execution_mode = str(runtime_execution["execution_mode"])
    agent_role = str(runtime_execution["agent_role"])
    is_worker = execution_mode == "orchestrator" and agent_role == "worker"

    head_full = _stdout("rev-parse", "HEAD")
    head_sha = head_full[:7] if head_full else ""
    branch = _stdout("branch", "--show-current") or "detached"
    dirty_files = _porcelain_paths()
    ahead, behind, upstream = _ahead_behind()
    serena_current, serena_state = _serena_current()
    doc_files_present = [path for path in DOC_FILES if Path(path).is_file()]
    doc_files_changed = [path for path in dirty_files if path in DOC_FILES]
    worktree_count = _worktree_count()
    fullrepo_state = _fullrepo_state()
    instruction_docs_state = _instruction_docs_state()
    branch_cleanup_state = _branch_cleanup_state(branch, project_policy)

    worktree_agent_paths = fullrepo_state.get("worktree_agent_paths")
    if not isinstance(worktree_agent_paths, list):
        worktree_agent_paths = []
    tracked_agent_paths = fullrepo_state.get("tracked_agent_paths")
    if not isinstance(tracked_agent_paths, list):
        tracked_agent_paths = []
    has_existing_fullrepo_context = bool(
        tracked_agent_paths
        or fullrepo_state.get("remote_fullrepo_exists")
        or fullrepo_state.get("local_fullrepo_sha")
        or fullrepo_state.get("exclude_installed")
    )
    has_agent_paths = bool(worktree_agent_paths or tracked_agent_paths)
    network_checked = bool(fullrepo_state.get("network_checked", True))
    remote_configured = bool(fullrepo_state.get("remote_configured", True))
    remote_missing_attention = bool(
        fullrepo_mode == "required"
        and worktree_agent_paths
        and network_checked
        and remote_configured
        and not bool(fullrepo_state.get("remote_fullrepo_exists", False))
    )
    fullrepo_mismatch = bool(
        fullrepo_state
        and has_agent_paths
        and not bool(fullrepo_state.get("fullrepo_matches_worktree", True))
    )
    exclude_missing = bool(
        fullrepo_state
        and has_existing_fullrepo_context
        and not bool(fullrepo_state.get("exclude_installed", True))
    )
    fullrepo_attention_candidate = bool(exclude_missing or remote_missing_attention or fullrepo_mismatch)
    fullrepo_blocks_stop = bool(stop_policy.get("block_on_fullrepo", True)) and bool(
        fullrepo_policy.get("block_stop", True)
    )
    fullrepo_needs_attention = False
    if fullrepo_mode == "required":
        fullrepo_needs_attention = fullrepo_attention_candidate and fullrepo_blocks_stop
    elif fullrepo_mode == "auto":
        fullrepo_needs_attention = bool(has_existing_fullrepo_context and fullrepo_attention_candidate and fullrepo_blocks_stop)

    blocking_reasons: list[str] = []
    advisory_reasons: list[str] = []
    if is_worker:
        worker_scopes = runtime_execution.get("worker_allowed_paths")
        worker_scopes = worker_scopes if isinstance(worker_scopes, list) else []
        dirty_out_of_scope = [path for path in dirty_files if worker_scopes and not _path_matches_scope(path, worker_scopes)]
        if dirty_out_of_scope:
            blocking_reasons.append("worker-dirty-out-of-scope")
        if dirty_files and bool(stop_policy.get("block_on_dirty_source", True)):
            blocking_reasons.append("worker-report-required")
        if not serena_current and str(serena_policy.get("mode", "enabled")) != "disabled":
            advisory_reasons.append("worker-serena-stale-report")
        if ahead or behind:
            advisory_reasons.append("worker-branch-drift-report")
        if fullrepo_attention_candidate:
            advisory_reasons.append("worker-fullrepo-report")
        if bool(branch_cleanup_state.get("needs_cleanup")):
            advisory_reasons.append("worker-branch-cleanup-report")
        if bool(instruction_docs_state.get("needs_instruction_docs_review")):
            advisory_reasons.append("worker-instruction-docs-report")
    else:
        if not serena_current and str(serena_policy.get("mode", "enabled")) != "disabled":
            blocking_reasons.append("serena-memory-stale")
        if dirty_files and bool(stop_policy.get("block_on_dirty_source", True)):
            blocking_reasons.append("dirty-worktree")
        if (ahead or behind) and bool(stop_policy.get("block_on_ahead_behind", True)):
            blocking_reasons.append("branch-ahead-behind")
        if fullrepo_needs_attention:
            blocking_reasons.append("fullrepo-sync-required")
        elif fullrepo_attention_candidate and fullrepo_mode in {"auto", "advisory"}:
            advisory_reasons.append("fullrepo-sync-advisory")
        branch_cleanup_blocks_stop = bool(stop_policy.get("block_on_branch_cleanup", False)) or bool(
            branch_cleanup_state.get("block_stop")
        )
        if bool(branch_cleanup_state.get("needs_cleanup")) and branch_cleanup_blocks_stop:
            blocking_reasons.append("branch-cleanup-required")
        elif branch_cleanup_state.get("advisory_candidates"):
            advisory_reasons.append("branch-cleanup-advisory")
        if bool(instruction_docs_state.get("needs_instruction_docs_review")):
            blocking_reasons.append("instruction-docs-review")

    needs_flow_sync = bool(blocking_reasons)

    fingerprint_payload = {
        "head": head_full,
        "branch": branch,
        "dirty": dirty_files,
        "ahead": ahead,
        "behind": behind,
        "branch_cleanup": branch_cleanup_state,
        "serena_current": serena_current,
        "doc_files_changed": doc_files_changed,
        "fullrepo_needs_attention": fullrepo_needs_attention,
        "instruction_docs_needs_review": bool(
            instruction_docs_state.get("needs_instruction_docs_review")
        ),
        "blocking_reasons": blocking_reasons,
        "advisory_reasons": advisory_reasons,
        "policy_source": project_policy.get("source"),
        "policy_source_kind": project_policy.get("source_kind"),
        "execution": runtime_execution,
    }
    fingerprint = hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True).encode()).hexdigest()[:16]

    return {
        "is_git_repo": True,
        "head_sha": head_sha,
        "head_full": head_full,
        "branch": branch,
        "upstream": upstream,
        "ahead": ahead,
        "behind": behind,
        "dirty_files": dirty_files,
        "dirty_count": len(dirty_files),
        "doc_files_present": doc_files_present,
        "doc_files_changed": doc_files_changed,
        "worktree_count": worktree_count,
        "serena_current": serena_current,
        "serena_state": serena_state,
        "execution": runtime_execution,
        "project_policy": {
            "source": project_policy.get("source"),
            "source_kind": project_policy.get("source_kind"),
            "profile": effective_policy.get("profile"),
            "valid": project_policy.get("valid"),
            "errors": project_policy.get("errors", []),
            "warnings": project_policy.get("warnings", []),
            "effective": effective_policy,
        },
        "fullrepo_state": fullrepo_state,
        "instruction_docs_state": instruction_docs_state,
        "branch_cleanup_state": branch_cleanup_state,
        "fullrepo_needs_attention": fullrepo_needs_attention,
        "blocking_reasons": blocking_reasons,
        "advisory_reasons": advisory_reasons,
        "needs_flow_sync": needs_flow_sync,
        "fingerprint": fingerprint,
    }


def main() -> int:
    print(json.dumps(state(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
