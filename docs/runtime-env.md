# Runtime Environment Variables

`plugins/rldyour-mcps/.mcp.json` and several scripts reference environment
variables through `${VAR}` expansion. Claude Code aborts MCP config parse
when a referenced variable is unset and has no `${VAR:-default}` fallback,
so missing secrets fail at session start rather than silently degrading.

## Required (fail-fast)

These two variables are mandatory. `scripts/bootstrap_check.sh` FAILs when
either is unset.

| Variable | Used by | Purpose | Where to obtain |
| --- | --- | --- | --- |
| `CONTEXT7_API_KEY` | `plugins/rldyour-mcps/.mcp.json` `context7.env` | API key for the Upstash Context7 MCP server (`@upstash/context7-mcp`). | https://context7.com (dashboard -> API keys) |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | `plugins/rldyour-mcps/.mcp.json` `github.env` | PAT consumed by the local `github-mcp-server stdio` binary. | GitHub Settings -> Developer settings -> PAT (classic). Scopes: `repo` + `read:org`. No Copilot subscription required. |

## Optional Claude Code MCP knobs

These are env-only knobs documented in Claude Code MCP docs and intentionally
not part of `.mcp.json` schema:

| Variable | Effect |
| --- | --- |
| `MCP_TIMEOUT` | Milliseconds. Server-startup timeout for all MCP servers. |
| `MCP_TOOL_TIMEOUT` | Milliseconds. Per-tool-call timeout for HTTP/SSE MCP servers (v2.1.142+ fixes this for the HTTP transport too). |
| `MCP_CONNECTION_NONBLOCKING` | `1` to let the session start without waiting for slow MCP servers. |

## Skip flags for development hooks

These are NOT secrets but rldyour-flow / rldyour-serena-mcp lifecycle hooks
read them when present. Leaving them unset is the production default.

| Variable | Hook | Effect when `=1` |
| --- | --- | --- |
| `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT` | rldyour-flow SessionStart context | Skip session-start context advisory. |
| `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP` | rldyour-flow SessionStart worktree bootstrap | Skip auto-restore of agent-only files in a fresh worktree. |
| `RLDYOUR_SKIP_FLOW_COMMIT_ADVICE` | rldyour-flow PostToolUse:Bash | Skip commit-subject advisory check. |
| `RLDYOUR_SKIP_STOP_GATES` | both Stop hooks | Skip Serena memory + flow post-task Stop gates. |
| `RLDYOUR_SKIP_FLOW_SYNC` | rldyour-flow Stop | Skip flow Stop gate only (Serena Stop still runs). |
| `RLDYOUR_SKIP_SERENA_SYNC` | rldyour-serena-mcp Stop | Skip Serena memory Stop gate only (flow Stop still runs). |
| `RLDYOUR_FORCE_BOOTSTRAP` | `scripts/bootstrap_check.sh` | Bypass agent-only divergence guard before `--bootstrap-init`. Audit-trailed in `.serena/.bootstrap_overrides.log`. |

## Setup procedure

1. Copy `plugins/rldyour-mcps/.env.example` to your shell profile / `.env`
   file consumed before launching Claude Code.
2. Set `CONTEXT7_API_KEY` and `GITHUB_PERSONAL_ACCESS_TOKEN`.
3. Run `bash scripts/bootstrap_check.sh` once to verify the environment
   plus all other bootstrap invariants.
4. Launch `claude` from the repository root.

## Threat model notes

- Never commit `.env` or any file containing real tokens to git. The
  repository `.gitignore` already excludes `.env`, `.env.*`, `*.pem`,
  `*.key`, and similar credential file patterns.
- `RLDYOUR_FORCE_BOOTSTRAP=1` writes an audit-trail entry to
  `.serena/.bootstrap_overrides.log` (gitignored). Investigate that file
  if memory edits are unexpectedly reverted.
- The github PAT is the only authentication for the local stdio GitHub
  MCP server. Use a least-privilege PAT (no `admin:*`, no `delete_*`).
