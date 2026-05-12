# Dependency Updates

Policy and procedure for updating MCP runtime pins and Claude Code minimum version.

## Sources of truth

- `plugins/rldyour-mcps/.mcp.json` — primary runtime pinning consumed by Claude Code.
- `config/mcp-runtime-versions.env` — companion env file for scripts and CI; mirrors `.mcp.json` pins.
- `scripts/check_mcp_runtime_versions.py` — enforces parity between the two.
- `.github/workflows/dependency-check.yml` — scheduled (Mondays 06:00 UTC) drift check + manual via `workflow_dispatch`.

## Pinning rules (hard)

- **stdio servers**: pin with `==X.Y.Z` (uvx) or `@X.Y.Z` (bunx).
- **HTTP servers**: pin by exact URL — there is no version field.
- **No `@latest`, no unpinned `uvx --from`** specs. CI rejects them.
- Update intentionally — pin bump must be paired with `scripts/smoke_mcp_capabilities.sh` (or `--server <name>` for a targeted probe). The harness spawns each server, does the JSON-RPC `initialize` handshake, then `tools/list`, and verifies a non-empty tool set.

## Update workflow

1. **Check upstream releases** — Mondays automatically, otherwise `workflow_dispatch` the dependency-check workflow or run locally:

   ```bash
   python3 scripts/check_mcp_runtime_versions.py
   # Optionally probe upstream:
   uvx serena-agent --version
   bunx @upstash/context7-mcp@latest --version
   ```

2. **Read release notes** for the upstream — known breaking changes, removed tools, new auth requirements.

3. **Update both pins** — in the same commit, edit `.mcp.json` and `config/mcp-runtime-versions.env`. Drift between them is a CI failure.

4. **Run capability smoke** for the affected server:

   ```bash
   scripts/smoke_mcp_capabilities.sh --server <name>           # targeted probe
   scripts/smoke_mcp_capabilities.sh --timeout 120             # full sweep (uvx cold-starts up to ~2m on first run)
   scripts/smoke_mcp_capabilities.sh --skip-uvx                # fast subset (skips serena, semgrep)
   ```

   The harness performs JSON-RPC `initialize` + `tools/list` against each server (stdio spawn or HTTP POST), verifies a non-empty tool set, and reports `OK <n> tools` per server. HTTP servers behind OAuth (figma, github) accept 401/403 as a passing handshake. Restart Claude Code after the bump to invoke at least one read-only tool live (e.g. `mcp__plugin_rldyour-mcps_context7__resolve-library-id`) before merging.

5. **Update CHANGELOG** under `[Unreleased] / Changed` — list each updated server and the new pin.

6. **Commit** with conventional format:

   ```
   chore(mcps): bump <server> from <old> to <new>

   - Release notes: <link>
   - Capability smoke: passed
   ```

7. **Validate** before push: `scripts/validate_marketplace.sh`.

## Claude Code CLI minimum version

- Lives in `config/mcp-runtime-versions.env` as `CLAUDE_CODE_MIN_VERSION`.
- Currently `2.1.111` (for `model: opus[1m]` bracketed syntax).
- Bump only when a hard requirement appears (new manifest field, new hook event, new frontmatter field that we use). Bumping forces all consumers to upgrade — be deliberate.

## What CI checks

`.github/workflows/dependency-check.yml` runs three jobs on schedule + on PRs touching `.mcp.json` / `config/mcp-runtime-versions.env`:

1. `check_mcp_runtime_versions.py` — drift between the two sources of truth.
2. Unpinned-spec scan — fails if any `@latest` or unpinned `uvx --from` appears.
3. `validate_plugin_versions.py` — marketplace ↔ plugin.json version parity.

`.github/workflows/validate.yml` already runs `check_mcp_runtime_versions.py` on every push/PR for fast feedback.

## Adding a new MCP server

When introducing a new MCP server to `rldyour-mcps`:

1. Pin it in `.mcp.json` using stdio `==X.Y.Z` or HTTP URL form.
2. Add a corresponding entry in `config/mcp-runtime-versions.env` and update `SERVER_TO_ENV` / `HTTP_TO_ENV` mappings in `scripts/check_mcp_runtime_versions.py`.
3. Document the server (purpose, env requirements, special flags) in `plugins/rldyour-mcps/README.md` and `AGENTS.md` MCP transport section.
4. Add a capability smoke probe in `scripts/smoke_mcp_capabilities.sh` only if the server needs special handling beyond `initialize` + `tools/list` (e.g. credentials required → add to `ENV_REQUIRED`; auth-gated HTTP → add to `HTTP_AUTH_GATED`; slow cold-start → add to `UVX_SERVERS`). The base handshake works for every spec-conformant MCP server without code changes.
5. Mention in CHANGELOG under `[Unreleased] / Added`.
6. If any plugin's skills should pre-approve the new server's tools, add `mcp__plugin_rldyour-mcps_<server>__*` to the relevant `allowed-tools` lists.

## Removing an MCP server

Reverse the additions: remove from `.mcp.json`, env file, mapping dictionaries, README, AGENTS.md, capability smoke, and any `allowed-tools`. Note removal in CHANGELOG under `[Unreleased] / Removed`.
