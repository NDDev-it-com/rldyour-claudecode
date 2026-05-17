#!/usr/bin/env python3
"""validate_skill_allowed_tools.py - server-namespace check for SKILL.md tools.

Skills frontmatter `allowed-tools:` field is a UX hint (pre-approves listed
tools so the model can call them without per-call permission prompts). Unlike
agent frontmatter, it is not a hard runtime allowlist - see audit F-CONS-03.
But typos in MCP server names (e.g., `mcp__plugin_rldyour-mcps_figmaa__*`)
silently degrade the skill UX and only surface as runtime friction.

This validator enforces a single invariant: every `mcp__plugin_<plugin>_<server>__*`
or `mcp__plugin_<plugin>_<server>__<tool>` reference in any SKILL.md frontmatter
must name a real plugin (in marketplace.json) and a real MCP server (in
plugins/rldyour-mcps/.mcp.json). Wildcards (`__*`) are allowed - this is
namespace-only validation, not per-tool surface validation.

Companion: scripts/validate_agent_tools.py covers agent frontmatter with a
stricter contract (no wildcards for write-enabled servers). Skills validate
their server namespace here.

Exit codes: 0 success, 1 on any unknown plugin or server reference.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TOOLS_BLOCK_RE = re.compile(r"^allowed-tools:\s*\n((?:  -\s*.+\n)+)", re.MULTILINE)
TOOL_ITEM_RE = re.compile(r"^  -\s*(.+?)\s*$", re.MULTILINE)
MCP_PATTERN_RE = re.compile(
    r"^mcp__plugin_(?P<plugin>[A-Za-z0-9_-]+?)_(?P<server>[A-Za-z0-9-]+)__(?P<tool>.+)$"
)


def load_marketplace_plugins(root: Path) -> set[str]:
    manifest = root / ".claude-plugin" / "marketplace.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return {p["name"] for p in data.get("plugins", [])}


def load_mcp_servers(root: Path) -> set[str]:
    mcp = root / "plugins" / "rldyour-mcps" / ".mcp.json"
    data = json.loads(mcp.read_text(encoding="utf-8"))
    return set(data.get("mcpServers", {}).keys())


def extract_allowed_tools(skill_text: str) -> list[str]:
    fm_match = FRONTMATTER_RE.match(skill_text)
    if not fm_match:
        return []
    fm = fm_match.group(1)
    block_match = TOOLS_BLOCK_RE.search(fm)
    if not block_match:
        return []
    return [m.group(1).strip() for m in TOOL_ITEM_RE.finditer(block_match.group(1))]


def split_mcp_ref(ref: str, plugins: set[str]) -> tuple[str, str] | None:
    """Extract (plugin, server) from an MCP tool ref.

    `mcp__plugin_<plugin>_<server>__<tool>` - plugin may contain hyphens
    (rldyour-mcps), server may contain hyphens (chrome-devtools). We split by
    matching the longest plugin prefix that exists in `plugins`.
    """
    if not ref.startswith("mcp__plugin_"):
        return None
    rest = ref[len("mcp__plugin_"):]
    if "__" not in rest:
        return None
    prefix = rest.partition("__")[0]
    # Try matching plugin names by suffix replacement: prefix = "<plugin>_<server>"
    # We need to find a known plugin name `p` such that prefix.startswith(p + "_")
    # and the remainder after the underscore is the server.
    for p in sorted(plugins, key=len, reverse=True):
        if prefix.startswith(p + "_"):
            server = prefix[len(p) + 1:]
            return p, server
    return None


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    plugins = load_marketplace_plugins(root)
    servers = load_mcp_servers(root)

    failures: list[str] = []
    skill_count = 0
    ref_count = 0

    for skill in sorted(root.glob("plugins/*/skills/*/SKILL.md")):
        skill_count += 1
        text = skill.read_text(encoding="utf-8")
        for tool in extract_allowed_tools(text):
            if not tool.startswith("mcp__plugin_"):
                # Built-in tool name (Read, Write, Bash, ...) - not checked here.
                continue
            ref_count += 1
            parts = split_mcp_ref(tool, plugins)
            if parts is None:
                failures.append(f"{skill.relative_to(root)}: malformed MCP ref `{tool}`")
                continue
            plugin, server = parts
            if plugin not in plugins:
                failures.append(
                    f"{skill.relative_to(root)}: unknown plugin `{plugin}` in `{tool}` "
                    f"(known: {sorted(plugins)})"
                )
                continue
            if plugin == "rldyour-mcps" and server not in servers:
                failures.append(
                    f"{skill.relative_to(root)}: unknown MCP server `{server}` in `{tool}` "
                    f"(known: {sorted(servers)})"
                )

    if failures:
        for line in failures:
            print(f"FAIL {line}", file=sys.stderr)
        print(f"\nTotal: {len(failures)} failure(s) across {skill_count} skills.", file=sys.stderr)
        return 1

    print(
        f"OK {ref_count} MCP tool ref(s) across {skill_count} skill(s); "
        f"{len(plugins)} known plugin(s), {len(servers)} known MCP server(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
