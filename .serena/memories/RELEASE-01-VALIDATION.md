<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: ad97d9deb65b76cea82052322b9e6cee86af0407 fix(installer): guard report markdown printf
Scope: release readiness, versioning, and artifact hygiene
Area: RELEASE
-->

# RELEASE-01-VALIDATION

## Scope
release readiness, versioning, and artifact hygiene

## Current source of truth
- `path:VERSION`
- `path:CHANGELOG.md`
- `path:.github/workflows/release.yml`


## Source Of Truth
- `path:VERSION`
- `path:CHANGELOG.md`
- `path:.github/workflows/release.yml`

## Last verified
- date: 2026-05-28
- commit: `ad97d9deb65b76cea82052322b9e6cee86af0407`
- checked by: Codex system sync after Claude installer report fix

## Facts
- Release memories record numeric versioning, tags, CI gates, and clean artifact hygiene.
- Commit `1d8c2d951c1131e043989d8c4f5d2afa4f777b21` bumps the product/config
  version to `0.7.0` in `VERSION`, `package.json`, `pyproject.toml`, and
  `CHANGELOG.md` without changing Claude runtime semantics.
- Commit `32b25d2346d2fc59c441edd24ef8454db879bf18` updates
  `scripts/install-rldyour-marketplace.sh` for the current Claude CLI
  marketplace source format (`owner/repo`) and fixes final verification when
  the refreshed marketplace intentionally reuses the canonical
  `rldyour-claudecode` name.
- Commit `ad97d9deb65b76cea82052322b9e6cee86af0407` fixes the final install
  report writer so Markdown list entries use `printf --` and do not trip Bash
  option parsing after a successful marketplace install.

## Evidence
- `commit:ad97d9deb65b76cea82052322b9e6cee86af0407`
- `path:VERSION`
- `path:CHANGELOG.md`
- `path:config/mcp-runtime-versions.env`
- `path:.github/workflows/release.yml`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `CI-01-ACTIONS.md`
- `TESTS-01-VALIDATION-GATES.md`
- `RUNTIME-01-BASELINES.md`
