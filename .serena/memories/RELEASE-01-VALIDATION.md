<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: 54ef94c86d27775f294101b9da5a785cb3f5c1a9 chore(release): claude 1.7.20 (other)
Scope: release readiness, versioning, and artifact hygiene
Area: RELEASE
-->

# Release Validation

## Scope
release readiness, versioning, and artifact hygiene

## Current source of truth
- `path:VERSION`
- `path:CHANGELOG.md`
- `path:.github/workflows/release.yml`

## Last verified
- date: 2026-05-22
- commit: `54ef94c86d27775f294101b9da5a785cb3f5c1a9`
- checked by: Codex ry-start memory taxonomy sync

## Facts
- Current rldyour-claudecode adapter VERSION is `1.7.20`; the release workflow publishes the matching numeric GitHub Release tag at the released commit.
- Release memories record numeric versioning, tags, CI gates, and clean artifact hygiene.

## Evidence
- `commit:54ef94c86d27775f294101b9da5a785cb3f5c1a9`
- `path:VERSION`
- `path:CHANGELOG.md`
- `path:.github/workflows/release.yml`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.
