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
| `GITHUB_PERSONAL_ACCESS_TOKEN` | `plugins/rldyour-mcps/.mcp.json` `github.env` | PAT consumed by the local `github-mcp-server stdio` binary. | GitHub Settings -> Developer settings -> PAT. No Copilot subscription required. See PAT scope guidance below. |

### PAT scope guidance

Two PAT types are supported by `github-mcp-server`:

**Fine-grained PAT (recommended for least privilege)** - pick only the resources
the MCP server actually touches. For `--toolsets=repos,issues,pull_requests,users,context`
the minimum is:
- Repository permissions: `Contents: Read & write`, `Issues: Read & write`,
  `Pull requests: Read & write`, `Metadata: Read-only`, `Commit statuses: Read-only`.
- Account permissions: `Read access to user email` (optional, for user lookups).
- Resource scope: select only the repositories the MCP needs (private + public
  it should be able to operate on); avoid "all repositories" unless required.

**Classic PAT (legacy, broader scope)** - if fine-grained PAT is not viable
(some org policies still require classic), use `repo` + `read:org`. Caveat:
`repo` includes `workflow` and PR write across **all** repositories the user
can access, which is wider than fine-grained equivalents. Prefer fine-grained.

Rotate the PAT at least every 90 days. Never commit it to git; the repo
`.gitignore` blocks `.env`, `.env.*`, `*.pem`, `*.key` already.

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
| `RLDYOUR_SKIP_STOP_GATES` | registered Flow Stop dispatcher | Skip the dispatcher and all child Stop gates. |
| `RLDYOUR_SKIP_FLOW_SYNC` | Flow Stop child gate | Skip flow post-task child gate only. |
| `RLDYOUR_SKIP_SERENA_SYNC` | Serena memory child gate | Skip Serena memory child gate only. |
| `RLDYOUR_FORCE_BOOTSTRAP` | `scripts/bootstrap_check.sh` | Bypass agent-only divergence guard before `--bootstrap-init`. Audit-trailed in `.serena/.bootstrap_overrides.log`. |
| `RLDYOUR_SKIP_USER_PROMPT_HINT` | rldyour-serena-mcp UserPromptSubmit | Skip Serena-first context injection (parity with other rldyour skip flags). |

### Why `RLDYOUR_SKIP_ENV_CHECK` is intentionally absent

`scripts/bootstrap_check.sh` enforces `CONTEXT7_API_KEY` and
`GITHUB_PERSONAL_ACCESS_TOKEN` as **mandatory** for any session because
`plugins/rldyour-mcps/.mcp.json` references them via `${VAR}` (no fallback)
and Claude Code aborts config parse when they are unset. A bypass flag
would let the operator skip the check, but the downstream failure mode
(MCP servers refusing to start with confusing error messages) is worse
than the upfront block. Fix the env, not the check. (Verification F-5 closure.)

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
