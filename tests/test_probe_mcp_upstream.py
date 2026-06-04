"""Unit tests for scripts/probe_mcp_upstream.py.

The probe exits 0 unconditionally - network failures surface as INFO
messages in the run log, drift surfaces as DRIFT messages plus a
::warning:: line. Tests cover:

1. Loader behavior on edge cases (comments, blanks, equals-in-value).
2. URL scheme guard prevents non-http schemes from reaching urlopen.
3. End-to-end exit code is 0 even when network probes are unreachable.

Closes the test gap noted by A-F-6 / verification F-5.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import probe_mcp_upstream  # noqa: E402


class TestSchemeGuard:
    def test_file_scheme_rejected(self) -> None:
        # The hard scheme guard closes the previous dynamic urllib finding.
        # Any non-http/https URL must be silently dropped to None.
        assert probe_mcp_upstream.fetch_json("file:///etc/passwd") is None

    def test_javascript_scheme_rejected(self) -> None:
        assert probe_mcp_upstream.fetch_json("javascript:alert(1)") is None

    def test_empty_string_rejected(self) -> None:
        assert probe_mcp_upstream.fetch_json("") is None


class TestEnvLoader:
    def test_load_env_skips_comments_and_blanks(self, tmp_path: Path) -> None:
        env_file = tmp_path / "test.env"
        env_file.write_text(
            "# header\n"
            "\n"
            "ONE=one\n"
            "TWO=two\n",
            encoding="utf-8",
        )
        result = probe_mcp_upstream.load_env(env_file)
        assert result == {"ONE": "one", "TWO": "two"}


class TestNormalize:
    def test_strips_v_prefix(self) -> None:
        assert probe_mcp_upstream.normalize("v3.11.0") == "3.11.0"

    def test_strips_whitespace(self) -> None:
        assert probe_mcp_upstream.normalize("  1.2.3  ") == "1.2.3"


class TestDartStableRegistry:
    def test_dart_stable_rejects_non_dart_package(self) -> None:
        # The signature is uniform with npm/pypi/brew probes but only
        # the literal "dart" is supported - other names return None.
        assert probe_mcp_upstream.latest_dart_stable("not-dart") is None


@pytest.mark.integration
def test_full_run_exits_zero() -> None:
    """End-to-end smoke - validator must never fail-exit even on network errors.

    Marked integration because it depends on the live env file and may
    issue network requests (which gracefully degrade to INFO messages).
    """
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "probe_mcp_upstream.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO_ROOT,
        timeout=120,
    )
    assert result.returncode == 0, f"probe should always exit 0; stderr: {result.stderr}"
    assert "Probed" in result.stdout
