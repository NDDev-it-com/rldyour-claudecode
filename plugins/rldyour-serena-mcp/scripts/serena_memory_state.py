#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


MEMORY_DIR = Path(".serena/memories")
SYNC_STATE = Path(".serena/.serena_sync_state.json")
ANALYZE_SCRIPT = Path(__file__).resolve().parent / "analyze_sync_scope.py"
KNOWLEDGE_PREFIXES = (
    ".agents/commands/",
    ".agents/hooks/",
    ".agents/skills/",
    ".claude/",
    ".cursor/rules/",
    ".gemini/",
    ".roo/",
    ".windsurf/",
    ".openhands/",
    ".github/instructions/",
    ".github/prompts/",
    ".serena/memories/",
    ".serena/plans/",
    ".serena/research/",
    ".serena/newproj/",
    ".serena/deploy/",
)
KNOWLEDGE_FILES = {
    ".cursorrules",
    ".windsurfrules",
    ".aider",
    ".aider.conf.yml",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "QWEN.md",
    "REVIEW.md",
    ".github/copilot-instructions.md",
    ".serena/project.yml",
}
RUNTIME_IGNORED = {
    ".serena/.sync_marker",
    ".serena/.serena_sync_state.json",
    ".serena/.auto_sync_head",
    ".serena/.active_workflow_intent.json",
    ".serena/.dirty_stop_ack",
    ".serena/.flow_sync_marker",
    ".serena/.flow_post_task_state.json",
}
LAST_COMMIT_RE = re.compile(r"^Last commit:\s+([a-f0-9]{7,40})\b", re.MULTILINE)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True)


def _stdout(*args: str) -> str:
    return _git(*args).stdout.strip()


def _resolve_commit(ref: str) -> tuple[str, str] | None:
    proc = _git("rev-parse", f"{ref}^{{commit}}")
    if proc.returncode != 0:
        return None
    full = proc.stdout.strip()
    if not full:
        return None
    return full[:7], full


def _newest_synced_commit(candidates: list[tuple[str, str]]) -> tuple[str, str] | None:
    newest: tuple[str, str] | None = None
    for candidate in candidates:
        if newest is None:
            newest = candidate
            continue
        proc = _git("merge-base", "--is-ancestor", newest[1], candidate[1])
        if proc.returncode == 0:
            newest = candidate
    return newest


def _analysis_from_ref_range(from_ref: str, to_ref: str) -> dict[str, Any] | None:
    if not from_ref or not to_ref or not ANALYZE_SCRIPT.is_file():
        return None

    proc = subprocess.run(
        [
            "python3",
            str(ANALYZE_SCRIPT),
            "--from-ref",
            from_ref,
            "--to-ref",
            to_ref,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _analysis_from_changed_files(paths: list[str], state: dict[str, Any]) -> tuple[dict[str, Any], str]:
    explicit = state.get("analysis")
    if isinstance(explicit, dict) and explicit:
        return explicit, "sync_marker"

    marker_previous = str(state.get("previous_head_full") or "")
    marker_head = str(state.get("head_full") or "")
    if marker_previous and marker_head:
        analysis = _analysis_from_ref_range(marker_previous, marker_head)
        if isinstance(analysis, dict) and analysis:
            return analysis, f"sync_marker_ref_range:{marker_previous[:7]}..{marker_head[:7]}"

    if state.get("analysis") is not None and not isinstance(state.get("analysis"), dict):
        # defensive: ignore non-dict payloads instead of surfacing malformed JSON to callers
        pass

    newest_synced = state.get("newest_synced_full")
    if isinstance(newest_synced, str) and newest_synced:
        head_full = state.get("head_full")
        if isinstance(head_full, str):
            analysis = _analysis_from_ref_range(newest_synced, head_full)
            if isinstance(analysis, dict) and analysis:
                return analysis, f"newest_sync_ref_range:{newest_synced[:7]}..{head_full[:7]}"

    if paths and ANALYZE_SCRIPT.is_file():
        proc = subprocess.run(
            ["python3", str(ANALYZE_SCRIPT), "--stdin"],
            input="\n".join(paths) + "\n",
            text=True,
            check=False,
            capture_output=True,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                payload = json.loads(proc.stdout)
            except json.JSONDecodeError:
                payload = {}
            if isinstance(payload, dict):
                return payload, "path_list"

    return {}, "none"


def _is_knowledge_path(path: str) -> bool:
    return path in KNOWLEDGE_FILES or path.startswith(".aider") or any(path.startswith(prefix) for prefix in KNOWLEDGE_PREFIXES)


def _non_knowledge_paths(paths: list[str]) -> list[str]:
    return [path for path in paths if path not in RUNTIME_IGNORED and not _is_knowledge_path(path)]


def _load_sync_state() -> dict[str, Any]:
    if not SYNC_STATE.is_file():
        return {}
    try:
        payload = json.loads(SYNC_STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _memory_candidates(head_short: str) -> tuple[int, bool, list[tuple[str, str]]]:
    if not MEMORY_DIR.is_dir():
        return 0, False, []

    memory_files = sorted(MEMORY_DIR.glob("*.md"))
    memory_matches_head = False
    candidates: list[tuple[str, str]] = []

    for memory_file in memory_files:
        try:
            text = memory_file.read_text(encoding="utf-8")
        except OSError:
            continue
        if head_short and f"Last commit: {head_short}" in text:
            memory_matches_head = True
        match = LAST_COMMIT_RE.search(text)
        if not match:
            continue
        resolved = _resolve_commit(match.group(1))
        if resolved is not None:
            candidates.append(resolved)

    return len(memory_files), memory_matches_head, candidates


def status() -> dict[str, Any]:
    if _git("rev-parse", "--is-inside-work-tree").returncode != 0:
        return {"is_git_repo": False, "is_current": True, "memory_count": 0}

    head_full = _stdout("rev-parse", "HEAD")
    head_short = head_full[:7] if head_full else ""
    memory_count, memory_directly_mentions_head, candidates = _memory_candidates(head_short)
    newest = _newest_synced_commit(candidates)
    newest_short = newest[0] if newest else ""
    newest_full = newest[1] if newest else ""

    changed_files: list[str] = []
    non_knowledge_changed_files: list[str] = []
    only_knowledge_changes_since_sync = False
    if newest_full and head_full:
        raw_changed = _stdout("diff", "--name-only", f"{newest_full}..{head_full}")
        changed_files = [line for line in raw_changed.splitlines() if line]
        non_knowledge_changed_files = _non_knowledge_paths(changed_files)
        only_knowledge_changes_since_sync = bool(changed_files) and not non_knowledge_changed_files

    sync_state = _load_sync_state()
    marker_requires_sync = bool(sync_state.get("required"))
    sync_state_for_analysis = dict(sync_state)
    sync_state_for_analysis["newest_synced_full"] = newest_full
    sync_state_for_analysis["head_full"] = head_full
    analysis, analysis_source = _analysis_from_changed_files(changed_files, sync_state_for_analysis)
    marker_head = str(sync_state.get("head_full") or sync_state.get("head") or "")
    marker_matches_head = marker_requires_sync and bool(head_full) and marker_head in {head_full, head_short}

    memory_matches_head = (
        memory_directly_mentions_head
        or (bool(newest_short) and newest_short == head_short)
        or (bool(newest_short) and only_knowledge_changes_since_sync)
    )

    if memory_directly_mentions_head:
        memory_match_reason = "direct-head-reference"
    elif bool(newest_short) and newest_short == head_short:
        memory_match_reason = "newest-synced-head"
    elif bool(newest_short) and only_knowledge_changes_since_sync:
        memory_match_reason = "knowledge-only-commits-since-sync"
    else:
        memory_match_reason = "stale-or-missing"

    if memory_count == 0 and not marker_matches_head:
        is_current = True
    else:
        is_current = memory_matches_head
        if marker_matches_head:
            is_current = False
            memory_match_reason = "sync-marker-requires-refresh"

    return {
        "is_git_repo": True,
        "head_sha": head_short,
        "head_full": head_full,
        "memory_count": memory_count,
        "newest_synced_sha": newest_short,
        "newest_synced_full": newest_full,
        "memory_matches_head": memory_matches_head,
        "memory_directly_mentions_head": memory_directly_mentions_head,
        "memory_match_reason": memory_match_reason,
        "changed_files_since_sync": changed_files,
        "non_knowledge_changed_files_since_sync": non_knowledge_changed_files,
        "analysis": analysis,
        "analysis_source": analysis_source,
        "only_knowledge_changes_since_sync": only_knowledge_changes_since_sync,
        "sync_state": sync_state,
        "is_current": is_current,
    }


def main() -> int:
    json.dump(status(), sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
