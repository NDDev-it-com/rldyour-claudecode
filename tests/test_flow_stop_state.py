from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FLOW_PLUGIN = REPO_ROOT / "plugins" / "rldyour-flow"
FLOW_STATE = FLOW_PLUGIN / "scripts" / "flow_post_task_state.py"
FULLREPO_SYNC = FLOW_PLUGIN / "scripts" / "fullrepo_sync.py"
STOP_HOOK = FLOW_PLUGIN / "hooks" / "stop_post_task_sync.sh"


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=False)


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
        "\n".join(
            [
                "<!-- Memory Metadata",
                "Last updated: 2026-05-28",
                f"Last commit: {head_short}",
                "Scope: test",
                "Area: CORE",
                "-->",
                "# CORE-01-INDEX",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_direct_installed_flow_state_resolves_self_plugin_scripts(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    head_short = init_repo(repo)
    write_current_memory(repo, head_short)

    env = os.environ.copy()
    env["RLDYOUR_FLOW_STATE_LOCAL_ONLY"] = "1"
    proc = subprocess.run(
        ["python3", str(FLOW_STATE)],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["serena_current"] is True
    assert payload["fullrepo_state"]["network_checked"] is False


def test_fullrepo_status_local_only_does_not_mark_network_checked(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_repo(repo)

    proc = subprocess.run(
        ["python3", str(FULLREPO_SYNC), "--status-json", "--local-only"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["network_checked"] is False


def test_stop_post_task_loop_guard_works_from_subdirectory(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    head_short = init_repo(repo)
    write_current_memory(repo, head_short)
    workdir = repo / "src"
    workdir.mkdir()
    (repo / "pending.txt").write_text("dirty\n", encoding="utf-8")

    first = subprocess.run(
        ["bash", str(STOP_HOOK)],
        cwd=workdir,
        input='{"stop_hook_active":false}',
        text=True,
        capture_output=True,
        check=False,
    )

    assert first.returncode == 2
    assert "[RLDYOUR-FLOW POST-TASK SYNC REQUIRED]" in first.stderr

    second = subprocess.run(
        ["bash", str(STOP_HOOK)],
        cwd=workdir,
        input='{"stop_hook_active":true}',
        text=True,
        capture_output=True,
        check=False,
    )

    assert second.returncode == 0
    assert "Allowing stop now to avoid a Stop-hook loop" in second.stdout
