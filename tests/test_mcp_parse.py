"""Unit tests for scripts/_mcp_parse.py shared MCP reference parser.

These tests cover the parsing logic directly (no subprocess) so the
behavior is verified independent of any specific validator's call path.

Coverage:
- Longest-prefix match for known plugins (hyphen + underscore name shapes).
- rpartition fallback for unknown plugins (provides specific error path).
- Malformed input handling (missing prefix, missing tool, no separator).

Closes A-LOW-5 from 2026-05-17T0948Z-12a2bdc review wave: the docstring
of test_validate_skill_allowed_tools.py promises underscore-plugin
coverage but no test exercised it. The promise is now fulfilled here at
the parser layer, which is the actual code under test.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from _mcp_parse import split_mcp_ref  # noqa: E402


class TestLongestPrefixMatch:
    def test_hyphenated_plugin_matches(self) -> None:
        result = split_mcp_ref(
            "mcp__plugin_rldyour-mcps_serena__find_symbol", {"rldyour-mcps"}
        )
        assert result == ("rldyour-mcps", "serena", "find_symbol")

    def test_underscore_plugin_matches(self) -> None:
        # Locks in the LOW-6 fix: underscore plugin names parse via
        # longest-known-prefix match, not via greedy rsplit. Without this
        # behavior, `my_plugin_serena` would be split as ("my", "plugin_serena")
        # by the naive `prefix.split("_", 1)` approach.
        result = split_mcp_ref(
            "mcp__plugin_my_plugin_serena__*", {"my_plugin"}
        )
        assert result == ("my_plugin", "serena", "*")

    def test_hyphenated_server_works(self) -> None:
        # chrome-devtools server name has hyphen and would have been ambiguous
        # under the older rsplit('_', 1) strategy if combined with a hyphenated
        # plugin. The longest-prefix match resolves cleanly.
        result = split_mcp_ref(
            "mcp__plugin_rldyour-mcps_chrome-devtools__*", {"rldyour-mcps"}
        )
        assert result == ("rldyour-mcps", "chrome-devtools", "*")

    def test_longest_prefix_wins_when_two_known_plugins_share_root(self) -> None:
        # When two known plugin names share a leading substring (e.g., "my" and
        # "my_plugin"), the longer match must win so the tail is parsed as the
        # server, not as part of the plugin.
        result = split_mcp_ref(
            "mcp__plugin_my_plugin_serena__*", {"my", "my_plugin"}
        )
        assert result == ("my_plugin", "serena", "*")


class TestUnknownPluginFallback:
    def test_unknown_plugin_rpartition_fallback(self) -> None:
        # If the plugin is not in the known set, fall back to splitting on the
        # LAST underscore. This produces a specific (plugin, server) tuple so
        # callers can emit "unknown plugin" errors rather than the generic
        # "malformed MCP ref" message - better debugging UX.
        result = split_mcp_ref(
            "mcp__plugin_unknown-plugin_serena__*", {"rldyour-mcps"}
        )
        assert result == ("unknown-plugin", "serena", "*")


class TestMalformedInput:
    def test_missing_mcp_prefix_returns_none(self) -> None:
        assert split_mcp_ref("Read", set()) is None
        assert split_mcp_ref("Bash", {"any-plugin"}) is None

    def test_missing_double_underscore_returns_none(self) -> None:
        # No `__` separator between plugin/server segment and tool segment.
        assert split_mcp_ref("mcp__plugin_foo", set()) is None
        assert split_mcp_ref("mcp__plugin_foo_bar", {"foo"}) is None

    def test_empty_tool_returns_none(self) -> None:
        # `__` present but empty tool name - reject as malformed.
        assert split_mcp_ref("mcp__plugin_foo_bar__", {"foo"}) is None

    def test_no_underscore_in_prefix_for_unknown_plugin_returns_none(self) -> None:
        # prefix="foo", no known plugin matches, no underscore for rpartition.
        # Should return None rather than emit ("", "foo", "tool").
        assert split_mcp_ref("mcp__plugin_foo__tool", set()) is None
