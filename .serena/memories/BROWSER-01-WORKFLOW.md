<!-- Memory Metadata
Last updated: 2026-07-10
Last verified: 2026-07-10
Last commit: 9e6d4bf2d6287762c9cbdba4a8357cd071e51978 ci(deps): repin reusable workflows to 0.5.1
Scope: browser-visible validation and debugging workflows
Area: BROWSER
-->

# Browser Workflow

## Scope
browser-visible validation and debugging workflows

## Current source of truth
- `path:README.md`
- `path:plugins/rldyour-browser`
- `path:plugins/rldyour-mcps/.mcp.json`
- `path:docs/adr/0007-mcp-runtime-pinning-strategy.md`
- `path:scripts/validate_browser_provider_policy.py`

## Last verified
- date: 2026-07-10
- commit: `9e6d4bf2d6287762c9cbdba4a8357cd071e51978`
- checked by: Claude browser-provider boundary verification

## Facts
- Browser memories route UI and runtime validation through Webwright, Playwright CLI, and Chrome DevTools MCP when relevant.
- Chrome DevTools MCP must use the exact `/bin/sh -c` transport that executes `$HOME/.local/bin/chrome-devtools-mcp` with the managed privacy flags.
- The bootstrap owns CloakBrowser identity, version, endpoint, and health checks. This adapter intentionally carries no duplicate CloakBrowser version source and permits no stock-browser fallback.

## Evidence
- `commit:9e6d4bf2d6287762c9cbdba4a8357cd071e51978`
- `path:README.md`
- `path:plugins/rldyour-browser`
- `path:plugins/rldyour-mcps/.mcp.json`
- `path:docs/adr/0007-mcp-runtime-pinning-strategy.md`

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

- Run `python3 scripts/validate_browser_provider_policy.py` to verify provider roles and the exact bootstrap-managed Chrome DevTools transport.
- Run the rldyour control-plane Serena memory validators in strict mode: `validate_serena_memory_schema` (`--strict-mode strict-all`) and `validate_serena_memory_semantics` (`--strict-current-facts --strict-metadata-dates --strict-evidence-commits`).

## Repair Procedure

1. Re-read the source-of-truth files listed above.
2. Update only verified current facts; move stale facts into historical evidence.
3. Rerun the validation commands until green.
