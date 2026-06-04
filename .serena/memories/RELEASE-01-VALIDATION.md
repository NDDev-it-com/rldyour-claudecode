<!-- Memory Metadata
Last updated: 2026-06-04
Last verified: 2026-06-04
Last commit: d509ec3c2a038d714294f0767f8662d23007616c chore(runtime): update Claude Code baseline to 2.1.162
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
- date: 2026-06-04
- commit: `d509ec3c2a038d714294f0767f8662d23007616c`
- checked by: Codex ry-start docs/memory consistency audit

## Facts
- Release memories record numeric versioning, tags, CI gates, and clean artifact hygiene.
- Current product/config version is `1.1.26`; `VERSION`, `package.json`,
  `pyproject.toml`, and `CHANGELOG.md` are the source of truth for the
  adapter-local SemVer state.
- Release `1.1.26` keeps the Claude Code runtime baseline at `2.1.162`,
  preserves the workflow-aware `/rldyour-flow:ry-start` hybrid shim, keeps
  `ry-start` reviewer fanout explicit opt-in, and makes reviewer agent
  descriptions Russian-first with compact English compatibility.

## Historical evidence
- Earlier release-line work progressively adopted Claude Code `2.1.153`
  through `2.1.156` surfaces, including the Opus 4.8 selector baseline,
  thinking-block API hotfix evidence, the `ry-start-workflow` boundary
  contract, and the slash-command thin-wrapper invariant.
- Earlier release-line work aligned repository descriptions with the root
  `config/repository-description-policy.json` template, standardized the
  `workflow_dispatch` release input as `version`, created or reused numeric
  tags during manual release runs, published GitHub Releases through `gh
  release create/upload`, and refreshed generated inventory before release
  validation.
- Earlier release-line work hardened the rldyour-flow Stop post-task sync gate:
  direct installed-script invocation resolves sibling plugin scripts from
  `__file__`, Stop state runs in local-only mode, fullrepo status can avoid
  network checks during hooks, and repeated `stop_hook_active=true`
  fingerprints emit a system message then allow Stop instead of looping.
- Earlier release-line work refreshed the local `github-mcp-server`
  host-binary pin to `1.1.0` in `config/mcp-runtime-versions.env`, matching
  the installed Homebrew binary and GitHub MCP Server release.
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
- `commit:d509ec3c2a038d714294f0767f8662d23007616c`
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

## Applies to
- The scope declared in this memory and the source-of-truth paths listed below.

## Invariants
- Code, configuration, tests, and git state override this memory when they disagree.

## Current State
- See `Facts` for current durable facts. Do not treat `Historical evidence` or old commit notes as current state.

## Do Not Infer
- Do not infer runtime versions, product versions, commits, permissions, release state, or tool behavior from this memory without checking the source of truth.

## Update Triggers
- Update after verified changes to the source-of-truth files, runtime baselines, release tuple, validation gates, or durable agent workflow contracts.

## Validation Commands
- `python3 scripts/validate_serena_memory_schema.py --scope all --strict-mode strict-all`
- `python3 scripts/validate_serena_memory_semantics.py --scope all --strict-current-facts`
- `python3 scripts/validate_memory_freshness.py --scope all`

## Repair Procedure
- Re-read source-of-truth files, update only verified current facts, move stale facts to historical evidence, then rerun the validation commands.
