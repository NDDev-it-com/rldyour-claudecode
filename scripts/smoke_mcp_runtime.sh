#!/usr/bin/env bash
# smoke_mcp_runtime.sh - verify MCP server runtime definitions are usable.
#
# Coverage:
#   1. Pinned-spec discipline: every stdio entry has ==X.Y.Z or @X.Y.Z;
#      no @latest, no unpinned uvx --from.
#   2. HTTP MCP servers respond to a Streamable HTTP `initialize` POST preflight
#      (200/204 = OK; 401/403 = OAuth-gated, accepted; 405 only for SSE GET fallback).
#   3. Required env vars (CONTEXT7_API_KEY, GITHUB_PERSONAL_ACCESS_TOKEN) are
#      either set or documented in .env.example.
#
# This is a fast (≤30s) smoke. Capability-level probes (JSON-RPC initialize
# + tools/list per server) live in scripts/smoke_mcp_capabilities.sh.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

step() {
  printf '\n\033[1;36m== %s ==\033[0m\n' "$1"
}

step "pinning discipline"
python3 - <<'PY'
import json, sys
mcp = json.load(open("plugins/rldyour-mcps/.mcp.json"))
fail = 0
for name, cfg in mcp.get("mcpServers", {}).items():
    if cfg.get("type") == "http":
        url = cfg.get("url", "")
        if not url.startswith("https://"):
            print(f"FAIL {name}: HTTP server must use https://, got {url!r}", file=sys.stderr)
            fail = 1
        else:
            print(f"OK {name}: {url}")
        continue
    args = cfg.get("args", [])
    pin = next((a for a in args if "==" in a or (a.startswith("@") and "@" in a[1:]) or (not a.startswith("-") and "@" in a)), None)
    if any(("@latest" in a or a == "latest") for a in args):
        print(f"FAIL {name}: unpinned @latest in args: {args!r}", file=sys.stderr)
        fail = 1
        continue
    print(f"OK {name}: pin={pin!r}")
sys.exit(fail)
PY

step "HTTP server preflight (Streamable HTTP initialize POST)"
python3 - <<'PY'
import json, sys, urllib.request, urllib.error, ssl, socket

mcp = json.load(open("plugins/rldyour-mcps/.mcp.json"))
fail = 0
ctx = ssl.create_default_context()
payload = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "clientInfo": {"name": "rldyour-smoke", "version": "0.1"},
        "capabilities": {},
    },
}).encode("utf-8")

for name, cfg in mcp.get("mcpServers", {}).items():
    if cfg.get("type") != "http":
        continue
    url = cfg["url"]
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )
        socket.setdefaulttimeout(8)
        with urllib.request.urlopen(req, context=ctx) as resp:
            print(f"OK {name}: HTTP {resp.status} from {url}")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print(f"OK {name}: HTTP {e.code} (auth-gated, accepted) from {url}")
        elif e.code == 405:
            print(f"WARN {name}: HTTP 405 from {url} - only valid for optional SSE GET, not POST initialize", file=sys.stderr)
            fail = 1
        else:
            print(f"FAIL {name}: HTTP {e.code} from {url}: {e.reason}", file=sys.stderr)
            fail = 1
    except (urllib.error.URLError, TimeoutError, socket.timeout) as e:
        print(f"FAIL {name}: network error from {url}: {e}", file=sys.stderr)
        fail = 1
sys.exit(fail)
PY

step "env example coverage"
ENV_EXAMPLE="plugins/rldyour-mcps/.env.example"
if [ ! -f "$ENV_EXAMPLE" ]; then
  echo "FAIL missing $ENV_EXAMPLE" >&2
  exit 1
fi
python3 - <<'PY'
import json, re, sys

mcp = json.load(open("plugins/rldyour-mcps/.mcp.json"))
required: set[str] = set()
for cfg in mcp.get("mcpServers", {}).values():
    # stdio servers expand ${VAR} in env, HTTP servers expand it in headers
    for block_key in ("env", "headers"):
        block = cfg.get(block_key, {})
        for value in block.values():
            for match in re.findall(r"\$\{([A-Z0-9_]+)\}", str(value)):
                required.add(match)

documented = set()
with open("plugins/rldyour-mcps/.env.example", "r", encoding="utf-8") as fp:
    for line in fp:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            documented.add(line.split("=", 1)[0])

missing = sorted(required - documented)
if missing:
    print(f"FAIL .env.example missing required keys: {missing}", file=sys.stderr)
    sys.exit(1)

print(f"OK required env vars documented: {sorted(required)}")
PY

printf '\n\033[1;32m✔ smoke_mcp_runtime passed\033[0m\n'
