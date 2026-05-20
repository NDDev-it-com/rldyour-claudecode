#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

RUNTIME_IGNORED = {
    ".serena/.sync_marker",
    ".serena/.serena_sync_state.json",
    ".serena/.auto_sync_head",
    ".serena/.active_workflow_intent.json",
    ".serena/.dirty_stop_ack",
    ".serena/.flow_sync_marker",
    ".serena/.flow_post_task_state.json",
}

DOC_FILES = ("AGENTS.md", ".claude/CLAUDE.md", "CLAUDE.md")
PROTECTED_BRANCHES = {"main", "master", "develop", "development", "staging", "production", "prod", "fullrepo"}
WORKFLOW_BRANCH_PREFIXES = ("ai/", "claude/", "ry-", "rldyour/")


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True)


def _stdout(*args: str) -> str:
    return _git(*args).stdout.strip()


def _porcelain_paths() -> list[str]:
    raw = _git("status", "--porcelain").stdout.rstrip("\n")
    paths: list[str] = []
    for line in raw.splitlines():
        if not line:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and path not in RUNTIME_IGNORED:
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


def _local_merged_branches(base: str, current_branch: str) -> list[str]:
    raw = _stdout("branch", "--format=%(refname:short)", "--merged", base)
    branches: list[str] = []
    for branch in raw.splitlines():
        branch = branch.strip()
        if not branch or branch == current_branch or branch in PROTECTED_BRANCHES:
            continue
        branches.append(branch)
    return sorted(set(branches))


def _remote_merged_branches(base: str) -> list[str]:
    raw = _stdout("branch", "-r", "--format=%(refname:short)", "--merged", base)
    branches: list[str] = []
    for ref in raw.splitlines():
        ref = ref.strip()
        if not ref or ref.endswith("/HEAD") or " -> " in ref or "/" not in ref:
            continue
        branch = ref.split("/", 1)[1] if "/" in ref else ref
        if branch in PROTECTED_BRANCHES:
            continue
        branches.append(ref)
    return sorted(set(branches))


def _workflow_branch(branch: str) -> bool:
    normalized = branch.split("/", 1)[1] if branch.startswith("origin/") else branch
    return normalized.startswith(WORKFLOW_BRANCH_PREFIXES)


def _worktree_cleanup_candidates(base: str) -> list[dict[str, str]]:
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
        if not path or path == current_root or not branch or branch in PROTECTED_BRANCHES:
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


def _branch_cleanup_state(current_branch: str) -> dict[str, Any]:
    base = _default_cleanup_base()
    local_merged = _local_merged_branches(base, current_branch)
    remote_merged = _remote_merged_branches(base)
    worktree_candidates = _worktree_cleanup_candidates(base)
    workflow_local = [branch for branch in local_merged if _workflow_branch(branch)]
    workflow_remote = [branch for branch in remote_merged if _workflow_branch(branch)]
    needs_cleanup = bool(local_merged or remote_merged or worktree_candidates)
    return {
        "base": base,
        "protected_branches": sorted(PROTECTED_BRANCHES),
        "local_merged_branches": local_merged,
        "remote_merged_branches": remote_merged,
        "merged_workflow_branches": sorted(set(workflow_local + workflow_remote)),
        "worktree_cleanup_candidates": worktree_candidates,
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
    repo_relative = Path(f"plugins/{plugin}/{relative}")
    if repo_relative.is_file():
        return repo_relative
    plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root_env:
        sibling = (Path(plugin_root_env) / ".." / plugin / relative).resolve()
        if sibling.is_file():
            return sibling
    return None


def _serena_current() -> tuple[bool, dict[str, Any]]:
    candidate = _resolve_sibling_plugin_script("rldyour-serena-mcp", "scripts/serena_memory_state.py")
    if candidate is None:
        return True, {}
    proc = subprocess.run([sys.executable, str(candidate)], check=False, capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout.strip():
        return True, {}
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return True, {}
    return bool(payload.get("is_current", True)), payload


def _self_plugin_script(relative: str) -> Path | None:
    """Find a script in this plugin (rldyour-flow) via repo-relative or CLAUDE_PLUGIN_ROOT."""
    repo_relative = Path(f"plugins/rldyour-flow/{relative}")
    if repo_relative.is_file():
        return repo_relative
    plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root_env:
        candidate = (Path(plugin_root_env) / relative).resolve()
        if candidate.is_file():
            return candidate
    return None


def _fullrepo_state() -> dict[str, Any]:
    candidate = _self_plugin_script("scripts/fullrepo_sync.py")
    if candidate is None:
        return {}
    proc = subprocess.run(
        [sys.executable, str(candidate), "--status-json"],
        check=False,
        capture_output=True,
        text=True,
    )
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
    proc = subprocess.run(
        [sys.executable, str(candidate), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
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
    branch_cleanup_state = _branch_cleanup_state(branch)

    worktree_agent_paths = fullrepo_state.get("worktree_agent_paths")
    if not isinstance(worktree_agent_paths, list):
        worktree_agent_paths = []
    fullrepo_needs_attention = bool(fullrepo_state) and (
        not bool(fullrepo_state.get("exclude_installed", True))
        or (bool(worktree_agent_paths) and not bool(fullrepo_state.get("remote_fullrepo_exists", False)))
    )

    needs_flow_sync = serena_current and bool(
        dirty_files
        or ahead
        or behind
        or doc_files_changed
        or fullrepo_needs_attention
        or bool(branch_cleanup_state.get("needs_cleanup"))
        or bool(instruction_docs_state.get("needs_instruction_docs_review"))
    )

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
        "fullrepo_state": fullrepo_state,
        "instruction_docs_state": instruction_docs_state,
        "branch_cleanup_state": branch_cleanup_state,
        "fullrepo_needs_attention": fullrepo_needs_attention,
        "needs_flow_sync": needs_flow_sync,
        "fingerprint": fingerprint,
    }


def main() -> int:
    print(json.dumps(state(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
