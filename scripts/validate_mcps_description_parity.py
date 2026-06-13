#!/usr/bin/env python3
"""Validate the rldyour-mcps plugin description server count matches .mcp.json.

This guards against prose drift in the rldyour-mcps plugin/marketplace
descriptions (for example claiming "12 серверов" or listing Playwright as an
MCP server when Playwright is a CLI-only browser provider, not an MCP server).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCP = ROOT / "plugins" / "rldyour-mcps" / ".mcp.json"
PLUGIN = ROOT / "plugins" / "rldyour-mcps" / ".claude-plugin" / "plugin.json"
MARKET = ROOT / ".claude-plugin" / "marketplace.json"

_COUNT_RE = re.compile(r"(\d+)\s+серверов")


def _stated_count(description: str) -> int | None:
    match = _COUNT_RE.search(description)
    return int(match.group(1)) if match else None


def main() -> int:
    servers = json.loads(MCP.read_text(encoding="utf-8")).get("mcpServers", {})
    actual = len(servers)
    server_keys = {key.lower() for key in servers}
    errors: list[str] = []

    plugin_desc = json.loads(PLUGIN.read_text(encoding="utf-8")).get("description", "")
    market = json.loads(MARKET.read_text(encoding="utf-8"))
    market_plugins = market.get("plugins", []) if isinstance(market, dict) else []
    market_desc = next(
        (p.get("description", "") for p in market_plugins if p.get("name") == "rldyour-mcps"),
        "",
    )

    for label, desc in (("plugins/rldyour-mcps/.claude-plugin/plugin.json", plugin_desc),
                        (".claude-plugin/marketplace.json (rldyour-mcps)", market_desc)):
        stated = _stated_count(desc)
        if stated is None:
            errors.append(f"{label} description must state 'N серверов'")
        elif stated != actual:
            errors.append(f"{label} description says {stated} серверов but .mcp.json defines {actual}")
        # Playwright is a CLI-only browser provider, never an MCP server here.
        if "playwright" in desc.lower() and "playwright" not in server_keys:
            errors.append(f"{label} description lists Playwright, which is not an MCP server (Playwright is CLI-only)")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"ok: rldyour-mcps description server count matches .mcp.json ({actual})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
