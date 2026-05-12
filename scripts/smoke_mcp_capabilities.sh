#!/usr/bin/env bash
# smoke_mcp_capabilities.sh — capability-level MCP server smoke.
#
# Spawns each pinned MCP server (or POSTs to each HTTP endpoint), performs
# a JSON-RPC `initialize` handshake, then `tools/list`, and verifies the
# server reports at least one tool. This is a deeper smoke than
# `smoke_mcp_runtime.sh`, which only checks pin discipline and HTTP
# reachability.
#
# Stdio servers that require credentials (CONTEXT7_API_KEY, etc.) are
# skipped with a SKIP marker when the env var is absent. HTTP servers
# behind OAuth (figma, github) accept 401 as a passing handshake — the
# server is reachable; the client just lacks an authenticated session.
#
# Optional flags:
#   --server <name>     run only this server (e.g. --server serena)
#   --timeout <secs>    per-server timeout (default 45s)
#   --skip-uvx          skip uvx-based servers (faster for CI; uvx
#                       cold-start can pull ~80 packages for serena)
#
# Exit codes: 0 success, 1 on any FAIL.
#
# Required: python3, jq (jq optional — falls back to python json if absent).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP_JSON="${REPO_ROOT}/plugins/rldyour-mcps/.mcp.json"

if [[ ! -f "${MCP_JSON}" ]]; then
  echo "FAIL .mcp.json not found at ${MCP_JSON}" >&2
  exit 1
fi

# Forward args verbatim to the Python helper so flag parsing stays in one place.
# REPO_ROOT and MCP_JSON are exported so the heredoc'd Python finds them
# regardless of cwd (bash __file__ does not survive `python3 -`).
export RLDYOUR_SMOKE_REPO_ROOT="${REPO_ROOT}"
export RLDYOUR_SMOKE_MCP_JSON="${MCP_JSON}"
exec python3 - "$@" <<'PY'
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(os.environ["RLDYOUR_SMOKE_REPO_ROOT"])
MCP_JSON = Path(os.environ["RLDYOUR_SMOKE_MCP_JSON"])

# Servers that require env vars; absent env → SKIP, not FAIL.
ENV_REQUIRED = {
    "context7": "CONTEXT7_API_KEY",
    "github": "GITHUB_PERSONAL_ACCESS_TOKEN",
}

# Servers that are slow to cold-start (uvx pulls ~80 packages first time).
UVX_SERVERS = {"serena", "semgrep"}

# Servers that are auth-gated on HTTP; 401 is a passing handshake.
HTTP_AUTH_GATED = {"figma", "github"}

# Servers known to spam stderr noise on stdio startup. We log but ignore.
STDERR_NOISY = {"serena", "playwright", "chrome-devtools", "dart-flutter"}

DEFAULT_TIMEOUT_S = 45.0

PROTOCOL_VERSION = "2024-11-05"
CLIENT_INFO = {"name": "rldyour-smoke", "version": "1.0.0"}


def parse_args(argv):
    server_filter = None
    timeout = DEFAULT_TIMEOUT_S
    skip_uvx = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--server" and i + 1 < len(argv):
            server_filter = argv[i + 1]
            i += 2
            continue
        if a == "--timeout" and i + 1 < len(argv):
            timeout = float(argv[i + 1])
            i += 2
            continue
        if a == "--skip-uvx":
            skip_uvx = True
            i += 1
            continue
        if a in ("-h", "--help"):
            print(__doc__ or "smoke_mcp_capabilities.sh — see file header")
            sys.exit(0)
        print(f"unknown arg: {a!r}", file=sys.stderr)
        sys.exit(2)
    return server_filter, timeout, skip_uvx


def envvar_present(name):
    val = os.environ.get(name, "")
    return bool(val and val.strip())


def jsonrpc_request(method, rid, params=None):
    msg = {"jsonrpc": "2.0", "id": rid, "method": method}
    if params is not None:
        msg["params"] = params
    return json.dumps(msg, ensure_ascii=False)


def read_line_with_timeout(proc, deadline):
    """Read a single newline-terminated message from proc.stdout with deadline."""
    while True:
        if time.monotonic() > deadline:
            return None
        if proc.poll() is not None:
            # Process exited before producing a line.
            return None
        line = proc.stdout.readline()
        if line:
            return line.rstrip("\n")
        time.sleep(0.05)


def smoke_stdio(name, cfg, timeout_s):
    """Spawn stdio MCP server, do initialize + tools/list, count tools."""
    cmd = [cfg["command"]] + list(cfg.get("args", []))
    env = os.environ.copy()
    for k, v in cfg.get("env", {}).items():
        env[k] = os.path.expandvars(v)

    deadline = time.monotonic() + timeout_s
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=1,
        )
    except FileNotFoundError as exc:
        return ("FAIL", f"launcher not on PATH: {exc}")

    try:
        # 1. initialize
        init_req = jsonrpc_request(
            "initialize",
            1,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": CLIENT_INFO,
            },
        )
        proc.stdin.write(init_req + "\n")
        proc.stdin.flush()

        init_resp_raw = read_line_with_timeout(proc, deadline)
        if init_resp_raw is None:
            stderr_tail = ""
            try:
                proc.stderr.flush()
            except Exception:
                pass
            return ("FAIL", "initialize: no response (timeout or early exit)")

        # Tolerate non-JSON banner lines from noisy stdio servers — skip until we
        # find a valid JSON-RPC object that has a matching id.
        init_msg = None
        scan_deadline = deadline
        candidate = init_resp_raw
        for _ in range(20):
            try:
                obj = json.loads(candidate)
                if isinstance(obj, dict) and obj.get("id") == 1:
                    init_msg = obj
                    break
            except Exception:
                pass
            candidate = read_line_with_timeout(proc, scan_deadline)
            if candidate is None:
                break

        if init_msg is None:
            return ("FAIL", "initialize: did not receive a JSON-RPC response with id=1")
        if "error" in init_msg:
            return ("FAIL", f"initialize error: {init_msg['error']}")

        # Spec requires `notifications/initialized` before further calls.
        try:
            proc.stdin.write(jsonrpc_request_notify("notifications/initialized") + "\n")
            proc.stdin.flush()
        except BrokenPipeError:
            return ("FAIL", "initialize accepted but stdin pipe broke before tools/list")

        # 2. tools/list
        list_req = jsonrpc_request("tools/list", 2, {})
        proc.stdin.write(list_req + "\n")
        proc.stdin.flush()

        tools_resp_raw = read_line_with_timeout(proc, deadline)
        tools_msg = None
        for _ in range(20):
            if tools_resp_raw is None:
                break
            try:
                obj = json.loads(tools_resp_raw)
                if isinstance(obj, dict) and obj.get("id") == 2:
                    tools_msg = obj
                    break
            except Exception:
                pass
            tools_resp_raw = read_line_with_timeout(proc, deadline)

        if tools_msg is None:
            return ("FAIL", "tools/list: no JSON-RPC response with id=2")
        if "error" in tools_msg:
            return ("FAIL", f"tools/list error: {tools_msg['error']}")

        tools = tools_msg.get("result", {}).get("tools") or []
        if not tools:
            return ("FAIL", "tools/list returned zero tools")

        return ("OK", f"{len(tools)} tools")
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        except Exception:
            pass


def jsonrpc_request_notify(method, params=None):
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    return json.dumps(msg, ensure_ascii=False)


def smoke_http(name, cfg, timeout_s):
    """POST initialize JSON-RPC to an HTTP MCP server endpoint."""
    url = cfg.get("url", "")
    if not url:
        return ("FAIL", "no url in .mcp.json")

    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    for k, v in cfg.get("headers", {}).items():
        headers[k] = os.path.expandvars(v)

    body = jsonrpc_request(
        "initialize",
        1,
        {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": CLIENT_INFO,
        },
    ).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            status = resp.status
            payload = resp.read(8192)
    except urllib.error.HTTPError as exc:
        status = exc.code
        try:
            payload = exc.read(8192)
        except Exception:
            payload = b""
    except Exception as exc:
        return ("FAIL", f"HTTP error: {exc}")

    if status in (200, 204):
        return ("OK", f"HTTP {status}")
    if status in (401, 403) and name in HTTP_AUTH_GATED:
        return ("OK", f"HTTP {status} (auth-gated, accepted)")
    return ("FAIL", f"HTTP {status}; body[:200]={payload[:200]!r}")


def main():
    server_filter, timeout, skip_uvx = parse_args(sys.argv[1:])

    cfg = json.loads(MCP_JSON.read_text(encoding="utf-8"))
    servers = cfg.get("mcpServers", {})

    fail = 0
    skipped = 0
    passed = 0

    print(f"smoke_mcp_capabilities: timeout={timeout:.0f}s, servers={len(servers)}")
    for name, scfg in servers.items():
        if server_filter and server_filter != name:
            continue

        # Skip stdio servers gated on env we don't have.
        env_key = ENV_REQUIRED.get(name)
        if env_key and not envvar_present(env_key):
            print(f"SKIP {name}: env {env_key} not set")
            skipped += 1
            continue

        if skip_uvx and name in UVX_SERVERS:
            print(f"SKIP {name}: --skip-uvx")
            skipped += 1
            continue

        transport = scfg.get("type", "stdio")
        if transport == "http":
            status, detail = smoke_http(name, scfg, timeout)
        else:
            status, detail = smoke_stdio(name, scfg, timeout)

        marker = "\033[1;32mOK\033[0m" if status == "OK" else "\033[1;31mFAIL\033[0m"
        print(f"{marker} {name}: {detail}")
        if status == "OK":
            passed += 1
        else:
            fail = 1

    print(f"\nsummary: passed={passed} fail={fail and 'yes' or 'no'} skipped={skipped}")
    return fail


if __name__ == "__main__":
    sys.exit(main())
PY
