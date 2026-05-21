<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: e9f485c45f1d543f7fbfb1e36b285157f7100848 chore: bump Claude Code baseline
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
- date: 2026-05-22
- commit: `e9f485c45f1d543f7fbfb1e36b285157f7100848`
- checked by: Codex ry-start runtime baseline sync

## Facts
- Issues memories record how GitHub issues and PRs become verified evidence after code/config checks.
- Status policy: issues and PRs are evidence only after verification against current code/config.

## Evidence
- `commit:e9f485c45f1d543f7fbfb1e36b285157f7100848`
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
