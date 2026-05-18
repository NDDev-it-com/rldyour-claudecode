<!-- Memory Metadata
Last updated: 2026-05-18
Last commit: da432c6 docs(changelog): record reviewer-wave closures in [0.5.2]
Scope: plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py, plugins/rldyour-serena-mcp/scripts/serena_memory_state.py, plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh, plugins/rldyour-serena-mcp/hooks/*.sh, plugins/rldyour-serena-mcp/skills/serena-memory-sync/SKILL.md, plugins/rldyour-serena-mcp/agents/flow-memory-sync.md, scripts/smoke_serena_memory_taxonomy.sh, docs/adr/0011-agent-instruction-knowledge-equivalence.md, tests/test_serena_memory_state.py
Area: SERENA
-->

# SERENA-01-MEMORY-SYNC

## Purpose

Durable contract for Serena memory freshness, impact analysis, scoped sync, and fact-only memory writing.

## Source Of Truth

- `plugins/rldyour-serena-mcp/hooks/prepare_auto_sync.sh`: records `.serena/.auto_sync_head` before commit-like Bash commands.
- `plugins/rldyour-serena-mcp/hooks/mark_sync_required.sh`: writes `.serena/.serena_sync_state.json` after commit-like commands when sync-relevant files changed. Contains an inline Python `AGENT_INSTRUCTION_PATHS` mirror (separate subprocess cannot import the plugin module); `is_knowledge_path()` combines `SERENA_KNOWLEDGE_PREFIXES` + `AGENT_INSTRUCTION_PATHS`.
- `plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py`: classifies changed paths, emits schema v2 analysis, memory taxonomy, areas, risk profile, and memory targets.
- `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`: computes memory freshness against HEAD and exposes `analysis` + `analysis_source`. Contains `AGENT_INSTRUCTION_PATHS` constant and `_is_knowledge_path()` function.
- `plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh`: Stop gate that blocks with `exit 2` when memories are stale.
- `plugins/rldyour-serena-mcp/agents/flow-memory-sync.md`: canonical memory writer contract.
- `plugins/rldyour-serena-mcp/skills/serena-memory-sync/SKILL.md`: main-session fallback workflow and memory template.
- `plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh`: acknowledges successful sync and clears runtime markers.
- `scripts/smoke_serena_memory_taxonomy.sh`: focused regression smoke for this memory contract.
- `docs/adr/0011-agent-instruction-knowledge-equivalence.md`: ADR recording the decision to treat agent-instruction files as knowledge-equivalent for freshness gates (accepted 2026-05-18).
- `tests/test_serena_memory_state.py`: 49 unit tests covering `SERENA_KNOWLEDGE_PREFIXES`, full `AGENT_INSTRUCTION_PATHS` canon, negative classification, parity with `.git/info/exclude`, and inline hook canon drift detection.

## Current Behavior

- Analyzer output uses `analysis.schema_version = 2` and always includes `analysis.memory_taxonomy`.
- Memory taxonomy at HEAD: `filename_pattern = AREA-01-SLUG.md`, `index_memory = CORE-01-INDEX.md`, stable areas `CORE`, `CLAUDECODE`, `MCP`, `SERENA`, `HOOKS`, `FLOW`, `DOCS`, `RELEASE`, `TECHDEBT`.
- Empty commit ranges produce empty `memory_targets` and `candidate_memory_focus`, while still exposing taxonomy.
- **`AGENT_INSTRUCTION_PATHS` canon (0.5.2, commit `febf45f`)**: 23 paths mirroring the full `.git/info/exclude` "rldyour fullrepo agent-only files" block. Exact list at `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py:29-68` at HEAD `da432c6`:
  - Root files: `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, `GEMINI.md`, `QWEN.md`, `.cursorrules`, `.windsurfrules`, `.aider` (family prefix - see below).
  - IDE/agent root dirs: `.claude/`, `.codex/`, `.cursor/`, `.gemini/`, `.windsurf/`, `.roo/`, `.openhands/`.
  - GitHub agent paths: `.github/copilot-instructions.md`, `.github/instructions/`, `.github/prompts/`.
  - Cross-vendor agent: `.agents/skills/`, `.agents/commands/`, `.agents/hooks/`.
  - Serena metadata: `.serena/project.yml`.
  - Intentionally absent: `.serena/project.local.yml` (machine-local runtime config, negated in `.git/info/exclude`, in `fullrepo_sync.RUNTIME_EXCLUDE_PATTERNS`; never reaches commits in normal flow).
- **`_is_knowledge_path()` precise-match semantics (0.5.2, commit `03afa2f`, F-3 closure)**: directory entries (ending in `/`) use `startswith`; exact-file entries (e.g. `AGENTS.md`, `.github/copilot-instructions.md`) use `==`; `.aider` is a dotfile-family special case matching `.aider`, `.aiderignore`, `.aider.conf.yml`, `.aider.chat.history.md`. Prevents false-positive prefix matches like `AGENTS.md.bak` or `.github/copilot-instructions.mdx`. Verified at `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py:179-210` at HEAD `da432c6`.
- **`knowledge-only-commits-since-sync` freshness branch**: `serena_memory_state.py` sets `memory_match_reason = "knowledge-only-commits-since-sync"` when all commits since the newest synced memory touched only `SERENA_KNOWLEDGE_PREFIXES` + `AGENT_INSTRUCTION_PATHS`. Verified at `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py:285-295` at HEAD `da432c6`.
- Analyzer targets include `CLAUDECODE-01-PLUGIN-CANON.md` for plugin component contracts and Claude Code instruction context.
- `serena_memory_state.py` scans `.serena/memories/**/*.md` so nested memories remain freshness-aware if future taxonomy uses subdirectories.
- `commit_serena_knowledge.sh` uses `git status --porcelain -uall`, filters runtime marker files, clears markers only when memory state matches HEAD, and refuses fullrepo-managed stale memories even when the normal branch has no tracked knowledge diff.
- `stop_memory_sync.sh` writes compound fingerprint `${HEAD_SHA}:${NEWEST_SHA:-none}` to `.serena/.sync_marker` (commit `23901c6`, D32). Verified at `plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh:72-77` at HEAD.
- `serena_memory_state.py` surfaces non-dict analysis payload discards to stderr via `print(..., file=sys.stderr)` (commit `d563ea5`, D33). Verified at `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py:102-107` at HEAD.
- **Inline mirror in `mark_sync_required.sh`** (0.5.2, commit `03afa2f`): the inline Python heredoc in `mark_sync_required.sh` mirrors `AGENT_INSTRUCTION_PATHS` using the same precise-match semantics as `_is_knowledge_path()`. Drift between the two canons is enforced by `tests/test_serena_memory_state.py::TestInlineHookCanonDrift`. Verified at `plugins/rldyour-serena-mcp/hooks/mark_sync_required.sh` at HEAD `da432c6`.

## Contracts And Data

- `.serena/.serena_sync_state.json` contains: `version`, `required`, `reason`, `created_at`, `previous_head_full`, `head_full`, `head_sha`, `changed_files`, `non_knowledge_changed_files`, and `analysis`.
- `analysis.memory_targets` is advisory scope, not final truth. The writer must verify each claim against code/config/tests at HEAD.
- `analysis_source` emitted by `serena_memory_state.py` can be `sync_marker`, `sync_marker_ref_range:*`, `newest_sync_ref_range:*`, `path_list`, or `none`.
- A memory counts as current when it directly mentions `Last commit: <HEAD_SHA>` or when the newest synced memory commit equals HEAD; marker state can force stale.
- `flow-memory-sync` is the only automated writer for `.serena/memories`. Hooks compute scope and block Stop; they do not write durable facts.
- `.serena/plans/` and `.serena/research/` are written by the main `serena-memory-sync` workflow only when a reusable plan or source-backed research archive is explicitly needed.

## Invariants

- Do not pass large analyzer or state JSON as shell argv. `mark_sync_required.sh` uses a temp file and `stop_memory_sync.sh` reads state JSON through stdin to avoid shell limits.
- Do not write memories from `ry-init` unless explicitly requested or a Stop/stale-memory hook requires it.
- Do not store runtime observations as snapshot memories. Distill durable contracts into topic files.
- Every touched memory must contain a metadata block with `Last commit: <sha> <message>`.
- Existing memory content must be verified before preservation; stale claims are corrected or removed.
- `AGENT_INSTRUCTION_PATHS` in `serena_memory_state.py` and its inline mirror in `mark_sync_required.sh` must stay in sync. Enforced by `tests/test_serena_memory_state.py::TestInlineHookCanonDrift`.

## Change Rules

- Any change to analyzer schema, memory taxonomy, marker payloads, Stop hook parsing, `serena_memory_state.py`, `commit_serena_knowledge.sh`, `serena-memory-sync` skill, or `flow-memory-sync` agent must update this memory and `CORE-01-INDEX.md` if the taxonomy/map changes.
- If analyzer output shape changes, bump plugin version and update `CHANGELOG.md`.
- If a new durable area is introduced, add it to `analysis.memory_taxonomy`, create/rename the numbered memory, and update `CORE-01-INDEX.md`.
- Add a targeted case to `scripts/smoke_serena_memory_taxonomy.sh` for every new analyzer target family or freshness edge case.
- Any change to `AGENT_INSTRUCTION_PATHS` must update both `serena_memory_state.py` and the inline mirror in `mark_sync_required.sh`; add regression tests to `tests/test_serena_memory_state.py`.

## Verification

- `python3 plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py --from-ref HEAD --to-ref HEAD`: verifies empty-diff/no-target behavior and taxonomy emission.
- `bash scripts/smoke_serena_memory_taxonomy.sh`: verifies schema v2, analyzer target routing, instruction-only sync marker behavior, recursive memory scanning, Stop advisory taxonomy, Stop loop guard, and fullrepo-managed acknowledgement/refusal.
- `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`: verifies freshness, memory count, `analysis`, and `analysis_source`.
- `bash -n plugins/rldyour-serena-mcp/hooks/mark_sync_required.sh plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh`: verifies shell syntax.
- `bash scripts/smoke_hooks.sh`: verifies static hook registration, skip flags, and defensive guards.
- `bash scripts/validate_marketplace.sh`: includes `scripts/smoke_serena_memory_taxonomy.sh` at HEAD.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/test_serena_memory_state.py -v`: runs 49 unit tests covering AGENT_INSTRUCTION_PATHS canon, precise-match semantics, and inline mirror drift.

## Known Gaps

- Analyzer area/risk classification is heuristic and must remain advisory. The memory writer must verify exact facts from source files before writing.
- Hooks intentionally do not write memories; skipping the `flow-memory-sync` pass can still leave memories stale until Stop is handled.

## Cross-References

- Memory taxonomy map: [[CORE-01-INDEX]] (18 memories, area definitions, file naming contract).
- Hook coordination: [[HOOKS-01-LIFECYCLE]] (Stop gate, loop guard, skip flags, PYTHON_BIN resolver pattern).
- R5 divergence guard (bootstrap footgun): [[TECHDEBT-01-NOW]] R5 / D19.
- R2 (explicit sync pass requirement): [[TECHDEBT-01-NOW]] R2.
- Memory file pattern and metadata template: [[PATTERNS-01-CANONICAL]] Memory File Pattern.
- Agent tools allowlist (flow-memory-sync): [[CLAUDECODE-01-PLUGIN-CANON]] Subagent Matrix.
- Post-task sync workflow: [[FLOW-01-SDLC]].
- MCP transport (serena server): [[MCP-01-TRANSPORT]].
- ADR-0011 rationale: `docs/adr/0011-agent-instruction-knowledge-equivalence.md`.
