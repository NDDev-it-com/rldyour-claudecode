<!-- Memory Metadata
Last updated: 2026-07-10
Last verified: 2026-07-10
Last commit: 7f74e410781fbf6937e27e5d1d07e4cadb9c7900 chore(release): publish Claude adapter 1.8.5
Scope: MCP runtime transport and pin policy
Area: MCP
-->

# MCP Transport

## Scope
MCP runtime transport and pin policy

## Current source of truth
- `path:plugins/rldyour-mcps/.mcp.json`
- `path:config/mcp-runtime-versions.env`
- `path:README.md`

## Last verified
- date: 2026-07-10
- commit: `7f74e410781fbf6937e27e5d1d07e4cadb9c7900`
- checked by: Claude adapter MCP runtime pin refresh

## Facts
- `plugins/rldyour-mcps/.mcp.json` pins Sequential Thinking MCP `2026.7.4`
  and Context7 MCP `3.2.3`; `config/mcp-runtime-versions.env` mirrors both
  values for validators and CI.
- Chrome DevTools MCP remains an exact bootstrap-owned `/bin/sh -c` wrapper
  transport through `$HOME/.local/bin/chrome-devtools-mcp`; this pin refresh
  does not change CloakBrowser ownership or permit another browser backend.

## Evidence
- `commit:7f74e410781fbf6937e27e5d1d07e4cadb9c7900`
- `path:plugins/rldyour-mcps/.mcp.json`
- `path:config/mcp-runtime-versions.env`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Applies to

- The scope and source-of-truth paths declared in this memory.

## Source of truth

- The `Current source of truth` entries above, plus current code, configuration, tests, git state, and live GitHub state where this memory references live release or repository surfaces.

## Invariants

- Current code, configuration, tests, validators, git state, and live GitHub state override this memory whenever they disagree.

## Current State

- Treat the `Facts` section as the current durable state. Do not treat historical evidence, superseded notes, or previous release entries as current.

## Do Not Infer

- Do not infer runtime versions, product versions, commits, permissions, release state, security posture, or tool behavior from this memory without checking the source of truth.

## Update Triggers

- Update after verified changes to the source-of-truth files, runtime baselines, release tuple, validation gates, live release state, or durable agent-workflow contracts.

## Validation Commands

- Run `python3 scripts/check_mcp_runtime_versions.py` for canonical/env parity
  and exact managed-wrapper enforcement.
- Run `bash scripts/smoke_mcp_capabilities.sh --server sequential-thinking`
  and the Context7 exact-package probe with credentials or an isolated
  read-only safe call.
- Run the rldyour control-plane Serena memory validators in strict mode: `validate_serena_memory_schema` (`--strict-mode strict-all`) and `validate_serena_memory_semantics` (`--strict-current-facts --strict-metadata-dates --strict-evidence-commits`).

## Repair Procedure

1. Re-read the source-of-truth files listed above.
2. Update only verified current facts; move stale facts into historical evidence.
3. Rerun the validation commands until green.
