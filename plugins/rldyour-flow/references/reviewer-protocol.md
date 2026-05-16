# Reviewer Protocol

Reviewer tracks are designed to run as parallel subagents when `ry-start` or `ry-review` explicitly invokes the review phase. They live as `agents/flow-*-review.md` (not skills) per Claude Code May-2026 best practice for orchestrated-only review tracks.

## Subagent Permission

The user explicitly approved subagent usage when invoking `/ry-start` or `/ry-review`. Each spawned subagent must receive a self-contained prompt with task, scope, diff, constraints, expected output, and read-only status.

## Tracks

| Track | Agent | Focus |
| --- | --- | --- |
| Architecture | `flow-architecture-review` | boundaries, dependencies, module shape, data flow |
| Quality | `flow-quality-review` | correctness, hacks, tech debt, edge cases, error handling |
| Consistency | `flow-consistency-review` | conventions, naming, style, file placement, public API shape |
| Integration | `flow-integration-review` | cross-module synchronization, contracts, migrations, configs |
| Verification | `flow-verification-review` | tests, manual checks, browser/server evidence, quality gates |
| Security | `flow-security-review` | security-sensitive paths, OWASP, secrets, auth/authz, unsafe flows |

## Finding Format

Each finding must include:

- Severity: `critical`, `high`, `medium`, `low`.
- Confidence: `0-100`.
- Location: file and line when possible.
- Evidence: concrete code or behavior.
- Impact: what fails or becomes harder.
- Fix: actionable correction.
- Disposition: `must-fix`, `should-fix`, `defer`, or `false-positive`.

`flow-security-review` findings add `Category` (OWASP/ASVS class), `Attack path` (defensive, no weaponization), and `Verification` (test or check) fields.

Do not report confidence below 30. Validate confidence 30-49 in the parent workflow before acting.

## Output Transport

Claude Code 2.0.77+ has a confirmed regression where `task.output` from a subagent can be returned to the parent session as a full JSONL transcript instead of the final assistant text. Anthropic issues `#16789`, `#20531`, `#23463` are closed as "not planned"; combined subagent results (7 × ~20-30 KB each) can overflow the parent context window and crash the session. Anthropic's documented sub-agents guidance also states subagents should return only a summary.

To stay safe regardless of upstream behavior, every reviewer subagent in this marketplace uses a **file-first output contract** instead of inline-markdown-only returns.

### Run ID and report directory

The orchestrator (`ry-start` or `ry-review` skill body) generates one `run_id` per review wave and passes it inside each reviewer prompt:

```
run_id    = <UTC ISO-8601 compact>-<git-short-sha>
            e.g. 2026-05-16T18Z-91cc276
report_dir = .serena/reviews/<run_id>/
```

- `report_dir` is a runtime artifact directory, not durable knowledge. It must be ignored by git (`.gitignore: .serena/reviews/`).
- One subdirectory per review wave; one file per reviewer track: `<report_dir>/<reviewer-name>.md` (e.g. `flow-architecture-review.md`).
- The orchestrator may additionally write a consolidated `_summary.md` after aggregating all reviewer outputs.

### Reviewer write contract

Each reviewer:

1. Uses `Bash` (already in the allowlist) to `mkdir -p "${report_dir}"` and `cat > "${report_dir}/<reviewer-name>.md" <<'MD' ... MD` the full markdown report with every finding in long form (Severity / Confidence / Location / Evidence / Impact / Fix / Disposition, plus security extras when applicable).
2. Returns to the parent session a **compact summary ≤ 4 KB** with this exact structure:

```
## Review Summary — <reviewer-name>
Report: <relative path to report file from repo root>

Counts: critical=N, high=N, medium=N, low=N, info=N, total=N

All findings (one-liner, max 30 entries — additional findings only in the report file):
- F-1 <severity> (<confidence>): <relative path>:<line> — <one-sentence description, ≤ 100 chars>
- F-2 ...
- ... (cap at 30 entries; append "+M more findings in report file" when total > 30)

Notes: any blocker, error, or constraint encountered while writing the report.
```

3. If the runtime cannot write to `report_dir` (read-only filesystem, missing permissions, sandbox), the reviewer:
   - Falls back to inline summary-only output without a `Report:` line.
   - Adds `Notes: filesystem-readonly` (or the specific error) so the orchestrator records the limitation.
   - Still respects the 4 KB compact-summary cap.

### Orchestrator read contract

The orchestrator (`ry-start` or `ry-review` skill body) after subagent completion:

1. Reads each reviewer summary from the agent result.
2. Aggregates counts across all reviewers.
3. Reads each full report file (`Read` tool) only for the findings it needs to consolidate the plan — typically critical/high entries first.
4. Resolves contradictions across reviewer tracks against code evidence.
5. Optionally writes `<report_dir>/_summary.md` (consolidated cross-track findings + plan disposition) as durable wave artifact.
6. Reports back to the user in Russian. Lists report-file paths so the user can inspect full findings on disk.

### Why this works

- **Cap on parent context impact**: 6 reviewers × ≤ 4 KB summary = ≤ 24 KB injected into parent context, well below any plausible overflow threshold. The bug class described in Anthropic `#23463` (15-37 KB per reviewer × 7 reviewers → 150 KB → overflow) is structurally prevented.
- **Full evidence preserved**: long-form findings live on disk and are not lost even when subagent transport truncates.
- **Backward compatible**: reviewers that find few findings produce short summaries; the file is optional metadata, the summary alone is sufficient for the orchestrator to act.
- **Read-only invariant intact**: reviewers still only modify their own report files under `.serena/reviews/` — they do not touch project source. The marketplace `validate_agent_tools.py` invariant continues to allow `Bash` for read-only inspection plus reviewer-result writes; project files remain unreachable because `Edit`, `Write`, and `NotebookEdit` are absent from the allowlist.

## Parent Integration

The parent workflow (`ry-start` or `ry-review`) consolidates all findings, resolves contradictions with code evidence, fixes accepted findings, then reruns only the reviewer tracks that found problems.

## Why agents, not skills

As of May 2026, `disable-model-invocation: true` on plugin skills has known limitations (cannot be invoked by user via slash command either when installed in a plugin — issue #26251). The canonical pattern from `anthropics/claude-plugins-official/plugins/pr-review-toolkit` is reviewer **agents**, not skills. Reviewer agents have:

- Short orchestration-focused descriptions (no "use when..." trigger phrases) to discourage implicit invocation.
- `tools: [Read, Grep, Glob, Bash, mcp__plugin_rldyour-mcps_serena__*, mcp__plugin_rldyour-mcps_context7__*, mcp__plugin_rldyour-mcps_deepwiki__*, mcp__plugin_rldyour-mcps_grep__*]` explicit allowlist to enforce read-only review with future-proof safety. `flow-security-review` adds `WebFetch`, `WebSearch`, and `mcp__plugin_rldyour-mcps_semgrep__*` for CVE lookups and SAST. Pattern follows canonical `anthropics/claude-plugins-official/plugins/pr-review-toolkit/agents/code-reviewer` (explicit allowlist), not the older `disallowedTools` denylist — explicit positive intent is stronger than denying a finite list.
- `model: sonnet` for cost-efficiency on read-only inspection work.
- `effort: high` (uniform across all 6 tracks).
- `maxTurns: 36` for all tracks; `42` for `flow-security-review` (extra +6 turns reserved for variant-hunt sweep — searching sibling files and repeated helpers for the same root cause once an issue is found). Generous limits compensate for MCP-rich toolsets (Serena + Context7 + DeepWiki + Grep) consuming turns on tool plumbing — tight 12-14 caps left only 4-7 effective reasoning turns. When adding a new reviewer track, default to `maxTurns: 36` unless the track requires variant-hunting beyond the single finding.
- Distinct `color` per track for visual differentiation in the task list:
  - `flow-architecture-review`: `blue`
  - `flow-quality-review`: `green`
  - `flow-consistency-review`: `purple`
  - `flow-integration-review`: `orange`
  - `flow-verification-review`: `pink`
  - `flow-security-review`: `red`

Orchestrators (`ry-start`, `ry-review`) invoke them via prose body delegation in their workflow steps.
