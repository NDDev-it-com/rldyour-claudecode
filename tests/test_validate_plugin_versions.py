"""Unit tests for scripts/validate_plugin_versions.py.

Covers the marketplace.json <-> plugin.json version parity contract.

The validator is one of the four release-gate validators (plus
release_state, plugin_versions, boundaries) that block a release tag
push if the version sources disagree.

Closes the test gap noted by A-F-6 / verification F-5.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run(fake_repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "validate_plugin_versions.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=fake_repo,
    )


class TestParity:
    def test_matching_versions_pass(self, patch_repo_root: Path) -> None:
        # fake_repo ships sample-plugin and rldyour-mcps both at 0.4.0
        # in marketplace.json and plugin.json - the validator should report
        # OK for both.
        result = _run(patch_repo_root)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "sample-plugin" in result.stdout
        assert "rldyour-mcps" in result.stdout

    def test_plugin_version_drift_blocks(self, patch_repo_root: Path) -> None:
        # Drift sample-plugin's plugin.json away from the marketplace entry.
        manifest = (
            patch_repo_root / "plugins" / "sample-plugin" / ".claude-plugin" / "plugin.json"
        )
        manifest.write_text(
            '{"name": "sample-plugin", "version": "9.9.9"}', encoding="utf-8",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "sample-plugin" in result.stderr
        assert "9.9.9" in result.stderr
        assert "0.4.0" in result.stderr

    def test_missing_plugin_json_blocks(self, patch_repo_root: Path) -> None:
        # Delete sample-plugin's plugin.json - marketplace entry can no
        # longer be verified against a manifest.
        manifest = (
            patch_repo_root / "plugins" / "sample-plugin" / ".claude-plugin" / "plugin.json"
        )
        manifest.unlink()
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "plugin.json missing" in result.stderr

    def test_name_mismatch_blocks(self, patch_repo_root: Path) -> None:
        # plugin.json name does not match the marketplace entry name -
        # catches accidental copy-paste during scaffolding.
        manifest = (
            patch_repo_root / "plugins" / "sample-plugin" / ".claude-plugin" / "plugin.json"
        )
        manifest.write_text(
            '{"name": "wrong-name", "version": "0.4.0"}', encoding="utf-8",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "wrong-name" in result.stderr or "does not match" in result.stderr


class TestMarketplaceShape:
    def test_duplicate_name_blocks(self, patch_repo_root: Path) -> None:
        # Two marketplace entries with the same name - catches policy drift.
        marketplace = patch_repo_root / ".claude-plugin" / "marketplace.json"
        data = json.loads(marketplace.read_text(encoding="utf-8"))
        data["plugins"].append(
            {"name": "sample-plugin", "source": "./plugins/sample-plugin", "version": "0.4.0"}
        )
        marketplace.write_text(json.dumps(data), encoding="utf-8")
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "duplicate" in result.stderr.lower() or "sample-plugin" in result.stderr
