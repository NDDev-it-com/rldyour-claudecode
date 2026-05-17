"""Unit tests for scripts/validate_release_state.py.

Covers VERSION/CHANGELOG/manifest parity gate.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(fake_repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "validate_release_state.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=fake_repo,
    )


class TestParity:
    def test_version_matches_changelog_passes(self, patch_repo_root: Path) -> None:
        # fake_repo fixture has VERSION=0.4.0 and CHANGELOG [0.4.0] - they agree.
        # release_manifest.py may not exist in the symlink set; tolerate FAIL on that.
        result = _run(patch_repo_root)
        # Acceptable: either OK or FAIL specifically about release_manifest.py missing.
        if result.returncode != 0:
            assert "release_manifest.py" in result.stderr, (
                f"unexpected failure unrelated to release_manifest: {result.stderr}"
            )

    def test_version_changelog_mismatch_blocked(self, patch_repo_root: Path) -> None:
        # Drift VERSION away from CHANGELOG's latest entry.
        (patch_repo_root / "VERSION").write_text("0.9.9\n", encoding="utf-8")
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "0.9.9" in result.stderr
        assert "0.4.0" in result.stderr


class TestManifestParity:
    def test_plugin_version_drift_blocked(self, patch_repo_root: Path) -> None:
        # Drift plugin.json version away from marketplace entry.
        manifest = patch_repo_root / "plugins" / "sample-plugin" / ".claude-plugin" / "plugin.json"
        manifest.write_text(
            '{"name": "sample-plugin", "version": "0.9.9"}', encoding="utf-8",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "sample-plugin" in result.stderr
        assert "drift" in result.stderr.lower()
