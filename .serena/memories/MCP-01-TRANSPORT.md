<!-- Memory Metadata
Last updated: 2026-05-16
Last commit: 9bf3c70 chore(release): cut 0.1.8 (Wave 4 R5 hardening + smoke + memory graph)
Scope: plugins/rldyour-mcps/.mcp.json, config/mcp-runtime-versions.env, scripts/check_mcp_runtime_versions.py, scripts/smoke_mcp_runtime.sh, scripts/smoke_mcp_capabilities.sh, AGENTS.md
Area: MCP
-->

# MCP-01-TRANSPORT

## Purpose

MCP transport contracts for the marketplace. `rldyour-mcps` is the only plugin allowed to own MCP server definitions.

## Source Of Truth

- `plugins/rldyour-mcps/.mcp.json`: portable MCP server definitions consumed by Claude Code.
- `config/mcp-runtime-versions.env`: pinned runtime versions and host-binary version expectations.
- `scripts/check_mcp_runtime_versions.py`: drift detector for `.mcp.json` versus env pins and host binaries.
- `scripts/smoke_mcp_runtime.sh`: startup/runtime smoke.
- `scripts/smoke_mcp_capabilities.sh`: JSON-RPC initialize + tools/list capability smoke.

## Current Behavior

- `plugins/rldyour-mcps/.mcp.json` defines 13 servers at HEAD.
- Stdio/local servers and pins:
  - `serena`: `uvx --from serena-agent==1.3.0 --python 3.13 --prerelease allow serena start-mcp-server --project-from-cwd --context=agent --enable-web-dashboard False --open-web-dashboard False`.
  - `sequential-thinking`: `bunx @modelcontextprotocol/server-sequential-thinking@2025.12.18`.
  - `playwright`: `bunx @playwright/mcp@0.0.75 --headless --caps=network,storage,testing,devtools`.
  - `chrome-devtools`: `bunx chrome-devtools-mcp@0.26.0 --headless --isolated --no-usage-statistics --no-performance-crux`.
  - `context7`: `bunx @upstash/context7-mcp@2.2.5`.
  - `semgrep`: `uvx --from semgrep==1.163.0 semgrep mcp`.
  - `shadcn`: `bunx shadcn@4.7.0 mcp`.
  - `dart-flutter`: `dart mcp-server --force-roots-fallback`.
  - `github`: `github-mcp-server stdio --toolsets=repos,issues,pull_requests,users,context`.
- HTTP servers: `deepwiki` (`https://mcp.deepwiki.com/mcp`), `grep` (`https://mcp.grep.app`), `figma` (`https://mcp.figma.com/mcp`), `openai-docs` (`https://developers.openai.com/mcp`).
- Required env for current transport: `CONTEXT7_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`.
- Required host binaries: `github-mcp-server` and `dart`.

## Contracts And Data

- All MCP server versions are pinned. Do not use `@latest` or unpinned `uvx --from` package specs.
- GitHub MCP uses local stdio `github-mcp-server` to keep the marketplace self-contained without dependence on the `api.githubcopilot.com/mcp/` HTTP endpoint. A standard GitHub PAT with `repo` + `read:org` scopes is sufficient; no Copilot subscription is required. Source: `plugins/rldyour-mcps/README.md` line 28 at HEAD.
- `serena` uses `alwaysLoad: true` and `--context=agent`; it is eagerly loaded because Serena drives project understanding and UserPromptSubmit guidance.
- Per-server `startup_timeout_sec` and `tool_timeout_sec` are not documented Claude Code `.mcp.json` keys and must not be added.
- Runtime timeout control belongs to Claude Code env vars such as `MCP_TIMEOUT` and `MCP_TOOL_TIMEOUT`.

## Invariants

- No plugin except `rldyour-mcps` may define `.mcp.json` or own MCP transport.
- Runtime pin changes must update `.mcp.json`, `config/mcp-runtime-versions.env`, docs/changelog, and validation evidence together.
- Capability smoke must classify HTTP auth failures precisely; blanket 401/403 pass is forbidden because it previously hid the GitHub Copilot entitlement failure.
- Do not log tokens, auth headers, or secret values in smoke failures.

## Cross-References

- MCP ownership and plugin boundaries: [[CORE-02-MARKETPLACE]].
- Agent tools allowlist (R4 invariant): [[CLAUDECODE-01-PLUGIN-CANON]] + [[TECHDEBT-01-NOW]] R4.
- Serena MCP transport: [[SERENA-01-MEMORY-SYNC]] (serena server, alwaysLoad, context=agent).
- Security domain (Semgrep MCP pin): [[SECURITY-01-OWASP]].
- Browser domain (Playwright/Chrome MCP): [[BROWSER-01-WORKFLOW]].
- Design domain (Figma MCP): [[DESIGN-01-WORKFLOW]].
- Research domain (Context7/DeepWiki/Grep MCP): [[EXPLORE-01-RESEARCH]].
- Runtime version policy: [[TECHDEBT-01-NOW]] R1 (runtime-version drift).

## Verification

- `python3 scripts/check_mcp_runtime_versions.py`: checks configured pins and host-binary versions.
- `bash scripts/smoke_mcp_runtime.sh`: verifies startup/runtime parse behavior.
- `bash scripts/smoke_mcp_capabilities.sh`: verifies MCP initialize and tool-list capability path.
- `bash scripts/smoke_mcp_capabilities.sh --server <name>`: focused server smoke.
