<!-- Memory Metadata
Last updated: 2026-05-29
Last commit: 63abf7d4084cd892fea40e126d71cdd2ddf6d80e chore(release): claude 1.1.0
Scope: GitHub issue and PR evidence policy
Area: ISSUES
-->

# Verified Issues

## Scope
GitHub issue and PR evidence policy

## Current source of truth
- `path:README.md`
- `path:plugins/rldyour-flow/skills/ry-review`


## Source Of Truth
- `path:README.md`
- `path:plugins/rldyour-flow/skills/ry-review`

## Last verified
- date: 2026-05-29
- commit: `63abf7d4084cd892fea40e126d71cdd2ddf6d80e`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Issues memories record how GitHub issues and PRs become verified evidence after code/config checks.
- Status policy: issues and PRs are evidence only after verification against current code/config.

## Evidence
- `commit:cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- `path:README.md`
- `path:plugins/rldyour-flow/skills/ry-review`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `TECHDEBT-01-NOW.md`
- `TESTS-01-VALIDATION-GATES.md`
- `FLOW-01-SDLC.md`
