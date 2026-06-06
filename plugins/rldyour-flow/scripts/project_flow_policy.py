#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
TRACKED_POLICY = ".rldyour/project-policy.json"
LOCAL_POLICY = ".rldyour/project-policy.local.json"
ENV_POLICY = "RLDYOUR_PROJECT_POLICY"

PROTECTED_BRANCHES = (
    "main",
    "master",
    "dev",
    "develop",
    "development",
    "staging",
    "production",
    "prod",
    "fullrepo",
)
WORKFLOW_BRANCH_PREFIXES = ("ai/", "claude/", "ry-", "rldyour/")

DEFAULT_POLICY: dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "profile": "rldyour-default-auto",
    "description": "Built-in non-destructive rldyour Flow defaults.",
    "ownership": {
        "owned_by_user": True,
        "destructive_git_requires_explicit_user_confirmation": True,
        "remote_branch_delete_requires_explicit_user_confirmation": True,
        "force_push_requires_explicit_user_confirmation": True,
    },
    "operating_system": {
        "target": "auto",
        "install_profile": "auto",
    },
    "execution": {
        "mode": "standard",
        "agent_role": "auto",
        "default_agent": "codex",
        "worker_agents": ["codex", "claude", "opencode"],
        "worker_count_min": 1,
        "worker_count_max": 6,
        "task_delegation": "direct",
    },
    "cmux": {
        "enabled": False,
        "install_method": "auto",
        "global_config_path": "~/.config/cmux/cmux.json",
        "project_config_path": ".cmux/cmux.json",
        "install_hooks": False,
        "install_skills": False,
        "auto_resume_agent_sessions": False,
        "agent_hibernation_enabled": False,
        "socket_control_mode": "cmuxOnly",
        "workspace_layout": "standard",
        "version_policy": "latest-compatible",
    },
    "orchestrator": {
        "enabled": False,
        "agent": "codex",
        "user_facing_only": True,
        "owns_task_delegation": True,
        "owns_commits": True,
        "owns_push": True,
        "owns_fullrepo": True,
        "owns_system_install": True,
        "worker_permissions": {
            "commit": "forbidden-unless-delegated",
            "push": "forbidden",
            "fullrepo": "forbidden",
            "system_install": "forbidden",
            "branch_cleanup": "forbidden",
        },
        "concurrency": {
            "default_strategy": "single-writer",
            "read_only_workers_same_worktree": True,
            "write_workers_require_worktree_or_file_scope": True,
            "parallel_same_file_edits": "forbidden",
            "commit_owner": "orchestrator",
        },
    },
    "branches": {
        "allowed_work_branches": ["main", "dev", "feat/*", "fix/*", "chore/*"],
        "protected_branches": list(PROTECTED_BRANCHES),
        "default_base_branch": "main",
        "default_integration_branch": "dev",
    },
    "fullrepo": {
        "mode": "auto",
        "restore": True,
        "publish": True,
        "migrate_main": True,
        "install_exclude": True,
        "create_if_missing": False,
        "block_stop": True,
    },
    "normal_branch_policy": {
        "agent_files": "strict-fullrepo-default",
        "ai_marker_additions": "strict-fullrepo-default",
        "instruction_docs": "auto",
        "runtime_markers": "forbidden",
        "secrets": "forbidden",
    },
    "instruction_docs": {
        "mode": "auto",
        "codex": "AGENTS.md",
        "claude": ".claude/CLAUDE.md",
        "opencode": ".opencode/",
    },
    "serena": {
        "mode": "enabled",
        "memory_storage": "fullrepo-auto",
        "allow_memory_commits": True,
        "forbid_runtime_markers": True,
    },
    "branch_cleanup": {
        "mode": "advisory",
        "block_stop": False,
        "delete_local_branches": False,
        "delete_remote_branches": False,
        "workflow_branch_prefixes": list(WORKFLOW_BRANCH_PREFIXES),
        "blocking_prefixes": list(WORKFLOW_BRANCH_PREFIXES),
        "protected_branches": list(PROTECTED_BRANCHES),
    },
    "stop_hook": {
        "block_on_dirty_source": True,
        "block_on_ahead_behind": True,
        "block_on_fullrepo": True,
        "block_on_branch_cleanup": False,
        "allow_same_fingerprint_after_report": True,
    },
}

KNOWN_KEYS: dict[str, set[str]] = {
    "": {
        "schema_version",
        "profile",
        "description",
        "ownership",
        "operating_system",
        "execution",
        "cmux",
        "orchestrator",
        "branches",
        "fullrepo",
        "normal_branch_policy",
        "instruction_docs",
        "serena",
        "branch_cleanup",
        "stop_hook",
    },
    "ownership": {
        "owned_by_user",
        "remote_owner",
        "destructive_git_requires_explicit_user_confirmation",
        "remote_branch_delete_requires_explicit_user_confirmation",
        "force_push_requires_explicit_user_confirmation",
    },
    "operating_system": {
        "target",
        "install_profile",
    },
    "execution": {
        "mode",
        "agent_role",
        "default_agent",
        "worker_agents",
        "worker_count_min",
        "worker_count_max",
        "task_delegation",
    },
    "cmux": {
        "enabled",
        "install_method",
        "global_config_path",
        "project_config_path",
        "install_hooks",
        "install_skills",
        "auto_resume_agent_sessions",
        "agent_hibernation_enabled",
        "socket_control_mode",
        "workspace_layout",
        "version_policy",
    },
    "orchestrator": {
        "enabled",
        "agent",
        "user_facing_only",
        "owns_task_delegation",
        "owns_commits",
        "owns_push",
        "owns_fullrepo",
        "owns_system_install",
        "worker_permissions",
        "concurrency",
    },
    "orchestrator.worker_permissions": {
        "commit",
        "push",
        "fullrepo",
        "system_install",
        "branch_cleanup",
    },
    "orchestrator.concurrency": {
        "default_strategy",
        "read_only_workers_same_worktree",
        "write_workers_require_worktree_or_file_scope",
        "parallel_same_file_edits",
        "commit_owner",
    },
    "branches": {
        "allowed_work_branches",
        "protected_branches",
        "default_base_branch",
        "default_integration_branch",
    },
    "fullrepo": {
        "mode",
        "restore",
        "publish",
        "migrate_main",
        "install_exclude",
        "create_if_missing",
        "block_stop",
    },
    "normal_branch_policy": {
        "agent_files",
        "ai_marker_additions",
        "instruction_docs",
        "runtime_markers",
        "secrets",
    },
    "instruction_docs": {"mode", "codex", "claude", "opencode"},
    "serena": {"mode", "memory_storage", "allow_memory_commits", "forbid_runtime_markers"},
    "branch_cleanup": {
        "mode",
        "block_stop",
        "delete_local_branches",
        "delete_remote_branches",
        "workflow_branch_prefixes",
        "blocking_prefixes",
        "protected_branches",
    },
    "stop_hook": {
        "block_on_dirty_source",
        "block_on_ahead_behind",
        "block_on_fullrepo",
        "block_on_branch_cleanup",
        "allow_same_fingerprint_after_report",
    },
}

ALLOWED_VALUES: dict[tuple[str, str], set[str]] = {
    ("operating_system", "target"): {"auto", "macos", "linux", "windows", "wsl"},
    ("operating_system", "install_profile"): {
        "auto",
        "macos-standard",
        "macos-cmux-orchestrator",
        "linux-standard",
        "windows-standard",
        "wsl-standard",
    },
    ("execution", "mode"): {"standard", "orchestrator"},
    ("execution", "agent_role"): {"auto", "standalone", "orchestrator", "worker"},
    ("execution", "default_agent"): {"codex", "claude", "opencode"},
    ("execution", "task_delegation"): {"direct", "explicit-orchestrator-only"},
    ("cmux", "install_method"): {"auto", "brew-cask", "dmg", "manual"},
    ("cmux", "socket_control_mode"): {"cmuxOnly"},
    ("cmux", "version_policy"): {"latest-compatible"},
    ("orchestrator", "agent"): {"codex", "claude", "opencode"},
    ("orchestrator.worker_permissions", "commit"): {"forbidden", "forbidden-unless-delegated", "delegated"},
    ("orchestrator.worker_permissions", "push"): {"forbidden", "delegated"},
    ("orchestrator.worker_permissions", "fullrepo"): {"forbidden", "delegated"},
    ("orchestrator.worker_permissions", "system_install"): {"forbidden", "delegated"},
    ("orchestrator.worker_permissions", "branch_cleanup"): {"forbidden", "delegated"},
    ("orchestrator.concurrency", "default_strategy"): {"single-writer", "worktree-per-worker"},
    ("orchestrator.concurrency", "parallel_same_file_edits"): {"forbidden"},
    ("orchestrator.concurrency", "commit_owner"): {"orchestrator", "delegated-worker"},
    ("fullrepo", "mode"): {"required", "auto", "advisory", "disabled"},
    ("normal_branch_policy", "agent_files"): {"allowed", "strict-fullrepo-default"},
    ("normal_branch_policy", "ai_marker_additions"): {"allowed", "strict-fullrepo-default"},
    ("normal_branch_policy", "instruction_docs"): {"auto", "tracked-normal-branch", "fullrepo-managed", "disabled"},
    ("normal_branch_policy", "runtime_markers"): {"forbidden"},
    ("normal_branch_policy", "secrets"): {"forbidden"},
    ("instruction_docs", "mode"): {"auto", "tracked-normal-branch", "fullrepo-managed", "disabled"},
    ("serena", "mode"): {"enabled", "disabled"},
    ("serena", "memory_storage"): {"fullrepo-auto", "fullrepo", "normal-branch", "disabled"},
    ("branch_cleanup", "mode"): {"disabled", "advisory", "strict"},
}

BOOL_FIELDS = {
    ("ownership", "owned_by_user"),
    ("ownership", "destructive_git_requires_explicit_user_confirmation"),
    ("ownership", "remote_branch_delete_requires_explicit_user_confirmation"),
    ("ownership", "force_push_requires_explicit_user_confirmation"),
    ("cmux", "enabled"),
    ("cmux", "install_hooks"),
    ("cmux", "install_skills"),
    ("cmux", "auto_resume_agent_sessions"),
    ("cmux", "agent_hibernation_enabled"),
    ("orchestrator", "enabled"),
    ("orchestrator", "user_facing_only"),
    ("orchestrator", "owns_task_delegation"),
    ("orchestrator", "owns_commits"),
    ("orchestrator", "owns_push"),
    ("orchestrator", "owns_fullrepo"),
    ("orchestrator", "owns_system_install"),
    ("orchestrator.concurrency", "read_only_workers_same_worktree"),
    ("orchestrator.concurrency", "write_workers_require_worktree_or_file_scope"),
    ("fullrepo", "restore"),
    ("fullrepo", "publish"),
    ("fullrepo", "migrate_main"),
    ("fullrepo", "install_exclude"),
    ("fullrepo", "create_if_missing"),
    ("fullrepo", "block_stop"),
    ("serena", "allow_memory_commits"),
    ("serena", "forbid_runtime_markers"),
    ("branch_cleanup", "block_stop"),
    ("branch_cleanup", "delete_local_branches"),
    ("branch_cleanup", "delete_remote_branches"),
    ("stop_hook", "block_on_dirty_source"),
    ("stop_hook", "block_on_ahead_behind"),
    ("stop_hook", "block_on_fullrepo"),
    ("stop_hook", "block_on_branch_cleanup"),
    ("stop_hook", "allow_same_fingerprint_after_report"),
}

LIST_STRING_FIELDS = {
    ("execution", "worker_agents"),
    ("branches", "allowed_work_branches"),
    ("branches", "protected_branches"),
    ("branch_cleanup", "workflow_branch_prefixes"),
    ("branch_cleanup", "blocking_prefixes"),
    ("branch_cleanup", "protected_branches"),
}

INT_FIELDS = {
    ("execution", "worker_count_min"),
    ("execution", "worker_count_max"),
}


def _git_root(start: Path) -> tuple[Path, bool]:
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return Path(proc.stdout.strip()).resolve(), True
    return start.resolve(), False


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace(os.sep, "/")
    except ValueError:
        return str(path)


def _merge_dict(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_dict(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"{path} does not exist"
    except json.JSONDecodeError as exc:
        return None, f"{path}: invalid JSON: {exc}"
    if not isinstance(payload, dict):
        return None, f"{path}: policy root must be a JSON object"
    return payload, None


def _policy_paths(root: Path) -> list[tuple[str, Path]]:
    paths: list[tuple[str, Path]] = []
    tracked = root / TRACKED_POLICY
    if tracked.is_file():
        paths.append(("tracked", tracked))
    local = root / LOCAL_POLICY
    if local.is_file():
        paths.append(("local", local))
    env_value = os.environ.get(ENV_POLICY)
    if env_value:
        paths.append(("env", Path(env_value).expanduser()))
    return paths


def _unknown_key_warnings(payload: dict[str, Any], prefix: str = "") -> list[str]:
    warnings: list[str] = []
    allowed = KNOWN_KEYS.get(prefix)
    if allowed is not None:
        for key in payload:
            if key not in allowed:
                path = f"{prefix}.{key}" if prefix else key
                warnings.append(f"unknown policy field: {path}")
    for key, value in payload.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            warnings.extend(_unknown_key_warnings(value, path))
    return warnings


def _ensure_list(value: Any, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{path} must be a list of non-empty strings")
        return []
    return sorted(dict.fromkeys(value))


def _section_dict(policy: dict[str, Any], section: str) -> dict[str, Any] | None:
    current: Any = policy
    for part in section.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current if isinstance(current, dict) else None


def _validate_effective(policy: dict[str, Any], *, strict: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings = _unknown_key_warnings(policy)
    if strict:
        errors.extend(warnings)

    schema_version = policy.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    for (section, key), allowed in ALLOWED_VALUES.items():
        section_value = _section_dict(policy, section)
        if section_value is None:
            errors.append(f"{section} must be an object")
            continue
        value = section_value.get(key)
        if value not in allowed:
            errors.append(f"{section}.{key} must be one of {sorted(allowed)}")

    for section, key in BOOL_FIELDS:
        section_value = _section_dict(policy, section)
        if section_value is None:
            errors.append(f"{section} must be an object")
            continue
        if not isinstance(section_value.get(key), bool):
            errors.append(f"{section}.{key} must be a boolean")

    for section, key in LIST_STRING_FIELDS:
        section_value = _section_dict(policy, section)
        if section_value is None:
            errors.append(f"{section} must be an object")
            continue
        section_value[key] = _ensure_list(section_value.get(key), f"{section}.{key}", errors)

    for section, key in INT_FIELDS:
        section_value = _section_dict(policy, section)
        if section_value is None:
            errors.append(f"{section} must be an object")
            continue
        value = section_value.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{section}.{key} must be a non-negative integer")

    execution = policy.get("execution")
    if isinstance(execution, dict):
        worker_min = execution.get("worker_count_min")
        worker_max = execution.get("worker_count_max")
        if isinstance(worker_min, int) and not isinstance(worker_min, bool) and isinstance(worker_max, int) and not isinstance(worker_max, bool):
            if worker_min > worker_max:
                errors.append("execution.worker_count_min must be <= execution.worker_count_max")

    return errors, warnings


def _apply_safe_invalid_fallback(policy: dict[str, Any]) -> dict[str, Any]:
    fallback = copy.deepcopy(policy)
    fallback.setdefault("execution", {})
    if fallback["execution"].get("mode") not in {"standard", "orchestrator"}:
        fallback["execution"]["mode"] = "standard"
    if fallback["execution"].get("agent_role") not in {"auto", "standalone", "orchestrator", "worker"}:
        fallback["execution"]["agent_role"] = "auto"
    if fallback["execution"].get("task_delegation") not in {"direct", "explicit-orchestrator-only"}:
        fallback["execution"]["task_delegation"] = "direct"
    fallback.setdefault("cmux", {})
    if not isinstance(fallback["cmux"].get("enabled"), bool):
        fallback["cmux"]["enabled"] = False
    fallback.setdefault("normal_branch_policy", {})
    fallback["normal_branch_policy"]["runtime_markers"] = "forbidden"
    fallback["normal_branch_policy"]["secrets"] = "forbidden"
    fallback.setdefault("serena", {})
    fallback["serena"]["forbid_runtime_markers"] = True
    fallback.setdefault("fullrepo", {})
    if fallback["fullrepo"].get("mode") not in {"required", "auto", "advisory", "disabled"}:
        fallback["fullrepo"]["mode"] = "auto"
    fallback.setdefault("branch_cleanup", {})
    if fallback["branch_cleanup"].get("mode") not in {"disabled", "advisory", "strict"}:
        fallback["branch_cleanup"]["mode"] = "advisory"
    return fallback


def load_policy(root: Path | str | None = None, *, strict: bool = False) -> dict[str, Any]:
    start = Path(root or ".")
    repo_root, is_git_repo = _git_root(start)
    effective = copy.deepcopy(DEFAULT_POLICY)
    loaded_sources: list[dict[str, str]] = []
    errors: list[str] = []
    highest_source = "built-in defaults"
    highest_source_kind = "default"

    for kind, path in _policy_paths(repo_root):
        payload, error = _load_json(path)
        if error:
            errors.append(error)
            highest_source = _relative(path, repo_root)
            highest_source_kind = kind
            continue
        assert payload is not None
        effective = _merge_dict(effective, payload)
        highest_source = _relative(path, repo_root)
        highest_source_kind = kind
        loaded_sources.append({"kind": kind, "path": _relative(path, repo_root)})

    validation_errors, warnings = _validate_effective(effective, strict=strict)
    errors.extend(validation_errors)
    if errors:
        effective = _apply_safe_invalid_fallback(effective)

    return {
        "is_git_repo": is_git_repo,
        "root": str(repo_root),
        "source": highest_source,
        "source_kind": highest_source_kind,
        "sources": loaded_sources,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "effective": effective,
    }


def validate_policy_file(path: Path, *, strict: bool = False) -> dict[str, Any]:
    root = path.parent.resolve()
    payload, error = _load_json(path)
    effective = copy.deepcopy(DEFAULT_POLICY)
    errors: list[str] = []
    warnings: list[str] = []
    if error:
        errors.append(error)
    elif payload is not None:
        effective = _merge_dict(effective, payload)
        validation_errors, warnings = _validate_effective(effective, strict=strict)
        errors.extend(validation_errors)
    if errors:
        effective = _apply_safe_invalid_fallback(effective)
    return {
        "is_git_repo": False,
        "root": str(root),
        "source": str(path),
        "source_kind": "schema-check",
        "sources": [{"kind": "schema-check", "path": str(path)}],
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "effective": effective,
    }


def shell_payload(policy: dict[str, Any]) -> dict[str, str]:
    effective = policy.get("effective", {})
    fullrepo = effective.get("fullrepo", {})
    normal = effective.get("normal_branch_policy", {})
    instruction_docs = effective.get("instruction_docs", {})
    branch_cleanup = effective.get("branch_cleanup", {})
    stop_hook = effective.get("stop_hook", {})
    return {
        "RLDYOUR_PROJECT_POLICY_SOURCE": str(policy.get("source", "")),
        "RLDYOUR_PROJECT_POLICY_SOURCE_KIND": str(policy.get("source_kind", "")),
        "RLDYOUR_PROJECT_POLICY_VALID": "1" if policy.get("valid") else "0",
        "RLDYOUR_FULLREPO_MODE": str(fullrepo.get("mode", "auto")),
        "RLDYOUR_FULLREPO_RESTORE": "1" if fullrepo.get("restore") else "0",
        "RLDYOUR_FULLREPO_PUBLISH": "1" if fullrepo.get("publish") else "0",
        "RLDYOUR_FULLREPO_MIGRATE_MAIN": "1" if fullrepo.get("migrate_main") else "0",
        "RLDYOUR_FULLREPO_INSTALL_EXCLUDE": "1" if fullrepo.get("install_exclude") else "0",
        "RLDYOUR_FULLREPO_CREATE_IF_MISSING": "1" if fullrepo.get("create_if_missing") else "0",
        "RLDYOUR_AGENT_FILES_POLICY": str(normal.get("agent_files", "strict-fullrepo-default")),
        "RLDYOUR_AI_MARKER_ADDITIONS_POLICY": str(normal.get("ai_marker_additions", "strict-fullrepo-default")),
        "RLDYOUR_INSTRUCTION_DOCS_MODE": str(instruction_docs.get("mode", "auto")),
        "RLDYOUR_BRANCH_CLEANUP_MODE": str(branch_cleanup.get("mode", "advisory")),
        "RLDYOUR_BRANCH_CLEANUP_BLOCK_STOP": "1" if branch_cleanup.get("block_stop") else "0",
        "RLDYOUR_STOP_BLOCK_ON_FULLREPO": "1" if stop_hook.get("block_on_fullrepo") else "0",
        "RLDYOUR_STOP_BLOCK_ON_BRANCH_CLEANUP": "1" if stop_hook.get("block_on_branch_cleanup") else "0",
        "RLDYOUR_STOP_ALLOW_SAME_FINGERPRINT_AFTER_REPORT": "1"
        if stop_hook.get("allow_same_fingerprint_after_report")
        else "0",
    }


def explain(policy: dict[str, Any]) -> str:
    effective = policy.get("effective", {})
    fullrepo = effective.get("fullrepo", {})
    normal = effective.get("normal_branch_policy", {})
    instruction_docs = effective.get("instruction_docs", {})
    branch_cleanup = effective.get("branch_cleanup", {})
    lines = [
        f"policy source: {policy.get('source')} ({policy.get('source_kind')})",
        f"valid: {policy.get('valid')}",
        f"fullrepo.mode: {fullrepo.get('mode')}",
        f"fullrepo.create_if_missing: {fullrepo.get('create_if_missing')}",
        f"normal_branch_policy.agent_files: {normal.get('agent_files')}",
        f"normal_branch_policy.ai_marker_additions: {normal.get('ai_marker_additions')}",
        f"instruction_docs.mode: {instruction_docs.get('mode')}",
        f"branch_cleanup.mode: {branch_cleanup.get('mode')}",
        "protected branches: " + ", ".join(branch_cleanup.get("protected_branches", [])),
    ]
    for warning in policy.get("warnings", []):
        lines.append(f"warning: {warning}")
    for error in policy.get("errors", []):
        lines.append(f"error: {error}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve effective rldyour Flow project policy.")
    parser.add_argument("--root", default=".", help="Repository root or path inside the repository.")
    parser.add_argument("--strict", action="store_true", help="Treat unknown fields as validation errors.")
    parser.add_argument("--json", action="store_true", help="Emit compact JSON.")
    parser.add_argument("--explain", action="store_true", help="Emit a human-readable policy summary.")
    parser.add_argument("--shell", action="store_true", help="Emit shell assignments for hook scripts.")
    parser.add_argument("--schema-check", help="Validate a specific project policy JSON file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.schema_check:
        policy = validate_policy_file(Path(args.schema_check), strict=args.strict)
    else:
        policy = load_policy(Path(args.root), strict=args.strict)

    if args.shell:
        for key, value in shell_payload(policy).items():
            print(f"{key}={shlex.quote(value)}")
    elif args.explain:
        print(explain(policy))
    else:
        print(json.dumps(policy, sort_keys=True))

    return 0 if policy.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
