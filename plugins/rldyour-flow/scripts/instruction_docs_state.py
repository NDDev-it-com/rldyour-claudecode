#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_flow_policy import load_policy  # noqa: E402

CODEX_DOC = "AGENTS.md"
CLAUDE_DOC = ".claude/CLAUDE.md"
LEGACY_CLAUDE_DOC = "CLAUDE.md"
REQUIRED_AGENT_DOCS = (CODEX_DOC, CLAUDE_DOC)
INSTRUCTION_DOCS = (*REQUIRED_AGENT_DOCS, LEGACY_CLAUDE_DOC)

RUNTIME_IGNORED = {
    ".serena/.sync_marker",
    ".serena/.serena_sync_state.json",
    ".serena/.auto_sync_head",
    ".serena/.active_workflow_intent.json",
    ".serena/.dirty_stop_ack",
    ".serena/.flow_sync_marker",
    ".serena/.flow_post_task_state.json",
    ".serena/.flow_blocker_ack.json",
    ".serena/cache",
}

DURABLE_PATH_PATTERNS = (
    ".agents/plugins/**",
    ".codex-plugin/**",
    ".github/workflows/**",
    "config/**",
    "docs/**",
    "plugins/**",
    "scripts/**",
    "system/AGENTS.md",
    "README.md",
    "CHANGELOG.md",
    "VERSION",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lock",
    "tsconfig*.json",
    "vite.config.*",
    "next.config.*",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "pyrightconfig.json",
    "ruff.toml",
    "Dockerfile",
    "docker-compose*.yml",
    "compose*.yml",
    "Makefile",
    "justfile",
    "pubspec.yaml",
    "analysis_options.yaml",
)


def normalize(path: str | Path) -> str:
    return str(path).replace("\\", "/").strip("/")


def matches(path: str, patterns: tuple[str, ...]) -> bool:
    normalized = normalize(path)
    for pattern in patterns:
        pattern = normalize(pattern)
        if pattern.endswith("/**"):
            prefix = pattern[:-3].rstrip("/")
            if normalized == prefix or normalized.startswith(prefix + "/"):
                return True
        if fnmatch.fnmatchcase(normalized, pattern):
            return True
    return False


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=False, capture_output=True, text=True)


def stdout(root: Path, *args: str) -> str:
    return git(root, *args).stdout.strip()


def porcelain_paths(root: Path) -> list[str]:
    raw = git(root, "status", "--porcelain", "--untracked-files=all").stdout.rstrip("\n")
    paths: list[str] = []
    for line in raw.splitlines():
        if not line:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        normalized = normalize(path)
        if normalized and not is_runtime_path(normalized):
            paths.append(normalized)
    return sorted(set(paths))


def upstream(root: Path) -> str:
    return stdout(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")


def ahead_changed_paths(root: Path, upstream_ref: str) -> list[str]:
    if not upstream_ref:
        return []
    raw = stdout(root, "diff", "--name-only", f"{upstream_ref}..HEAD")
    return sorted({normalize(path) for path in raw.splitlines() if normalize(path)})


def is_runtime_path(path: str) -> bool:
    normalized = normalize(path)
    return any(normalized == item or normalized.startswith(item.rstrip("/") + "/") for item in RUNTIME_IGNORED)


def is_instruction_doc(path: str) -> bool:
    return normalize(path) in INSTRUCTION_DOCS


def is_durable_candidate(path: str) -> bool:
    normalized = normalize(path)
    if not normalized or is_runtime_path(normalized) or is_instruction_doc(normalized):
        return False
    if matches(normalized, DURABLE_PATH_PATTERNS):
        return True
    return bool("/" not in normalized and "." in normalized)


def file_line_count(path: Path) -> int:
    if not path.is_file():
        return 0
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def dict_section(value: object) -> dict[str, Any]:
    return cast(dict[str, Any], value) if isinstance(value, dict) else {}


def instruction_state(root: Path) -> dict[str, Any]:
    root = root.resolve()
    if git(root, "rev-parse", "--is-inside-work-tree").returncode != 0:
        return {
            "is_git_repo": False,
            "root": str(root),
            "needs_instruction_docs_review": False,
            "instruction_docs_managed": False,
        }

    project_policy = load_policy(root)
    effective_policy = dict_section(project_policy.get("effective"))
    normal_policy = dict_section(effective_policy.get("normal_branch_policy"))
    instruction_policy = dict_section(effective_policy.get("instruction_docs"))
    instruction_docs_mode = str(instruction_policy.get("mode", "tracked-main"))
    normal_instruction_mode = str(normal_policy.get("instruction_docs", "tracked-main"))
    if instruction_docs_mode == "tracked-main" and normal_instruction_mode == "disabled":
        instruction_docs_mode = normal_instruction_mode

    current_branch = stdout(root, "branch", "--show-current") or "detached"
    # Agent instruction docs are ordinary tracked source on the main branch.
    # They are "managed" (subject to freshness review) unless explicitly disabled.
    instruction_docs_managed = instruction_docs_mode != "disabled"

    present_docs = [path for path in REQUIRED_AGENT_DOCS if (root / path).is_file()]
    missing_docs = [
        path
        for path in REQUIRED_AGENT_DOCS
        if instruction_docs_managed and not (root / path).is_file()
    ]
    legacy_root_claude_present = (root / LEGACY_CLAUDE_DOC).is_file()

    dirty_paths = porcelain_paths(root)
    upstream_ref = upstream(root)
    committed_paths = ahead_changed_paths(root, upstream_ref)
    changed_paths = sorted(set(dirty_paths + committed_paths))
    durable_change_candidates = sorted(path for path in changed_paths if is_durable_candidate(path))
    dirty_instruction_docs = sorted(path for path in dirty_paths if is_instruction_doc(path))

    review_reasons: list[str] = []
    # Missing instruction docs are advisory only (surfaced via `missing_docs`),
    # never a Stop blocker: repos legitimately differ in layout (Codex uses
    # system/AGENTS.md; OpenCode uses .opencode/) and a bare/new repo must not be
    # blocked for absent docs. validate_instruction_docs.py is the presence gate.
    if legacy_root_claude_present:
        review_reasons.append("legacy root CLAUDE.md exists; preferred project memory path is .claude/CLAUDE.md")
    if dirty_instruction_docs:
        review_reasons.append("instruction docs have uncommitted changes")
    if durable_change_candidates:
        review_reasons.append("durable project facts changed")
    needs_review = bool(instruction_docs_managed and review_reasons)
    if instruction_docs_mode == "disabled":
        review_reasons = []
        needs_review = False

    return {
        "is_git_repo": True,
        "root": str(root),
        "branch": current_branch,
        "head": stdout(root, "rev-parse", "--short=12", "HEAD"),
        "upstream": upstream_ref,
        "instruction_docs_managed": instruction_docs_managed,
        "instruction_docs_mode": instruction_docs_mode,
        "policy_source": project_policy.get("source"),
        "policy_source_kind": project_policy.get("source_kind"),
        "project_policy_valid": project_policy.get("valid"),
        "required_docs": list(REQUIRED_AGENT_DOCS),
        "present_docs": present_docs,
        "missing_docs": missing_docs,
        "legacy_root_claude_present": legacy_root_claude_present,
        "dirty_instruction_docs": dirty_instruction_docs,
        "durable_change_candidates": durable_change_candidates,
        "dirty_paths": dirty_paths,
        "committed_paths_since_upstream": committed_paths,
        "line_counts": {
            CODEX_DOC: file_line_count(root / CODEX_DOC),
            CLAUDE_DOC: file_line_count(root / CLAUDE_DOC),
            LEGACY_CLAUDE_DOC: file_line_count(root / LEGACY_CLAUDE_DOC),
        },
        "review_reasons": review_reasons,
        "needs_instruction_docs_review": needs_review,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report rldyour project instruction document freshness state.")
    parser.add_argument("--root", default=".", help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Emit compact JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = instruction_state(Path(args.root))
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
