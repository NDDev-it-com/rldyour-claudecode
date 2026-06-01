"""Integration + unit tests for scripts/check_mcp_runtime_versions.py.

The validator has hardcoded SERVER_TO_ENV + HTTP_TO_ENV + SYSTEM_BINARY_TO_ENV
mappings that target the real `plugins/rldyour-mcps/.mcp.json` server set.
Building a complete synthetic fixture covering all 12 servers is more
work than it's worth - this test file instead:

1. Runs the validator against the live repository state (integration).
2. Verifies the env loader behavior on edge cases (unit).

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

import check_mcp_runtime_versions  # noqa: E402


@pytest.mark.integration
def test_real_repo_passes() -> None:
    """End-to-end smoke against the live repository.

    The .mcp.json shipped at HEAD must align with the env file; any
    drift would fail this assertion. Marked integration because it
    depends on the live repo state including .mcp.json + env file.
    """
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check_mcp_runtime_versions.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO_ROOT,
        timeout=30,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"


class TestEnvLoader:
    def test_load_env_skips_comments_and_blanks(self, tmp_path: Path) -> None:
        env_file = tmp_path / "test.env"
        env_file.write_text(
            "# header comment\n"
            "\n"
            "FIRST=value-one\n"
            "  # indented comment\n"
            "SECOND=value-two\n"
            "MALFORMED_NO_EQUALS\n"
            "THIRD=value=with=equals\n",
            encoding="utf-8",
        )
        result = check_mcp_runtime_versions.load_env(env_file)
        assert result == {
            "FIRST": "value-one",
            "SECOND": "value-two",
            "THIRD": "value=with=equals",
        }

    def test_load_env_missing_file_returns_empty(self, tmp_path: Path) -> None:
        result = check_mcp_runtime_versions.load_env(tmp_path / "nonexistent.env")
        assert result == {}


class TestExtractVersion:
    def test_finds_prefix_in_args_list(self) -> None:
        args = ["uvx", "serena-agent==1.5.3", "--something"]
        assert (
            check_mcp_runtime_versions.extract_version(args, "serena-agent==")
            == "1.5.3"
        )

    def test_returns_none_when_prefix_missing(self) -> None:
        args = ["uvx", "other-package==2.0.0"]
        assert (
            check_mcp_runtime_versions.extract_version(args, "serena-agent==")
            is None
        )
