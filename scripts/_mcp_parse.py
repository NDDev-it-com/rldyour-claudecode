"""Shared MCP tool reference parser.

Unified parser used by validate_skill_allowed_tools.py and
validate_agent_tools.py so both validators apply the same semantics. The
historic split (longest-prefix in one, rsplit in the other) was flagged by
the 2026-05-17 review wave (architecture F-5, low 80) as a latent
consistency risk for plugin names containing underscores.

This module is the single source of truth. New MCP-aware validators must
import `split_mcp_ref` from here rather than duplicate the parsing logic.

Underscore-prefix `_mcp_parse` is intentional: Pyright + Ruff treat the
module as private to the `scripts/` package, which keeps it out of the
public-script surface and prevents accidental cross-tree imports.
"""

from __future__ import annotations


def split_mcp_ref(ref: str, plugins: set[str]) -> tuple[str, str, str] | None:
    """Parse an `mcp__plugin_<plugin>_<server>__<tool_or_star>` reference.

    Args:
        ref:     The raw tool reference string from `allowed-tools:` (skill
                 frontmatter) or `tools:` (agent frontmatter).
        plugins: Known plugin names from `.claude-plugin/marketplace.json`.

    Returns:
        `(plugin, server, tool_or_star)` tuple when the reference has the
        canonical shape. Returns `None` only when the input is not an
        MCP reference at all (missing `mcp__plugin_` prefix or no `__` tool
        delimiter). For unknown plugins, falls back to `rpartition('_')` so
        callers can emit a specific `unknown plugin` error rather than a
        generic `malformed MCP ref` error.

    Disambiguation strategy:
        1. Try longest-known-prefix match (handles `rldyour-mcps`, `chrome-devtools`
           and other hyphen-separated names cleanly).
        2. If no known plugin matches the prefix, fall back to splitting on the
           last underscore - the caller's subsequent `plugin not in plugins`
           check will surface the typo.
    """
    if not ref.startswith("mcp__plugin_"):
        return None
    rest = ref[len("mcp__plugin_"):]
    if "__" not in rest:
        return None
    prefix, _, tool = rest.partition("__")
    if not tool:
        return None
    for p in sorted(plugins, key=len, reverse=True):
        if prefix.startswith(p + "_"):
            server = prefix[len(p) + 1:]
            return p, server, tool
    if "_" in prefix:
        plugin, _, server = prefix.rpartition("_")
        return plugin, server, tool
    return None
