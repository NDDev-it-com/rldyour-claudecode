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
    return json.loads((repo / "config" / "marketplace-policy.json").read_text(encoding="utf-8"))


def _write_policy(repo: Path, data: dict[str, object]) -> None:
    (repo / "config" / "marketplace-policy.json").write_text(json.dumps(data), encoding="utf-8")


RETIRED_CONTEXT_KEY = "full" + "repo"


class TestTrackedContextPolicy:
    def test_matching_policy_passes(self, patch_repo_root: Path) -> None:
        result = _run(patch_repo_root)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "durable AI context tracked on main" in result.stdout

    def test_legacy_context_branch_policy_key_blocks(self, patch_repo_root: Path) -> None:
        data = _load_policy(patch_repo_root)
        data[f"{RETIRED_CONTEXT_KEY}_branch"] = RETIRED_CONTEXT_KEY
        _write_policy(patch_repo_root, data)
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "legacy secondary-context policy key" in result.stderr

    def test_tracked_context_globs_required(self, patch_repo_root: Path) -> None:
        data = _load_policy(patch_repo_root)
        data["tracked_context_globs"] = ["README.md"]
        _write_policy(patch_repo_root, data)
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "tracked_context_globs" in result.stderr
