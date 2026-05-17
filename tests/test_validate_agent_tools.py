"""Unit tests for scripts/validate_agent_tools.py.

Security-critical validator: enforces the read-only-by-design invariant
for non-Serena MCP wildcards. Tests cover:

- Built-in tools pass unconditionally (Read, Write, Bash, etc.).
- Agents with no `tools:` block inherit default toolset (no validation needed).
- Wildcards for write-capable servers (Serena) are blocked.
- Wildcards for read-only-by-design servers (context7, deepwiki, ...) pass.
- Unknown MCP server names are blocked.
- Unknown plugin names are blocked (new branch after LOW-6 refactor).
- Malformed MCP refs are blocked.

Closes A-LOW-7 / A-F-6 from 2026-05-17T0948Z-12a2bdc review wave: the
security-critical validator was previously untested.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(fake_repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "validate_agent_tools.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=fake_repo,
    )


def _make_agent(plugin_root: Path, name: str, tools: list[str] | None) -> None:
    """Create an agent .md file with the given `tools:` list.

    When `tools` is None, the agent has no `tools:` block (inherits default
    toolset). Otherwise the YAML frontmatter contains a populated list.
    """
    agents_dir = plugin_root / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    if tools is None:
        body = (
            "---\n"
            f"name: {name}\n"
            "description: test agent\n"
            "---\n\nbody\n"
        )
    else:
        tools_yaml = "\n".join(f"  - {t}" for t in tools)
        body = (
            "---\n"
            f"name: {name}\n"
            "description: test agent\n"
            "tools:\n"
            f"{tools_yaml}\n"
            "---\n\nbody\n"
        )
    (agents_dir / f"{name}.md").write_text(body, encoding="utf-8")


class TestBuiltinTools:
    def test_builtin_only_passes(self, patch_repo_root: Path) -> None:
        plugin = patch_repo_root / "plugins" / "sample-plugin"
        _make_agent(plugin, "builtin-agent", ["Read", "Write", "Bash"])
        result = _run(patch_repo_root)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "OK" in result.stdout

    def test_no_tools_block_inherits_default(self, patch_repo_root: Path) -> None:
        # No `tools:` block at all - agent inherits default toolset and the
        # validator should pass without checking anything. This is the
        # flow-memory-sync pattern (uses default toolset).
        plugin = patch_repo_root / "plugins" / "sample-plugin"
        _make_agent(plugin, "default-tools-agent", tools=None)
        result = _run(patch_repo_root)
        assert result.returncode == 0, f"stderr: {result.stderr}"


class TestReadOnlyInvariant:
    def test_serena_wildcard_blocked(self, patch_repo_root: Path) -> None:
        # Serena exposes write tools (edit_file, replace_symbol_body, etc.) so
        # a wildcard would grant write capability to a read-only-by-contract
        # subagent. This is the core security invariant validate_agent_tools.py
        # enforces (TECHDEBT R4 closure).
        plugin = patch_repo_root / "plugins" / "sample-plugin"
        _make_agent(plugin, "bad-wildcard-agent", ["mcp__plugin_rldyour-mcps_serena__*"])
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "serena" in result.stderr
        assert "forbidden" in result.stderr.lower() or "write tools" in result.stderr

    def test_context7_wildcard_passes(self, patch_repo_root: Path) -> None:
        # context7 is in READ_ONLY_BY_DESIGN_MCPS so the wildcard is allowed
        # for read-only subagents.
        plugin = patch_repo_root / "plugins" / "sample-plugin"
        _make_agent(plugin, "context7-agent", ["mcp__plugin_rldyour-mcps_context7__*"])
        result = _run(patch_repo_root)
        assert result.returncode == 0, f"stderr: {result.stderr}"


class TestUnknownReferences:
    def test_unknown_mcp_server_blocked(self, patch_repo_root: Path) -> None:
        # Server name typo - validator catches the unknown server name.
        plugin = patch_repo_root / "plugins" / "sample-plugin"
        _make_agent(
            plugin, "typo-agent", ["mcp__plugin_rldyour-mcps_serenna__find_symbol"]
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "serenna" in result.stderr

    def test_unknown_plugin_blocked(self, patch_repo_root: Path) -> None:
        # New branch enabled by LOW-6 refactor: agent_tools now uses the
        # shared split_mcp_ref and recognises plugin names from the marketplace.
        # Unknown plugin yields a specific "unknown plugin" error.
        plugin = patch_repo_root / "plugins" / "sample-plugin"
        _make_agent(
            plugin, "unknown-plugin-agent",
            ["mcp__plugin_nonexistent-plugin_serena__find_symbol"],
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "nonexistent-plugin" in result.stderr

    def test_malformed_mcp_ref_blocked(self, patch_repo_root: Path) -> None:
        # Reference is not an mcp__plugin_* pattern and not a built-in tool.
        plugin = patch_repo_root / "plugins" / "sample-plugin"
        _make_agent(plugin, "weird-agent", ["NotARealTool"])
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "NotARealTool" in result.stderr
        assert "unrecognised" in result.stderr or "unrecognized" in result.stderr
