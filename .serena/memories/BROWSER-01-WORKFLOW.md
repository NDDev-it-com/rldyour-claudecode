<!-- Memory Metadata
Last updated: 2026-05-29
Last commit: f78a246df180e912fd4090f89f25f8b74b16e80c chore(runtime): bump claude code baseline to 2.1.156
Scope: browser-visible validation and debugging workflows
Area: BROWSER
-->

# BROWSER-01-WORKFLOW

## Scope
browser-visible validation and debugging workflows

## Current source of truth
- `path:README.md`
- `path:plugins/rldyour-browser`


## Source Of Truth
- `path:README.md`
- `path:plugins/rldyour-browser`

## Last verified
- date: 2026-05-29
- commit: `f78a246df180e912fd4090f89f25f8b74b16e80c`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Browser memories route UI and runtime validation through Playwright and Chrome DevTools when relevant.

## Evidence
- `commit:f78a246df180e912fd4090f89f25f8b74b16e80c`
- `path:README.md`
- `path:plugins/rldyour-browser`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `DESIGN-01-WORKFLOW.md`
- `TESTS-01-VALIDATION-GATES.md`
- `MCP-01-TRANSPORT.md`
