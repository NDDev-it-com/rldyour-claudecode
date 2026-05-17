"""Unit tests for scripts/validate_text_hygiene.py.

Covers F-TEST-05 audit closure for the text hygiene validator: positive
(clean repo passes), negative (em-dash, en-dash, BIDI control), and
allowlist (BIDI inside a documented hook sanitizer file is permitted).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _run(fake_repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "validate_text_hygiene.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=fake_repo,
        timeout=30,
    )


class TestPositive:
    def test_clean_repo_passes(self, patch_repo_root: Path) -> None:
        result = _run(patch_repo_root)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "OK" in result.stdout
        assert "0 typography violations" in result.stdout


class TestNegative:
    def test_em_dash_is_blocked(self, patch_repo_root: Path) -> None:
        (patch_repo_root / "drift.md").write_text("text — with em-dash", encoding="utf-8")
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "em-dash" in result.stderr
        assert "drift.md" in result.stderr

    def test_en_dash_is_blocked(self, patch_repo_root: Path) -> None:
        (patch_repo_root / "drift.md").write_text("range 1–3", encoding="utf-8")  # noqa: RUF001 - intentional EN DASH detection fixture
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "en-dash" in result.stderr

    def test_bidi_control_is_blocked(self, patch_repo_root: Path) -> None:
        # U+202E RLO is one of the Trojan Source family chars the validator forbids.
        (patch_repo_root / "drift.md").write_text("normal‮malicious", encoding="utf-8")
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "bidi-202e" in result.stderr


class TestAllowlist:
    def test_validator_self_skip(self, patch_repo_root: Path) -> None:
        """The validator itself contains EM_DASH/EN_DASH literals; it self-skips."""
        # Already verified by TestPositive (validator source is in scripts/)
        result = _run(patch_repo_root)
        assert result.returncode == 0

    def test_bidi_allowlist_skips_documented_file(self, patch_repo_root: Path) -> None:
        """The BIDI allowlist exempts the hook sanitiser source from scanning.

        Wave 0.4.4 externalised the allowlist to config/text-hygiene-allowlist.json
        and the fake_repo fixture now ships a matching stub at the documented
        path with an embedded BIDI char. Validator must return 0 (exemption
        respected) instead of flagging the BIDI sequence.
        """
        result = _run(patch_repo_root)
        assert result.returncode == 0, (
            f"BIDI exemption broken: stderr={result.stderr!r}, stdout={result.stdout!r}"
        )
        # Sanity: the stub file is actually present and contains the BIDI char.
        hook_path = (
            patch_repo_root / "plugins" / "rldyour-flow"
            / "hooks" / "post_tool_use_commit_advice.sh"
        )
        assert hook_path.is_file()
        assert "‮" in hook_path.read_text(encoding="utf-8")
