"""Unit tests for scripts/generate_inventory.py.

Covers --check / --print modes and drift detection.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(fake_repo: Path, *flags: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "generate_inventory.py"), *flags],
        capture_output=True,
        text=True,
        check=False,
        cwd=fake_repo,
        timeout=30,
    )


class TestPrintMode:
    def test_print_emits_block(self, patch_repo_root: Path) -> None:
        result = _run(patch_repo_root, "--print")
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "<!-- inventory:begin -->" in result.stdout
        assert "<!-- inventory:end -->" in result.stdout
        assert "sample-plugin" in result.stdout
        assert "0.4.0" in result.stdout


class TestCheckMode:
    def test_check_detects_stale_inventory(self, patch_repo_root: Path) -> None:
        # First populate inventory.
        populate = _run(patch_repo_root)
        assert populate.returncode == 0

        # Drift README inventory by hand (remove the table row).
        readme = patch_repo_root / "README.md"
        text = readme.read_text(encoding="utf-8")
        before = text.split("<!-- inventory:begin -->")[0]
        after = text.split("<!-- inventory:end -->")[1]
        readme.write_text(
            f"{before}<!-- inventory:begin -->\nSTALE\n<!-- inventory:end -->{after}",
            encoding="utf-8",
        )

        result = _run(patch_repo_root, "--check")
        assert result.returncode == 1
        assert "stale" in result.stderr.lower()


class TestRefresh:
    def test_default_writes_block(self, patch_repo_root: Path) -> None:
        result = _run(patch_repo_root)
        assert result.returncode == 0
        text = (patch_repo_root / "README.md").read_text(encoding="utf-8")
        assert "sample-plugin" in text
        assert "0.4.0" in text
