#!/usr/bin/env python3
"""release_manifest.py — emit a single-snapshot release manifest as JSON.

Combines the marketplace VERSION file, every plugin.json (`name`+`version`),
the active MCP server pins from .mcp.json, the current `main` HEAD SHA, and the
contents of CHANGELOG.md's `[Unreleased]` section into a machine-readable
manifest. Useful for tagging releases (`claude plugin tag --push`), auditing
shipped versions, and building release-notes evidence.

Output to stdout. Exit code 0 on success, 1 if any required input is missing.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def git(*args: str) -> str:
    proc = subprocess.run(["git", *args], check=False, capture_output=True, text=True)
    return proc.stdout.strip()


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").rstrip()


def extract_unreleased_section(changelog_text: str) -> str:
    """Return the body of [Unreleased] up to (but not including) the next
    `## [` heading, trimmed."""
    match = re.search(
        r"^## \[Unreleased\][^\n]*\n(.*?)(?=\n## \[)",
        changelog_text,
        re.DOTALL | re.MULTILINE,
    )
    if not match:
        return ""
    return match.group(1).strip()


def main() -> int:
    root = Path(__file__).resolve().parent.parent

    version_path = root / "VERSION"
    if not version_path.is_file():
        print(f"FAIL missing {version_path}", file=sys.stderr)
        return 1
    marketplace_version = version_path.read_text(encoding="utf-8").strip()

    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    if not marketplace_path.is_file():
        print(f"FAIL missing {marketplace_path}", file=sys.stderr)
        return 1
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))

    mcp_path = root / "plugins" / "rldyour-mcps" / ".mcp.json"
    mcp_servers: dict[str, dict] = {}
    if mcp_path.is_file():
        mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
        mcp_servers = mcp.get("mcpServers", {})

    plugins: list[dict] = []
    for entry in marketplace.get("plugins", []):
        name = entry.get("name")
        source = entry.get("source", "")
        version = None
        if source.startswith("./"):
            plugin_manifest = (root / source / ".claude-plugin" / "plugin.json").resolve()
            if plugin_manifest.is_file():
                pdata = json.loads(plugin_manifest.read_text(encoding="utf-8"))
                version = pdata.get("version")
        plugins.append(
            {
                "name": name,
                "source": source,
                "category": entry.get("category"),
                "version": version,
                "marketplace_version": entry.get("version"),
            }
        )

    mcp_summary: list[dict] = []
    for name, cfg in mcp_servers.items():
        if cfg.get("type") == "http":
            mcp_summary.append({"name": name, "transport": "http", "url": cfg.get("url")})
        else:
            args = cfg.get("args", [])
            pin = next((a for a in args if "==" in a or (a.startswith("@") and "@" in a[1:])), None)
            mcp_summary.append(
                {
                    "name": name,
                    "transport": cfg.get("type", "stdio"),
                    "command": cfg.get("command"),
                    "pin": pin,
                    "always_load": bool(cfg.get("alwaysLoad")),
                }
            )

    head_full = git("rev-parse", "HEAD")
    head_short = head_full[:7] if head_full else ""
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}") or None

    changelog_text = read_text(root / "CHANGELOG.md")
    unreleased = extract_unreleased_section(changelog_text)

    manifest = {
        "marketplace": {
            "name": marketplace.get("name"),
            "version": marketplace_version,
            "pluginRoot": marketplace.get("metadata", {}).get("pluginRoot"),
            "owner": marketplace.get("owner"),
            "plugin_count": len(plugins),
        },
        "git": {
            "head_full": head_full,
            "head_short": head_short,
            "branch": branch,
            "upstream": upstream,
        },
        "plugins": plugins,
        "mcp_servers": mcp_summary,
        "changelog_unreleased": unreleased,
    }

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
