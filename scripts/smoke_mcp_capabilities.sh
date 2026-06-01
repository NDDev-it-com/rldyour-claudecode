#!/usr/bin/env bash
# smoke_mcp_capabilities.sh - capability-level MCP server smoke.
#
# Spawns each pinned MCP server (or POSTs to each HTTP endpoint), performs
# a JSON-RPC `initialize` handshake, then `tools/list`, and verifies the
# server reports at least one tool. This is a deeper smoke than
# `smoke_mcp_runtime.sh`, which only checks pin discipline and HTTP
# reachability.
#
# SKIP rules (do not FAIL the harness):
#   - stdio server in ENV_REQUIRED but the env var is absent.
#   - stdio server in BINARY_REQUIRED but the binary is not on PATH.
#   - HTTP server expects ${ENV_VAR} in headers and the var is empty (auth
#     header would resolve to empty bearer - counted as SKIP, not FAIL).
#
# HTTP auth handling (no blanket 401/403 = PASS shortcut):
#   - 200/204 + parseable initialize.result.serverInfo → OK
#   - 200/204 without serverInfo → FAIL (server is reachable but speaks the
#     wrong protocol; this is exactly the silent-misconfig we want to catch)
#   - 401 with no env-substituted auth header sent → SKIP (server reachable;
#     CI just lacks credentials)
#   - 401 with auth header sent → FAIL (token rejected - wrong scopes/expired)
#   - 403 always → FAIL with explicit message ("entitlement-denied or org
#     policy blocks the configured token") - this is the failure mode that
#     `api.githubcopilot.com/mcp/` returns for non-Copilot accounts.
#
# Optional flags:
#   --server <name>     run only this server (e.g. --server serena)
#   --timeout <secs>    per-server timeout (default 45s)
#   --skip-uvx          skip uvx-based servers (faster for CI; uvx
#                       cold-start can pull ~80 packages for serena)
#
# Exit codes: 0 success, 1 on any FAIL.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT}"

MCP_JSON="${ROOT}/plugins/rldyour-mcps/.mcp.json"

if [[ ! -f "${MCP_JSON}" ]]; then
  echo "FAIL .mcp.json not found at ${MCP_JSON}" >&2
  exit 1
fi

# Forward args verbatim to the Python helper so flag parsing stays in one place.
# ROOT and MCP_JSON are exported so the heredoc'd Python finds them
# regardless of cwd (bash __file__ does not survive `python3 -`).
export RLDYOUR_SMOKE_ROOT="${ROOT}"
export RLDYOUR_SMOKE_MCP_JSON="${MCP_JSON}"
exec python3 - "$@" <<'PY'
import json
import os
import re
import select
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(os.environ["RLDYOUR_SMOKE_ROOT"])
MCP_JSON = Path(os.environ["RLDYOUR_SMOKE_MCP_JSON"])

# Stdio servers gated by credential env vars; absent env → SKIP, not FAIL.
# HTTP servers handle their own auth via HTTP_AUTH_GATED (401/403 = pass)
# so they are NOT listed here.
ENV_REQUIRED = {
    "context7": "CONTEXT7_API_KEY",
}

# Stdio servers that depend on a system binary on PATH (no uvx/bunx
# bootstrap). Absent binary → SKIP, not FAIL - CI without that toolchain
# should not regress the harness.
BINARY_REQUIRED = {
    "dart-flutter": "dart",
}

# Servers slow to cold-start (uvx pulls ~80 packages on first run).
UVX_SERVERS = {"serena"}

# Servers that authenticate via a bearer header containing an ${ENV_VAR}
# placeholder. If the var is empty after substitution we SKIP rather than FAIL;
# the server is reachable but the harness has no token to drive a real
# handshake with. 401 with a real token still FAILs.
HTTP_AUTH_GATED = {"figma"}

DEFAULT_TIMEOUT_S = 45.0

PROTOCOL_VERSION = "2024-11-05"
CLIENT_INFO = {"name": "rldyour-smoke", "version": "1.0.0"}

ANSI_GREEN = "\033[1;32m"
ANSI_RED = "\033[1;31m"
ANSI_RESET = "\033[0m"


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
            print("smoke_mcp_capabilities.sh - see file header for usage")
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


def jsonrpc_notify(method, params=None):
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    return json.dumps(msg, ensure_ascii=False)


def read_line_with_timeout(proc, deadline):
    """Read one newline-terminated message from proc.stdout, respecting deadline.

    Uses select() on the underlying fd so a stalled server can never block us
    past the deadline (bare readline() with bufsize=1 was blocking despite the
    poll() check in the prior implementation).
    """
    if proc.stdout is None:
        return None
    fd = proc.stdout.fileno()
    buf = []
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        if proc.poll() is not None and not select_ready(fd, 0):
            # Process exited and no more bytes pending.
            return None
        ready, _, _ = select.select([fd], [], [], min(remaining, 0.5))
        if not ready:
            continue
        try:
            chunk = os.read(fd, 1)
        except OSError:
            return None
        if not chunk:
            return None  # EOF
        ch = chunk.decode("utf-8", errors="replace")
        if ch == "\n":
            return "".join(buf)
        buf.append(ch)


def select_ready(fd, timeout):
    """Non-blocking check whether fd has data ready."""
    ready, _, _ = select.select([fd], [], [], timeout)
    return bool(ready)


def smoke_stdio(name, cfg, timeout_s):
    """Spawn stdio MCP server, perform initialize + tools/list, count tools."""
    cmd = [cfg["command"]] + list(cfg.get("args", []))
    env = os.environ.copy()
    for k, v in cfg.get("env", {}).items():
        env[k] = os.path.expandvars(v)

    deadline = time.monotonic() + timeout_s

    # start_new_session=True puts the child (and any uvx-spawned grandchildren)
    # in a fresh process group so we can SIGTERM the entire group on cleanup.
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env=env,
            bufsize=0,
            start_new_session=True,
        )
    except FileNotFoundError as exc:
        return ("FAIL", f"launcher not on PATH: {exc}")

    try:
        # 1. initialize
        proc.stdin.write(
            jsonrpc_request(
                "initialize",
                1,
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": CLIENT_INFO,
                },
            )
            + "\n"
        )
        proc.stdin.flush()

        init_msg = read_json_with_id(proc, deadline, expected_id=1)
        if init_msg is None:
            return ("FAIL", "initialize: no JSON-RPC response with id=1 before deadline")
        if "error" in init_msg:
            return ("FAIL", f"initialize error: {init_msg['error']}")

        # Per MCP spec, send `notifications/initialized` before further calls.
        try:
            proc.stdin.write(jsonrpc_notify("notifications/initialized") + "\n")
            proc.stdin.flush()
        except BrokenPipeError:
            return ("FAIL", "initialize accepted but stdin pipe broke before tools/list")

        # 2. tools/list
        proc.stdin.write(jsonrpc_request("tools/list", 2, {}) + "\n")
        proc.stdin.flush()

        tools_msg = read_json_with_id(proc, deadline, expected_id=2)
        if tools_msg is None:
            return ("FAIL", "tools/list: no JSON-RPC response with id=2 before deadline")
        if "error" in tools_msg:
            return ("FAIL", f"tools/list error: {tools_msg['error']}")

        tools = tools_msg.get("result", {}).get("tools") or []
        if not tools:
            return ("FAIL", "tools/list returned zero tools")

        return ("OK", f"{len(tools)} tools")
    finally:
        cleanup_process(proc)


def read_json_with_id(proc, deadline, expected_id, max_lines=40):
    """Read up to `max_lines` JSON-RPC messages; return the one with matching id."""
    for _ in range(max_lines):
        line = read_line_with_timeout(proc, deadline)
        if line is None:
            return None
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("id") == expected_id:
            return obj
    return None


def cleanup_process(proc):
    """Best-effort termination of the child and any grandchildren in its pgid."""
    if proc.poll() is not None:
        return
    pgid = None
    try:
        pgid = os.getpgid(proc.pid)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        if pgid is not None:
            os.killpg(pgid, signal.SIGTERM)
        else:
            proc.terminate()
    except (ProcessLookupError, PermissionError):
        pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            if pgid is not None:
                os.killpg(pgid, signal.SIGKILL)
            else:
                proc.kill()
        except (ProcessLookupError, PermissionError):
            pass


def expand_headers(raw_headers):
    """Substitute ${VAR} in header values and report which vars were empty.

    Returns (expanded_dict, missing_var_names). A header keeps its slot even
    if its value substituted to empty - we want to know whether the *upstream*
    treats the request as authenticated (the empty bearer typically yields
    401), not silently drop the header and accidentally pass an unauth probe.
    """
    expanded = {}
    missing = []
    var_pattern = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")
    for k, v in raw_headers.items():
        names = var_pattern.findall(v)
        substituted = os.path.expandvars(v)
        # Detect "all referenced vars were empty" - common in CI without secrets.
        if names and all(not os.environ.get(n, "").strip() for n in names):
            missing.extend(names)
        expanded[k] = substituted
    return expanded, missing


def parse_mcp_response_body(payload, content_type):
    """Decode an MCP HTTP response body into a JSON-RPC object.

    Per MCP spec 2025-06-18 the body is either:
      - application/json: single JSON object
      - text/event-stream: SSE frames with `event: message` + `data: {...}`
    We try JSON first, then fall back to extracting the first `data:` line.
    """
    if not payload:
        return None
    text = payload.decode("utf-8", errors="replace").strip()
    if not text:
        return None
    # Plain JSON path.
    if (content_type or "").startswith("application/json") or text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    # SSE path: pick the first `data: …` line and json-decode it.
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data = line[len("data:"):].strip()
        if not data:
            continue
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            continue
    return None


def smoke_http(name, cfg, timeout_s):
    """POST initialize JSON-RPC to an HTTP MCP server endpoint.

    Verifies a real protocol handshake - the server must return a JSON-RPC
    `result.serverInfo` object, not just an HTTP 200. 401/403 are evaluated
    against whether a real auth header was actually sent.
    """
    url = cfg.get("url", "")
    if not url:
        return ("FAIL", "no url in .mcp.json")

    base_headers = cfg.get("headers", {}) or {}
    expanded_headers, missing_vars = expand_headers(base_headers)
    auth_sent = bool(expanded_headers.get("Authorization", "").replace("Bearer ", "").strip())

    if missing_vars and not auth_sent:
        return ("SKIP", f"auth headers reference unset env: {','.join(sorted(set(missing_vars)))}")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": PROTOCOL_VERSION,
    }
    headers.update(expanded_headers)

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
    content_type = ""
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            payload = resp.read(16384)
    except urllib.error.HTTPError as exc:
        status = exc.code
        content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
        try:
            payload = exc.read(16384)
        except Exception:
            payload = b""
    except Exception as exc:
        return ("FAIL", f"HTTP error: {exc}")

    if status == 401:
        if not auth_sent:
            return ("SKIP", f"HTTP 401 with no auth sent - server reachable, no credentials in env")
        return ("FAIL", f"HTTP 401 with auth sent - token rejected (check scopes/expiry)")

    if status == 403:
        return (
            "FAIL",
            "HTTP 403 - entitlement denied (token valid but account/org lacks access; "
            "for github MCP this means no Copilot allowlist - switch to stdio github-mcp-server)"
        )

    if status not in (200, 204):
        # Never echo body - it may contain upstream headers/tokens.
        return ("FAIL", f"HTTP {status} (body {len(payload)} bytes)")

    # 200/204: must parse as JSON-RPC and contain serverInfo.
    msg = parse_mcp_response_body(payload, content_type)
    if not msg:
        return ("FAIL", f"HTTP {status} but response body is not a JSON-RPC payload")
    if "error" in msg:
        return ("FAIL", f"initialize error: {msg['error']}")
    server_info = msg.get("result", {}).get("serverInfo") or {}
    server_name = server_info.get("name")
    if not server_name:
        # Some servers (figma) accept initialize but don't return serverInfo
        # until after a session id is established. Fall back to "auth-gated
        # reachable" only when we explicitly opted in.
        if name in HTTP_AUTH_GATED:
            return ("OK", f"HTTP {status} (auth-gated handshake, no serverInfo yet)")
        return ("FAIL", f"HTTP {status} but result.serverInfo missing")
    return ("OK", f"serverInfo={server_name}")


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

        transport = scfg.get("type", "stdio")

        # Skip rules apply to stdio only - HTTP auth is handled via 401/403.
        if transport != "http":
            env_key = ENV_REQUIRED.get(name)
            if env_key and not envvar_present(env_key):
                print(f"SKIP {name}: env {env_key} not set")
                skipped += 1
                continue

            bin_key = BINARY_REQUIRED.get(name)
            if bin_key and shutil.which(bin_key) is None:
                print(f"SKIP {name}: binary {bin_key!r} not on PATH")
                skipped += 1
                continue

            if skip_uvx and name in UVX_SERVERS:
                print(f"SKIP {name}: --skip-uvx")
                skipped += 1
                continue

            status, detail = smoke_stdio(name, scfg, timeout)
        else:
            status, detail = smoke_http(name, scfg, timeout)

        if status == "SKIP":
            print(f"SKIP {name}: {detail}")
            skipped += 1
            continue

        marker = f"{ANSI_GREEN}OK{ANSI_RESET}" if status == "OK" else f"{ANSI_RED}FAIL{ANSI_RESET}"
        print(f"{marker} {name}: {detail}")
        if status == "OK":
            passed += 1
        else:
            fail = 1

    banner = f"{ANSI_GREEN}✔ smoke_mcp_capabilities passed{ANSI_RESET}" if fail == 0 \
        else f"{ANSI_RED}✗ smoke_mcp_capabilities failed{ANSI_RESET}"
    print(f"\nsummary: passed={passed} skipped={skipped} fail={'yes' if fail else 'no'}")
    print(banner)
    return fail


if __name__ == "__main__":
    sys.exit(main())
PY
