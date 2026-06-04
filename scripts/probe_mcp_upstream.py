#!/usr/bin/env python3
"""probe_mcp_upstream.py - probe upstream registries for MCP server updates.

Compares config/mcp-runtime-versions.env against:
- npm registry for bunx servers (sequential-thinking, playwright, chrome-devtools,
  context7, shadcn)
- PyPI JSON for uvx-installed packages (serena-agent)
- Homebrew formula JSON for system binaries (github-mcp-server)

Each probe is best-effort: a network failure is reported as INFO, not FAIL.
The script exits 0 always; output is consumed by the dependency-check.yml
workflow to surface drift in the job log via `::warning::`.

Closes audit F-SYNC-02 (docs claimed upstream monitoring but config only
detected local drift).
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

NPM_REGISTRY = "https://registry.npmjs.org"
PYPI = "https://pypi.org/pypi"
HOMEBREW = "https://formulae.brew.sh/api/formula"

# Maps env var -> (registry, package identifier).
PROBES: tuple[tuple[str, str, str], ...] = (
    ("SERENA_AGENT_VERSION", "pypi", "serena-agent"),
    ("SEQUENTIAL_THINKING_MCP_VERSION", "npm", "@modelcontextprotocol/server-sequential-thinking"),
    ("PLAYWRIGHT_MCP_VERSION", "npm", "@playwright/mcp"),
    ("CHROME_DEVTOOLS_MCP_VERSION", "npm", "chrome-devtools-mcp"),
    ("CONTEXT7_MCP_VERSION", "npm", "@upstash/context7-mcp"),
    ("SHADCN_VERSION", "npm", "shadcn"),
    ("GITHUB_MCP_SERVER_VERSION", "brew", "github-mcp-server"),
    # Dart SDK ships the `dart mcp-server` host binary; track latest stable
    # from the official Dart archive so weekly drift checks notify on new
    # 3.x.y releases (host binary needs `brew upgrade dart` or equivalent
    # SDK update, then bump DART_SDK_VERSION in config/mcp-runtime-versions.env).
    ("DART_SDK_VERSION", "dart-stable", "dart"),
)


def load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip()
    return out


def fetch_json(url: str, timeout: float = 10.0) -> dict[str, object] | None:
    # Hard scheme guard: urllib supports file:// and other local schemes by
    # default. All URLs in this script are constructed from hardcoded
    # NPM_REGISTRY/PYPI/HOMEBREW base strings + hardcoded package names, but the
    # static guard documents the intent and prevents future contributors from
    # accidentally accepting a file:// URL through the same code path.
    if not url.startswith(("https://", "http://")):
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rldyour-mcp-upstream-probe"})
        # nosem: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None


def latest_npm(package: str) -> str | None:
    data = fetch_json(f"{NPM_REGISTRY}/{package}/latest")
    if data is None:
        return None
    version = data.get("version")
    return str(version) if isinstance(version, str) else None


def latest_pypi(package: str) -> str | None:
    data = fetch_json(f"{PYPI}/{package}/json")
    if data is None:
        return None
    info = data.get("info", {})
    if isinstance(info, dict):
        version = info.get("version")
        return str(version) if isinstance(version, str) else None
    return None


def latest_brew(formula: str) -> str | None:
    data = fetch_json(f"{HOMEBREW}/{formula}.json")
    if data is None:
        return None
    versions = data.get("versions", {})
    if isinstance(versions, dict):
        stable = versions.get("stable")
        return str(stable) if isinstance(stable, str) else None
    return None


def latest_dart_stable(package: str) -> str | None:
    """Latest Dart SDK stable release per https://storage.googleapis.com/dart-archive/.

    The `package` argument keeps the registry function signature uniform with
    the npm/pypi/brew probes; only the literal value "dart" is supported.
    """
    if package != "dart":
        return None
    data = fetch_json(
        "https://storage.googleapis.com/dart-archive/channels/stable/release/latest/VERSION"
    )
    if data is None:
        return None
    version = data.get("version")
    return str(version) if isinstance(version, str) else None


def normalize(version: str) -> str:
    return version.lstrip("v").strip()


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    env_path = root / "config" / "mcp-runtime-versions.env"
    if not env_path.is_file():
        print(f"FAIL {env_path} missing", file=sys.stderr)
        return 0
    env = load_env(env_path)

    drift = 0
    checked = 0
    for env_key, registry, package in PROBES:
        pinned = env.get(env_key)
        if not pinned:
            print(f"SKIP {env_key}: not in env file")
            continue
        checked += 1
        if registry == "npm":
            latest = latest_npm(package)
        elif registry == "pypi":
            latest = latest_pypi(package)
        elif registry == "brew":
            latest = latest_brew(package)
        elif registry == "dart-stable":
            latest = latest_dart_stable(package)
        else:
            print(f"SKIP {env_key}: unknown registry {registry!r}")
            continue

        if latest is None:
            print(f"INFO {env_key} ({package}): upstream probe unreachable (network/timeout)")
            continue
        if normalize(latest) == normalize(pinned):
            print(f"OK   {env_key}: pinned={pinned} == latest={latest}")
        else:
            print(f"DRIFT {env_key} ({package}): pinned={pinned}, latest={latest}")
            drift += 1

    print(f"\nProbed {checked} upstreams; {drift} drift(s) detected.")
    if drift > 0:
        print(f"::warning::Probed {checked} MCP upstreams; {drift} drift(s) detected. See job log for details.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
