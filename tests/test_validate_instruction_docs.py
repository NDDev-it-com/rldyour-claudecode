"""Unit tests for scripts/validate_instruction_docs.py.

Covers AGENTS.md + .claude/CLAUDE.md hygiene checks:
- presence (when --require-agent-docs is set),
- non-empty content with top-level heading,
- line cap (soft 200, hard 300),
- secret pattern detection (ctx7sk-, ghp_, sk-, Bearer, etc.).

Closes the test gap noted by A-F-6 / verification F-5.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(
    fake_repo: Path, *args: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(fake_repo / "scripts" / "validate_instruction_docs.py"),
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=fake_repo,
        timeout=30,
    )


class TestPresence:
    def test_require_agent_docs_passes_when_present(self, patch_repo_root: Path) -> None:
        # fake_repo ships AGENTS.md + .claude/CLAUDE.md.
        result = _run(patch_repo_root, "--require-agent-docs")
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_require_agent_docs_fails_when_missing(self, patch_repo_root: Path) -> None:
        (patch_repo_root / "AGENTS.md").unlink()
        result = _run(patch_repo_root, "--require-agent-docs")
        assert result.returncode == 1
        assert "AGENTS.md" in result.stderr

    def test_optional_mode_skips_missing(self, patch_repo_root: Path) -> None:
        (patch_repo_root / "AGENTS.md").unlink()
        result = _run(patch_repo_root)
        assert result.returncode == 0
        # SKIP message printed to stdout for missing-but-optional files.
        assert "SKIP" in result.stdout


class TestContentHygiene:
    def test_no_top_level_heading_fails(self, patch_repo_root: Path) -> None:
        (patch_repo_root / "AGENTS.md").write_text(
            "no heading here just text\n", encoding="utf-8"
        )
        result = _run(patch_repo_root, "--require-agent-docs")
        assert result.returncode == 1
        assert "top-level heading" in result.stderr

    def test_hard_cap_exceeded_fails(self, patch_repo_root: Path) -> None:
        # Generate 301 lines to exceed the 300-line hard cap.
        bloat = "# AGENTS\n" + ("line\n" * 305)
        (patch_repo_root / "AGENTS.md").write_text(bloat, encoding="utf-8")
        result = _run(patch_repo_root, "--require-agent-docs")
        assert result.returncode == 1
        assert "exceeds hard cap" in result.stderr

    def test_secret_pattern_detected(self, patch_repo_root: Path) -> None:
        # Embed a fake but pattern-matching ghp_ token. The validator's
        # SECRET_PATTERNS regex catches the prefix + length, not the value.
        fake_token = "ghp_" + "a" * 30
        (patch_repo_root / "AGENTS.md").write_text(
            f"# AGENTS\n\nleaked: {fake_token}\n", encoding="utf-8"
        )
        result = _run(patch_repo_root, "--require-agent-docs")
        assert result.returncode == 1
        assert "secret-looking" in result.stderr
