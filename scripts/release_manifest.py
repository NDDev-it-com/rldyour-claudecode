#!/usr/bin/env python3
"""release_manifest.py - emit a single-snapshot release manifest as JSON.

Combines the marketplace VERSION file, every plugin.json (`name`+`version`),
the active MCP server pins from `.mcp.json`, host-binary pins from
`config/mcp-runtime-versions.env`, the current `main` HEAD SHA, and the
contents of `CHANGELOG.md`'s `[Unreleased]` section into a machine-readable
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

# Matches scoped (`@scope/name@1.2.3`) AND unscoped (`name@1.2.3`) npm specs.
# Requires the version segment to begin with a digit so flag-like tokens such
# as `--from` or option values like `--python=3.13` are not misclassified.
# Quality F-5 closure: leading char must be alphanumeric to reject
# hyphen/underscore/dot-leading names like "-pkg@1.0" or ".hidden@1.0"
# that npm itself rejects but the previous regex accepted.
NPM_PIN_RE = re.compile(
    r"^(?:@[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*|[A-Za-z0-9][A-Za-z0-9_.-]*)@[0-9][A-Za-z0-9_.+-]*$"
)

# Host-binary MCP servers - their pin is not in `.mcp.json` `args` but in the
# `config/mcp-runtime-versions.env` file (system toolchain binaries).
HOST_BINARY_SERVERS: dict[str, dict[str, str]] = {
    "github": {"binary": "github-mcp-server", "version_env": "GITHUB_MCP_SERVER_VERSION"},
    "dart-flutter": {"binary": "dart", "version_env": "DART_SDK_VERSION"},
}


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
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


def extract_pin(args: list[str]) -> str | None:
    """Extract the version pin from a list of stdio MCP `args`.

    Recognises three forms produced by `bunx`/`uvx`/native commands:
      1. Python-style `package==1.2.3` (uvx style).
      2. Scoped npm `@scope/name@1.2.3` (`bunx @anthropic-ai/mcp@1`).
      3. Unscoped npm `name@1.2.3` (`bunx chrome-devtools-mcp@0.26.0`).

    Returns the first matching token or `None` if none match.
    """
    for arg in args:
        if "==" in arg:
            return arg
        if NPM_PIN_RE.match(arg):
            return arg
    return None


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a simple KEY=VALUE env file. Lines starting with `#` and blank
    lines are skipped. Values are not unquoted (we own this file). Returns
    an empty dict if the file is absent."""
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def build_host_binary_pins(env_values: dict[str, str]) -> dict[str, dict[str, str | None]]:
    """Return the host-binary pin block: { server_name: {binary, version_env, version} }.

    Pulls the version string from `env_values[version_env]`. When the env file
    is missing or the key is absent, `version` is `None` so consumers can
    distinguish "no pin file" from "empty pin".
    """
    pins: dict[str, dict[str, str | None]] = {}
    for server, meta in HOST_BINARY_SERVERS.items():
        pins[server] = {
            "binary": meta["binary"],
            "version_env": meta["version_env"],
            "version": env_values.get(meta["version_env"]),
        }
    return pins


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
    mcp_servers: dict[str, dict[str, object]] = {}
    if mcp_path.is_file():
        mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
        mcp_servers = mcp.get("mcpServers", {})

    env_path = root / "config" / "mcp-runtime-versions.env"
    env_values = parse_env_file(env_path)
    host_binary_pins = build_host_binary_pins(env_values)

    plugins: list[dict[str, object]] = []
    for entry in marketplace.get("plugins", []):
        name = entry.get("name")
        source_raw = entry.get("source", "")
        source = source_raw if isinstance(source_raw, str) else ""
        version: str | None = None
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

    mcp_summary: list[dict[str, object]] = []
    for name, cfg in mcp_servers.items():
        if cfg.get("type") == "http":
            url = cfg.get("url")
            if not url:
                print(
                    f"WARN release_manifest: HTTP server {name!r} has no url in .mcp.json",
                    file=sys.stderr,
                )
            mcp_summary.append({"name": name, "transport": "http", "url": url})
            continue

        args_raw = cfg.get("args", [])
        args: list[str] = args_raw if isinstance(args_raw, list) else []
        pin = extract_pin(args)
        host_pin = host_binary_pins.get(name)
        # Integration F-3 + Security F-10 closure: surface silent-null pins
        # to stderr so operators see the gap during release builds rather
        # than ship a manifest with `"pin": null` they did not expect.
        if pin is None and host_pin is None:
            print(
                f"WARN release_manifest: server {name!r} has no extractable "
                f"npm/uvx pin in args and no host_binary_pin in "
                f"config/mcp-runtime-versions.env",
                file=sys.stderr,
            )
        elif pin is None and host_pin is not None and host_pin.get("version") is None:
            print(
                f"WARN release_manifest: host-binary server {name!r} has "
                f"version_env {host_pin.get('version_env')!r} but the env "
                f"file does not define it",
                file=sys.stderr,
            )
        entry: dict[str, object] = {
            "name": name,
            "transport": cfg.get("type", "stdio"),
            "command": cfg.get("command"),
            "pin": pin,
            "always_load": bool(cfg.get("alwaysLoad")),
        }
        if host_pin is not None:
            entry["host_binary_pin"] = host_pin
            entry["pin_source"] = "config/mcp-runtime-versions.env"
        mcp_summary.append(entry)

    head_full = git("rev-parse", "HEAD")
    head_short = head_full[:7] if head_full else ""
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}") or None

    changelog_text = read_text(root / "CHANGELOG.md")
    unreleased = extract_unreleased_section(changelog_text)

    manifest: dict[str, object] = {
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
        "host_binary_pins": host_binary_pins,
        "claude_code_min_version": env_values.get("CLAUDE_CODE_MIN_VERSION"),
        "changelog_unreleased": unreleased,
    }

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
