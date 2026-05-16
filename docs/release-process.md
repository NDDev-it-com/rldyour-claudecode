# Release Process

Lifecycle for cutting a versioned release of the `rldyour-claudecode` marketplace.

## Versioning model

- **Marketplace version** lives in the root `VERSION` file. Semantic Versioning. Bumped only when there is a meaningful coordinated change across plugins or scripts.
- **Plugin version** lives in `plugins/<plugin>/.claude-plugin/plugin.json`. Each plugin can move independently.
- Per Claude Code docs: when both `marketplace.json` plugin entry and `plugin.json` declare a `version`, **`plugin.json` wins**. We enforce parity via `scripts/validate_plugin_versions.py` so the two never disagree silently.

## Release cadence

- Patch (`0.1.x`) — bug fixes, documentation, frontmatter polish, no new components.
- Minor (`0.x.0`) — new skills, agents, hooks, slash commands, or scripts; backward-compatible changes.
- Major (`x.0.0`) — boundary changes (plugin renamed/removed, hooks repurposed, marketplace name changed). Reserve for after the project leaves `0.x` territory.

## Pre-release checks

Run from repo root before tagging:

```bash
scripts/validate_marketplace.sh           # full harness — must be green
scripts/smoke_mcp_runtime.sh              # MCP servers reachable / pinned
scripts/smoke_hooks.sh                    # hook lifecycle smoke
scripts/smoke_fullrepo_sync.sh            # fullrepo state machine
python3 scripts/release_manifest.py       # capture release evidence
```

GitHub Actions `validate.yml` must already be green for the commit you intend to tag.

Verify final state:

```bash
git status -sb                            # clean of non-agent files
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json
plugins/rldyour-flow/scripts/flow_post_task_state.py | python3 -m json.tool
plugins/rldyour-serena-mcp/scripts/serena_memory_state.py | python3 -m json.tool
```

## CHANGELOG

Update `CHANGELOG.md` (Keep-a-Changelog format) before tagging:

1. Move items from `## [Unreleased]` into the new version section.
2. Use ISO date: `## [0.1.1] - 2026-MM-DD`.
3. Group entries under `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, `### Security`.
4. Reserve a fresh empty `## [Unreleased]` block for ongoing work.

## Tagging

Use `claude plugin tag --push` (CC v2.1.119+) — it validates that `plugin.json` and the marketplace entry agree on version, refuses dirty worktrees and pre-existing tags, then pushes the tag.

Tag conventions:

- Per-plugin: `<plugin-name>--v<version>` (e.g. `rldyour-flow--v0.2.0`).
- Marketplace-wide (rare): `marketplace--v<version>` based on root `VERSION`.

Manual fallback when `claude plugin tag` is not available:

```bash
git tag -a rldyour-flow--v0.2.0 -m "rldyour-flow 0.2.0"
git push origin rldyour-flow--v0.2.0
```

## Release evidence

Each release should carry:

- The output of `python3 scripts/release_manifest.py` — JSON snapshot of marketplace + plugin versions + MCP pins + git HEAD + `[Unreleased]` section.
- A green CI run for the tagged commit.
- The pre-release checks output saved alongside the release notes.

The `collect_diagnostics.sh` script can bundle the snapshot into a tarball under `.serena/diagnostics/` for archival without committing it.

## Synchronizing fullrepo

After tagging on `main`, refresh `fullrepo` so the agent-only context for the tagged release is preserved:

```bash
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --publish
```

The fullrepo branch is rebuilt from the current `HEAD` plus local agent-only files, with safe `--force-with-lease` push.
