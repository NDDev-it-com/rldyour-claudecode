# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and marketplace/plugin versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.1] - 2026-05-16

### Fixed

- **Reviewer subagent output transport (D29, R6)** — Claude Code 2.0.77+
  has a confirmed regression where `task.output` from a subagent can be
  returned to the parent session as the full JSONL transcript (up to
  200-500 KB) instead of the final assistant text (~500 bytes), and
  combined results from multiple subagents can overflow the parent
  context and crash the session. The regression is documented in
  Anthropic issues
  [#16789](https://github.com/anthropics/claude-code/issues/16789),
  [#20531](https://github.com/anthropics/claude-code/issues/20531), and
  [#23463](https://github.com/anthropics/claude-code/issues/23463), all
  closed as "not planned". This wave adopts the Anthropic-suggested
  workaround from `#23463` ("cap agent result sizes and write full
  results to a file with summary + path") for every reviewer track in
  this marketplace.

### Changed

- `plugins/rldyour-flow/references/reviewer-protocol.md` gained an
  **Output Transport** section defining the file-first contract:
  orchestrator generates one `run_id = <UTC-ISO-compact>-<git-short-sha>`
  per review wave and `report_dir = .serena/reviews/<run_id>/`, injects
  both into every reviewer prompt; each reviewer writes the full
  long-form report to `<report_dir>/<reviewer-name>.md` via `Bash`
  (`mkdir -p` + `cat` heredoc) and returns a compact summary ≤ 4 KB
  containing `Report:` path, `Counts:` by severity, and `All findings`
  one-liner with hard cap 30 entries (`... +M more findings in report
  file` when total exceeds 30).
- All six reviewer agents
  (`plugins/rldyour-flow/agents/flow-architecture-review.md`,
  `flow-quality-review.md`, `flow-consistency-review.md`,
  `flow-integration-review.md`, `flow-verification-review.md`,
  `flow-security-review.md`) replaced their inline `Output Format`
  section with an `Output Transport` block citing the new protocol.
  `flow-security-review` keeps OWASP/ASVS `Category`, `Attack path`, and
  `Verification` fields in the long-form report and surfaces only the
  category bracketed in the one-liner; secret redaction applies to both
  the summary and the report file.
- `plugins/rldyour-flow/skills/ry-start/SKILL.md` and
  `plugins/rldyour-flow/skills/ry-review/SKILL.md` gained
  orchestrator-side `Output Transport` sections describing `run_id`
  generation, report-dir creation, prompt injection, summary
  aggregation, targeted `Read` of report files for critical/high
  findings, and writing a consolidated `<report_dir>/_summary.md`
  cross-track artefact.
- `.gitignore` adds `.serena/reviews/` alongside the existing
  `.serena/cache/` and `.serena/diagnostics/` runtime-artefact entries.
  Fullrepo policy unchanged — `.serena/reviews/` is not in
  `AGENT_ONLY_PATTERNS` in
  `plugins/rldyour-flow/scripts/fullrepo_sync.py`, so it stays regular
  gitignored content and is not fullrepo-managed.
- `plugins/rldyour-flow/.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json` `rldyour-flow` entry bumped
  `0.2.0` → `0.2.1` to invalidate the per-plugin runtime cache
  (`~/.claude/plugins/cache/rldyour-claudecode/rldyour-flow/0.2.1/`).
  Marketplace `VERSION` bumped `0.2.0` → `0.2.1` to mark the patch
  release boundary. All other plugins stay at `0.2.0`.

### Notes

- Read-only invariant for reviewer subagents is unchanged: `Edit`,
  `Write`, and `NotebookEdit` remain absent from every reviewer
  `tools:` allowlist. `Bash` continues to be the only write-capable
  mechanism, and the new contract uses it solely to write reviewer
  result files under `.serena/reviews/<run_id>/`; it cannot reach
  project source. `scripts/validate_agent_tools.py` continues to pass
  with all 8 agent files validated.
- Reviewer agents that face a read-only filesystem (sandbox, restored
  worktree without write access) fall back to inline summary-only
  output with `Notes: filesystem-readonly`, still respecting the 4 KB
  summary cap.
- Done criteria: `claude plugin validate plugins/rldyour-flow` passes;
  `python3 scripts/validate_plugin_versions.py` reports `rldyour-flow
  0.2.1` and all other plugins `0.2.0`; `python3
  scripts/validate_instruction_docs.py --require-agent-docs` confirms
  `AGENTS.md` and `.claude/CLAUDE.md` line budgets remain under 200;
  `bash scripts/validate_marketplace.sh` runs cleanly end-to-end.

## [0.2.0] - 2026-05-16

### Changed

- **Marketplace + all 9 plugins synchronised to `0.2.0`** — first
  MINOR-line boundary that consolidates the Wave 1-5 series into a
  single release tag set. No plugin runtime files added or modified
  relative to 0.1.9; the bump invalidates the per-plugin runtime cache at
  `~/.claude/plugins/cache/rldyour-claudecode/<plugin>/<version>/` so the
  operator picks up all marketplace-level hardening that accumulated
  through Waves 4-5. Plugin version transitions:
  `rldyour-mcps` 0.1.3 → 0.2.0,
  `rldyour-explore` 0.1.3 → 0.2.0,
  `rldyour-serena-mcp` 0.1.5 → 0.2.0,
  `rldyour-flow` 0.1.4 → 0.2.0,
  `rldyour-security` / `rldyour-browser` / `rldyour-design` /
  `rldyour-lsps` / `rldyour-rules` all 0.1.2 → 0.2.0. Marketplace
  `VERSION` 0.1.9 → 0.2.0. `.claude-plugin/marketplace.json` plugin
  entries aligned. Tags created via `claude plugin tag --push` per
  plugin plus `marketplace--v0.2.0` for the marketplace boundary.

- **Wave 1-2 consolidation** — Conventional Commits discipline, strict-mode propagation
  to 14 utility/plugin scripts, prompt-injection markers expanded to 13+
  families with `re.IGNORECASE | re.UNICODE`, branch-name two-gate
  validation, agent `tools:` allowlist invariant via
  `scripts/validate_agent_tools.py`.
- **Wave 3 consolidation** — Serena memory base extended into the project brain: 8 new
  topic memories (`PHILOSOPHY-01-QUALITY-FIRST`, `PATTERNS-01-CANONICAL`,
  `BROWSER-01-WORKFLOW`, `DESIGN-01-WORKFLOW`, `EXPLORE-01-RESEARCH`,
  `LSPS-01-LANGUAGE-SERVERS`, `RULES-01-POLICY`, `SECURITY-01-OWASP`).
- **Wave 4 consolidation** — `bootstrap_check.sh` agent-only divergence guard (R5
  closure as `D19`), `.aider*` glob expansion at runtime, `WARN` to
  stderr for `RLDYOUR_FORCE_BOOTSTRAP=1` bypass and `git fetch`
  failures, `scripts/smoke_bootstrap_check.sh` with 7 assertions plus
  `AGENT_ONLY_PATHS` bash↔python drift detector, 18 memories
  cross-linked into a bidirectional `[[wikilinks]]` graph (≤2 hops from
  `CORE-01-INDEX`), OWASP Top 10:2025 (Final 2025-11-06) + ASVS 5.0.0
  precision, `TECHDEBT-01-NOW` Source Of Truth (11 anchors), D19-D23
  closures.
- **Wave 5 consolidation** — repository transferred from `rldyourmnd/rldyour-claude`
  to `NDDev-it-com/rldyour-claudecode` (private). Marketplace slug
  renamed to `rldyour-claudecode`. CI hardening per OWASP A01:2025 +
  A03:2025: SHA-pinned `actions/checkout@v6.0.2`,
  `actions/setup-{node,python}@v6.x`,
  `step-security/harden-runner@v2.19.3`, top-level `permissions: {}` +
  per-job read-only, concurrency cancel-in-progress, harden-runner
  egress audit, Claude Code CLI pinned to `@anthropic-ai/claude-code@2.1.143`.
  New workflows `actionlint.yml` (SHA256-verified
  `rhysd/actionlint@v1.7.12`), `semgrep.yml` (`semgrep/semgrep:1.163.0`
  Docker image with OSS packs `p/python, p/github-actions,
  p/security-audit, p/secrets, p/owasp-top-ten, p/ci`),
  `dependabot.yml` (monthly grouped github-actions updates).

### Notes

- **No plugin runtime files added or modified in this release.** All hooks,
  skills, agents, slash commands, references, and scripts retain their
  Wave 5 state byte-for-byte. The bump is purely a cache-invalidation +
  tag boundary — same pattern Anthropic uses for minor-version bumps that
  consolidate doc and CI improvements without behavior change.
- **Done criteria for 0.2.0** (operator-verifiable):
  - `bash scripts/validate_marketplace.sh` passes (incl.
    `smoke_bootstrap_check.sh`, `smoke_hooks.sh`,
    `smoke_serena_memory_taxonomy.sh`).
  - `python3 scripts/validate_plugin_versions.py` reports 9 plugins at
    0.2.0 aligned with `.claude-plugin/marketplace.json`.
  - `git tag --list 'rldyour-*--v0.2.0'` returns 9 plugin tags;
    `git tag --list 'marketplace--v0.2.0'` returns the marketplace tag.
  - CI workflows on the release commit: `validate`, `semgrep`,
    `dependency-check` green. `actionlint` is skipped by its
    path-filter on pure version-bump commits (no
    `.github/workflows/**` changes) — the last green `actionlint` run
    is on `334fe09` where workflow YAML was last touched. This is
    intentional and documented; not a regression.
  - Fullrepo branch republished with `tracked_agent_paths: []` and
    R5 guard reporting `OK agent-only files match origin/fullrepo`.
  - Serena memories `RELEASE-01-VALIDATION` + `TECHDEBT-01-NOW` updated
    via `flow-memory-sync` subagent against the new HEAD SHA.

## [0.1.9] - 2026-05-16

### Changed

- **Wave 5 — CI hardening + org transfer** (repository moves from
  `rldyourmnd/rldyour-claude` to `nddev-it-com/rldyour-claudecode`,
  private visibility preserved).
  - **SHA-pinned actions** per OWASP A03:2025 supply-chain hardening.
    `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd` (v6.0.2),
    `actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e` (v6.4.0),
    `actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405` (v6.2.0),
    `step-security/harden-runner@ab7a9404c0f3da075243ca237b5fac12c98deaa5`
    (v2.19.3), `github/codeql-action@f411752efdf656cb71aa17b755b22c890960da1d`
    (v3.35.5). Tag-to-SHA refresh procedure documented in workflow file headers.
    Closes Wave 4 security F-3 (LOW 90).
  - **Top-level `permissions: {}`** deny-all default + per-job read-only grants
    per OWASP A01:2025 least-privilege.
  - **Concurrency group** cancels redundant runs on the same ref across all four
    workflows.
  - **harden-runner egress audit** at the start of every job — surfaces
    unexpected outbound network calls in the GitHub Security tab.
  - **Claude Code CLI pinned**: `npm install -g @anthropic-ai/claude-code@2.1.143`
    (was unpinned). Closes Wave 4 security F-5 (INFO 35).
  - **New `.github/workflows/semgrep.yml`** — SAST via Semgrep OSS rules
    (Docker image `semgrep/semgrep:1.163.0`, matches the MCP server pin).
    Runs `semgrep scan --config=auto --error --metrics=off` on push, PR,
    and weekly schedule. Replaces an initial CodeQL workflow that required
    GitHub Advanced Security (paid add-on, not available for this repo's
    plan); Semgrep runs as a CLI without GHAS and fails CI on
    WARNING/ERROR-severity findings.
  - **New `.github/workflows/actionlint.yml`** — workflow YAML linter using
    `rhysd/actionlint` v1.7.12 binary, SHA256-verified against upstream
    `checksums.txt` (`8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8`).
  - **New `.github/dependabot.yml`** — monthly `github-actions` ecosystem
    updates, grouped minor+patch bumps, max 5 open PRs.
  - **Python AST + JSON parse checks** in `validate.yml` now use `fail=1` +
    `sys.exit(fail)` instead of fail-first behavior, surfacing all failures
    in a single CI run.
  - **Repo URL updates**: 9 plugin manifests (`homepage` + `repository`),
    `install-rldyour-marketplace.sh` (`NEW_MARKETPLACE_SOURCE`),
    `docs/rollback-restore.md` clone URL all point to
    `nddev-it-com/rldyour-claudecode`.
  - **Marketplace slug rename**: `.claude-plugin/marketplace.json` `name` field
    `rldyour-claude` → `rldyour-claudecode`. README install commands updated
    (`@rldyour-claudecode` suffix). Plugin install one-liners updated.
  - **Title updates**: `README.md`, `AGENTS.md`, `.claude/CLAUDE.md`,
    `docs/release-process.md`, plugin README descriptions.
  - **GitHub redirect**: old `github.com/rldyourmnd/rldyour-claude` URL
    auto-redirects to the new location for ~12 months. No external consumer
    notification required (personal marketplace per `.claude/CLAUDE.md`).

### Notes

- No plugin runtime files changed. No plugin `plugin.json` version bumps needed.
  `VERSION` 0.1.8 → 0.1.9 reflects marketplace-level changes (CI hardening +
  org transfer + slug rename).
- Local directory will be renamed `rldyour-claude` → `rldyour-claudecode`
  after the transfer completes; local origin remote updated to
  `git@github.com:nddev-it-com/rldyour-claudecode.git`.
- `bash scripts/validate_marketplace.sh` passes all gates including the new
  hardened workflows verified by `yaml.safe_load` parse.
- `~/.claude/plugins/cache/rldyour-claudecode/...` is the new cache path.
  Existing users (only the owner) re-run `claude /plugin marketplace add
  nddev-it-com/rldyour-claudecode` to migrate.

## [0.1.8] - 2026-05-16

### Changed

- **Wave 4 polish — R5 hardening + memory graph + research precision** (continues Wave 3
  vision: "Serena memories — мозг проекта" with quality-first / scalability-first
  defaults). Closes 6 deferred items from Wave 3 audit plus 21 findings from 6 parallel
  reviewer subagents (architecture, quality, consistency, integration, verification,
  security):
  - **R5 hardening (was open in TECHDEBT-01, now D19)**: `scripts/bootstrap_check.sh`
    new pre-`--bootstrap-init` divergence guard. For each agent-only path root,
    `git cat-file -e origin/fullrepo:$file` + `cmp -s $file <(git show ...)` detects
    content drift and refuses to proceed if local edits would be silently overwritten.
    Override via `RLDYOUR_FORCE_BOOTSTRAP=1` (now `WARN ... BYPASSED` to stderr, was
    `INFO` to stdout — closes Wave 4 security F-2, conf 70). `.aider*` glob expansion
    via `shopt -s nullglob` covers `.aiderignore` / `.aider.conf.yml` / etc. that the
    earlier literal `.aider` entry missed (closes Wave 4 quality+integration F-1,
    conf 90). `git fetch` failure emits explicit `WARN ... possibly stale local ref`
    instead of `|| true` silent swallow (closes Wave 4 quality F-2, conf 85).
    Sync-contract comment clarifies `fullrepo_sync.py` `AGENT_ONLY_PATTERNS` is the
    canonical full list, not `SKILL.md` (which covers only downstream minimal subset).
  - **R5 test coverage**: new `scripts/smoke_bootstrap_check.sh` asserts all 4 R5
    guard code paths (static), `.aider*` glob expansion wiring, `AGENT_ONLY_PATHS`
    bash array vs `AGENT_ONLY_PATTERNS` python tuple count drift `<=5`, and runtime
    path-(a) bypass behavior (extracted guard block + `RLDYOUR_FORCE_BOOTSTRAP=1`
    asserts WARN to stderr + sentinel reached). Closes Wave 4 verification F-1
    (HIGH, conf 90) and grounds Wave 4 architecture Q2.
  - **SC2044 portability**: `scripts/validate_marketplace.sh` and
    `.github/workflows/validate.yml` two-loop refactor from `for f in $(find ...)`
    to `while IFS= read -r -d '' f; do ... done < <(find ... -print0)`. Handles
    paths with spaces, newlines, and shell metacharacters safely (shellcheck SC2044
    compliance).
  - **CI/local parity**: `scripts/validate_marketplace.sh` wires `smoke_hooks.sh` to
    match CI (closes Wave 4 integration F-3 CI/local asymmetry, LOW 95) plus
    `smoke_bootstrap_check.sh` as new gate. CI also gains the new bootstrap smoke.
  - **Memory graph completion** (`.serena/memories`): 7 pre-existing memories
    (CLAUDECODE-01, MCP-01, SERENA-01, HOOKS-01, DOCS-01, RELEASE-01, TECHDEBT-01)
    gained `## Cross-References` with 8-9 anchored `[[wikilinks]]` each. Combined
    with Wave 3's 8 new memories + back-edges added to PATTERNS-01-CANONICAL, the
    full 18-memory graph is bidirectional with BFS reachability `<=2` hops from
    `CORE-01-INDEX` to every memory; link count 7-53 per file (TECHDEBT-01 D20).
  - **TECHDEBT-01 Source Of Truth**: new `## Source Of Truth` section in
    `.serena/memories/TECHDEBT-01-NOW.md` lists 11 canonical anchors (commit SHAs,
    analyzer scripts, hook scripts, `fullrepo_sync.py`, `.mcp.json` + config,
    smoke scripts, validators, `INJECTION_MARKERS` regex location, bootstrap guard).
    Every D/R entry now anchors to a verifiable code/commit/test source per
    `PHILOSOPHY-01-QUALITY-FIRST` scientific-anchoring principle (TECHDEBT-01 D21).
  - **OWASP Top 10:2025 precision**: `.serena/memories/SECURITY-01-OWASP.md` updated
    from generic "OWASP Top 10 2025 revision" to authoritative "OWASP Top 10:2025
    (Final, released 2025-11-06 at Global AppSec DC by Tanya Janca and Neil
    Smithline)" with canonical URL `https://owasp.org/Top10/2025/` and paired ASVS
    5.0.0 (released 2025-05-30) reference. Added trajectory detail (A03:2025 from
    A06:2021 community vote 50% #1), A10:2025 24 CWEs replacing SSRF, and full
    A07/A08/A09 rename history. Sourced from `ry-explore` cross-validation across
    owasp.org, GitHub OWASP/Top10 `SUPERSEDED` README marker, TripWire 2025
    advisories (TECHDEBT-01 D22).
  - **R6 (new, open)**: `AGENT_ONLY_PATHS` bash array vs `AGENT_ONLY_PATTERNS`
    python tuple manual synchronization. Mitigation: smoke drift detector with
    tolerance `<=5`. Future hardening: generate bash array from python via
    `--list-agent-only-patterns` CLI flag (deferred — smoke gate sufficient at
    current scale).
- **Deferred to Wave 5** (acknowledged, not blocking 0.1.8): GitHub Actions SHA
  pinning (security F-3, LOW 90 — `actions/checkout@v5` and `actions/setup-{node,
  python}@v5` use mutable tags), `npm install -g @anthropic-ai/claude-code` pinning
  (security F-5, INFO 35), symlink handling in `cmp -s` content compare (quality
  F-3, LOW 80), `flow-memory-sync` ↔ `session_start_*` path sanitization variant
  (security F-1, LOW 55).

### Notes

- No plugin runtime files changed. No plugin `plugin.json` version bumps needed.
  Marketplace boundary version `VERSION` 0.1.7 -> 0.1.8 reflects R5 hardening,
  smoke coverage addition, and memory graph completion.
- `bash scripts/validate_marketplace.sh` passes all 18 steps including new
  bootstrap R5 smoke. `bash scripts/smoke_bootstrap_check.sh` reports 7/7 OK.

## [0.1.7] - 2026-05-16

### Changed

- **Wave 2 polish — "идеально выточенная система" (single seamless mechanism)**:
  - **Tier 1 (critical fixes)**: cross-plugin path in `flow-post-task-sync` SKILL replaced
    with `$(git rev-parse --show-toplevel)` (cwd-independent; `${CLAUDE_PROJECT_DIR}` is
    documented only for hook commands and stdio MCP env, not for skill execution context).
    New `scripts/validate_agent_tools.py` enforces agent `tools:` allowlist invariants
    (built-in tool names, MCP wildcard discipline, read-only-by-design MCP set).
    TECHDEBT-01-NOW.md gained R4 (non-Serena MCP wildcard future-proofing) and R5
    (bootstrap_check.sh footgun documentation).
  - **Tier 2 (consistency + observability)**: 14 utility/plugin scripts gained
    `IFS=$'\n\t'` + `unset CDPATH` after `set -euo pipefail` — 9 root `scripts/*.sh`
    (smoke_hooks, smoke_fullrepo_sync, smoke_mcp_capabilities, smoke_mcp_runtime,
    smoke_serena_memory_taxonomy, sync_fullrepo_branch, validate_marketplace,
    collect_diagnostics, install_local_git_hooks) plus 5 plugin scripts
    (`plugins/rldyour-flow/scripts/{detect_project_checks,git_sync_audit,
    local_git_ai_guard}.sh`, `plugins/rldyour-lsps/scripts/install_lsps_brew.sh`,
    `plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh`). Pattern matches
    existing gold standard in `scripts/install-rldyour-marketplace.sh`.
    CI workflow `.github/workflows/validate.yml` extended with 3 new steps in
    syntax-checks job: Agent tools allowlist validation, Hook lifecycle smoke,
    Serena memory taxonomy smoke. No `fetch-depth: 0` — current smokes don't need it.
  - **Tier 3 (defensive security)**: `scripts/worktree_add.sh` adds `git
    check-ref-format --branch` as second gate after the conservative regex
    `^[A-Za-z0-9._/-]{1,255}$` — rejects refs the regex accepts but git refuses
    (`-/foo`, `/foo`, `feat/../etc/passwd`, double slash, etc.) as defence-in-depth
    against future caller-misuse. `plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh`
    expanded prompt-injection markers from 3 to 13+ families including Llama/Mistral
    `[INST]`/`<<SYS>>`, Llama-3 `<|begin_of_text|>`/`<|end_of_text|>`, chat-template
    `<|user|>`/`<|assistant|>`, Markdown `---system---`, role-play prefixes
    (`you are now`, `from now on`), and Russian-language equivalents (`[СИСТЕМА]`,
    `игнорируй все предыдущие инструкции`, `забудь предыдущие команды`, `теперь ты`).
    Regex flags upgraded to `re.IGNORECASE | re.UNICODE` for Cyrillic word boundaries.
  - **Tier 4 (polish)**: `scripts/smoke_hooks.sh` adds new "runtime stdin payloads" step
    with 6 test cases (empty/non-trigger/RU/EN prompt scenarios for `user_prompt_submit`,
    clean state for `stop_memory_sync`, non-git command for `post_tool_use_commit_advice`).
    SC2064 fixed (single-quoted trap to defer `$TMP` expansion).
    `scripts/bootstrap_check.sh` gains "git pre-push hook (advisory)" step that detects
    whether the rldyour pre-push guard is installed and suggests
    `scripts/install_local_git_hooks.sh --apply` when absent.

- **Plugin runtime versions**:
  - `rldyour-flow` bumped `0.1.3` → `0.1.4` (`flow-post-task-sync` SKILL.md changed
    — triggers `claude plugin update` cache refresh).
  - VERSION bumped `0.1.6` → `0.1.7` (release boundary; Wave 2 contains durable
    runtime and safety changes).
  - Other 8 plugins unchanged (shell scripts and hook bodies don't trigger plugin
    cache; hooks are re-read at subprocess invocation time).

### Security

- **Prompt-injection coverage gap closed (HIGH, conf 85)**:
  `post_tool_use_commit_advice.sh` now redacts 13+ marker families before echoing
  commit subject into LLM context. Covers Llama/Mistral instruction tags, Llama-3
  special tokens, chat-template tags, Markdown system prefix, English role-play
  prefixes, and Russian-language equivalents (project is Russian-leading per
  `AGENTS.md` Engineering Constraints — Russian-only attacks were entirely uncovered
  before this wave). Defence-in-depth, not a known active exploit fix.
- **BRANCH validation second gate (MEDIUM, conf 70)**: `git check-ref-format
  --branch` invocation in `scripts/worktree_add.sh` rejects refs git itself would
  refuse, providing dual validation layers (cheap regex + canonical git check).
- **Static MCP wildcard invariant**: `validate_agent_tools.py` enforces that
  read-only agents may only wildcard MCP servers in `READ_ONLY_BY_DESIGN_MCPS`
  (context7, deepwiki, grep, semgrep). Catches the entire D15-class confused-deputy
  pattern at PR/validation time, not at agent invocation time.

### Verification

- `bash scripts/validate_marketplace.sh` — full harness passes including new
  "Agent tools allowlist validation" step (8 agent files × 13 MCP servers).
- `bash scripts/smoke_hooks.sh` — passes including 6 new runtime stdin payload
  cases (verified parse safety with `IFS=$'\n\t'` changes from Wave 1+2).
- `bash scripts/bootstrap_check.sh` — passes including new pre-push hook advisory.
- Manual injection tests: `[INST]`, `[SYSTEM]`, `Игнорируй все предыдущие
  инструкции`, `теперь ты` — all redacted to `[REDACTED]` in `additionalContext`.
- Manual branch validation tests: `-/foo`, `feat/../etc/passwd`,
  `--upload-pack=evil` — all REJECT (regex layer + git check-ref-format layer);
  `feat/test-validation_v1.0` — ACCEPT, dry-run produces correct git command.
- 6 parallel reviewer subagents (architecture, quality, consistency, integration,
  verification, security) executed with self-contained prompts; 6 must-fix
  findings applied (Architecture F-1 + F-3, Consistency F-1, Integration F-2,
  Security F-1 + F-2). Remaining findings (Architecture F-2/F-4/F-6, Consistency
  F-2/F-3/F-4/F-5/F-6/F-7, Integration F-3/F-4, Security F-3/F-4) classified as
  defer / false-positive with documented rationale.

## [0.1.6] - 2026-05-15

### Changed

- **Agent tools migration (`disallowedTools` → explicit `tools:` allowlist)**:
  - All 6 `rldyour-flow` reviewer agents (`flow-architecture-review`, `flow-quality-review`, `flow-consistency-review`, `flow-integration-review`, `flow-verification-review`, `flow-security-review`) migrated to explicit positive allowlist.
  - `rldyour-explore/ry-explore` agent migrated to the same pattern.
  - Pattern follows canonical `anthropics/claude-plugins-official/plugins/pr-review-toolkit/agents/code-reviewer` — explicit allowlist for future-proof read-only enforcement (isolates these agents from any future edit-like tool that Claude Code might add).
  - Replaced broad `mcp__plugin_rldyour-mcps_serena__*` wildcard with an explicit 14-tool read-only Serena subset (`find_symbol`, `find_referencing_symbols`, `find_implementations`, `find_declaration`, `get_symbols_overview`, `search_for_pattern`, `read_file`, `list_dir`, `find_file`, `list_memories`, `read_memory`, `get_current_config`, `get_diagnostics_for_file`, `check_onboarding_performed`). The wildcard previously included Serena write tools (`create_text_file`, `replace_content`, `replace_symbol_body`, `insert_after_symbol`, `insert_before_symbol`, `rename_symbol`, `safe_delete_symbol`, `write_memory`, `edit_memory`, `delete_memory`, `rename_memory`) — the new explicit list eliminates that confused-deputy / prompt-injection risk for read-only reviewer and research agents.
  - `flow-security-review` additionally allows `WebFetch`, `WebSearch`, `mcp__plugin_rldyour-mcps_semgrep__*` for CVE lookups and SAST. Semgrep MCP wildcard kept (server exposes only scan/analysis tools).
  - `flow-memory-sync` intentionally retains `disallowedTools: [Edit, Write, NotebookEdit]` denylist (its `tools:` allowlist already grants Serena memory write tools needed for its canonical writer role; the denylist is defence-in-depth against project-file mutation).
  - Plugin version bumps: `rldyour-flow` `0.1.2` → `0.1.3` and `rldyour-explore` `0.1.2` → `0.1.3` (agent frontmatter affects runtime; bump triggers `claude plugin update` cache refresh).

- **Shell strict mode harmonization (defence-in-depth, no functional change)**:
  - 8 hook scripts in `plugins/rldyour-{flow,serena-mcp}/hooks/*.sh` and 3 root/plugin scripts (`scripts/worktree_add.sh`, `scripts/bootstrap_check.sh`, `plugins/rldyour-flow/scripts/deploy_readiness.sh`) gained `IFS=$'\n\t'` + `unset CDPATH` after `set -euo pipefail`.
  - Pattern matches existing gold-standard in `scripts/install-rldyour-marketplace.sh`.
  - `IFS=$'\n\t'` removes default space-word-splitting surprises in any unquoted expansion; `unset CDPATH` removes attacker-controlled-environment `cd` redirection risk.
  - Verified by `bash -n` + `scripts/smoke_hooks.sh` + manual stdin smoke: no regression.

- **Instruction docs expansion (cross-tool best practices, no `@import` redirection)**:
  - `AGENTS.md`: new `## Codex CLI Compatibility` section (OpenAI Codex CLI reads AGENTS.md, layered `~/.codex/AGENTS.md` + repository concatenation, Codex runs test commands listed in AGENTS.md before finishing); new `## Cross-Tool Support` section (Linux Foundation AAIF since `2025-12-09`, 30+ supported tools, 60k+ adopting repos per `https://agents.md/` as of May 2026); bilingual descriptions rationale in Engineering Constraints; HTML maintainer comment line cap raised `180` → `200`.
  - `.claude/CLAUDE.md`: new `## Anthropic Precedent Confirmations` section (7 verified canonical patterns with citations to `anthropics/claude-plugins-official` SHA `1a2f18b05cf5652fd25403e8d229fc884fb84103` + community precedents); `skillListingBudgetFraction` recommendation `0.03` → `0.04` (Sonnet 200K context truncates tail-end auto-trigger descriptions for bilingual entries averaging ~373-400 chars at 0.03 — 0.04 fits both 200K and 1M context); agent frontmatter spec updated (`tools:` allowlist primary, `disallowedTools:` legacy); v2.1.139 `args: string[]` exec-form decline expanded with verification evidence (none of Anthropic's own plugin hooks.json use exec-form either).

### Fixed

- Hook count drift across documentation: `AGENTS.md` Repository Layout, `.claude/CLAUDE.md` Plugins And Components, `plugins/rldyour-flow/README.md` What's inside, `README.md` Active Catalog corrected from `3 hooks` to `4 hooks` for `rldyour-flow` (4 registered hook scripts in `hooks.json`: 2× SessionStart + PostToolUse:Bash + Stop). The historical `3 hooks` count in `CHANGELOG.md [0.1.0]` is intentionally preserved as accurate-for-that-release.
- `CHANGELOG.md [0.1.1]`: env var name typo `WORKTREE_BASE_REF=HEAD` → `RLDYOUR_WORKTREE_BASE_REF=HEAD` to match actual code in `scripts/worktree_add.sh` and FLOW-01-SDLC Serena memory.
- `plugins/rldyour-mcps/README.md`: GitHub MCP rationale rephrased to avoid unsubstantiated "Copilot entitlement 403" framing; now describes the local stdio choice as "self-contained without dependence on `api.githubcopilot.com/mcp/`" with documented PAT scopes (`repo` + `read:org` are sufficient, no Copilot subscription required).
- `plugins/rldyour-flow/agents/flow-architecture-review.md` anti-pattern text now references `tools:` allowlist mechanism instead of stale `disallowedTools` description (aligns with own frontmatter and the other 5 reviewer agent bodies).
- `plugins/rldyour-flow/README.md` and `plugins/rldyour-explore/README.md` subagent listings updated to reflect new `tools:` allowlist (was still describing `disallowedTools` denylist).
- `plugins/rldyour-serena-mcp/README.md` `flow-memory-sync` description updated to mention both the explicit `tools:` allowlist (Serena memory write tools + read-only inspection tools) and the `disallowedTools` defence-in-depth layer.
- `AGENTS.md` Codex CLI Compatibility section: removed unverified `~/.codex/AGENTS.override.md` claim (not documented in official Codex docs or agents.md spec).
- `.claude/CLAUDE.md` Changelog Adoption section: `skillListingBudgetFraction` line hedged with explicit "Anthropic + claudekit-cli baseline `0.03`; this repo recommends `0.04`" so the changelog note doesn't contradict the Skill Listing Budget section above it.

## [0.1.5] - 2026-05-15

### Changed

- `plugins/rldyour-serena-mcp`:
  - Standardized Serena memory taxonomy on numbered topic files (`AREA-01-SLUG.md`)
    with `CORE-01-INDEX.md` as the required navigation map.
  - Bumped analyzer payload to `analysis.schema_version = 2` and added
    `analysis.memory_taxonomy` so hooks, skills, and the `flow-memory-sync`
    subagent share one memory naming and split contract.
  - Updated `analyze_sync_scope.py` memory targets from broad legacy memory names
    to canonical topic files such as `SERENA-01-MEMORY-SYNC.md`,
    `HOOKS-01-LIFECYCLE.md`, `FLOW-01-SDLC.md`, `MCP-01-TRANSPORT.md`,
    `DOCS-01-INSTRUCTIONS.md`, `RELEASE-01-VALIDATION.md`, and
    `TECHDEBT-01-NOW.md`.
  - Added `CLAUDECODE-01-PLUGIN-CANON.md` targeting for plugin component and
    instruction contract changes.
  - Fixed memory freshness gating so agent-instruction-only commits (`AGENTS.md`,
    `.claude/**`, `.agents/**`, and similar instruction files) require memory sync
    instead of being treated as knowledge-only no-ops.
  - Updated Stop-hook guidance and memory-sync instructions so sync runs maintain
    the index, split broad files, and keep stable numbering instead of appending
    unrelated facts to catch-all memories.
  - Made `serena_memory_state.py` scan `.serena/memories/**/*.md` so future nested
    topic layouts remain freshness-aware.
  - Aligned `commit_serena_knowledge.sh` runtime-marker filtering with flow sync
    markers (`.serena/.flow_sync_marker`, `.serena/.flow_post_task_state.json`).
  - Hardened `commit_serena_knowledge.sh` so fullrepo-managed stale memories are
    refused instead of acknowledged with an empty tracked diff.
  - Added `scripts/smoke_serena_memory_taxonomy.sh` and wired it into
    `scripts/validate_marketplace.sh` to assert analyzer schema/targets, nested
    memory scanning, Stop-hook taxonomy advisory, agent-instruction sync markers,
    and fullrepo-managed acknowledgement behavior.
  - Bumped plugin version to `0.1.5` in plugin manifest and marketplace entry.
- Migrated project Serena memories from broad dated filenames to the numbered
  topic taxonomy and synchronized agent-only `AGENTS.md` / `.claude/CLAUDE.md`
  with the new memory-brain contract.

## [0.1.4] - 2026-05-15

### Changed

- `plugins/rldyour-serena-mcp`:
  - Added `scripts/analyze_sync_scope.py` impact analysis and persisted analysis payload in
    `.serena/.serena_sync_state.json` for deterministic, low-noise memory-sync targeting.
  - Updated hook pipeline so `mark_sync_required.sh` stores `non_knowledge_changed_files`,
    `analysis.areas`, and `analysis.memory_targets`; `stop_memory_sync.sh` prints analysis context
    (risk profile/high-priority areas/memory targets) when stale.
  - Expanded analyzer coverage for agent-only instruction paths, plugin commands, MCP transport,
    MCP runtime config, release/version files, and repository docs.
  - Ensured empty commit ranges produce empty memory targets to avoid no-op sync noise.
  - Bumped plugin version to `0.1.4` in plugin manifest and marketplace entry.
- Refined `.serena/memories/serena_memory_sync_protocol_2026-05.md` as a durable protocol memory for
  Serena lifecycle, marker payload contracts, and memory-sync execution rules.
- Synchronized `AGENTS.md` and `.claude/CLAUDE.md` with current hook/flow dependency contracts and
  Claude Code v2.1.142 documentation facts.

## [0.1.3] - 2026-05-15

### Changed

- `plugins/rldyour-mcps/.mcp.json` updated MCP runtime pins to latest verified:
  - `chrome-devtools-mcp` `0.25.0` → `0.26.0`
  - `semgrep` `1.162.0` → `1.163.0`
- `config/mcp-runtime-versions.env` aligned with MCP pin updates.
- `plugins/rldyour-mcps/README.md` updated transport documentation for GitHub MCP stdio transport and current CC context behavior note.
- `AGENTS.md` and `.claude/CLAUDE.md` synchronized with local Claude Code `v2.1.142` and verified MCP pin set.
- `plugins/rldyour-mcps` version bumped to `0.1.3` in both `plugin.json` and marketplace manifest to ensure cache refresh on `claude plugin update`.

## [0.1.2] - 2026-05-13

Hotfix for GitHub MCP server: the previous `https://api.githubcopilot.com/mcp/` HTTP endpoint is entitlement-gated and returns `HTTP 403 "unauthorized: not authorized to use this Copilot feature"` for accounts without an active GitHub Copilot allowlist, even when the bearer PAT is otherwise valid. Switched to the canonical local stdio transport via the Homebrew-installed `github-mcp-server` binary (v1.0.4, released 2026-05-11), which works with a standard `gho_*`/`github_pat_*` PAT and exposes 39 tools by default (`repos,issues,pull_requests,users,context` toolset). Cache-bump release so users get the new `.mcp.json` on `claude plugin update`.

### Fixed

- `plugins/rldyour-mcps/.mcp.json` `github` entry rewritten from HTTP transport (`api.githubcopilot.com/mcp/`, Copilot-gated) to local stdio `github-mcp-server stdio --toolsets=repos,issues,pull_requests,users,context` with `GITHUB_PERSONAL_ACCESS_TOKEN` env. Requires `brew install github-mcp-server` (or equivalent) on PATH; minimum version v1.0.4. PAT scopes: `repo` + `read:org` (Copilot subscription not required).
- `scripts/smoke_mcp_capabilities.sh` no longer blanket-passes HTTP 401/403 for `HTTP_AUTH_GATED` servers — that shortcut hid the exact 403 entitlement-denial above. Now performs a real MCP `initialize` JSON-RPC handshake against HTTP endpoints, parses both `application/json` and `text/event-stream` response bodies, checks `result.serverInfo.name`, and classifies failures: 401 without auth → SKIP (reachable, no creds), 401 with auth → FAIL (token rejected), 403 → FAIL with explicit "switch to stdio github-mcp-server" hint, 200 without `serverInfo` → FAIL (silent-misconfig catch). Sends canonical `MCP-Protocol-Version` header. `figma` remains in `HTTP_AUTH_GATED` (accepts 200 without `serverInfo` until session id is established); `github` removed because it is now stdio.

### Changed

- `scripts/check_mcp_runtime_versions.py` gained a `SYSTEM_BINARY_TO_ENV` track that probes host binaries via `<binary> --version` and enforces parity with the env pin. Used for `github-mcp-server`. Missing binary on PATH reports `INFO` (not `FAIL`) so CI without Homebrew does not regress. Drift between local binary and env pin reports `FAIL` with a `brew upgrade` hint.
- `config/mcp-runtime-versions.env`: added `GITHUB_MCP_SERVER_VERSION=1.0.4`; removed `GITHUB_MCP_URL` (no longer HTTP). Comment block expanded to document system-binary servers (github, dart-flutter).

### Removed

- `GITHUB_MCP_URL` env entry and the corresponding `github → HTTP_TO_ENV` row in `check_mcp_runtime_versions.py`. The HTTP-transport pattern for github MCP is preserved in `anthropics/claude-plugins-official` for Copilot users; we cannot use it without an allowlist.

## [0.1.1] - 2026-05-12

Release boundary cut after the 2026-05-08..2026-05-12 wave of best-practice, MCP-runtime, capability-smoke, serena-bump, audit and worktree-workflow commits accumulated in the `[Unreleased]` block. Bumps every plugin from `0.1.0` to `0.1.1` so that the Claude Code plugin cache at `~/.claude/plugins/cache/rldyour-claude/<plugin>/<version>/` actually refreshes on next `claude plugin update` (cache compares plugin.json `version` strings, so content-only changes under the same version are silently ignored by the user-facing runtime).

### Changed

- Bumped pinned MCP runtime versions after manual launcher smoke
  (release notes verified via GitHub Releases on 2026-05-12):
  - `@playwright/mcp` `0.0.74` → `0.0.75` (bug fixes: serialize shared browser
    launch in `--isolated`, forward browser-level CDP commands in extension
    mode; we use neither, low risk).
  - `@upstash/context7-mcp` `2.2.4` → `2.2.5` (accept hallucinated arg names
    on `tools/call` requests; backwards-compatible quality fix).
  - `semgrep` `1.161.0` → `1.162.0` (taint tracking through nested functions,
    ~5x faster JSON rule parsing; backwards-compatible).
- `scripts/check_mcp_runtime_versions.py` now also enforces URL parity for
  the `github` HTTP MCP server (added `GITHUB_MCP_URL` to env file and to
  `HTTP_TO_ENV`). Closes a tracking gap left by 47387ee when github moved
  from stdio to HTTP transport.

- `serena-agent` `1.2.0` → `1.3.0` (released 2026-05-11). The 81-commit
  delta includes new LSP tools (`find_declaration`, `find_implementations`,
  `get_diagnostics_for_file`, `get_diagnostics_for_symbol`), Ada/SPARK and
  Angular/HTML/SCSS experimental language support, the "Revamp mode
  selection" mode-system refactor, and BSL/Lombok improvements. Breaking
  change for `project.yml`: `base_modes` override is replaced by
  `added_modes`. We do not override `base_modes` in `.serena/project.yml`,
  so the bump is non-breaking for this marketplace. CLI flag `--context=agent`
  is preserved; `mcp__plugin_rldyour-mcps_serena__*` tool surface narrows
  from 45 to 28 tools under `agent` context (the mode refactor scopes tool
  exposure more tightly per context). `scripts/smoke_mcp_capabilities.sh`
  passed 13/13 servers post-bump on 2026-05-12.
- Stop hooks restored to advisory enforcement gates: hooks compute
  machine-readable state and block Stop with `exit 2` when work remains, but
  do not perform high-blast-radius git operations (push, merge, force-with-lease,
  branch deletion). Those operations belong to the `flow-post-task-sync` skill
  executor under model judgement.
- `reviewer-protocol.md` documents the canonical effort/maxTurns/color matrix
  for reviewer subagents and the `+6 turns` security-track variant-hunt rule.

### Added

- Worktree workflow:
  - `plugins/rldyour-flow/hooks/session_start_worktree_bootstrap.sh` —
    `SessionStart` hook (timeout 30s) that detects a fresh worktree
    (missing AGENTS.md / .claude/CLAUDE.md / .serena/project.yml marker)
    and auto-runs `fullrepo_sync.py --restore` to install the
    per-worktree `.git/info/exclude` block and check out agent-only
    paths from `origin/fullrepo`. Skip via
    `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1`. The hook never publishes,
    never mutates origin.
  - `scripts/worktree_add.sh` — one-step helper for the manual
    `git worktree add` flow: detects whether the branch is local /
    remote / new, runs `git worktree add` with the right ref, then
    bootstraps agent-only context. Supports `RLDYOUR_DRY_RUN=1` and
    `RLDYOUR_WORKTREE_BASE_REF=HEAD` to mirror Claude Code's
    `worktree.baseRef: "head"` setting.
  - AGENTS.md "Worktree Workflow" section documenting the manual + auto
    flow, the Claude Code v2.1.139 `worktree.{baseRef,symlinkDirectories,
    sparsePaths}` settings, and the maintenance contract (per-worktree
    `.serena/memories/`, reconciled via `flow-post-task-sync` publish).
- `scripts/smoke_mcp_capabilities.sh` — capability-level smoke harness.
  Spawns each pinned MCP server (stdio) or POSTs to its endpoint (HTTP),
  performs the JSON-RPC `initialize` + `tools/list` handshake, and asserts
  a non-empty tool set. Supports `--server <name>` for targeted probes,
  `--timeout <s>` for slow cold-starts, and `--skip-uvx` for fast CI
  subsets. Servers requiring credentials (`CONTEXT7_API_KEY`,
  `GITHUB_PERSONAL_ACCESS_TOKEN`) are SKIPped when env is absent rather
  than FAILing. Auth-gated HTTP endpoints (figma, github) accept 401/403
  as a passing handshake.
- Root-level public files: `README.md`, `CHANGELOG.md`, `VERSION`, `LICENSE`.
- Operations harness adapted to Claude Code conventions: marketplace
  validation script (`scripts/validate_marketplace.sh`), smoke tests for
  hooks / MCP runtime / fullrepo / branch-cleanup, scheduled MCP runtime
  pin freshness CI (`.github/workflows/dependency-check.yml`), plugin-version
  validator, instruction-docs validator, skill-routing policy tests, release
  manifest, runtime-version drift check, diagnostics collection, local git
  pre-push guard installer.
- `docs/` reference set for release process, rollback/restore, dependency updates,
  observability.
- `config/` directory: `mcp-runtime-versions.env` (canonical pinned launcher versions
  outside `.mcp.json`), `skill-routing-policy.json` (deterministic Russian/English
  prompt routing tests).
- Per-plugin `README.md` for the nine first-party plugins.
- `statusMessage` field on Stop/PostToolUse/SessionStart hook handlers for
  user-visible runtime indicators while hooks fire.
- `flow-memory-sync` plugin-shipped subagent with anti-hallucination contract
  (source-of-truth hierarchy code > tests > git diff > existing memories;
  citation per claim; removal-first principle; narrow tools — Serena memory
  MCP plus read-only Bash/Read/Grep/Glob; `disallowedTools: [Edit, Write,
  NotebookEdit]`). Invoked by orchestrator from Stop hook advisory.

### May-2026 best-practice waves (2026-05-08, applied incrementally on `main`)

- `optimize/may-2026-best-practices` (3fe9005..2e22652, 6 commits): unified
  reviewer subagent frontmatter, ×3 maxTurns increase to compensate MCP-rich
  toolsets, distinct colors per reviewer, `$schema` switched to SchemaStore
  canonical URL, serena MCP `alwaysLoad: true`, explicit `allowed-tools` on
  10 skills, `disable-model-invocation: true` on `ry-deploy` and `ry-newp`,
  reviewer-protocol aligned.
- `docs/canonical-may2026` (ca13470, 1 commit): aggressive `.claude/CLAUDE.md`
  rewrite (206 → 124 lines, removed duplicates with `AGENTS.md`), Skill Listing
  Budget section moved exclusively to CLAUDE.md (Claude Code-specific concern),
  HTML maintainer comments added (stripped from agent context per CC v2.1.72).
  Body fix `ry-explore.md` `maxTurns: 30 → 90` to match frontmatter.
- `polish/deferred-findings` (3ce7970..f23765d, 3 commits): `allowed-tools`
  on 4 of 5 design skills, `disable-model-invocation` on audit skills
  `ry-rules-review` and `ry-sec-review`, documented `maxTurns: 36/42` rationale
  in `reviewer-protocol.md`.
- `feat/memory-sync-subagent` (772f6e8, 1 commit): `flow-memory-sync` subagent
  introduced.

## [0.1.0] - 2026-05-07

### Added

- Initial controlled Claude Code marketplace with nine first-party plugins —
  `rldyour-mcps` (MCP transport, 13 pinned servers), `rldyour-serena-mcp`
  (semantic code workflow + memory sync + 4 lifecycle hooks), `rldyour-flow`
  (SDLC orchestrator: ry-init/start/newp/review/deploy + 6 reviewer subagents
  + 3 hooks + 7 scripts + 7 references), `rldyour-explore` (deep research via
  ry-explore agent, model `opus[1m]`), `rldyour-security` (OWASP Top 10 + ry-sec-review),
  `rldyour-browser` (Playwright + Chrome DevTools MCP), `rldyour-design`
  (Figma → code, FSD, shadcn/ui, ReactBits, browser validation),
  `rldyour-lsps` (LSP routing + brew-first install + Serena LSP integration),
  `rldyour-rules` (quality-first engineering + architecture/dependency policy +
  AGENTS.md/CLAUDE.md/MADR 4.0.0 conventions).
- Cross-plugin `dependencies` declared in each `plugin.json`; `rldyour-mcps`
  is the single owner of `.mcp.json`; only `rldyour-flow` and
  `rldyour-serena-mcp` declare `hooks.json`.
- `fullrepo` branch policy for portable agent-only files, with
  `fullrepo_sync.py` covering `--bootstrap-init`, `--restore`, `--migrate-main`,
  `--publish` (safe `--force-with-lease`), `--status-json`.
- GitHub Actions `validate.yml` workflow running `claude plugin validate` for
  marketplace and per-plugin manifests, JSON manifest parse, Python AST and
  shell syntax checks, frontmatter presence verification on all skills,
  agents, and commands.

[Unreleased]: https://github.com/NDDev-it-com/rldyour-claudecode/compare/marketplace--v0.2.1...HEAD
[0.2.1]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.2.1
[0.2.0]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.2.0
[0.1.9]: https://github.com/NDDev-it-com/rldyour-claudecode/commit/99f9809
[0.1.8]: https://github.com/NDDev-it-com/rldyour-claudecode/commit/9bf3c70
[0.1.7]: https://github.com/NDDev-it-com/rldyour-claudecode/commit/eaccf59
[0.1.6]: https://github.com/NDDev-it-com/rldyour-claudecode/commit/bf54d02
[0.1.5]: https://github.com/NDDev-it-com/rldyour-claudecode/commit/bf54d02
[0.1.4]: https://github.com/NDDev-it-com/rldyour-claudecode/commit/eaccf59
[0.1.3]: https://github.com/NDDev-it-com/rldyour-claudecode/commits/main
[0.1.2]: https://github.com/NDDev-it-com/rldyour-claudecode/commit/d50e94c
[0.1.1]: https://github.com/NDDev-it-com/rldyour-claudecode/commit/ef18bd9
[0.1.0]: https://github.com/NDDev-it-com/rldyour-claudecode/commit/ef18bd9
