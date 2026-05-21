# ADR-0009: Release version and tag convention

- **Status**: accepted
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd

## Context and Problem Statement

The marketplace has two version axes:

1. **Marketplace boundary**: single VERSION file at the repo root,
   marking aggregate release state. Used as the cache namespace anchor
   in `~/.claude/plugins/cache/rldyour-claudecode/`.
2. **Per-plugin behavior**: nine `plugins/<name>/.claude-plugin/plugin.json`
   `version` fields. Used by Claude Code as plugin cache keys; bumping a
   per-plugin version forces consumers to refresh that plugin's component
   cache (skills, agents, hooks, MCP, LSP).

These can move independently (a plugin can bump 0.2.1 -> 0.2.2 while
others stay 0.2.0). But the maintainer also wants a unified "release
boundary" for CHANGELOG entries and GitHub Releases.

A naive single-tag approach loses per-plugin cache invalidation. A pure
per-plugin tag approach loses the aggregate release artefact. Both axes
are needed.

Evidence: VERSION (single file), `.claude-plugin/marketplace.json`
plugin entries with `version`, plugin.json `version` fields,
docs/release-process.md, `.github/workflows/release.yml` (G11).

## Decision Drivers

- Cache invalidation correctness per plugin.
- Single human-readable release narrative (CHANGELOG, GitHub Release).
- Reproducibility: tag must point at exact commit, signed.

## Considered Options

- A: Single numeric product tag only. Loses per-plugin cache invalidation.
- B: Per-plugin tags only. Loses aggregate release narrative.
- C: Both - marketplace boundary tag `marketplace--vX.Y.Z` plus per-plugin
  tags `<plugin>--vX.Y.Z`, both pushed at release.
- D: Numeric product tag `X.Y.Z` as the only GitHub Release trigger; optional
  plugin-scoped tags remain implementation metadata and do not trigger release.

## Decision Outcome

Chosen option: **D**. Tag conventions:

- `X.Y.Z` (e.g. `0.6.8`): primary product tag, manually created via
  `git tag -s 0.6.8 -m "..."` when signing is available, or annotated
  otherwise. This is the only tag family that triggers
  `.github/workflows/release.yml`.
- `<plugin-name>--v<X.Y.Z>` (e.g. `rldyour-flow--v0.3.0`): created via
  `claude plugin tag --push` (CC v2.1.118+). The CLI validates that
  `plugin.json` and the marketplace entry agree on version, refuses
  dirty worktrees and pre-existing tags. These tags are historical/cache
  metadata only and do not trigger release.yml.

Bump policy:

- After any change touching marketplace or plugin files (including docs,
  memories, agent-only context, scripts, hooks, references, skill
  bodies), bump BOTH the affected per-plugin versions AND the marketplace
  VERSION. This is stronger than the cache-refresh-only AGENTS.md rule
  (limiting bumps to `SKILL.md/agent.md/hooks.json/.mcp.json` changes)
  because the maintainer prefers explicit signaling.

CHANGELOG (`Keep a Changelog 1.1.0`):
- `[X.Y.Z] - YYYY-MM-DD` per release with `### Added / Changed / Fixed /
  Removed / Security` subsections. Reference-link block at file tail
  `[X.Y.Z]: https://github.com/.../releases/tag/X.Y.Z`.

### Consequences

- Good: product release tags now match SemVer core (`X.Y.Z`) exactly across all
  adapters; per-plugin cache tags remain available without becoming public
  release coordinates.
- Good: `scripts/validate_release_state.py` enforces parity (VERSION ==
  latest CHANGELOG section == marketplace.json top-level VERSION).
- Good: signed tags via `git tag -s` give provenance; release.yml uses
  `--verify-tag` to refuse unsigned tags.
- Bad: 10 tags per release (1 marketplace + 9 plugin). Mitigation:
  `claude plugin tag --push` handles per-plugin tags in a loop.
- Bad: bump policy means even doc-only commits typically result in a
  version bump. Acceptable trade-off for unambiguous cache invalidation.

## Confirmation

- `python3 scripts/validate_release_state.py` enforces parity.
- `python3 scripts/validate_plugin_versions.py` ensures marketplace
  entries match plugin.json versions.
- `.github/workflows/release.yml` (G11) `gh release create --verify-tag`
  refuses to create a release if the tag is not present at HEAD.
- `git tag --list "*--v<X.Y.Z>"` lists all 10 tags for a release.

## More Information

- Related: ADR-0008 (CI baseline that runs release.yml).
- Changelog format: https://keepachangelog.com/en/1.1.0/
- SemVer 2.0.0: https://semver.org/
