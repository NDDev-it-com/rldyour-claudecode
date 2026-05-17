# ADR-0004: File-first reviewer transport with RLDYOUR_REPORT_EOF heredoc

- **Status**: accepted
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd

## Context and Problem Statement

Claude Code 2.0.77+ has a confirmed regression where `task.output` from a
subagent can be returned to the parent session as the full JSONL transcript
(up to 200-500 KB) instead of the final assistant text (~500 bytes).
Combined results from multiple subagents can overflow the parent context
and crash the session. Documented in Anthropic issues
[`#16789`](https://github.com/anthropics/claude-code/issues/16789),
[`#20531`](https://github.com/anthropics/claude-code/issues/20531),
[`#23463`](https://github.com/anthropics/claude-code/issues/23463), all
closed as "not planned".

`ry-start` and `ry-review` invoke 6 parallel reviewer subagents per wave
(architecture, quality, consistency, integration, verification, security).
At ~30 KB per agent transcript, a single wave can deliver ~180 KB into
the parent - structurally above any plausible context overflow threshold.

Evidence: `plugins/rldyour-flow/references/reviewer-protocol.md` Output
Transport section, `scripts/validate_reviewer_contracts.sh` (46 PASS / 0
drift), CHANGELOG.md [0.2.1] and [0.2.2] entries.

## Decision Drivers

- Reviewer wave correctness must not be limited by transport quirks.
- Full evidence (long-form findings, security `Category` / `Attack path` /
  `Verification` fields) must survive to disk even when transport
  truncates.
- 6 reviewers per wave must inject ≤ 24 KB total into parent context.

## Considered Options

- A: Inline reviewer output. Subject to the regression; not viable.
- B: JSON-stream stdout from reviewer. Adds protocol overhead; still
  flows through `task.output`.
- C: File-first transport. Reviewer writes full report to
  `.serena/reviews/<run_id>/<reviewer-name>.md` via Bash heredoc; returns
  a compact ≤ 4 KB summary with file path. Orchestrator reads the file
  for every `critical`/`high` finding before disposition.

## Decision Outcome

Chosen option: **C**. Wave-2 hardening (0.2.2 release, commit `0ff613d`)
finalized the contract:

- **Run ID**: `<UTC-ISO-compact>-<git-short-sha>` (minute precision)
  per wave, injected into every reviewer prompt.
- **Report directory**: `.serena/reviews/<run_id>/` (gitignored; in
  `RUNTIME_EXCLUDE_PATTERNS` so it never enters `fullrepo` publish).
- **Heredoc EOF marker**: `RLDYOUR_REPORT_EOF`. Short markers (`MD`,
  `EOF`, `END`) can appear legitimately in report bodies and prematurely
  close the heredoc.
- **Per-reviewer file**: `<report_dir>/<reviewer-name>.md` where
  `<reviewer-name>` matches agent frontmatter `name:`. Distinct filenames
  prevent collision with 6 parallel reviewers.
- **Compact summary**: ≤ 4 KB, cap 30 one-liner findings; counts include
  `info` severity.
- **Orchestrator contract**: `Read` every `critical`/`high` finding's
  report file before disposition (security fields exist only in the body).

### Consequences

- Good: 6 tracks × ≤ 4 KB = ≤ 24 KB parent-context injection;
  structurally prevents the documented overflow class.
- Good: full evidence on disk; security fields preserved.
- Good: read-only invariant intact - `Bash` allowed in reviewer
  `tools:` allowlist but contractually bounded to one write path per
  reviewer; `Edit`/`Write`/`NotebookEdit` remain absent from every
  reviewer allowlist.
- Bad: drift between the contract (in protocol.md + 6 agent bodies + 2
  skill bodies + AGENTS.md + .claude/CLAUDE.md + CHANGELOG.md) is easy
  to miss. Mitigation: `scripts/validate_reviewer_contracts.sh` checks 9
  invariant types across 6 reviewers + protocol (46 PASS total).

## Confirmation

- `bash scripts/validate_reviewer_contracts.sh` reports `46 PASS / 0 drift`.
- `python3 scripts/validate_agent_tools.py` confirms `Edit`, `Write`,
  `NotebookEdit` are absent from every reviewer agent allowlist.
- `fullrepo_sync.py` `RUNTIME_EXCLUDE_PATTERNS` keeps `.serena/reviews/**`
  out of `fullrepo`.

## More Information

- Protocol: `plugins/rldyour-flow/references/reviewer-protocol.md` section
  "Output Transport".
- Anthropic regression: issues #16789, #20531, #23463 (all closed "not planned").
- Related: ADR-0001 (fullrepo runtime exclude), ADR-0006 (boundaries).
