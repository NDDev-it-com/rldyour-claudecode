"""Unit tests for scripts/validate_skill_allowed_tools.py.

Covers server-namespace resolution including longest-plugin-prefix matching
for plugin names that contain underscores or hyphens.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(fake_repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "validate_skill_allowed_tools.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=fake_repo,
    )


def _make_skill(plugin_root: Path, name: str, allowed_tools: list[str]) -> None:
    """Helper: create a SKILL.md with the given allowed-tools."""
    skill_dir = plugin_root / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    tools_yaml = "\n".join(f"  - {t}" for t in allowed_tools)
    skill_dir.joinpath("SKILL.md").write_text(
        f"---\nname: {name}\ndescription: test\nallowed-tools:\n{tools_yaml}\n---\n\nbody\n",
        encoding="utf-8",
    )


class TestServerNamespace:
    def test_wildcard_for_known_server_passes(self, patch_repo_root: Path) -> None:
        # sample-plugin already in marketplace; rldyour-mcps has `serena` server.
        plugin = patch_repo_root / "plugins" / "sample-plugin"
        _make_skill(plugin, "sample-skill", ["mcp__plugin_rldyour-mcps_serena__*"])
        result = _run(patch_repo_root)
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_unknown_server_blocked(self, patch_repo_root: Path) -> None:
        plugin = patch_repo_root / "plugins" / "sample-plugin"
        _make_skill(plugin, "sample-skill", ["mcp__plugin_rldyour-mcps_figmaa__*"])
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "figmaa" in result.stderr
        assert "unknown MCP server" in result.stderr

    def test_unknown_plugin_blocked(self, patch_repo_root: Path) -> None:
        plugin = patch_repo_root / "plugins" / "sample-plugin"
        _make_skill(plugin, "sample-skill", ["mcp__plugin_unknown-plugin_serena__*"])
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "unknown plugin" in result.stderr
