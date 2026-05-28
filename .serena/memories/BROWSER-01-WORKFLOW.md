<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: ece8d844c2696c92d7a938601258340cab91147b chore(release): claude 1.0.5
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
- date: 2026-05-28
- commit: `ece8d844c2696c92d7a938601258340cab91147b`
- checked by: Codex ry-start Claude CI stabilization

## Facts
- Browser memories route UI and runtime validation through Playwright and Chrome DevTools when relevant.

## Evidence
- `commit:cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
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
