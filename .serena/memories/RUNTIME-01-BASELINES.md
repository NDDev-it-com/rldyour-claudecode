<!-- Memory Metadata
Last updated: 2026-07-10
Last verified: 2026-07-10
Last commit: 9e6d4bf2d6287762c9cbdba4a8357cd071e51978 ci(deps): repin reusable workflows to 0.5.1
Scope: CLI runtime and package baselines
Area: RUNTIME
-->

# Runtime Baselines

## Scope
CLI runtime and package baselines

## Current source of truth
- `path:references/claude-baseline.json`
- `path:package.json`
- `path:config/mcp-runtime-versions.env`
- `path:references/claude-surface-adoption.md`

## Last verified
- date: 2026-07-10
- commit: `9e6d4bf2d6287762c9cbdba4a8357cd071e51978`
- checked by: Claude Code stable-baseline refresh

## Facts
- Claude Code `2.1.206` is the current adapter runtime pin in `package.json`, `references/claude-baseline.json`, and `config/mcp-runtime-versions.env`.
- npm `latest` and `next` resolve to `2.1.206`; the official upstream changelog records MCP timeout/OAuth, worktree-confirmation, resume-input, background-agent, login, model-picker, and `/doctor` reliability changes without an adapter schema migration.
- Runtime memories record pinned CLI/package baselines and freshness checks.

## Evidence
- `commit:9e6d4bf2d6287762c9cbdba4a8357cd071e51978`
- `path:references/claude-baseline.json`
- `path:package.json`
- `path:config/mcp-runtime-versions.env`
- `https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Applies to

- The scope and source-of-truth paths declared in this memory.

## Source of truth

- The `Current source of truth` entries above, plus current code, configuration, tests, git state, and live GitHub state where this memory references live release or repository surfaces.

## Invariants

- Current code, configuration, tests, validators, git state, and live GitHub state override this memory whenever they disagree.

## Current State

- Treat the `Facts` section as the current durable state. Do not treat historical evidence, superseded notes, or previous release entries as current.

## Do Not Infer

- Do not infer runtime versions, product versions, commits, permissions, release state, security posture, or tool behavior from this memory without checking the source of truth.

## Update Triggers

- Update after verified changes to the source-of-truth files, runtime baselines, release tuple, validation gates, live release state, or durable agent-workflow contracts.

## Validation Commands

- Run `python3 scripts/validate_claude_surface_adoption.py` to verify that every runtime fix in the baseline has a documented adapter decision.
- Run `python3 scripts/validate_release_state.py` to verify runtime and adapter release metadata parity.
- Run the rldyour control-plane Serena memory validators in strict mode: `validate_serena_memory_schema` (`--strict-mode strict-all`) and `validate_serena_memory_semantics` (`--strict-current-facts --strict-metadata-dates --strict-evidence-commits`).

## Repair Procedure

1. Re-read the source-of-truth files listed above.
2. Update only verified current facts; move stale facts into historical evidence.
3. Rerun the validation commands until green.
