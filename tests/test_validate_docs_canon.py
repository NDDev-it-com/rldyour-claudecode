"""Unit tests for scripts/validate_docs_canon.py.

Covers forbidden_tokens detection and version_floors window heuristic
(max(30, len(knob)+15) direct-association). Closes F-TEST-05 for docs
canon track plus quality-review MED-1 regression lock-in for long knob
names like `maxSkillDescriptionChars` (24 chars).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run(fake_repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "validate_docs_canon.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=fake_repo,
        timeout=30,
    )


class TestForbiddenTokens:
    def test_passes_when_token_absent(self, patch_repo_root: Path) -> None:
        # fake_repo has README.md, AGENTS.md, .claude/CLAUDE.md - none mention "oldName"
        result = _run(patch_repo_root)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "0 canon drift" in result.stdout

    def test_blocks_forbidden_token(self, patch_repo_root: Path) -> None:
        (patch_repo_root / "README.md").write_text(
            "use oldName here\n\n<!-- inventory:begin -->\n<!-- inventory:end -->\n",
            encoding="utf-8",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "oldName" in result.stderr
        assert "newName" in result.stderr  # replacement suggestion present


class TestVersionFloors:
    def test_direct_association_detected(self, patch_repo_root: Path) -> None:
        (patch_repo_root / "README.md").write_text(
            "the foo knob was added in v1.9 long ago\n\n<!-- inventory:begin -->\n<!-- inventory:end -->\n",
            encoding="utf-8",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "foo" in result.stderr
        assert "v1.9" in result.stderr

    def test_far_separated_floor_not_flagged(self, patch_repo_root: Path) -> None:
        # foo and v1.9 separated by >30 chars - should NOT be flagged (window heuristic)
        (patch_repo_root / "README.md").write_text(
            "foo " + "padding-text " * 10 + "v1.9 unrelated\n\n<!-- inventory:begin -->\n<!-- inventory:end -->\n",
            encoding="utf-8",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 0, f"unexpected drift: {result.stderr}"

    def test_long_knob_window_expands_dynamically(self, patch_repo_root: Path) -> None:
        # Lock-in for MED-1: knob `aVeryLongConfigKnob` (19 chars) placed 33
        # chars before `v1.9`. Old fixed-30 window would miss it (window starts
        # at offset 3, knob starts at 0). New max(30, len(knob)+15) window =
        # max(30, 34) = 34, which clamps to start at 0 and catches the knob.
        canon = patch_repo_root / "config" / "cc-canon.json"
        data = json.loads(canon.read_text(encoding="utf-8"))
        data["version_floors"]["aVeryLongConfigKnob"] = {
            "floor": "v2.0+", "wrong_floors": ["v1.9"],
        }
        canon.write_text(json.dumps(data), encoding="utf-8")
        (patch_repo_root / "README.md").write_text(
            "aVeryLongConfigKnob added once in v1.9 here\n\n"
            "<!-- inventory:begin -->\n<!-- inventory:end -->\n",
            encoding="utf-8",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1, (
            f"long-knob heuristic regression: returncode={result.returncode}, "
            f"stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
        assert "aVeryLongConfigKnob" in result.stderr
        assert "v1.9" in result.stderr


class TestGracefulSkip:
    def test_skip_when_canon_missing(
        self, fake_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Remove cc-canon.json so the validator skips gracefully (per docstring contract).
        (fake_repo / "config" / "cc-canon.json").unlink()
        # Symlink validator into fake_repo/scripts so it sees fake_repo as root.
        scripts_link = fake_repo / "scripts"
        scripts_link.mkdir(exist_ok=True)
        src = Path(__file__).resolve().parent.parent / "scripts" / "validate_docs_canon.py"
        (scripts_link / "validate_docs_canon.py").write_bytes(src.read_bytes())
        monkeypatch.chdir(fake_repo)
        result = subprocess.run(
            [sys.executable, str(scripts_link / "validate_docs_canon.py")],
            capture_output=True,
            text=True,
            check=False,
            cwd=fake_repo,
            timeout=30,
        )
        assert result.returncode == 0
        assert "SKIP" in result.stdout
