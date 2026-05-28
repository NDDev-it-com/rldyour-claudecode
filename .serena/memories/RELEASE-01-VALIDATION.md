<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: 12db0e862933c4b51450bf6c56000ca6424855d9 chore(release): claude 1.0.6
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
- commit: `12db0e862933c4b51450bf6c56000ca6424855d9`
- checked by: Codex ry-start Claude Stop hook loop-guard hardening

## Facts
- Release memories record numeric versioning, tags, CI gates, and clean artifact hygiene.
- Current product/config version is `1.0.6`; `VERSION`, `package.json`,
  `pyproject.toml`, and `CHANGELOG.md` are the source of truth for the
  adapter-local SemVer state.
- Release `1.0.0` adopted Claude Code `2.1.153` and the refreshed common MCP
  policy; release `1.0.1` synchronizes internal plugin and index versions with
  the adapter release without changing Claude runtime semantics.
- Release `1.0.2` hardens the rldyour-flow Stop post-task sync gate: direct
  installed-script invocation now resolves sibling plugin scripts from
  `__file__`, Stop state runs in local-only mode, fullrepo status can avoid
  network checks during hooks, and repeated `stop_hook_active=true` fingerprints
  emit a system message then allow Stop instead of looping.
- Historical release evidence:
- Commit `1d8c2d951c1131e043989d8c4f5d2afa4f777b21` bumps the product/config
  version to `0.7.0` in `VERSION`, `package.json`, `pyproject.toml`, and
  `CHANGELOG.md` without changing Claude runtime semantics.
- Commit `32b25d2346d2fc59c441edd24ef8454db879bf18` updates
  `scripts/install-rldyour-marketplace.sh` for the current Claude CLI
  marketplace source format (`owner/repo`) and fixes final verification when
  the refreshed marketplace intentionally reuses the canonical
  `rldyour-claudecode` name.

## Evidence
- `commit:12db0e862933c4b51450bf6c56000ca6424855d9`
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
