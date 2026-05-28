#!/usr/bin/env python3
"""validate_agent_tools.py - static validation of agent `tools:` allowlists.

Parses every `plugins/*/agents/*.md` frontmatter and verifies that each entry
in the `tools:` list is syntactically valid and references a real MCP server
when an `mcp__plugin_*` pattern is used. Also enforces the read-only-by-design
invariant for non-Serena MCP wildcards (TECHDEBT R4).

Validation rules:
  1. Built-in tool names must be in `KNOWN_BUILTIN_TOOLS`.
  2. MCP pattern `mcp__plugin_<plugin>_<server>__<tool_or_star>` must:
     - Reference a real plugin from `.claude-plugin/marketplace.json`.
     - Reference a real server name from `plugins/rldyour-mcps/.mcp.json`
       (or a known external pattern when plugin owns its own .mcp.json).
  3. Wildcards (`__*`) for non-Serena MCP servers must be listed in
     `READ_ONLY_BY_DESIGN_MCPS` - these servers are documented invariant as
     read-only-by-contract. Adding a wildcard for a server that exposes write
     tools (currently only Serena) is a FAIL.

Exit codes: 0 success, 1 on any validation error.

Companion: TECHDEBT-01-NOW.md R4 documents the read-only-by-design invariant
for context7, deepwiki, grep, semgrep MCP servers. This script is the
deterministic check that enforces it.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from _mcp_parse import split_mcp_ref

# Built-in tool names supported by Claude Code (verified against v2.1.154 docs).
# Source: code.claude.com/docs/en/sub-agents + plugin-shipped agents canonical examples.
KNOWN_BUILTIN_TOOLS: frozenset[str] = frozenset(
    {
        "Read",
        "Edit",
        "Write",
        "Bash",
        "BashOutput",
        "Grep",
        "Glob",
        "Task",
        "WebFetch",
        "WebSearch",
        "NotebookEdit",
        "NotebookRead",
        "KillShell",
        "TodoWrite",
        "ExitPlanMode",
        "MultiEdit",
        "SlashCommand",
        "Skill",
    }
)

# MCP servers whose tool surface is read-only-by-design (verified 2026-05-15 via
# scripts/smoke_mcp_capabilities.sh tools/list inspection):
#   - context7: only resolve-library-id and get-library-docs (read).
#   - deepwiki: only ask_question and read_wiki_* tools (read).
#   - grep: only searchGitHub (read).
#   - openai-docs: fetch/get/list/search OpenAI docs and OpenAPI specs (read).
#     Added 2026-05-17 closing security F-8 from review wave
#     `2026-05-16T1859Z-61b913d`; no agent currently uses the wildcard but
#     the set is now complete for all four read-only HTTP MCP servers.
#   - semgrep: only scan/analyze tools (read).
# Adding a new server to this set means asserting it has no write/edit/create/
# delete/modify/insert/replace tools at runtime. Re-verify via
# scripts/smoke_mcp_capabilities.sh when MCP servers bump versions.
READ_ONLY_BY_DESIGN_MCPS: frozenset[str] = frozenset(
    {
        "context7",
        "deepwiki",
        "grep",
        "openai-docs",
        "semgrep",
    }
)

# Servers that have known write/mutating tools and therefore MUST use explicit
# tool name allowlists (not wildcards) in read-only agent frontmatters.
SERVERS_WITH_WRITE_TOOLS: frozenset[str] = frozenset(
    {
        "serena",
    }
)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TOOLS_BLOCK_RE = re.compile(r"^tools:\s*\n((?:  -\s*.+\n?)+)", re.MULTILINE)
TOOL_ITEM_RE = re.compile(r"^  -\s*(.+?)\s*$", re.MULTILINE)


def load_marketplace_plugins(repo_root: Path) -> set[str]:
    """Return the set of plugin names declared in marketplace.json.

    Names preserved verbatim (hyphenated) for parity with the shared
    `split_mcp_ref` helper which longest-prefix-matches against the
    `mcp__plugin_<plugin>_<server>__*` reference form.
    """
    manifest = repo_root / ".claude-plugin" / "marketplace.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return {p["name"] for p in data.get("plugins", [])}


def load_mcp_servers(repo_root: Path) -> set[str]:
    """Return the set of MCP server names declared in rldyour-mcps/.mcp.json."""
    manifest = repo_root / "plugins" / "rldyour-mcps" / ".mcp.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return set(data.get("mcpServers", {}).keys())


def extract_tools_list(frontmatter_text: str) -> list[str] | None:
    """Extract the `tools:` list items, returns None when no `tools:` block."""
    block_match = TOOLS_BLOCK_RE.search(frontmatter_text)
    if not block_match:
        return None
    block = block_match.group(1)
    return [m.group(1) for m in TOOL_ITEM_RE.finditer(block)]


def validate_agent_file(
    path: Path,
    valid_plugins: set[str],
    valid_servers: set[str],
    failures: list[str],
) -> None:
    """Validate one agent's frontmatter `tools:` block."""
    text = path.read_text(encoding="utf-8")
    fm_match = FRONTMATTER_RE.match(text)
    if not fm_match:
        failures.append(f"{path}: missing or malformed frontmatter")
        return
    tools = extract_tools_list(fm_match.group(1))
    if tools is None:
        # No tools: block means agent inherits default toolset; nothing to
        # validate here. flow-memory-sync uses this pattern intentionally.
        return
    for raw in tools:
        if raw in KNOWN_BUILTIN_TOOLS:
            continue
        parsed = split_mcp_ref(raw, valid_plugins)
        if parsed is None:
            failures.append(f"{path}: unrecognised tool entry `{raw}` "
                            "(not a built-in tool and not an mcp__plugin_* pattern)")
            continue
        plugin, server, tool = parsed
        # Scope: this validator targets rldyour-mcps MCP namespace only.
        # Other plugins are recognised by `split_mcp_ref` but their server
        # surface is not currently audited here. If/when another plugin ships
        # its own .mcp.json, add it to the scope below + load its servers.
        if plugin != "rldyour-mcps":
            if plugin not in valid_plugins:
                failures.append(
                    f"{path}: tool `{raw}` references unknown plugin `{plugin}` "
                    f"(known: {sorted(valid_plugins)})"
                )
            continue
        if server not in valid_servers:
            failures.append(
                f"{path}: tool `{raw}` references MCP server `{server}` "
                f"which is not declared in plugins/rldyour-mcps/.mcp.json"
            )
            continue
        if tool == "*":
            if server in SERVERS_WITH_WRITE_TOOLS:
                failures.append(
                    f"{path}: wildcard `mcp__plugin_rldyour-mcps_{server}__*` is "
                    f"forbidden for read-only agents because `{server}` exposes "
                    "write tools. Use an explicit read-only tool list instead."
                )
                continue
            if server not in READ_ONLY_BY_DESIGN_MCPS:
                failures.append(
                    f"{path}: wildcard `mcp__plugin_rldyour-mcps_{server}__*` "
                    f"uses MCP server `{server}` that is not in "
                    "READ_ONLY_BY_DESIGN_MCPS. Either confirm the server has no "
                    "write tools and add it to that set, or replace the wildcard "
                    "with explicit read-only tool names."
                )


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    valid_servers = load_mcp_servers(repo_root)
    valid_plugins = load_marketplace_plugins(repo_root)

    # Scope: this validator targets `plugins/*/agents/*.md` ONLY.
    # SKILL.md and slash command files are intentionally excluded for these
    # reasons (closure of architecture F-6, info 95, from review wave
    # `2026-05-16T1859Z-61b913d`):
    #   1. Skills carry `allowed-tools` (UX hint that suppresses permission
    #      prompts during work); agents carry `tools` (hard runtime allowlist
    #      enforced by Claude Code). Different semantics, different invariants.
    #   2. The confused-deputy class this validator prevents (D15 closure,
    #      R4 mitigation) is about subagent runtime capabilities, not about
    #      main-session skill UX. A skill misusing a wildcard does not
    #      escalate privilege; an agent doing so does.
    #   3. Skills are routinely re-invoked from the main session under the
    #      orchestrator's tool-use approval; agents run autonomously in
    #      forked context for review/research workflows.
    # If/when skills gain agent-equivalent runtime semantics, extend this
    # validator to cover them.
    agent_files = sorted((repo_root / "plugins").glob("*/agents/*.md"))
    if not agent_files:
        print("FAIL no plugin agent files found", file=sys.stderr)
        return 1

    failures: list[str] = []
    for agent_path in agent_files:
        validate_agent_file(agent_path, valid_plugins, valid_servers, failures)

    if failures:
        print("validate_agent_tools.py: validation FAILED", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    print(
        f"OK {len(agent_files)} agent file(s) validated, "
        f"{len(valid_servers)} MCP servers known"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
