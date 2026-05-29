<!-- Memory Metadata
Last updated: 2026-05-29
Last commit: f78a246df180e912fd4090f89f25f8b74b16e80c chore(runtime): bump claude code baseline to 2.1.156
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
- date: 2026-05-29
- commit: `f78a246df180e912fd4090f89f25f8b74b16e80c`
- checked by: Codex ry-start automated release and metadata sync

## Facts
- Release memories record numeric versioning, tags, CI gates, and clean artifact hygiene.
- Current product/config version is `1.1.2`; `VERSION`, `package.json`,
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
- Release `1.0.7` aligns active repository descriptions with the root
  `config/repository-description-policy.json` template, standardizes the
  `workflow_dispatch` release input as `version`, creates or reuses numeric
  tags during manual release runs, publishes GitHub Releases through `gh
  release create/upload`, and refreshes generated inventory before release
  validation.
- Release `1.1.0` adopts the Claude Code `2.1.154` baseline required for
  Opus 4.8 targeting, keeps `ry-explore` on the Claude-native `opus[1m]`
  selector, and updates active model/runtime metadata from verified package
  and official model-config evidence.
- Release `1.1.1` refreshes the local `github-mcp-server` host-binary pin to
  `1.1.0` in `config/mcp-runtime-versions.env`, matching the installed
  Homebrew binary and GitHub MCP Server release.
- Release `1.1.2` pins Claude Code `2.1.156`, records the Opus 4.8
  thinking-block API hotfix in the surface matrix, and adds the
  `ry-start-workflow` boundary contract while keeping `/rldyour-flow:ry-start`
  as the stable plugin entrypoint.
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
- `commit:f78a246df180e912fd4090f89f25f8b74b16e80c`
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
