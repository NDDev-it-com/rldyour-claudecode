from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FLOW_PLUGIN = REPO_ROOT / "plugins" / "rldyour-flow"
FLOW_STATE = FLOW_PLUGIN / "scripts" / "flow_post_task_state.py"
STOP_HOOK = FLOW_PLUGIN / "hooks" / "stop_post_task_sync.sh"
DEFAULT_TIMEOUT = 30


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=False, timeout=DEFAULT_TIMEOUT)


def init_repo(repo: Path) -> str:
    run_git(repo, "init", "-q")
    run_git(repo, "config", "user.name", "Test User")
    run_git(repo, "config", "user.email", "test@example.invalid")
    (repo / "README.md").write_text("# fixture\n", encoding="utf-8")
    run_git(repo, "add", "README.md")
    assert run_git(repo, "commit", "-qm", "init").returncode == 0
    return run_git(repo, "rev-parse", "--short=7", "HEAD").stdout.strip()


def write_current_memory(repo: Path, head_short: str) -> None:
    memories = repo / ".serena" / "memories"
    memories.mkdir(parents=True)
    (memories / "CORE-01-INDEX.md").write_text(
        "\n".join([
            "<!-- Memory Metadata",
            "Last updated: 2026-05-28",
            f"Last commit: {head_short}",
            "Scope: test",
            "Area: CORE",
            "-->",
            "# CORE-01-INDEX",
        ]) + "\n",
        encoding="utf-8",
    )


def test_direct_flow_state_uses_tracked_context_without_secondary_branch(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    head_short = init_repo(repo)
    write_current_memory(repo, head_short)
    run_git(repo, "add", ".serena")
    assert run_git(repo, "commit", "-qm", "track memory").returncode == 0

    proc = subprocess.run(
        ["python3", str(FLOW_STATE)],
        cwd=repo,
        env={**os.environ, "RLDYOUR_FLOW_STATE_LOCAL_ONLY": "1"},
        text=True,
        capture_output=True,
        check=False,
        timeout=DEFAULT_TIMEOUT,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["serena_current"] is True
    assert "full" + "repo" not in json.dumps(payload)
    assert payload["blocking_reasons"] == []


def test_tracked_ai_docs_do_not_trigger_stop_loop(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)
    (repo / ".rldyour").mkdir()
    (repo / ".rldyour/project-policy.json").write_text(
        json.dumps({
            "schema_version": 1,
            "normal_branch_policy": {"agent_files": "allowed", "ai_marker_additions": "allowed", "instruction_docs": "tracked-normal-branch"},
            "instruction_docs": {"mode": "tracked-normal-branch"},
            "branch_cleanup": {"mode": "advisory", "protected_branches": ["main", "dev"]},
            "stop_hook": {"block_on_branch_cleanup": False},
        }),
        encoding="utf-8",
    )
    (repo / "AGENTS.md").write_text("# project instructions\n", encoding="utf-8")
    (repo / ".claude").mkdir()
    (repo / ".claude/CLAUDE.md").write_text("# claude project memory\n", encoding="utf-8")
    run_git(repo, "add", ".")
    assert run_git(repo, "commit", "-qm", "track ai docs with policy").returncode == 0

    state = subprocess.run(
        ["python3", str(FLOW_STATE)],
        cwd=repo,
        env={**os.environ, "RLDYOUR_FLOW_STATE_LOCAL_ONLY": "1"},
        text=True,
        capture_output=True,
        check=False,
        timeout=DEFAULT_TIMEOUT,
    )
    assert state.returncode == 0, state.stderr
    payload = json.loads(state.stdout)
    assert payload["blocking_reasons"] == []
    assert payload["needs_flow_sync"] is False

    stop = subprocess.run(
        ["bash", str(STOP_HOOK)],
        cwd=repo,
        input='{"stop_hook_active":false}',
        text=True,
        capture_output=True,
        check=False,
        timeout=DEFAULT_TIMEOUT,
    )
    assert stop.returncode == 0
