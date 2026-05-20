"""Tests for scripts/validate_boundaries.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run(fake_repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "validate_boundaries.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=fake_repo,
        timeout=30,
    )


def _load_policy(repo: Path) -> dict[str, object]:
    policy = repo / "config" / "marketplace-policy.json"
    return json.loads(policy.read_text(encoding="utf-8"))


def _write_policy(repo: Path, data: dict[str, object]) -> None:
    policy = repo / "config" / "marketplace-policy.json"
    policy.write_text(json.dumps(data), encoding="utf-8")


class TestFullrepoPolicyParity:
    def test_matching_policy_passes(self, patch_repo_root: Path) -> None:
        result = _run(patch_repo_root)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "agent-only path policy" in result.stdout

    def test_agent_only_path_drift_blocks(self, patch_repo_root: Path) -> None:
        data = _load_policy(patch_repo_root)
        data["agent_only_path_globs"] = ["AGENTS.md"]
        _write_policy(patch_repo_root, data)

        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "agent_only_path_globs drift" in result.stderr
        assert ".codex/**" in result.stderr

    def test_runtime_exclude_drift_blocks(self, patch_repo_root: Path) -> None:
        data = _load_policy(patch_repo_root)
        data["runtime_exclude_globs"] = []
        _write_policy(patch_repo_root, data)

        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "runtime_exclude_globs drift" in result.stderr
        assert ".serena/.gitignore" in result.stderr
