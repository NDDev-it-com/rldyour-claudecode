"""Unit tests for scripts/validate_instruction_sync.py.

Covers sync_contract YAML block extraction and drift detection between
AGENTS.md and .claude/CLAUDE.md.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(fake_repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "validate_instruction_sync.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=fake_repo,
        timeout=30,
    )


class TestSyncContract:
    def test_matching_claims_pass(self, patch_repo_root: Path) -> None:
        # fake_repo fixture has shared='value-a' in both files - they match.
        result = _run(patch_repo_root)
        # Either OK with matching claims OR SKIP if yaml not importable.
        assert result.returncode == 0
        assert "shared claim(s) match" in result.stdout or "SKIP" in result.stdout

    def test_drift_detected_and_reported(self, patch_repo_root: Path) -> None:
        # Mutate CLAUDE.md to introduce drift on the shared claim.
        (patch_repo_root / ".claude" / "CLAUDE.md").write_text(
            "# CLAUDE\n\n<!-- sync_contract:\nclaims:\n  shared: 'value-b'\n-->\n",
            encoding="utf-8",
        )
        result = _run(patch_repo_root)
        # If yaml is importable, drift fails; otherwise SKIP.
        if "SKIP" in result.stdout:
            return  # yaml not installed in this environment
        assert result.returncode == 1
        assert "shared" in result.stderr
        assert "value-a" in result.stderr
        assert "value-b" in result.stderr


class TestGracefulSkip:
    def test_skip_when_no_blocks(self, patch_repo_root: Path) -> None:
        # Strip the sync_contract blocks - validator should SKIP not FAIL.
        (patch_repo_root / "AGENTS.md").write_text("# no contract\n", encoding="utf-8")
        (patch_repo_root / ".claude" / "CLAUDE.md").write_text("# no contract\n", encoding="utf-8")
        result = _run(patch_repo_root)
        assert result.returncode == 0
        assert "SKIP" in result.stdout or "no sync_contract" in result.stdout
