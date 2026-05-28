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
SERENA_KNOWLEDGE_PREFIXES = (
    ".serena/memories/",
    ".serena/plans/",
    ".serena/research/",
    ".serena/newproj/",
    ".serena/deploy/",
)
# Agent-instruction paths that are knowledge-equivalent: durable agent
# guidance lives here. On projects with a `main`/`fullrepo` branch split
# these files exist only on `fullrepo`; treating them as knowledge keeps
# `only_knowledge_changes_since_sync` true after an agent-only wave, so
# a `Last commit:` pinned to the main-side ancestor SHA still satisfies
# `memory_matches_head` without needing prose mentions of the current
# fullrepo merge HEAD (which CI verify-memory-sync.py would reject as
# non-ancestor of main HEAD).
AGENT_INSTRUCTION_PATHS = (
    # Root-level instruction files (canonical per .git/info/exclude
    # "rldyour fullrepo agent-only files" block).
    "AGENTS.md",
    "CLAUDE.md",
    "REVIEW.md",
    "GEMINI.md",
    "QWEN.md",
    ".cursorrules",
    ".windsurfrules",
    ".aider",  # prefix-match: .aider, .aider.conf.yml, .aiderignore, .aider.chat.history.md
    # IDE / agent root directories.
    ".claude/",
    ".codex/",
    ".cursor/",
    ".gemini/",
    ".windsurf/",
    ".roo/",
    ".openhands/",
    # GitHub agent paths (Copilot instructions, prompts, agent-shared files).
    ".github/copilot-instructions.md",
    ".github/instructions/",
    ".github/prompts/",
    # .agents/ tool-shared paths (cross-vendor agent skills/commands/hooks).
    ".agents/skills/",
    ".agents/commands/",
    ".agents/hooks/",
    # Serena project metadata (knowledge directories live in
    # SERENA_KNOWLEDGE_PREFIXES; project.yml is metadata, not knowledge).
    # `.serena/project.local.yml` is intentionally absent: it is
    # machine-local runtime config (negated in .git/info/exclude,
    # listed in fullrepo_sync RUNTIME_EXCLUDE_PATTERNS) and should NOT
    # classify as knowledge - it never reaches commits in normal flow.
    ".serena/project.yml",
)
RUNTIME_IGNORED = {
    ".serena/.sync_marker",
    ".serena/.serena_sync_state.json",
    ".serena/.auto_sync_head",
    ".serena/.active_workflow_intent.json",
    ".serena/.dirty_stop_ack",
    ".serena/.flow_sync_marker",
    ".serena/.flow_post_task_state.json",
    ".serena/.stop_lifecycle_timeout_marker",
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
        [sys.executable,
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

    malformed_analysis = state.get("analysis")
    if malformed_analysis is not None and not isinstance(malformed_analysis, dict):
        print(
            f"serena_memory_state: discarding non-dict analysis payload "
            f"(type={type(malformed_analysis).__name__}); falling back to ref-range",
            file=sys.stderr,
        )

    newest_synced = state.get("newest_synced_full")
    if isinstance(newest_synced, str) and newest_synced:
        head_full = state.get("head_full")
        if isinstance(head_full, str):
            analysis = _analysis_from_ref_range(newest_synced, head_full)
            if isinstance(analysis, dict) and analysis:
                return analysis, f"newest_sync_ref_range:{newest_synced[:7]}..{head_full[:7]}"

    if paths and ANALYZE_SCRIPT.is_file():
        proc = subprocess.run(
            [sys.executable, str(ANALYZE_SCRIPT), "--stdin"],
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
    if any(path.startswith(prefix) for prefix in SERENA_KNOWLEDGE_PREFIXES):
        return True
    # Agent-instruction files are knowledge-equivalent: their churn on
    # `fullrepo` after a `main`-side ancestor sync should NOT force a
    # fresh memory bump to satisfy `memory_matches_head`.
    #
    # Matching semantics (F-3 verification-review closure, 2026-05-18):
    # - entry ending in '/' (e.g. '.claude/') is a directory prefix:
    #   use startswith so '.claude/CLAUDE.md' matches '.claude/'.
    # - entry not ending in '/' is treated as an exact file path
    #   (e.g. 'AGENTS.md', '.github/copilot-instructions.md') OR a
    #   dotfile-family prefix '.aider' covering '.aider*' files.
    #   Use exact equality + the '.aider' special case to avoid the
    #   false-positive class (e.g. 'AGENTS.md.bak' or
    #   '.github/copilot-instructions.mdx' should NOT be classified
    #   as knowledge).
    for ai_path in AGENT_INSTRUCTION_PATHS:
        if ai_path.endswith("/"):
            if path.startswith(ai_path):
                return True
        elif ai_path == ".aider":
            # .aider is the canonical .aider* dotfile-family prefix
            # (.aider, .aiderignore, .aider.conf.yml, .aider.chat.history.md).
            if path == ai_path or path.startswith(".aider"):
                return True
        else:
            if path == ai_path:
                return True
    return False


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

    memory_files = sorted(MEMORY_DIR.rglob("*.md"))
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
