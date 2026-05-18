# ADR-0011: Agent-instruction files are knowledge-equivalent for Serena freshness gates

- **Status**: accepted
- **Date**: 2026-05-18
- **Decision-Makers**: rldyourmnd
- **Related**: [ADR-0001](./0001-fullrepo-branch-policy.md) (fullrepo branch policy), [ADR-0002](./0002-dual-doc-agents-claude-split.md) (AGENTS.md + .claude/CLAUDE.md dual-doc), [ADR-0009](./0009-release-version-and-tag-convention.md) (release versioning)

## Context and Problem Statement

`plugins/rldyour-serena-mcp/scripts/serena_memory_state.py` computes
`memory_matches_head` to drive the `commit_serena_knowledge.sh` hook
and the Stop gate. Before this ADR, it had three branches:

1. **`direct-head-reference`** - a memory's `Last commit:` metadata
   directly mentions the current HEAD short SHA.
2. **`marker-matches-head`** - `.serena/.sync_marker` contains a
   fingerprint that matches HEAD.
3. **`knowledge-only-commits-since-sync`** - all commits since the
   newest synced memory commit touched only `SERENA_KNOWLEDGE_PREFIXES`
   paths (`.serena/memories/`, `.serena/plans/`, `.serena/research/`,
   `.serena/newproj/`, `.serena/deploy/`).

This worked correctly for repositories where Serena memories live in
`.serena/memories/` AND product code lives on the same branch as agent
guidance. It **broke** for repositories using the canonical
`rldyour-flow` **main + fullrepo branch split**:

- `main` carries product code + product docs.
- `fullrepo` carries `main` + agent-only files (`AGENTS.md`,
  `.claude/CLAUDE.md`, `REVIEW.md`, `.serena/**`, IDE/agent root
  directories, `.github/copilot-instructions.md`, etc.) excluded from
  `main` via `.git/info/exclude`.
- After a sync wave, `fullrepo` HEAD is a merge commit that is NOT an
  ancestor of `main` HEAD.

The `almaty-libraries` repository (Claude Code session on 2026-05-18)
hit a structural impossibility:

- Project-side CI gate (`infrastructure/scripts/verify-memory-sync.py`)
  uses a strict `METADATA_RE` regex and `git merge-base --is-ancestor`
  to enforce that `Last commit:` SHA must be an ancestor of `main` HEAD.
- Our hook (`commit_serena_knowledge.sh` via `serena_memory_state.py`)
  used substring match looking for `Last commit: <current-fullrepo-HEAD>`.
- The fullrepo merge HEAD was NOT an ancestor of `main`, so satisfying
  one gate broke the other. Each hook auto-commit moved HEAD forward,
  triggering an unwinnable loop.

A first attempt (commit `4dcc1d1`, 2026-05-18) added `AGENT_INSTRUCTION_PATHS`
to `_is_knowledge_path()` so agent-instruction churn would route through
the `knowledge-only-commits-since-sync` branch. That fix was correct in
direction but covered only 14 of 23 canonical agent-only paths, lacked
tests, version bumps, memory updates, and documentation.

## Decision Drivers

- Hooks must not block work indefinitely on structurally impossible
  conditions. The `branch-split + dual-gate` shape is a canonical
  rldyour-flow pattern, not an edge case.
- A single source of truth for what counts as "agent-only" must exist.
  The `.git/info/exclude` "rldyour fullrepo agent-only files" block is
  that source; the freshness classifier must mirror it.
- Drift between `serena_memory_state.AGENT_INSTRUCTION_PATHS` and the
  inline mirror in `mark_sync_required.sh` (which runs in a separate
  Python heredoc subprocess) must be detected automatically.
- Adding paths to `_is_knowledge_path()` must not weaken the
  classification for real product code, configs, or workflows.

## Considered Options

### Option A. Treat agent-instruction files as knowledge-equivalent (accepted)

Extend `_is_knowledge_path()` with `AGENT_INSTRUCTION_PATHS` covering the
full canonical exclude block. Memories pinned to a main-side ancestor
SHA satisfy `memory_matches_head=true` via the
`knowledge-only-commits-since-sync` branch when agent-instruction churn
is the only delta since the newest synced commit.

### Option B. Read paths from `marketplace-policy.json` at runtime

Add an `agent_only_path_prefixes` field to `config/marketplace-policy.json`
and load it dynamically. Centralises configuration but introduces a
runtime dependency in a freshness-critical hook, complicates testing,
and is overkill while inline lists remain small (~23 entries).

### Option C. Read paths from `fullrepo_sync.py` directly

`rldyour-flow/scripts/fullrepo_sync.py` already tracks agent-only paths
for `--bootstrap-init` / `--restore` / `--publish`. Cross-plugin import
would invert the dependency direction (rldyour-flow depends on
rldyour-serena-mcp; not the other way around). Rejected.

### Option D. Loosen the substring match to ancestor-of-anywhere

`commit_serena_knowledge.sh` could accept any memory `Last commit:` SHA
that is an ancestor of HEAD on any branch. This would make false-positive
sync states possible (a memory mentioning a long-stale SHA on a deleted
branch would still pass). Rejected.

## Decision

Accepted: Option A. Agent-instruction files are knowledge-equivalent for
the freshness classifier.

**Canonical AGENT_INSTRUCTION_PATHS** mirrors the
`.git/info/exclude` "rldyour fullrepo agent-only files" block:

- Root-level: `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, `GEMINI.md`,
  `QWEN.md`, `.cursorrules`, `.windsurfrules`, `.aider` (prefix-match
  family).
- IDE / agent roots: `.claude/`, `.codex/`, `.cursor/`, `.gemini/`,
  `.windsurf/`, `.roo/`, `.openhands/`.
- GitHub: `.github/copilot-instructions.md`, `.github/instructions/`,
  `.github/prompts/`.
- `.agents/`: `.agents/skills/`, `.agents/commands/`, `.agents/hooks/`.
- Serena metadata: `.serena/project.yml`, `.serena/project.local.yml`.

`.serena/memories/`, `.serena/plans/`, `.serena/research/`,
`.serena/newproj/`, `.serena/deploy/` remain in
`SERENA_KNOWLEDGE_PREFIXES` (knowledge directories).

`mark_sync_required.sh` inline canon (separate Python heredoc subprocess
with no import access) carries an explicit duplicate of
`AGENT_INSTRUCTION_PATHS`. Drift is asserted by
`tests/test_serena_memory_state.py::TestInlineHookCanonDrift::test_inline_hook_path_canon_matches`.

## Consequences

### Positive

- Branch-split projects (almaty-libraries, future rldyour-flow consumers)
  can satisfy both CI ancestor-check gate AND our local freshness hook
  without prose-mention churn or unwinnable loops.
- 23-path canon mirrors the actual exclude block; missing paths
  (`.cursorrules`, `.windsurfrules`, `.openhands/`,
  `.github/copilot-instructions.md`, etc. from commit `4dcc1d1`) are
  now covered.
- Drift between `serena_memory_state.AGENT_INSTRUCTION_PATHS` and the
  inline mirror is automatically caught by tests.

### Negative

- Two source-of-truth lists (Python module + inline shell heredoc) must
  stay synchronised. Drift detection test exists; manual update is still
  required when paths are added.
- Adding a new agent-instruction path family requires two edits + ADR
  acknowledgement (this ADR + the path canon block).

### Trade-offs accepted

- **Coverage > exact parity**: we use `.cursor/` (broader) where exclude
  block has `.cursor/rules/**` (narrower). This is intentional - any IDE
  config under `.cursor/` is treated as agent-only.
- **Inline duplication > runtime config dependency**: a runtime config
  load would couple hook freshness to JSON parsing reliability.

## Confirmation

`tests/test_serena_memory_state.py` (49 tests) covers:

- 5 `SERENA_KNOWLEDGE_PREFIXES` paths classified as knowledge.
- 23 `AGENT_INSTRUCTION_PATHS` paths classified as knowledge.
- 12 real code/config paths NOT classified as knowledge.
- Filter behaviour on mixed inputs.
- Parity between `AGENT_INSTRUCTION_PATHS` and `.git/info/exclude`
  agent-only block (semantic match: broader-OK).
- Drift detection between Python module canon and `mark_sync_required.sh`
  inline canon.

CI runs `tests/test_serena_memory_state.py` as part of
`.github/workflows/pytest.yml`. Drift is caught at PR-review time.

## Open Questions

- Should `marketplace-policy.json` eventually expose
  `agent_only_path_prefixes` as a config knob? Deferred until a second
  consumer of the canon emerges beyond `serena_memory_state.py` and
  `mark_sync_required.sh`.

## References

- Source: `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`
  (`AGENT_INSTRUCTION_PATHS`, `_is_knowledge_path`).
- Inline mirror: `plugins/rldyour-serena-mcp/hooks/mark_sync_required.sh`
  (`AGENT_INSTRUCTION_PATHS` inside the Python heredoc).
- Tests: `tests/test_serena_memory_state.py`.
- Memory: `[[SERENA-01-MEMORY-SYNC]]`, `[[HOOKS-01-LIFECYCLE]]`,
  `[[TECHDEBT-01-NOW]]` D77.
- Pre-existing reference: commit `4dcc1d1` (first incomplete attempt,
  closed via this ADR's full canonical fix).
- Origin trigger: `almaty-libraries` Claude Code session on 2026-05-18
  (CI gate `verify-memory-sync.py` vs `commit_serena_knowledge.sh`
  hook structural conflict).
