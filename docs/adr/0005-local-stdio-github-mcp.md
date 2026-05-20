# ADR-0005: Local stdio GitHub MCP server

- **Status**: accepted
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd

## Context and Problem Statement

Claude Code's official MCP docs recommend the hosted GitHub Copilot MCP
endpoint `api.githubcopilot.com/mcp/` for GitHub integration. That endpoint
is gated by a Copilot subscription entitlement and returns
`HTTP 403 "unauthorized: not authorized to use this Copilot feature"`
during `initialize` for any non-Copilot account, including standard GitHub
plans without Copilot.

The maintainer's GitHub plan does not include Copilot. The hosted endpoint
is unusable. The MCP transport is needed for repos / issues / PRs / users /
context tools across all SDLC workflows.

Evidence: `plugins/rldyour-mcps/.mcp.json` github entry (lines 90-98),
`plugins/rldyour-mcps/README.md`, `config/mcp-runtime-versions.env`
GITHUB_MCP_SERVER_VERSION pin.

## Decision Drivers

- Maintainer plan: standard GitHub, no Copilot.
- All SDLC commands (ry-start, ry-review, ry-deploy, ry-init) need
  GitHub integration.
- No third-party Copilot proxy acceptable (introduces another dependency).

## Considered Options

- A: Drop GitHub MCP entirely. Loses repos/issues/PRs visibility.
- B: Use hosted `api.githubcopilot.com/mcp/`. Returns 403 for our plan.
- C: Use local stdio `github-mcp-server` (Homebrew bottle). Works with a
  standard PAT (`repo` + `read:org` scopes); no Copilot required.

## Decision Outcome

Chosen option: **C**. `.mcp.json` registers:

```jsonc
"github": {
  "command": "github-mcp-server",
  "args": ["stdio", "--toolsets=repos,issues,pull_requests,users,context"],
  "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}" }
}
```

The host binary is pinned via `GITHUB_MCP_SERVER_VERSION=1.0.5` in
`config/mcp-runtime-versions.env` and verified at runtime via
`scripts/check_mcp_runtime_versions.py` (probes `github-mcp-server --version`
and parses `Version:\s+(\S+)`).

### Consequences

- Good: works on any GitHub plan with a standard PAT.
- Good: pinned host binary version; drift detected by checker.
- Good: stdio transport keeps the data path local (no HTTP proxy).
- Bad: each contributor must install the binary
  (`brew install github-mcp-server` on macOS/Linux). Mitigation:
  `scripts/install-rldyour-marketplace.sh` and the bootstrap docs call
  this out; `check_mcp_runtime_versions.py` prints a remediation hint
  when the binary is absent.
- Bad: diverges from the Anthropic-suggested hosted endpoint; future
  Anthropic docs updates may not match our configuration. Mitigation:
  document the rationale here so future contributors do not "fix" us back
  to the hosted endpoint.

## Confirmation

- `python3 scripts/check_mcp_runtime_versions.py` includes a `github`
  SYSTEM_BINARY_TO_ENV entry that probes `github-mcp-server --version`.
- `bash scripts/smoke_mcp_capabilities.sh --server github` performs the
  full MCP `initialize` + `tools/list` handshake and confirms a non-empty
  tool set.

## More Information

- Upstream binary: https://github.com/github/github-mcp-server
- Related: ADR-0007 (MCP runtime pinning), ADR-0006 (mcp-owner boundary).
