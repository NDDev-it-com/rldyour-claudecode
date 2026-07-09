# ADR-0007: MCP runtime pinning strategy

- **Status**: accepted
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd

## Context and Problem Statement

11 MCP servers (`rldyour-mcps`) span four transport types: stdio uvx
(serena), stdio bunx (sequential-thinking, context7, shadcn), managed local
wrapper (chrome-devtools), HTTP (deepwiki, grep, figma,
openai-docs), and stdio host binary (github, dart-flutter). Without
explicit pinning, `@latest` semantics can flip a server's tool surface
overnight (e.g., Serena 1.3.0 mode-selection refactor reduced the
`--context=agent` tool surface from 45 to 28 tools without breaking
backwards-incompatible field shapes).

Two source-of-truth files exist intentionally:
1. `plugins/rldyour-mcps/.mcp.json` - what Claude Code actually launches.
2. `config/mcp-runtime-versions.env` - portable companion read by scripts
   and CI without parsing JSON.

Drift between these files is a real risk class (audit F-SYNC-01 originally
flagged that dart-flutter was in `.mcp.json` but not in the env file or
the checker before the host-binary rule closed that gap).

Evidence: `plugins/rldyour-mcps/.mcp.json:1-101`,
`config/mcp-runtime-versions.env`, `scripts/check_mcp_runtime_versions.py`
SERVER_TO_ENV + HTTP_TO_ENV + SYSTEM_BINARY_TO_ENV.

## Decision Drivers

- Reproducibility: same versions across local + CI + downstream.
- Drift detection: structural validator catches mismatch on PR.
- Host binary versions verifiable at runtime (`--version` probe).

## Considered Options

- A: Manifest-only pins. Scripts must parse JSON to read versions.
- B: Env-only pins. `.mcp.json` becomes opaque to humans browsing the
  manifest.
- C: Both, with structural parity validator. Two source-of-truth files,
  hard-fail on drift.

## Decision Outcome

Chosen option: **C**. Pinning rules:

- **stdio uvx**: `==X.Y.Z` (e.g. `--from serena-agent==1.5.3`).
- **stdio bunx**: `@X.Y.Z` for registry-launched MCP runtimes.
- **managed browser wrapper**: exact `/bin/sh -c` invocation of
  `$HOME/.local/bin/chrome-devtools-mcp`; the runtime version pin remains in
  `config/mcp-runtime-versions.env`, while bootstrap owns CloakBrowser identity,
  the fixed endpoint, and health checks.
- **HTTP**: pinned by exact URL only (`https://mcp.deepwiki.com/mcp`).
- **Host binary** (github, dart-flutter): version literal in
  `config/mcp-runtime-versions.env` only (the manifest carries no version);
  enforced at runtime via `<binary> --version` probe in
  `check_mcp_runtime_versions.py` SYSTEM_BINARY_TO_ENV.

The `HOST_BINARY_ALLOWLIST = {github, dart-flutter}` in
`scripts/smoke_mcp_runtime.sh` is the explicit list of servers permitted
to lack an args-embedded version literal; pin=None for any other server
FAILs the smoke (F-TEST-02 closure).

Bumps must touch both files in the same commit; the checker fails on
drift. Capability smoke (`scripts/smoke_mcp_capabilities.sh --server <name>`)
must be run after a bump.

### Consequences

- Good: all 11 active MCP servers are enforceable; browser flow automation
  remains outside MCP through Webwright and Playwright CLI.
- Good: env file readable by humans + scripts without JSON parsing.
- Good: pin=None silently passing is structurally prevented.
- Bad: bumps require two-file edits. Mitigation: project rule documented
  in docs/dependency-updates.md update workflow section.

## Confirmation

- `python3 scripts/check_mcp_runtime_versions.py` reports OK for all 11
  active MCP servers (5 stdio + 4 HTTP + 2 host binaries).
- `bash scripts/smoke_mcp_runtime.sh` exits non-zero on any pin=None
  outside HOST_BINARY_ALLOWLIST.
- `bash scripts/smoke_mcp_capabilities.sh --server <name>` performs MCP
  `initialize` + `tools/list` per server.
- `python3 scripts/probe_mcp_upstream.py` (G11 addition) checks weekly
  for upstream drift via npm / PyPI / Homebrew JSON.

## More Information

- Related: ADR-0005 (github local stdio), ADR-0008 (CI baseline).
