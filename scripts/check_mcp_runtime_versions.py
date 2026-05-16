#!/usr/bin/env python3
"""check_mcp_runtime_versions.py - detect drift between .mcp.json and config/mcp-runtime-versions.env.

The canonical pinning lives inside `plugins/rldyour-mcps/.mcp.json`. The env
file `config/mcp-runtime-versions.env` is a portable companion that humans and
CI scripts read when they need to query versions without parsing JSON. This
checker enforces parity: every stdio MCP server must have its version pin
mirrored in the env file with the matching value, and every env entry must
reference a real server in `.mcp.json`.

Exit codes: 0 success, 1 on any drift.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


# Map between server name in .mcp.json and the env variable that should pin it.
SERVER_TO_ENV = {
    "serena": ("SERENA_AGENT_VERSION", "serena-agent=="),
    "sequential-thinking": ("SEQUENTIAL_THINKING_MCP_VERSION", "@modelcontextprotocol/server-sequential-thinking@"),
    "playwright": ("PLAYWRIGHT_MCP_VERSION", "@playwright/mcp@"),
    "chrome-devtools": ("CHROME_DEVTOOLS_MCP_VERSION", "chrome-devtools-mcp@"),
    "context7": ("CONTEXT7_MCP_VERSION", "@upstash/context7-mcp@"),
    "semgrep": ("SEMGREP_VERSION", "semgrep=="),
    "shadcn": ("SHADCN_VERSION", "shadcn@"),
}

HTTP_TO_ENV = {
    "deepwiki": "DEEPWIKI_MCP_URL",
    "grep": "GREP_MCP_URL",
    "figma": "FIGMA_MCP_URL",
    "openai-docs": "OPENAI_DOCS_MCP_URL",
}

# Host-binary MCP servers: command must match `binary`, version is probed via
# `<binary> --version` and parsed against `version_regex` (first capture group).
# Used for github-mcp-server (Homebrew bottle) where .mcp.json args carry no
# version literal.
SYSTEM_BINARY_TO_ENV = {
    "github": {
        "env_key": "GITHUB_MCP_SERVER_VERSION",
        "binary": "github-mcp-server",
        "version_regex": r"Version:\s*(\S+)",
    },
}


def probe_binary_version(binary: str, regex: str) -> str | None:
    """Run `<binary> --version` and extract the version with the given regex."""
    path = shutil.which(binary)
    if not path:
        return None
    try:
        proc = subprocess.run(
            [path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    blob = (proc.stdout or "") + (proc.stderr or "")
    match = re.search(regex, blob)
    return match.group(1) if match else None


def load_env(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip()
    return out


def extract_version(args: list[str], prefix: str) -> str | None:
    """Find the first arg containing prefix and return everything after it."""
    for arg in args:
        if prefix in arg:
            return arg.split(prefix, 1)[1]
    return None


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    mcp_path = root / "plugins" / "rldyour-mcps" / ".mcp.json"
    env_path = root / "config" / "mcp-runtime-versions.env"

    if not mcp_path.is_file():
        print(f"FAIL missing {mcp_path}", file=sys.stderr)
        return 1
    if not env_path.is_file():
        print(f"FAIL missing {env_path}", file=sys.stderr)
        return 1

    mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
    servers = mcp.get("mcpServers", {})
    env = load_env(env_path)

    fail = 0

    for name, (env_key, prefix) in SERVER_TO_ENV.items():
        cfg = servers.get(name)
        if not cfg:
            print(f"FAIL .mcp.json missing server {name!r} (referenced in env mapping)", file=sys.stderr)
            fail = 1
            continue
        args = cfg.get("args", [])
        actual = extract_version(args, prefix)
        if not actual:
            print(f"FAIL {name}: cannot find version pin {prefix!r} in .mcp.json args", file=sys.stderr)
            fail = 1
            continue
        expected = env.get(env_key, "")
        if not expected:
            print(f"FAIL {env_path.name} missing {env_key} (server {name})", file=sys.stderr)
            fail = 1
            continue
        if actual != expected:
            print(
                f"FAIL {name}: drift detected - .mcp.json pins {actual!r}, "
                f"{env_path.name} pins {env_key}={expected!r}",
                file=sys.stderr,
            )
            fail = 1
            continue
        print(f"OK {name}: {actual}")

    for name, env_key in HTTP_TO_ENV.items():
        cfg = servers.get(name)
        if not cfg:
            print(f"FAIL .mcp.json missing http server {name!r}", file=sys.stderr)
            fail = 1
            continue
        if cfg.get("type") != "http":
            print(f"FAIL {name}: expected type=http in .mcp.json", file=sys.stderr)
            fail = 1
            continue
        actual_url = cfg.get("url", "")
        expected_url = env.get(env_key, "")
        if actual_url != expected_url:
            print(
                f"FAIL {name}: URL drift - .mcp.json={actual_url!r}, "
                f"{env_path.name} {env_key}={expected_url!r}",
                file=sys.stderr,
            )
            fail = 1
            continue
        print(f"OK {name}: {actual_url}")

    for name, spec in SYSTEM_BINARY_TO_ENV.items():
        cfg = servers.get(name)
        if not cfg:
            print(f"FAIL .mcp.json missing system-binary server {name!r}", file=sys.stderr)
            fail = 1
            continue
        actual_cmd = cfg.get("command", "")
        if actual_cmd != spec["binary"]:
            print(
                f"FAIL {name}: expected command={spec['binary']!r} in .mcp.json, got {actual_cmd!r}",
                file=sys.stderr,
            )
            fail = 1
            continue
        expected = env.get(spec["env_key"], "")
        if not expected:
            print(f"FAIL {env_path.name} missing {spec['env_key']} (server {name})", file=sys.stderr)
            fail = 1
            continue
        actual = probe_binary_version(spec["binary"], spec["version_regex"])
        if actual is None:
            print(
                f"INFO {name}: binary {spec['binary']!r} absent on PATH - "
                f"pin {spec['env_key']}={expected} cannot be enforced locally"
            )
            continue
        if actual != expected:
            print(
                f"FAIL {name}: drift detected - host {spec['binary']} reports {actual!r}, "
                f"{env_path.name} pins {spec['env_key']}={expected!r}. "
                f"Run `brew upgrade {spec['binary']}` or update the env pin.",
                file=sys.stderr,
            )
            fail = 1
            continue
        print(f"OK {name}: {actual} (host binary)")

    return fail


if __name__ == "__main__":
    sys.exit(main())
