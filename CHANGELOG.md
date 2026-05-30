# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and marketplace/plugin versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]


## [1.1.9] - 2026-05-30

### Changed

- Make `ry-start` reviewer fanout explicit-opt-in while keeping `ry-review` reviewer orchestration available.

## [1.1.8] - 2026-05-30

### Fixed

- Remove stale Claude model claim after hardening release.

## [1.1.7] - 2026-05-30

### Fixed

- Harden Claude and OpenCode release gates.

## [1.1.6] - 2026-05-30

### Changed

- Refresh Claude Code runtime baseline to 2.1.158 after live npm drift.

## [1.1.5] - 2026-05-29

### Changed

- Refresh Claude release inventory after ry-start workflow hardening.

## [1.1.4] - 2026-05-29

### Changed

- Clarify ry-start workflow hybrid state and smoke validation.

## [1.1.3] - 2026-05-29

### Fixed

- Fix ry-start command workflow shim delegation invariant.

## [1.1.2] - 2026-05-29

### Changed

- Adopt Claude Code 2.1.156 and the ry-start workflow boundary.

## [1.1.1] - 2026-05-29

### Changed

- Refresh GitHub MCP Server host-binary pin to 1.1.0.

## [1.1.0] - 2026-05-29

### Changed

- Adopt Claude Code 2.1.154 and Opus 4.8 runtime metadata.

## [1.0.7] - 2026-05-29

### Changed

- Standardize release automation and repository descriptions.

## [1.0.6] - 2026-05-29

### Changed

- Refresh Claude release inventory after Stop lifecycle validator.

## [1.0.5] - 2026-05-29

### Changed

- Harden Claude Stop lifecycle docs and validation.

## [1.0.4] - 2026-05-28

### Fixed

- Synchronize Stop lifecycle timeout marker with marketplace policy boundary validation.

## [1.0.3] - 2026-05-28

### Fixed

- Harden Claude Stop lifecycle dispatcher timeout handling and hook-doc validation.
- `scripts/install-rldyour-marketplace.sh` now writes Markdown list entries in
  the final install report without tripping Bash `printf` option parsing.

## [1.0.2] - 2026-05-28

### Fixed

- Harden rldyour-flow Stop hook loop guard and local-only sync state checks.

## [1.0.1] - 2026-05-28

### Changed

- Synchronize internal plugin and index versions with the adapter release.

## [1.0.0] - 2026-05-28

### Changed

- Claude Code CLI baseline now tracks `2.1.153`, matching the current upstream
  stable package on the 2026-05-28 release-hardening sweep.
- Shared MCP runtime pins now track `semgrep==1.164.0` and `shadcn@4.8.2`;
  the Semgrep CI container digest was refreshed in lockstep.

## [0.7.0] - 2026-05-27

### Changed

- Claude Code CLI baseline now tracks `2.1.152`, matching the current upstream
  stable package and the refreshed owner runtime target.
- Dart SDK runtime pin now matches the Homebrew-installed Flutter/Dart owner
  runtime (`Dart 3.12.0`).
- Shared MCP runtime pins now match current upstream stable packages:
  `serena-agent==1.5.3`, `chrome-devtools-mcp@1.1.1`, and `shadcn@4.8.1`.

### Fixed

- CodeQL CI egress allowlist now includes `release-assets.githubusercontent.com`
  so CodeQL bundle downloads work when the GitHub runner cache misses.
- Gitleaks CI now retries Docker pull exit `125` infrastructure failures without
  masking real gitleaks findings.

## [0.6.9] - 2026-05-22

### Changed

- Claude Code CLI baseline moved from `2.1.146` to `2.1.147`, matching the
  currently published npm package and installed owner runtime.
- README generated inventory now reports the restored Serena memory count.

## [0.6.8] - 2026-05-22

### Changed

- Primary GitHub Release tags are now numeric-only (`X.Y.Z`) and must match
  root `VERSION`; legacy `marketplace--v*` and per-plugin `--v*` tags are kept
  as historical/cache metadata only.
- `ry-start` now routes explicit deploy/server rollout intent into `ry-deploy`
  after implementation validation and sync instead of stopping at code changes.
- `ry-review` now defines time-window, PR, issue, branch, and last-deploy target
  parsing before reviewer dispatch.
- `ry-newp` now explicitly seeds `CONTEXT-01-CORE.md` and
  `FUTURE-01-VISION.md` after approved scaffold commits.

### Fixed

- `rldyour-flow` is the single authoritative Claude Stop lifecycle owner;
  `rldyour-serena-mcp` no longer registers a parallel Stop hook that could race
  the ordered dispatcher.

## [0.6.7] - 2026-05-22

### Fixed

- `scripts/bootstrap_check.sh` now resolves `.git/info/exclude` and
  `hooks/pre-push` through `git rev-parse --git-path`, so fresh-bootstrap
  validation works in submodule checkouts where `.git` is a file.

## [0.6.6] - 2026-05-22

### Changed

- `rldyour-flow` now registers an ordered Stop lifecycle dispatcher for
  Claude Code. The dispatcher drains hook stdin, runs Serena memory freshness
  first, then runs Flow post-task sync checks with bounded child-process
  timeouts.
- `rldyour-flow` and `rldyour-design` skill text now explicitly references the
  root policy contract concepts validated across adapters: current code,
  deploy preflight/postflight, and accessibility checks.

## [0.6.5] - 2026-05-21

### Changed

- `rldyour-mcps` now pins `shadcn@4.8.0`, the current stable shadcn MCP CLI
  package on 2026-05-21, and mirrors that value in
  `config/mcp-runtime-versions.env`.

## [0.6.4] - 2026-05-21

### Changed

- Marketplace `VERSION`, root package metadata, and all 9 plugin manifests
  bumped to `0.6.4`. Local release evidence: `bash
  scripts/validate_marketplace.sh` passed end-to-end on 2026-05-21.
- Claude Code CLI compatibility pin moved from `2.1.145` to `2.1.146`.
  The 2026-05-21 baseline matters for rldyour flows because it fixes MCP
  pagination and preserves explicit AskUserQuestion decision gates in Auto
  mode.
- Repository, marketplace, and plugin metadata now use AGPL-3.0-or-later with
  canonical authorship for Danil Silantyev (`github:rldyourmnd`), CEO NDDev.
  Release validators now fail on license or author drift.
- `fullrepo_sync.py` now records remote configuration, local tree parity, and
  generated `fullrepo` commit author/committer identity; `flow_post_task_state.py`
  no longer treats a missing remote as a Stop-loop condition when the local
  `fullrepo` snapshot already matches agent-only context.

## [0.6.3] - 2026-05-21

**Cross-tool contract hardening.** This patch closes the remaining audit gap
that was not local to Claude Code runtime behavior: the shared rldyour system
now has a machine-readable business contract and generated matrix mapping the
canonical domains, public flows, skills, agent roles, hook lifecycle, and CI
baseline across Claude Code, Codex, and OpenCode.

### Added

- **`config/rldyour-contract.json`** as the canonical cross-tool contract for
  the nine shared domains, 10 public flows, 32 Claude skills, 8 agent roles,
  9 lifecycle hook scripts, and unified CI baseline.
- **`scripts/validate_contract.py`** local adapter gate. It proves the Claude
  Code implementation against real marketplace plugins, skill files, slash
  command files, agent files, hook manifests, hook scripts, and workflow/script
  paths, while requiring Codex/OpenCode adapter mappings to be explicit.
- **`scripts/generate_contract_matrix.py`** and generated
  **`docs/contract-matrix.md`** so humans review the same contract that CI
  validates.
- **`tests/test_validate_contract.py`** coverage for valid contracts, missing
  Claude skill paths, hook manifest/script drift, and generated matrix
  freshness.
- **`.github/workflows/dependency-review.yml`** as a required PR dependency
  diff review gate, pinned to `actions/dependency-review-action` v4.9.0 by
  commit SHA and guarded by harden-runner egress allowlisting.

### Changed

- Marketplace `VERSION`, all 9 plugin versions, root `package.json.version`,
  and `pyproject.toml [project].version` bumped to `0.6.3`.
- `scripts/validate_marketplace.sh` and `.github/workflows/validate.yml` now
  run `validate_contract.py` and `generate_contract_matrix.py --check`.
- README, workflow inventory, `AGENTS.md`, and `.claude/CLAUDE.md` now point
  at the contract/matrix as the source of truth for cross-tool parity.

## [0.6.2] - 2026-05-20

**Claude Code 2.1.145 and release-hygiene hardening.** This patch turns the
external audit findings into enforced repository contracts: root metadata
versions now participate in release validation, the current Claude Code CLI
and GitHub MCP host-binary pins are refreshed, agent-only path policy is
validated against the `fullrepo_sync.py` source of truth, and post-task sync
is exposed as a first-class `/rldyour-flow:ry-sync` command.

### Added

- **`/rldyour-flow:ry-sync`** slash command as a public wrapper for the
  existing `flow-post-task-sync` skill. It gives Claude Code users the same
  explicit finalization entrypoint as the Stop-hook advisory path: Serena
  freshness, instruction docs, checks, atomic commits, upstream push,
  `fullrepo` publish, and safe branch/worktree cleanup.
- **`tests/test_validate_boundaries.py`** coverage for `agent_only_path_globs`
  and `runtime_exclude_globs` parity between `config/marketplace-policy.json`
  and `plugins/rldyour-flow/scripts/fullrepo_sync.py`.
- **Release-state unit tests** proving that drift in `package.json.version`
  and `pyproject.toml [project].version` now fails the release gate.

### Changed

- Marketplace `VERSION`, all 9 plugin versions, root `package.json.version`,
  and `pyproject.toml [project].version` bumped to `0.6.2`.
- Claude Code CLI pin bumped from `2.1.143` to `2.1.145` in `package.json`,
  `config/mcp-runtime-versions.env`, `config/cc-canon.json`, docs, and
  agent instruction contracts. Local evidence: `claude --version` reported
  `2.1.145`; npm latest/next was `2.1.145` on 2026-05-20.
- MCP runtime pins refreshed where local validation could prove compatibility:
  `serena-agent` `1.3.0 -> 1.5.1`, `chrome-devtools-mcp` `0.26.0 -> 1.0.1`,
  and `GITHUB_MCP_SERVER_VERSION` `1.0.4 -> 1.0.5`. Dart remains pinned to
  local host SDK `3.11.0` while upstream stable is `3.12.0`; bumping without
  upgrading the host SDK would correctly fail the runtime-version gate.
- `scripts/smoke_bootstrap_check.sh` now compares the bash
  `AGENT_ONLY_PATHS` mirror exactly against `fullrepo_sync.py`
  `AGENT_ONLY_PATTERNS` instead of allowing count-based drift.
- `scripts/validate_command_skill_drift.py` now validates commands that
  intentionally delegate to a different existing skill, so `/ry-sync`
  delegates to `flow-post-task-sync` without becoming an unvalidated
  command-only exception.
- Documentation corrected to the actual Claude Code marketplace source
  layout (`source: "./plugins/<name>"`, no `metadata.pluginRoot`), the
  10-workflow CI inventory, and current reviewer `maxTurns` values
  (`90` standard, `100` security).

### Fixed

- `scripts/validate_release_state.py` now fails when `package.json` or
  `pyproject.toml` versions drift from `VERSION`, closing the concrete
  `0.6.1` vs `0.5.1` release-trust gap from the audit.
- `config/marketplace-policy.json`, `scripts/bootstrap_check.sh`, and
  `fullrepo_sync.py` now agree on `.codex/**` as an agent-only path and on
  runtime-only Serena markers such as `.serena/.gitignore`,
  `.serena/project.local.yml`, and `.serena/.bootstrap_overrides.log`.
- `.github/workflows/README.md` now lists `codeql.yml` as a required PR gate
  and describes the actual total of 10 workflows.

## [0.6.1] - 2026-05-18

**Post-public-toggle stabilisation patch.** The repository visibility
toggle to public surfaced CI configuration drift that did not show up
on the private runner. This patch closes the 4 remaining reviewer-wave
follow-ups, fixes 2 harden-runner egress allowlist gaps that broke CI
on the first public push, and clarifies that GitHub Secret Scanning +
Push Protection are intentionally disabled (paid-tier feature blocked
by organization enterprise policy - not a future TODO).

No behavior changes to plugins; no API changes; PATCH bump per
Keep a Changelog.

### Changed

- **`.github/workflows/validate.yml`** harden-runner allowed-endpoints
  list gained 4 entries for the HTTP MCP endpoints that
  `scripts/smoke_mcp_runtime.sh` HTTP-preflights: `mcp.deepwiki.com:443`,
  `mcp.grep.app:443`, `mcp.figma.com:443`, `developers.openai.com:443`.
  Drift between `.mcp.json` and the allowlist would now surface as CI
  failure - intentional. Closes the first-public-push regression where
  the MCP smoke step failed with `errno 111 Connection refused`.
- **`.github/workflows/actionlint.yml`** harden-runner allowed-endpoints
  list gained `release-assets.githubusercontent.com:443`. The actionlint
  download step pulls the pinned binary from GitHub's release-asset CDN;
  the egress block rejected the connection with `curl exit 7`. Closes
  the first-public-push regression.
- **`docs/security/threat-model.md`** "Known acceptable risks" section
  rewritten: the prior "Push protection: configurable for public repos"
  wording incorrectly implied future enablement. GitHub Secret Scanning
  and Push Protection are paid-tier features intentionally kept disabled
  by organization enterprise policy. Workflow-layer scanners
  (gitleaks weekly + push/PR, Semgrep `p/secrets`, CodeQL, local
  pre-push guard) deliver equivalent secret-scan risk-class coverage
  without the paid-feature unlock.
- **`docs/adr/0008-ci-baseline-without-paid-addons.md`** "Bad: no GHAS
  push protection" entry rewritten with the same accept-risk framing.
  Removed "Future option: add push protection" line (the org policy is
  durable, not a future TODO).
- **`docs/security/threat-model.md`** "No GHAS (paid)" section updated
  to reflect public-repo CodeQL availability (ADR-0008 amendment from
  the 0.6.0 wave).
- **`.github/workflows/semgrep.yml`** header comment block updated:
  "Replaces CodeQL because GHAS is not enabled" replaced with
  "Complements (does NOT replace) CodeQL" - the public-repo toggle
  unlocked CodeQL at zero cost; CodeQL + Semgrep + gitleaks are now
  three complementary security workflows running on every push/PR.
- **`scripts/validate_release_state.py:158`** + **`scripts/smoke_serena_memory_taxonomy.sh:51`**:
  hardcoded `"python3"` replaced with `sys.executable` in subprocess
  calls. Closes the 2 sites that commit `c432f54` (0.6.0 wave) missed.

### Notes

- This patch does NOT change any plugin behavior, contract, or API.
  All 9 plugin runtime files (skills, agents, hooks, commands, scripts)
  unchanged from 0.6.0. Version bump is per the owner-set rule
  (any wave touching marketplace/CI/docs bumps all 9 plugins +
  marketplace VERSION together; 2026-05-17 owner clarification in
  `[[RELEASE-01-VALIDATION]]` memory).
- All 18 Serena memories synced to HEAD via mixed flow-memory-sync
  subagent run + direct edit_memory calls for the metadata-only bumps.
  Memory taxonomy + agent-only-files invariants per ADR-0011 unchanged.

## [0.6.0] - 2026-05-18

**Public-readiness wave.** Removes personal contact email from the
marketplace manifest, adds open-source-standard public-readiness assets
(SECURITY.md / CONTRIBUTING.md / CODE_OF_CONDUCT.md / Issue + PR
templates), expands the per-PR CI matrix to Ubuntu + macOS for pytest
and validate harnesses, adds CodeQL semantic analysis for Python +
GitHub Actions, and closes the remaining `python3` hardcode finding
from the 0.5.2 reviewer wave (F-3 security INFO / F-6 consistency INFO).

This is the first release intended for public visibility on GitHub.
gitleaks scan over all 270 commits found zero secrets; manual sweep
confirmed no `/home/<user>` literals, no internal IPs, no Bearer
tokens, no API keys in any tracked file across the full history.

### Added

- **`SECURITY.md`**: vulnerability disclosure policy via private
  GitHub Security Advisories; supported-versions table tied to the
  `marketplace--v<X.Y.Z>` tag; threat model focused on prompt injection
  via hook output, supply-chain integrity, branch-boundary leakage,
  and hook freshness invariants (ADR-0011). Documents the defensive
  tooling stack (gitleaks, Semgrep, CodeQL, Dependabot, harden-runner)
  and what counts vs does NOT count as a security issue.
- **`CONTRIBUTING.md`**: quick-start install + `validate_marketplace.sh`
  gate + Conventional Commits v1.0.0 enforcement; "what fits" vs
  "what does NOT fit" sections aligned with the personal-marketplace
  scope; branch policy (main + fullrepo) and version-bump rule
  (owner-set 2026-05-17) documented for contributors.
- **`CODE_OF_CONDUCT.md`**: Contributor Covenant 2.1 verbatim adoption.
  Reporting channel routed through GitHub Security Advisories (same
  private channel as security disclosure).
- **`.github/ISSUE_TEMPLATE/bug_report.yml`**: structured bug intake
  with required fields (marketplace version, affected plugin, Claude
  Code CLI version, OS, repro steps, expected/actual, evidence). Built
  with GitHub Forms schema for input validation.
- **`.github/ISSUE_TEMPLATE/feature_request.yml`**: structured feature
  intake with use-case + alternatives + plugin-domain dropdown +
  alignment checklist gating boundary-respecting proposals.
- **`.github/ISSUE_TEMPLATE/config.yml`**: disables blank Issues,
  routes security reports to private advisories and discussions to
  GitHub Discussions.
- **`.github/PULL_REQUEST_TEMPLATE.md`**: pre-flight checklist
  enforcing Conventional Commits, atomic commits, validator pass,
  ADR for breaking changes, CHANGELOG entry, version bump, no
  secrets/tokens/PII, no `latest` pins, agent-only-files-on-fullrepo.
- **`.github/workflows/codeql.yml`**: semantic security analysis for
  `python` + `actions` (workflow YAML) languages. Free for public
  repositories. `security-extended` + `security-and-quality` query
  packs enabled; SARIF results upload to the Security tab.
  SHA-pinned to `github/codeql-action@95e58e9a...` (v4.35.2).

### Changed

- **`.claude-plugin/marketplace.json`** owner block: removed `email`
  field (`danilsilantyevnewlife+claude@gmail.com`). The marketplace
  schema (`config/schemas/marketplace.json`) does NOT require owner
  email; the `url` field (https://github.com/rldyourmnd) is sufficient
  contact attribution. Public preparation: removes personal contact
  data from the marketplace manifest before public visibility toggle.
- **`.github/workflows/pytest.yml`** matrix expansion: `runs-on:
  ${{ matrix.os }}` with `[ubuntu-latest, macos-latest]` strategy.
  Pytest now runs on both platforms on every push to main + every PR
  + workflow_dispatch. macOS coverage catches BSD vs GNU encoding /
  path / regex edge cases. Harden-runner remains Linux-only per
  ADR-0010 (macOS upstream limitation). Timeout raised 5 → 10 min
  to accommodate slower macOS runners. `persist-credentials: false`
  on checkout per OWASP A07 hardening.
- **`.github/workflows/validate.yml`** `syntax-checks` job matrix
  expansion: same Ubuntu + macOS strategy. Catches bash 3.2 vs 5.x
  compatibility issues, sed -i / find / readlink / awk userland
  differences. Timeout raised 8 → 12 min. `validate-marketplace`
  job (Claude CLI plugin validate) stays Ubuntu-only - no userland
  divergence in `claude plugin validate` execution path.
- **`plugins/rldyour-flow/scripts/flow_post_task_state.py`** +
  **`plugins/rldyour-flow/scripts/instruction_docs_state.py`** +
  **`plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`**:
  4 hardcoded `["python3", str(candidate), ...]` subprocess strings
  replaced with `[sys.executable, str(candidate), ...]`. Closes F-3
  security INFO + F-6 consistency INFO from review wave 2026-05-18T1238Z
  (hook layer used defensive `PYTHON_BIN` resolver; Python module
  internal subprocesses inherited the same intent but used hardcoded
  string). Now consistent across both layers.

### Notes

- Git history (270 commits authored by Danil Silantyev
  <danilsilantyevwork@gmail.com>) is intentionally NOT rewritten.
  Canonical open-source attribution; rewriting would invalidate all
  10 release tags from 0.5.2, break clone state for any existing
  downstream user, and offers no privacy benefit (the author identity
  is already known via the GitHub profile URL in the marketplace
  manifest). Future commits MAY use a noreply email at the author's
  discretion; existing history stays as canonical attribution.
- This release does NOT toggle GitHub repository visibility. The
  visibility change is a separate, explicit, user-authorized operation
  via `gh repo edit --visibility public` after this CHANGELOG entry
  ships and reviewers have confirmed public-readiness.

## [0.5.2] - 2026-05-18

**Hook freshness invariants for branch-split projects.** Closes a structural
conflict surfaced in the `almaty-libraries` Claude Code session
on 2026-05-18 between project-side CI gates (ancestor-of-main check) and
the local `commit_serena_knowledge.sh` hook (direct-head-mention check)
on `main + fullrepo` branch-split repositories.

Also hardens all 9 hook scripts against transient `python3` PATH/symlink
failures (canonical defensive resolver pattern), and closes the 9-path
gap left by the incomplete commit `4dcc1d1` (`AGENT_INSTRUCTION_PATHS`
now mirrors the full `.git/info/exclude` agent-only block).

### Added

- **`docs/adr/0011-agent-instruction-knowledge-equivalence.md`** (MADR
  4.0.0): records the decision to treat agent-instruction files
  (`AGENTS.md`, `.claude/CLAUDE.md`, `REVIEW.md`, IDE/agent roots,
  `.github/copilot-instructions.md`, `.agents/{skills,commands,hooks}/`,
  `.serena/project.yml`) as knowledge-equivalent for
  `memory_matches_head`. Resolves the structural conflict between
  branch-split CI ancestor-check gates and direct-head-mention hooks.
- **`tests/test_serena_memory_state.py`** (49 tests): covers
  `SERENA_KNOWLEDGE_PREFIXES`, full `AGENT_INSTRUCTION_PATHS` canon,
  negative classification for real product code, parity with
  `.git/info/exclude` agent-only block (semantic match: broader-OK),
  and drift detection between `serena_memory_state.AGENT_INSTRUCTION_PATHS`
  and the inline mirror in `mark_sync_required.sh`. New file.
- **Defensive `PYTHON_BIN` resolver block** in all 9 hook scripts
  (`plugins/rldyour-{serena-mcp,flow}/hooks/*.sh`). Canonical pattern
  from tw93/Mole, rsyslog, dmauser/opnazure: resolve `command -v python3`
  with fallback to `command -v python`, exit 0 if unavailable. Eliminates
  the transient failure class observed on Python 3.14 user environments
  with `uv`-managed symlinks (`/home/$USER/.local/bin/python3` symlink
  can be broken mid-upgrade; sanitized subprocess PATH may omit
  `~/.local/bin`).

### Changed

- **`plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`**:
  `AGENT_INSTRUCTION_PATHS` extended from 14 to 23 paths to mirror the
  full canonical `.git/info/exclude` "rldyour fullrepo agent-only files"
  block. Added: `.cursorrules`, `.windsurfrules`, `.openhands/`,
  `.github/copilot-instructions.md`, `.github/instructions/`,
  `.github/prompts/`, `.agents/skills/`, `.agents/commands/`,
  `.agents/hooks/`. Closes the gap left by commit `4dcc1d1` (first
  incomplete attempt added 14 paths but missed 9 entries from the
  exclude block). See ADR-0011 for full rationale.
- **`plugins/rldyour-serena-mcp/hooks/mark_sync_required.sh`**: inline
  Python heredoc gained `AGENT_INSTRUCTION_PATHS` mirror (separate
  subprocess cannot import the plugin module). `is_knowledge_path()`
  now combines `SERENA_KNOWLEDGE_PREFIXES` + `AGENT_INSTRUCTION_PATHS`.
  Drift between the two canons is enforced by
  `tests/test_serena_memory_state.py::TestInlineHookCanonDrift`.
- **All 9 hook scripts** (`plugins/rldyour-{serena-mcp,flow}/hooks/*.sh`)
  replace bare `python3` invocations with `"${PYTHON_BIN}"` (49
  replacements total) for defensive resolution. Each script preserves
  its existing exit semantics (Stop hooks still `exit 2` to block;
  advisory hooks still `exit 0`).

### Reviewer-wave closures (review run `2026-05-18T1238Z-027b6f9`)

Six parallel reviewer subagents (`flow-{architecture,quality,consistency,
integration,verification,security}-review`) ran against the initial
5-commit wave (febf45f..027b6f9) and surfaced 1 critical + 1 high + 4
medium findings. Closed in 3 follow-up commits:

- **F-1 CRITICAL (verification, conf 99)**: `smoke_serena_memory_taxonomy.sh`
  "agent-instruction commits require sync" step was written for the
  pre-ADR-0011 contract and asserted the inverted invariant after the
  classifier change - `validate_marketplace.sh` exited 1. Rewritten in
  commit `779350a` to assert the new invariant (`required=False` for
  agent-instruction-only wave) plus a companion negative case (product-
  code commit still requires sync). Stop-hook-stale fixture now commits
  both `src/main.py` (forces stale) AND `AGENTS.md` (so analyzer still
  emits the DOCS memory target the advisory checks for).
- **F-2 HIGH (verification, conf 95)**: `.github/workflows/pytest.yml`
  `paths:` trigger lacked `plugins/**`, so plugin-side script changes
  bypassed pytest CI silently. Added in commit `1be98e0`.
- **F-3 MEDIUM (verification, conf 85)**: `_is_knowledge_path()` used
  `startswith` for all `AGENT_INSTRUCTION_PATHS` entries, producing
  false-positive prefix matches (`AGENTS.md.bak`,
  `.github/copilot-instructions.mdx`). Fixed in `03afa2f` by separating
  semantics: directory entries (ending in `/`) use `startswith`; exact-
  file entries use `==`; `.aider` is a dotfile-family special case.
  Inline mirror in `mark_sync_required.sh` updated to match. Regression
  tests added in `1be98e0` (7 new `test_exact_file_entries_no_false_
  positive_prefix` cases).
- **F-1 MEDIUM (integration, conf 85) + F-7 LOW (architecture, conf 88)**:
  `.codex/` was in `AGENT_INSTRUCTION_PATHS` but missing from
  `fullrepo_sync.AGENT_ONLY_PATTERNS` and `.git/info/exclude` - a
  three-way inconsistency for a path family used by the `rldyour-codex`
  plugin. Added `.codex/**` to both lists in `03afa2f`.
- **F-8 INFO (architecture, conf 80) + F-2 LOW (integration)**:
  `.serena/project.local.yml` was classified as knowledge-equivalent but
  is `!`-negated in `.git/info/exclude` and listed in
  `fullrepo_sync.RUNTIME_EXCLUDE_PATTERNS` - it never reaches commits in
  normal flow. Removed from `AGENT_INSTRUCTION_PATHS` in `03afa2f`.

Test count: 124 → 131 passing (7 new F-3 regression tests). All
reviewer LOW/INFO findings retained as deferred (documented in
`.serena/reviews/2026-05-18T1238Z-027b6f9/*.md`).

### Notes

- This wave does NOT add path canon to a runtime config file. Decision
  deferred to a future wave when a second consumer of
  `AGENT_INSTRUCTION_PATHS` emerges beyond `serena_memory_state.py`
  and `mark_sync_required.sh` (ADR-0011 Open Questions).
- This wave does NOT update memories directly. Memory sync runs through
  the `flow-memory-sync` subagent after the reviewer phase, per the
  canonical `ry-start` lifecycle (skill body is the source of truth).

## [0.5.1] - 2026-05-17

Patch-level **hardening wave** that closes the 13 deferred low/medium
findings carried over from the 0.5.0 reviewer phase plus actionable info
items. No new features; no contract changes. Goal: zero outstanding
deferred findings before tag boundary.

### Added

- **`docs/adr/0010-macos-egress-trust-gap.md`** (MADR 4.0.0): documents
  the macOS-runner egress gap as an accepted upstream limitation of
  `step-security/harden-runner` (no macOS support since 2022), with
  the four non-egress mitigations actually in place (schedule-only
  trigger, `contents: read`, read-only validators, 10-min timeout).
  Closes Security F-1 (MEDIUM 75).
- **`plugins/rldyour-flow/hooks/pre_tool_use_ci_advisory.sh`**: new
  PreToolUse hook fires on `Bash(gh workflow*)`, `Bash(gh run*)`,
  `Bash(gh actions*)` and emits a stderr advisory reminding the model
  that GitHub Actions control commands are reserved for explicit user
  gestures (`сделай ci`, `запусти сиай`, etc.). Advisory ONLY, exits 0,
  no blocking. Skip flag: `RLDYOUR_SKIP_CI_ADVISORY=1`. Closes
  Security F-3 (MEDIUM 65) - the manual-first CI rule now has a
  programmatic reminder, not just docs.
- **`RLDYOUR_SKIP_USER_PROMPT_HINT`** skip flag on
  `plugins/rldyour-serena-mcp/hooks/user_prompt_submit.sh`: parity with
  every other rldyour hook. Documented in `docs/runtime-env.md` skip-flag
  table. Closes Consistency F-3 (LOW 75).

### Changed

- **Serena hooks `if` filter narrowed**: `plugins/rldyour-serena-mcp/hooks/hooks.json`
  PreToolUse + PostToolUse switched from broad `Bash(git *)` (which
  spawned the script on every git read - log/status/diff/etc.) to
  five explicit handlers per event scoping to `git commit*`, `git merge*`,
  `git cherry-pick*`, `git rebase*`, `git am*`. Each handler points at
  the same script. Net effect: zero subprocess spawn on `git log` /
  `git status` / `git diff` (was 3 spawns per call). Closes
  Architecture F-2 (LOW 85).
- **Hook `command` field switched from `"bash"` to `"/bin/bash"` (absolute
  path)** across both `hooks.json` files. Eliminates the PATH-resolution
  risk class flagged as Security F-6 (LOW 75). Verified all 8 hook
  scripts use only bash 3.2-compatible features (macOS system bash).
- **`config/schemas/plugin.json`**: `dependencies[].version` field gained
  a semver pattern constraint (`^[~^>=<]{0,2}\d+.\d+.\d+(-pre)?(+meta)?$`
  with `||` and `&&` separators, plus `*` wildcard). Blocks shell-injection
  chars per Security F-8 (LOW 70).
- **`scripts/release_manifest.py`** `NPM_PIN_RE` tightened: first char of
  unscoped and scoped names must be alphanumeric. Rejects `-pkg@1.0`,
  `.hidden@1.0`, `_priv@1.0` that npm itself refuses. Closes Quality F-5
  (info 70).
- **`scripts/release_manifest.py`** emits WARN to stderr when a server has
  neither an extractable npm/uvx pin nor a host_binary_pin (or when its
  version_env is absent from the env file). The JSON shape is unchanged
  (`"pin": null` stays); operators now see the gap during the build
  rather than after shipping. Closes Integration F-3 (LOW 80) + Security
  F-10 (LOW 65).
- **`.github/workflows/cross-platform.yml`**: removed `pull_request:
  types: [labeled]` trigger (created skipped-run noise in Actions UI
  on every label add); reordered `on:` keys to schedule-first per the
  README convention. Operators who want cross-platform verification on
  a PR can now use `gh workflow run cross-platform.yml --ref <branch>`.
  Closes Architecture F-3 (LOW 78) + Consistency F-8 (info 65).
- **`.github/CODEOWNERS`**: replaced reliance on the default `*`
  wildcard for security-critical files with explicit glob patterns
  for `bootstrap_check.sh`, `check_mcp_runtime_versions.py`,
  `release_manifest.py`, `smoke_*.sh`, `_mcp_parse.py`,
  `probe_mcp_upstream.py`, and all `config/*.json` policy files.
  Closes Security F-4 (MEDIUM 60).
- **`docs/runtime-env.md`**: added "PAT scope guidance" section
  recommending fine-grained PAT (per-resource permissions) over the
  classic `repo` + `read:org` PAT with explicit caveat that `repo`
  is wider scope than the fine-grained equivalents. Documents the
  intentional absence of `RLDYOUR_SKIP_ENV_CHECK` (downstream MCP
  failure mode is worse than the upfront block - fix the env, not
  the check). Closes Security F-9 (LOW 60) + Verification F-5 (LOW 80).
- **`tests/conftest.py`**: alphabetized `patch_repo_root` copy list
  (17 entries). Closes Consistency F-1 (info 85).

### Verified

- `python3 scripts/validate_json_schemas.py`: 14/14 OK.
- `bash scripts/smoke_hooks.sh`: PASS (8 hook scripts now include the
  new `pre_tool_use_ci_advisory.sh`).
- `bash scripts/validate_reviewer_contracts.sh`: 52 PASS / 0 drift.
- `python3 scripts/release_manifest.py`: emits no WARN at HEAD; emits
  expected WARN when env file is removed (manual test).
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/ -m "not integration"`:
  75 passed, 3 deselected.
- `bash scripts/validate_marketplace.sh`: passed end-to-end.

### Notes

- Consistency F-5 (info 88, `$defs` usage variance across schemas):
  intentionally skipped. `$defs` is applied where subschemas are reused
  (hooks.json, mcp.json); not applied where each item is inline-defined
  (lsp.json, marketplace.json, plugin.json). Refactoring inline schemas
  to `$defs` adds indirection without functional benefit.
- Consistency F-2 (LOW 80, "14 files updated" in CHANGELOG):
  retroactive fix declined. The 0.5.0 entry was descriptive prose; line
  count vs file count was an approximation, not a load-bearing claim.

## [0.5.0] - 2026-05-17

Minor-version wave closing the external audit findings (P0/P1/P2/P3) into
a single coherent release. Touches plugin runtime contracts (hooks JSON
canonical form, schema corrections, agent tool boundaries, command/skill
drift, MCP env policy), validator surface (+1 validator, +1 negative test
in an existing one, +6 unit tests), CI/CD policy (manual-first agent gate,
macOS cross-platform schedule, CODEOWNERS), and docs (runtime-env, workflow
README). All 9 plugins and the marketplace VERSION bumped to 0.5.0.

### Added

- `scripts/validate_command_skill_drift.py` + 6 unit tests. Enforces that
  any slash command whose `name` matches a skill stays a thin wrapper
  (<= 800 chars body, `Use the \`<name>\` skill` delegation phrase, no
  forbidden workflow headings, numbered checklist <= 3 items). Skips the
  ry-explore command+agent pattern silently. Wired into
  `scripts/validate_marketplace.sh`.
- `docs/runtime-env.md`: full reference for required (CONTEXT7_API_KEY,
  GITHUB_PERSONAL_ACCESS_TOKEN), optional MCP knobs (MCP_TIMEOUT etc.),
  and all `RLDYOUR_SKIP_*` skip flags.
- `.github/CODEOWNERS`: auto-review requests for workflows, schemas, MCP
  transport, hook owners, validators, release surface, ADRs.
- `.github/workflows/README.md`: Required PR / Advisory Scheduled /
  Release-only split with GHEC cost-policy notes; documents the
  manual-first CI rule for AI agents.
- `.github/workflows/cross-platform.yml`: macOS + Ubuntu smoke matrix on
  workflow_dispatch + Sunday 04:00 UTC schedule + opt-in PR label
  `cross-platform`. NOT triggered on every PR (macOS = 10x cost factor).
- `--strict` flag on `scripts/check_mcp_runtime_versions.py`: promotes
  absent host binaries (`github-mcp-server`, `dart`) from INFO to FAIL
  for release-build machines.
- Negative write-scope test in `scripts/validate_reviewer_contracts.sh`:
  reviewer bodies cannot contain shell write tokens (`rm -`, `mv `,
  `cp -`, `sed -i`, `tee `, `touch `, `>>`) outside the bounded
  `RLDYOUR_REPORT_EOF` heredoc. Brings total assertions to 52 PASS.

### Changed

- **Hooks JSON canonical form** (P0):
  `plugins/rldyour-flow/hooks/hooks.json` and
  `plugins/rldyour-serena-mcp/hooks/hooks.json` rewritten so the `if`
  filter lives INSIDE the inner hook handler (sibling to `type`/`command`),
  not at the matcher-group level. All hook handlers use exec-form
  `command: "bash"` + `args: ["${CLAUDE_PLUGIN_ROOT}/hooks/X.sh"]` per
  v2.1.139+ recommendation. Serena PreToolUse/PostToolUse use a broad
  `Bash(git *)` rule plus script-level self-filter (one rule per `if`).
- **`config/schemas/hooks.json`** rewritten to mirror canonical Claude
  Code: `if` is a hookHandler property; full v2.1.142 field set added
  (`args`, `async`, `asyncRewake`, `shell`, `continueOnBlock`, `url`,
  `headers`, `allowedEnvVars`, `server`, `tool`, `input`, `prompt`,
  `model`, `agent`, `once`). `additionalProperties: false` keeps drift
  surfaced.
- **`$schema` format**: all 5 schemas changed `format: "uri"` -> `"uri-reference"`
  so the repo-relative `$schema` paths in JSON manifests validate
  (`format: "uri"` requires absolute URI per RFC 3986).
- **`config/schemas/plugin.json`** expanded: `dependencies` items accept
  `string` OR `{name, version}` object; component paths
  (`skills`/`commands`/`agents`/`hooks`) accept `string` OR `array of strings`
  matching documented Claude Code component-path shapes (string replaces
  default, array adds to default).
- **`scripts/release_manifest.py`**: new `NPM_PIN_RE` extracts unscoped
  npm pins (`chrome-devtools-mcp@0.26.0`, `shadcn@4.7.0`) that the
  previous parser missed (pin=null). New `host_binary_pins` block from
  `config/mcp-runtime-versions.env` for `github-mcp-server` v1.0.4 and
  `dart` v3.11.0. Top-level `claude_code_min_version` exposed.
- **Slash commands thinned** (8 wrappers <= 800 chars each):
  `ry-start`, `ry-init`, `ry-newp`, `ry-review`, `ry-deploy` (rldyour-flow),
  `ry-design` (rldyour-design), `ry-rules-review` (rldyour-rules),
  `ry-sec-review` (rldyour-security). All delegate to their same-named
  skill via the canonical `Use the \`<name>\` skill` phrase. `ry-explore`
  remains as-is (command + agent, no skill - audit recommendation).
- **Agent descriptions shortened**:
  `ry-explore` 1660 -> 407 chars, `flow-memory-sync` 1574 -> 552 chars.
  Examples moved out of frontmatter into agent body.
- **`scripts/bootstrap_check.sh`**: new mandatory `required MCP credentials`
  step FAILs on missing CONTEXT7_API_KEY or GITHUB_PERSONAL_ACCESS_TOKEN
  (Claude Code aborts config parse on these unset). Existing
  `env example coverage` demoted to optional-vars INFO.
- **`scripts/check_mcp_runtime_versions.py`**: argparse + `--strict` mode
  (see Added).
- **`plugins/rldyour-serena-mcp/hooks/user_prompt_submit.sh`**: surgical
  trigger rewrite. Strong triggers (code/class/function/refactor/...)
  inject directly; weak triggers (project/directory/file) inject only
  when paired with an action verb. Single python3 parser/emitter
  replaces the python|grep|python pipeline.
- **`tests/test_*.py`**: every `subprocess.run()` helper now carries
  `timeout=30` (14 files updated) so any future validator regression
  surfaces as `TimeoutExpired` instead of an infinite hang.
- **`.github/workflows/pytest.yml`**: runs `pytest -m "not integration"`
  so live network probes never execute in the unit-test gate.
- **`AGENTS.md`** trimmed from 205 to 198 lines (within the 200-line
  soft cap) by collapsing repeated Claude Code version-floor claims,
  shortening the worktree trust-model paragraph, and compressing the
  MCP transport listing.

### Reviewer wave closures (commits e956be5, 69d1105, a6bde4d)

Six parallel reviewer subagents (`flow-architecture/quality/consistency/
integration/verification/security-review`) ran against HEAD `b5e78d4`,
file-first transport to `.serena/reviews/2026-05-17T1448Z-b5e78d4/`. 0
critical, 1 high, 9 medium, 11 low, 28 info findings total.

Closed in 3 fix commits within this same release block:

- `e956be5` - **Quality F-1 HIGH (95)**: `scripts/smoke_hooks.sh`
  discovery walked only `handler["command"]`; the exec-form migration
  silently dropped all 8 hook scripts from the `bash -n` check. Now
  walks both `command` AND `args` tokens. Verified: 8/8 scripts found.
- `69d1105` - **Architecture F-1 + Integration F-2 + Verification F-1
  (convergent)**: `validate_command_skill_drift.py` added to
  `.github/workflows/validate.yml` PR gate. Same for
  `validate_instruction_docs.py --require-agent-docs` (Verification F-4).
  **Integration F-1**: `validate_boundaries.py` normalizes `{name, version}`
  dependency dicts (forward-compat for 0.5.0 schema expansion).
  **Security F-5**: drift validator FAIL output moved to stderr.
- `a6bde4d` - **Quality F-3 + F-6**: numbered-list blank-line reset +
  ACTION regex `\b` boundary (`editor` no longer triggers `edit`).
  **Security F-2**: `validate_reviewer_contracts.sh` comment sync
  (`rm -`). **Verification F-2**: new test `test_wrong_delegation_target_blocks`
  covers the previously-untested branch.
  **`.claude/CLAUDE.md`** lines 123 + 145 updated to reflect exec-form
  adoption (Quality F-2).

Deferred (documented in `.serena/memories/TECHDEBT-01-NOW.md`):
Architecture F-2/F-3 (broader git filter, labeled trigger noise),
Integration F-3 (silent null host_binary_pin), Security F-1/F-3/F-4/F-8
(macOS egress, manual-first docs-only, CODEOWNERS wildcards, dependency
version pattern).

### Verified

- `python3 scripts/validate_json_schemas.py`: 14/14 OK.
- `bash scripts/smoke_hooks.sh`: PASS (now 8/8 hook scripts discovered + bash-n).
- `bash scripts/validate_reviewer_contracts.sh`: 52 PASS / 0 drift.
- `python3 scripts/validate_command_skill_drift.py`: 8 OK / 1 SKIP.
- `python3 scripts/validate_boundaries.py`: OK (mcp_owner + hook_owners
  + 9 plugin dependency contracts; `{name, version}` form also accepted).
- `python3 scripts/check_mcp_runtime_versions.py [--strict]`: 13/13 OK
  on maintainer machine (github-mcp-server v1.0.4 + dart v3.11.0 present).
- `python3 scripts/release_manifest.py`: all 13 MCP pins extracted,
  `host_binary_pins` populated, `claude_code_min_version: 2.1.143`.
- `bash scripts/validate_marketplace.sh`: passed end-to-end.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/ -m "not integration"`:
  **75 passed, 3 deselected** (added 2 drift tests for F-2/F-3 closures).
- `python3 scripts/validate_instruction_docs.py --require-agent-docs`:
  AGENTS.md 198 lines OK, `.claude/CLAUDE.md` 200 lines OK.

## [0.4.4] - 2026-05-17

Fourth wave from the 2026-05-17 review wave
(`2026-05-17T0948Z-12a2bdc`) - cosmetic polish closure. Seven items
brought the marketplace to zero outstanding actionable findings:
six new validator test files (+28 tests, total 70), one allowlist
externalisation (LOW-10), four cosmetic fixes (LOW-9, INFO-2, INFO-3,
INFO-6), and the BIDI allowlist test unskipped (INFO-4).

### Added

- **6 new validator test files** (`tests/test_validate_json_schemas.py`,
  `test_validate_plugin_versions.py`, `test_validate_instruction_docs.py`,
  `test_validate_skill_routing.py`, `test_check_mcp_runtime_versions.py`,
  `test_probe_mcp_upstream.py`). 28 new test cases joining the existing
  42 -> 70 total. Closes F-TEST-05 fully: all 10 validators under
  `scripts/validate_*` plus the supporting `check_mcp_runtime_versions`,
  `probe_mcp_upstream`, and `_mcp_parse` modules now have at minimum
  one happy-path + one negative test. Integration tests
  (`@pytest.mark.integration`) cover the three validators whose
  contract depends on full repo state.
- **`config/text-hygiene-allowlist.json`**: centralises em-dash /
  en-dash / BIDI exemption sets. The validator now loads exemptions
  via `load_allowlists(root)` with backward-compat fallback to
  compiled-in defaults when the config is absent. Closes LOW-10
  (architecture F-4): adding or moving an exempted file is now a
  config edit, not a script edit.

### Changed

- **`scripts/validate_text_hygiene.py`**: gained `load_allowlists`
  function that loads from `config/text-hygiene-allowlist.json` with
  malformed-JSON fallback to defaults + WARN to stderr.
  `ALLOWLIST_EM/EN/BIDI` constants renamed to `_DEFAULT_ALLOWLIST_*`
  to signal fallback role.
- **`scripts/validate_instruction_sync.py:45`**: `CONTRACT_BLOCK_RE`
  gained `\s*` tolerance before closing `-->` for indented HTML-comment
  style. Defensive change - no production block uses this form at HEAD.
  Closes INFO-3.
- **`.github/workflows/claude-cli-drift.yml:21-26`**: concurrency
  group + cancel-in-progress aligned with `dependency-check.yml`
  pattern (group includes `github.ref`, cancel-in-progress true). Both
  weekly drift workflows now share the same lifecycle contract. Closes
  LOW-9.
- **`docs/adr/0003-bilingual-skill-descriptions.md:72`**: Confirmation
  section count updated from "15 routing cases" to "19" with a note
  that the validator auto-extends as new skills ship. Closes INFO-2.
- **`tests/test_validate_docs_canon.py:91`**: `monkeypatch` parameter
  gained `pytest.MonkeyPatch` type annotation for consistency with
  `conftest.py:104`. Closes INFO-6.
- **`tests/test_validate_text_hygiene.py`**:
  `test_bidi_allowlist_skips_documented_file` no longer
  `@pytest.mark.skip` - fake_repo fixture now ships the allowlist
  config + a stub hook file with embedded U+202E via `chr(0x202E)`
  so the test exercises the exemption path end-to-end in fake_repo
  isolation. Closes INFO-4.
- **`tests/conftest.py`**: fixture extended with
  `config/text-hygiene-allowlist.json`, hook stub at
  `plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh`, and
  `rldyour-flow` plugin.json + marketplace entry so `validate_release_state`
  and `validate_boundaries` keep passing against the extended layout.
  `patch_repo_root` copy list gained 5 missing scripts
  (`validate_instruction_docs`, `validate_skill_routing`,
  `validate_boundaries`, `check_mcp_runtime_versions`,
  `probe_mcp_upstream`) so the new test files can exec them.

## [0.4.3] - 2026-05-17

Third wave from the 2026-05-17 review (`2026-05-17T0948Z-12a2bdc`) -
architectural debt closure. Eight items: shared MCP parser extraction,
new boundary-enforcement validator (closes ADR-0006 gap), pyright +
ruff advisory CI gates, subprocess timeouts, dead-code removal, broad
self-skip hardening, security-critical test coverage, lint backlog
cleared across `scripts/` + `plugins/`. The validator-layer of the
marketplace now has 39 unit tests (up from 23 in 0.4.2) and zero
ruff/pyright diagnostics.

### Added

- **`scripts/_mcp_parse.py`**: shared MCP tool reference parser. Single
  `split_mcp_ref(ref, plugins) -> (plugin, server, tool) | None`. Used
  by both `validate_skill_allowed_tools.py` and `validate_agent_tools.py`,
  eliminating the divergent parsing strategies flagged by A-F-5 (one
  used `rsplit('_', 1)`, the other longest-prefix). Closes A-LOW-6.
- **`scripts/validate_boundaries.py`**: new structural validator
  reading `config/marketplace-policy.json`. Enforces four invariants:
  exactly one `.mcp.json` owned by `policy.mcp_owner`, `hooks/hooks.json`
  set matches `policy.hook_owners` exactly, every plugin.json `name`
  matches its directory, every plugin.json `dependencies` array equals
  `policy.plugin_dependencies[<plugin>]`. Wired into
  `validate_marketplace.sh` + `.github/workflows/validate.yml`. Closes
  A-MED-3 and the ADR-0006 self-acknowledged gap.
- **`tests/test_mcp_parse.py`** (9 tests): direct unit tests for the
  shared `split_mcp_ref` parser - hyphen + underscore + longest-prefix
  + rpartition-fallback + 4 malformed-input rejection cases. Closes
  A-LOW-5 (the `test_validate_skill_allowed_tools.py` docstring
  promised underscore-plugin coverage; the actual contract is now
  tested at the parser layer).
- **`tests/test_validate_agent_tools.py`** (7 tests): security-critical
  coverage for the read-only-by-design enforcer. Builtin tools pass,
  no-tools-block inherits default, serena wildcard blocked,
  context7 wildcard passes, unknown server blocked, unknown plugin
  blocked (new branch from the LOW-6 refactor), malformed ref blocked.
  Closes A-LOW-7 / A-F-6.
- **Ruff lint + Pyright type check advisory CI steps** in
  `.github/workflows/validate.yml`. Both `continue-on-error: true`
  until MED-2 graduates to hard-fail; visibility comes from the
  workflow run summary. Closes A-MED-2 (Recommended).

### Changed

- **`scripts/validate_skill_allowed_tools.py`** + **`scripts/validate_agent_tools.py`**:
  both now import `split_mcp_ref` from `_mcp_parse`. Old dead
  `MCP_PATTERN_RE` removed (closes Q-F-2). `validate_agent_tools.py`
  gained explicit plugin-name validation against marketplace - unknown
  plugin refs now yield specific "unknown plugin" errors instead of
  passing silently.
- **`scripts/validate_release_state.py`**: `_git`, `_head_sha`,
  `_tag_sha`, and the `release_manifest.py` subprocess call all gained
  `timeout=30s` + `TimeoutExpired` handling. A stuck git or stuck
  subprocess now returns a FAIL line instead of hanging until the
  workflow-level job timeout fires. Closes Q-LOW-6.
- **`scripts/validate_text_hygiene.py`**: self-skip changed from
  `path.name == "validate_text_hygiene.py"` (any file with that name
  anywhere) to `path.resolve() == Path(__file__).resolve()` (only the
  script file itself). A future file named `validate_text_hygiene.py`
  placed elsewhere is no longer silently exempted from scanning.
  Closes Q-LOW-4. `EN_DASH` constant got `# noqa: RUF001` with
  rationale since the constant IS the EN DASH detection target.
- **`tests/conftest.py`**: fake `.mcp.json` extended with `context7`
  HTTP server alongside the existing `serena` stdio server, allowing
  the new agent-tools tests to exercise both write-server-blocked and
  read-only-server-passes branches. `patch_repo_root` copy list also
  gained `validate_agent_tools.py` + `_mcp_parse.py` so the new
  tests can run in `fake_repo` isolation.
- **`pyproject.toml`**: pyright `include` now covers `tests/` so the
  test layer is type-checked alongside `scripts/` + `plugins/`.
  `extraPaths = ["scripts"]` resolves `from _mcp_parse import ...`
  the same way Python's runtime sys.path treatment does.
- **`docs/adr/0006-mcp-hook-ownership-boundaries.md`**: Confirmation
  section rewritten to cite the now-shipped `validate_boundaries.py`
  with all four invariants enumerated. Replaces the
  "(not yet implemented)" language from 0.3.0.

### Fixed

- **`plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py:285`**:
  added `# type: ignore[operator]` for a pre-existing Pyright type
  narrowing limitation. Construction site sets `item["count"]` to int,
  but Pyright cannot narrow from the dict's mixed `str | int | list[str]`
  value type. No behavior change.
- **9 ruff auto-fixes** across `plugins/rldyour-flow/scripts/` and
  `plugins/rldyour-serena-mcp/scripts/`: import sort, `collections.abc.Iterable`,
  ternary expression, `return bool(...)`, tuple unpacking. Cosmetic
  modernization to bring the lint backlog to zero before enabling the
  MED-2 advisory CI gate.

## [0.4.2] - 2026-05-17

Second wave from the 2026-05-17 review (`2026-05-17T0948Z-12a2bdc`) -
high-value medium fixes after 0.4.1 closed the three CI-blocking
HIGHs. Targets the monitoring blind spot (egress allowlist), CLI
version single-source-of-truth, validator UX (SKIP stream + window
heuristic), and OWASP wording drift in the security reviewer skill.
Zero production runtime behavior changes; CI monitoring widens
coverage from 2/9 effective upstream probes to 9/9.

### Fixed

- **CI egress allowlist closed for 7/9 MCP upstream probes**
  (`.github/workflows/dependency-check.yml:36-48`). The
  mcp-runtime-drift job ran `probe_mcp_upstream.py` with an allowlist
  that included only GitHub and PyPI endpoints; the probe also queries
  `registry.npmjs.org` (5 servers), `formulae.brew.sh` (1 server), and
  `storage.googleapis.com` (Dart SDK). Without these three endpoints
  the npm/brew/dart probes silently returned `None` and drift went
  undetected in weekly CI - a false-negative monitoring pattern that
  defeated the purpose of weekly drift checks. Added all three with an
  inline rationale comment. Closes A-MED-3 (architecture) + S-LOW-1
  (security) cross-reviewer finding.
- **validate.yml CLI version now reads from package.json dynamically**
  (`.github/workflows/validate.yml:55-65`). Previously the npm install
  step hardcoded `'@anthropic-ai/claude-code@2.1.143'` as a shell
  literal; release.yml and claude-cli-drift.yml both read the pin from
  package.json. Dependabot bumps package.json (npm ecosystem) but does
  NOT update inline shell strings in `run:` blocks, so the next CLI
  bump would leave validate.yml stale while the other workflows
  auto-picked the new version. New step reads version via Python +
  `$GITHUB_OUTPUT`, install step references the output. Same pattern
  as release.yml + cli-drift. Closes A-MED-2 (architecture).
- **SKIP messages now consistently on stdout in 2 validators**
  (`scripts/validate_instruction_sync.py:87`,
  `scripts/validate_json_schemas.py:61`). Both validators printed SKIP
  messages to `sys.stderr` while every other validator's SKIP path
  goes to stdout. Tests that assert `'SKIP' in result.stdout` silently
  falsely passed when pyyaml or jsonschema was absent locally (SKIP
  went to stderr, stdout was empty). Removed `file=sys.stderr` from
  both lines. Closes Q-LOW-2 (quality) + I-MED-4 (integration)
  cross-reviewer finding.
- **validate_docs_canon window now adapts to knob length**
  (`scripts/validate_docs_canon.py:82-92`). The 30-char backwards
  window was shorter than long knob names like `maxSkillDescriptionChars`
  (24 chars) plus reasonable prose budget ('added in', 10 chars =
  34 total). Real canonical-drift bugs phrased naturally went
  undetected. Window is now `max(30, len(knob) + 15)` - preserves the
  original baseline for short knobs while adapting up for long names.
  Closes Q-MED-1 (quality).
- **ry-sec-review SKILL.md A01-A10 OWASP wording aligned**
  (`plugins/rldyour-security/skills/ry-sec-review/SKILL.md:64-73`).
  Quality reviewer flagged A09 only (missing year + 'and' instead of
  '&'). Cross-file verification at HEAD showed the entire A01-A10
  block in this skill lacked the `:2025` year suffix while four other
  canonical locations (sister skill, cc-canon.json, threat-model,
  SECURITY-01 memory) all used the OWASP 2025 form. Updated all 10
  entries. Closes Q-INFO-1 (quality, expanded scope after manual
  verification).

### Added

- **tests/test_validate_docs_canon.py::test_long_knob_window_expands_dynamically**:
  regression lock-in for the docs_canon window heuristic. Uses a
  synthetic 19-char knob `aVeryLongConfigKnob` placed 33 chars before
  v1.9 - distance that the old fixed-30 window missed and the new
  `max(30, len(knob)+15) = 34` window catches.

## [0.4.1] - 2026-05-17

Critical fixes from the 2026-05-17 review wave (run
`2026-05-17T0948Z-12a2bdc`, 6 parallel reviewer subagents on 22 commits
since `bf19b44`). Two root causes verified by multiple reviewers + one
Pyright diagnostic closed; pytest CI was failing at 0.4.0 with 3 broken
tests, all recovered. No production runtime behavior changes beyond the
validator gap closure.

### Fixed

- **CONS-1 `TOOLS_BLOCK_RE` parser silently skipped last
  `allowed-tools` item** (`scripts/validate_skill_allowed_tools.py:31`).
  Regex required `\n` after every item; when `allowed-tools:` was the
  last frontmatter key (no trailing newline before `---`), the block
  was silently dropped. `plugins/rldyour-browser/skills/browser-validation/SKILL.md`
  hit this case; its MCP namespace was never validated. Tool name is
  correct at HEAD (`playwright`) so no live misconfig, but the guard
  was broken. Changed regex to `\n?` on the trailing newline match.
  Verified by 2 independent reviewers (verification F-1b, integration F-1).
- **CONS-1 `split_mcp_ref` fallback for unknown plugins**
  (`scripts/validate_skill_allowed_tools.py:62-83`). Longest-plugin-prefix
  match returned `None` for refs whose plugin was not in the marketplace,
  causing generic "malformed MCP ref" errors instead of specific "unknown
  plugin X" messages. Added `rpartition("_")` fallback so unknown plugin
  refs still parse to `(plugin, server)` tuples and reach the proper
  "unknown plugin" branch with a clearer error message. Better debugging
  UX for new plugin manifests.
- **CONS-2 `fake_repo` fixture missing rldyour-mcps `plugin.json`**
  (`tests/conftest.py:60-79`). Fixture created `plugins/rldyour-mcps/`
  with only `.mcp.json`; `validate_release_state.py` iterates
  `plugins/*` and requires `.claude-plugin/plugin.json` in every
  subdirectory, causing `test_version_matches_changelog_passes` to
  fail with an unexpected error. Fixture now adds a minimal
  `.claude-plugin/plugin.json` to the rldyour-mcps subdir AND adds
  `rldyour-mcps` to the fake `marketplace.json` so `split_mcp_ref`
  recognizes the plugin for unknown-server tests. Verified by 2
  independent reviewers (verification F-1a, integration F-3).
- **`validate_release_state.py` "not a git repository" warning
  miscategorized** (`scripts/validate_release_state.py:112`). The
  warning was passed through to `failures` instead of `info`, causing
  `FAIL not a git repository or HEAD unreadable` when the validator
  runs outside a git context (e.g., test fixtures). Added `INFO ` prefix
  so the warning lands in the info pile correctly. Closes the third
  pytest failure mode.
- **`_git` subprocess wrappers ignored `root` parameter** (Pyright
  diagnostic on `scripts/validate_release_state.py:108`). The `root`
  parameter in `validate_tag_alignment` was declared but unused;
  `_git`/`_head_sha`/`_tag_sha` ran with default cwd, which is fragile
  if the validator is launched from outside the repo root. Propagated
  optional `cwd: Path | None` through all three helpers and pass
  `cwd=root` from `validate_tag_alignment`. Fixes the warning AND
  hardens against out-of-repo callers.

### Test

- **All 22 unit tests pass + 1 expected SKIP**. `test_unknown_server_blocked`,
  `test_unknown_plugin_blocked`, `test_version_matches_changelog_passes`
  recovered from 0.4.0 failures. `pytest.yml` CI workflow expected to
  return GREEN on next run.

## [0.4.0] - 2026-05-17

Polish wave following 0.3.0. Verified the full dependency stack against
live registries on 2026-05-17 via ry-explore deep research (opus[1m] max
effort): all 8 MCP runtimes, all 5 GitHub Actions, Claude Code CLI,
Docker images, Node engine, OWASP Top 10:2025, MCP spec 2025-11-25, and
MADR 4.0.0 confirmed latest stable. Three patch/cosmetic drifts found
and closed; one major (actions/upload-artifact v4 -> v7) upgraded after
compatibility analysis.

### Changed

- **actions/upload-artifact v4.6.2 -> v7.0.1** in both release.yml and
  gitleaks.yml (`043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`). 3 majors
  forward: v5 declared Node v24 support, v6 moved runtime to Node 24
  (runner v2.327.1+), v7 added ESM upgrade + `archive: false` direct-upload
  parameter. ubuntu-latest runners (v2.327.1+ since Dec 2025) satisfy
  every prerequisite; our use cases (single-file/directory uploads, no
  multi-file glob, no `archive` param) fully compatible. Closes
  Dependabot signal previously deferred in 0.3.0.
- **gitleaks Docker image v8.30.0 -> v8.30.1** completed in 0.3.0+1
  (commit `6da7e80`) - this wave aligns the comment header (line 10)
  + ADR-0008 description with the actual image tag/digest in use.
  v8.30.1 patch is non-breaking (goreleaser update, report template
  cleanup, Go 1.24 build).
- **OWASP A09 wording** in 4 places (security skill, threat model, cc-canon
  database, SECURITY-01-OWASP memory) corrected from "Security Logging
  and Alerting Failures" to canonical OWASP "Security Logging &
  Alerting Failures" with ampersand.

### Added

- **Pytest test suite** (`tests/`, 6 files, ~280 LOC): F-TEST-05 audit
  closure for new validators. Each test imports from `conftest.py`
  `fake_repo` fixture which builds a minimal marketplace tree per test,
  then execs the validator subprocess and asserts on exit code + stderr.
  Coverage:
  - `test_validate_text_hygiene.py`: positive + em-dash/en-dash/BIDI
    negatives + ALLOWLIST contract.
  - `test_validate_docs_canon.py`: forbidden_tokens + version_floors
    direct-association window + graceful SKIP without cc-canon.json.
  - `test_validate_instruction_sync.py`: matching claims pass + drift
    detected + SKIP when blocks absent.
  - `test_validate_skill_allowed_tools.py`: known server passes +
    unknown server/plugin blocked.
  - `test_validate_release_state.py`: VERSION/CHANGELOG/plugin parity.
  - `test_generate_inventory.py`: --print/--check/refresh modes.
- **pyproject.toml** (87 lines): Ruff + pytest + Pyright shared config.
  Ruff `select = [E, W, F, I, B, UP, SIM, RUF]` baseline; pytest
  strict-markers + strict-config; Pyright basic mode with `include
  scripts plugins`. Repository remains metadata-only (no Python package
  built) - file exists purely as canonical settings anchor.
- **.github/workflows/pytest.yml**: SHA-pinned, harden-runner egress
  block, pip cache, runs `python3 -m pytest tests/ -v --tb=short` on
  push to main + path-filtered PRs. Path filter (`scripts/**`,
  `tests/**`, `pyproject.toml`, `.github/workflows/pytest.yml`)
  prevents redundant runs on docs-only commits. Closes audit F-CI gap
  for unit test coverage of new validators.
- **`probe_mcp_upstream.py` Dart probe**: extended PROBES tuple with
  `("DART_SDK_VERSION", "dart-stable", "dart")`. New `latest_dart_stable()`
  queries `storage.googleapis.com/dart-archive/channels/stable/release/latest/VERSION`.
  Probe reports `DRIFT DART_SDK_VERSION (dart): pinned=3.11.0, latest=3.11.6`
  as `::warning::` (advisory, not failing) so weekly CI surfaces Dart SDK
  bumps without forcing host toolchain upgrade.
- **`tests/conftest.py`** `fake_repo` + `patch_repo_root` fixtures:
  reusable across all validator tests, isolates filesystem state per
  test, monkeypatches cwd, copies validator scripts into the fake repo
  so `Path(__file__).resolve().parent.parent` lands on the fixture.

### Fixed

- **`scripts/validate_text_hygiene.py` ALLOWLIST extended** for
  `tests/test_validate_text_hygiene.py` (em-dash, en-dash, BIDI). The
  negative test fixtures intentionally embed dirty content to exercise
  the detection path; allowlisting the test file is the canonical
  "test fixture override" pattern.
- **`tests/conftest.py`**: removed unused `os` import (Pyright clean).
- **gitleaks.yml comment line 10**: now references `v8.30.1` (was
  `v8.30.0`) - drift between the comment-pinned refresh command and the
  actual image tag/digest in use.

### Notes

- **No version bumps required** for: `@anthropic-ai/claude-code 2.1.143`,
  `serena-agent 1.3.0`, `semgrep 1.163.0`, `@modelcontextprotocol/server-sequential-thinking 2025.12.18`,
  `@playwright/mcp 0.0.75`, `chrome-devtools-mcp 0.26.0`,
  `@upstash/context7-mcp 2.2.5`, `shadcn 4.7.0`, `github-mcp-server 1.0.4`,
  `actions/checkout v6.0.2`, `actions/setup-node v6.4.0`,
  `actions/setup-python v6.2.0`, `step-security/harden-runner v2.19.3`,
  `semgrep/semgrep:1.163.0` Docker digest, Node `>=22` engine, OWASP
  Top 10:2025, MCP spec 2025-11-25, MADR 4.0.0. All verified === upstream
  latest stable.
- **Dart SDK 3.11.0 -> 3.11.6** patch upgrade deferred to operator action
  (`brew upgrade dart`) since local toolchain currently reports 3.11.0;
  pin stays consistent with installed binary. Probe surfaces the
  drift as `::warning::` in weekly CI so the bump is not forgotten.
- **No security advisories found** for any pinned tool in the stack
  (verified via `gh api /repos/<owner>/<repo>/security-advisories` for
  serena, semgrep, playwright-mcp, context7, gitleaks; cvedetails.com
  semgrep sweep clean).
- **Anthropic plugins-official** verified at 2026-05-16 commit: 35
  plugins (was ~30 in 0.3.0 inspection), latest additions
  `carta-cap-table` (2026-05-16), `code-modernization` (2026-05-12).
  No new top-level manifest fields detected; `tools:` allowlist
  pattern remains canonical for read-only agents.
- **Reviewer phase intentionally skipped** in 0.4.0 per user directive
  ("ревью заново, но только когда я скажу"). All polish landed via
  static analysis + ry-explore deep research instead of subagent
  parallel review.
- **flow-memory-sync subagent** invoked to refresh all 18 numbered
  memories against new HEAD post-version-bump.

## [0.3.0] - 2026-05-17

Feature wave consolidating the 4-audit closure (research mеta-audit,
Python extractor methodology, full Health-84 audit, and Health-84
audit with self-critique). 28 user decisions captured across 7
AskUserQuestion rounds drove the implementation. All findings
verified live (live grep + ry-explore deep research with opus[1m]
max effort, 14 canonical Claude Code claims cross-validated against
official docs at 2026-05-17).

### Added

- **ADR corpus** (`docs/adr/`): 9 MADR 4.0.0 records covering
  irreversible decisions (fullrepo branch policy, dual-doc split,
  bilingual skill descriptions, file-first reviewer transport, local
  stdio GitHub MCP, MCP/hook ownership boundaries, MCP runtime pinning,
  CI baseline without paid add-ons, release version + tag convention).
  Plus `0000-template.md` and indexing `README.md`. Closes audit
  F-DEBT-01 / F-DOC-01.
- **Threat model** (`docs/security/threat-model.md`, ~250 lines):
  OWASP 2025-mapped surfaces with per-A0X mitigation cross-references
  to ADR / validator / D-number. Closes audit F-SEC-05.
- **JSON schemas** (`config/schemas/`): 5 schemas (marketplace, plugin,
  mcp, lsp, hooks) validated via new `scripts/validate_json_schemas.py`
  (jsonschema-backed; graceful SKIP when not importable). Includes
  `$dynamicRef`-aware Draft 2020-12 schemas with full canonical field
  coverage (e.g., `experimental.{themes,monitors}` wrapper v2.1.129+).
  Closes audit F-CONS-02 (.lsp.json validation).
- **Canon database** (`config/cc-canon.json`): forbidden_tokens,
  version_floors (7 knobs), hook_events (29), owasp_top_10_2025 (full
  canonical names). Read by new `scripts/validate_docs_canon.py`.
- **Marketplace policy** (`config/marketplace-policy.json`): centralized
  invariants table (mcp_owner, hook_owners, lsp_owner, skills_only_plugins,
  plugin dependency graph, protected branches, agent-only globs, runtime
  excludes, tag conventions, skill listing budget).
- **6 new validators** (`scripts/`): `validate_text_hygiene.py`,
  `validate_skill_allowed_tools.py`, `validate_release_state.py`,
  `validate_docs_canon.py`, `validate_instruction_sync.py`,
  `generate_inventory.py`. Plus `validate_json_schemas.py` (G9). All
  seven wired into `validate_marketplace.sh` + `.github/workflows/validate.yml`
  (harness grew from 13 to 22 steps). `probe_mcp_upstream.py` (G11) is
  wired separately into `.github/workflows/dependency-check.yml` (weekly
  cron + workflow_dispatch); it is intentionally NOT in the per-PR
  validate.yml because the network probe is best-effort and adds wall-clock
  to every PR.
- **3 new CI workflows**: `release.yml` (fully automated on tag push -
  validates release state, generates evidence bundle, creates GitHub
  Release via `gh release create --verify-tag`), `gitleaks.yml`
  (standalone secret scanner, docker zricethezav/gitleaks v8.30.0),
  `claude-cli-drift.yml` (weekly compare of pinned CLI to npm latest).
- **package.json** at root: pins `@anthropic-ai/claude-code@2.1.143`
  for Dependabot npm ecosystem tracking. `.github/dependabot.yml` now
  also tracks npm.
- **`scripts/refresh_actions_pins.sh`** (159 lines): resolves tag
  comments to fresh SHAs via `gh api`. Closes audit F-CI-03 (script was
  referenced in validate.yml comment but did not exist).
- **MCP upstream drift probes**: `scripts/probe_mcp_upstream.py` probes
  npm / PyPI / Homebrew JSON weekly via `dependency-check.yml`. Closes
  audit F-SYNC-02.
- **sync_contract YAML blocks** in AGENTS.md and .claude/CLAUDE.md
  (agent-only): 14 shared claims validated by
  `validate_instruction_sync.py`. Closes audit F-SYNC-01.
- **README inventory** (`<!-- inventory:begin --> ... <!-- inventory:end -->`):
  auto-generated 10-column per-plugin table + summary line.
  `generate_inventory.py --check` enforces freshness. Closes audit
  F-CONS-04 (drift between manual counts: README "10 skills with
  allowed-tools" was actually 15).

### Changed

- **`.claude/CLAUDE.md` + AGENTS.md docs canon** (audit F-CANON-01):
  `skillListingMaxDescChars` -> `maxSkillDescriptionChars` (canonical
  name); version floors corrected to v2.1.105+ for
  `maxSkillDescriptionChars` and `skillListingBudgetFraction`;
  `skillOverrides` documented as v2.1.129+ and NOT applying to plugin
  skills; `claude plugin tag --push` v2.1.119+ -> v2.1.118+; counts
  4 skills with `disable-model-invocation` (was 2), 15 skills with
  `allowed-tools` (was 10).
- **Claude Code compatibility floor** raised from `v2.1.111` to
  **`v2.1.143`** (matches CI pin). Covers all features used:
  `opus[1m]` (v2.1.111+), `alwaysLoad` (v2.1.121+), `claude plugin
  tag` (v2.1.118+), hook `if` filter (v2.1.118+), skill listing
  settings (v2.1.105+), `skillOverrides` (v2.1.129+), `experimental
  .{themes,monitors}` (v2.1.129+). Updated in
  `config/mcp-runtime-versions.env`, `docs/dependency-updates.md`,
  `README.md`, `AGENTS.md`. Closes audit F-COMPAT-01.
- **Dart SDK pin added**: `DART_SDK_VERSION=3.11.0` in
  `config/mcp-runtime-versions.env`;
  `scripts/check_mcp_runtime_versions.py` `SYSTEM_BINARY_TO_ENV` now
  includes `dart-flutter` (binary=`dart`, regex captures `Dart SDK
  version:`). 13/13 MCP servers now enforceable (was 12/13). Closes
  audit F-SYNC-01.
- **Marketplace manifest hardening**:
  `.claude-plugin/marketplace.json` `rldyour-flow` description corrected
  from `SessionStart/PreToolUse/Stop` to `SessionStart/PostToolUse/Stop`
  (audit F-ARCH-01). `metadata.pluginRoot: "./plugins"` removed to match
  Anthropic plugins-official precedent (audit F-ARCH-03). `$schema` URL
  replaced from broken 404 `https://anthropic.com/claude-code/marketplace.schema.json`
  to local `../config/schemas/marketplace.json`.
- **Hook `if` filters** (CC v2.1.118+) added to all 3 Bash lifecycle
  hooks (`post_tool_use_commit_advice`, `prepare_auto_sync`,
  `mark_sync_required`). Scope: `Bash(git commit*)` family. Reduces
  process spawning on unrelated Bash calls. Shell-side stdin filtering
  retained as defence-in-depth. Closes audit F-SCALE-01.
- **47 em-dashes + 1 en-dash normalized** to ASCII hyphens across 6
  files (`marketplace.json`, `docs/release-process.md`,
  `docs/rollback-restore.md`, `docs/dependency-updates.md`,
  `docs/observability.md`, `web-research/SKILL.md`) plus 5 em-dashes in
  `.github/workflows/*.yml` (caught by `validate_text_hygiene.py`).
  CHANGELOG [0.2.3] "zero em-dashes" claim is now retroactively true.
  Closes audit F-CONS-01 / F-DOC-02.
- **`docs/observability.md:96`** describes `.serena/.sync_marker`
  correctly as compound `${HEAD_SHA}:${NEWEST_SHA:-none}` fingerprint
  (D32 fix) plus full 10-field SHA-256 hash description for
  `.flow_sync_marker` (D31 fix). Closes audit F-SYNC-04.
- **`plugins/rldyour-lsps/README.md`** removes `.hcl/Bake` claims from
  Docker LSP coverage section (`.lsp.json` only maps `.dockerfile`).
  Closes audit F-LSP-01.
- **Semgrep `.serena/**` exclude narrowed** to explicit runtime
  artefact list (cache/reviews/diagnostics/markers); `.serena/memories/**`
  is now in scope of the secrets pack. Closes audit F-SEC-01.
- **All marketplace and plugin versions bumped** (project rule):
  VERSION `0.2.3 -> 0.3.0`; all 9 per-plugin versions bumped to
  **0.3.0** (was 0.2.1 for 8 plugins + 0.2.3 for `rldyour-flow`).
  Minor bump (not patch) signals feature wave: 8+ new validators,
  3 new workflows, ADR corpus, threat model, JSON schemas, centralized
  policy, sync_contract validator.

### Fixed

- **`smoke_serena_memory_taxonomy.sh:192`** stdin closure
  (`</dev/null`) so stop hook invocation does not block. Closes audit
  F-TEST-01.
- **`smoke_mcp_runtime.sh`** `HOST_BINARY_ALLOWLIST = {github,
  dart-flutter}` - pin=None outside the allowlist now FAILs. Closes
  audit F-TEST-02.
- **`.lsp.json` JSON validation**: now included in both
  `validate_marketplace.sh` and `.github/workflows/validate.yml` JSON
  parse step. Closes audit F-CONS-02.
- **dependabot.yml comment** corrected from "and the Claude Code npm
  pin" (was misleading: only github-actions ecosystem was actually
  tracked) to accurate dual-ecosystem language after G11 added npm
  block. Closes audit F-CI-01 / F-SYNC-03.

### Security

- **Tighter injection sanitization** (G8 + previous waves): repo-wide
  `validate_text_hygiene.py` enforces no em-dashes, no en-dashes, no
  BIDI control chars outside the hook-sanitizer regex (legitimate
  detection input).
- **gitleaks workflow** (G11): defence-in-depth on top of Semgrep
  p/secrets pack. Full-history scan with `--redact` mode.

### Notes

- All 14 audit-flagged technical claims verified against official
  Claude Code docs at 2026-05-17 (ry-explore deep research, opus[1m]
  max effort, 90 maxTurns). 7 verified-true, 3 partial, 0 verified-false.
- Feature branch: `feat/v0.3.0-comprehensive-audit-fixes`; 14 atomic
  commits.
- Memory sync via `flow-memory-sync` subagent + post-task sync to
  publish `fullrepo` snapshot follow this commit.
- Tags planned: `marketplace--v0.3.0` + 9 `<plugin>--v0.3.0` tags
  (10 tags total). `release.yml` triggers on tag push.

## [0.2.3] - 2026-05-17

### Fixed

- **Stop-hook loop guard fingerprint coverage gap (HIGH, D31)** -
  closure of `2026-05-16T1859Z-61b913d` systemic audit wave quality F-1
  (severity high, confidence 85). `plugins/rldyour-flow/scripts/flow_post_task_state.py:267-279`
  `fingerprint_payload` previously excluded three contributors to
  `needs_flow_sync`: `doc_files_changed`, `fullrepo_needs_attention`,
  and `instruction_docs_state.needs_instruction_docs_review`. Two
  consecutive Stop events with identical `(head, dirty, ahead/behind,
  branch_cleanup, serena_current)` but differing fullrepo / instruction
  / doc-file state produced an identical fingerprint, the loop guard at
  `plugins/rldyour-flow/hooks/stop_post_task_sync.sh:74` matched the
  stale marker, and Stop passed silently despite `needs_flow_sync=true`.
  Fix adds the three missing fields to `fingerprint_payload`. Verified
  live in this wave: fingerprint changed from `4b98fbf9540c2719`
  (clean state, HEAD 557bc00) to `a828ea1a9635f8eb` (clean state,
  HEAD 00d3f82) - two different fingerprints for the same `ahead=0,
  dirty=0` state because the new fields now correctly enter the hash.
  Commit `23901c6`.
- **Serena Stop-hook loop guard asymmetry (MEDIUM, D32)** -
  closure of `2026-05-16T1859Z-61b913d` quality F-2 (medium, 80).
  `plugins/rldyour-serena-mcp/hooks/stop_memory_sync.sh:72,77` wrote a
  bare `HEAD_SHA` to `.serena/.sync_marker` while
  `stop_post_task_sync.sh` wrote a full content-hash fingerprint. If a
  partial memory sync wrote memories without advancing HEAD, the next
  Stop saw the same `HEAD_SHA` and silently passed. Fix mirrors the
  flow pattern: marker now contains `${HEAD_SHA}:${NEWEST_SHA:-none}`
  compound fingerprint that captures both the project HEAD and the most
  recent memory-sync commit. Commit `23901c6`.
- **Swallowed non-dict analysis payload (MEDIUM, D33)** -
  closure of `2026-05-16T1859Z-61b913d` quality F-3 (medium, 75).
  `plugins/rldyour-serena-mcp/scripts/serena_memory_state.py:102-107`
  had a bare `pass` that silently discarded malformed analysis
  payloads, violating PHILOSOPHY-01-QUALITY-FIRST "no swallowed errors"
  hard ban. Fix logs the discard to stderr with type information; the
  control flow continues with the ref-range fallback as before.
  Commit `d563ea5`.
- **`validate_reviewer_contracts.sh` header listed 8 invariants but
  script checks 9 (D36)** - closure of wave-3 doc-fix pass.
  `scripts/validate_reviewer_contracts.sh` header comment missed
  invariant #9 (`RLDYOUR_REPORT_EOF` appears `>= 3` times in protocol)
  at line 100. Header now lists all 9 invariants and adds the concrete
  PASS breakdown: 7 PASS per agent x 6 agents = 42, plus 4
  protocol-level PASS = 46 total. No functional change. Commit
  `6f0c70d`.
- **Non-canonical cross-plugin path in rldyour-rules (D37)** -
  closure of architecture F-2 (info 78). `plugins/rldyour-rules/skills/project-instructions-policy/SKILL.md:28`
  referenced `${CLAUDE_PLUGIN_ROOT}/../rldyour-flow/scripts/fullrepo_sync.py`,
  a relative cross-plugin path that fails under partial install since
  `rldyour-rules/plugin.json` does not declare `rldyour-flow` as a
  dependency. Replaced with the canonical cross-plugin pattern
  `python3 "$(git rev-parse --show-toplevel)"/plugins/rldyour-flow/scripts/fullrepo_sync.py --bootstrap-init`
  per PATTERNS-01-CANONICAL Cross-Plugin Path Patterns. Both plugins
  co-exist inside the marketplace `pluginRoot: ./plugins`, so the
  git-toplevel path resolves correctly without a declared dependency.
  Commit `9a49121`.

### Added

- **`config/REVIEW.md.template` (D38)** - closure of verification F-4
  (info 90). Global `~/.claude/CLAUDE.md` REVIEW.md section promised
  `Template in config/REVIEW.md.template` but the template was absent
  from the repository - a documented promise without an artifact. New
  68-line template with eight sections (Always Check, Architecture,
  Quality, Consistency, Tests, Security, Skip, Notes) plus
  project-specific examples. Downstream projects consuming this
  marketplace copy the template to their repo root as `REVIEW.md`;
  reviewer agents (`flow-*-review`, `ry-rules-review`, `ry-sec-review`)
  auto-discover and read `REVIEW.md` when present. Commit `00d3f82`.

### Changed

- **CI parity with local validation harness (D34)** -
  closure of `2026-05-16T1859Z-61b913d` verification F-1 + F-2 (both
  medium, confidence 90/85). `.github/workflows/validate.yml`
  `syntax-checks` job now invokes `scripts/validate_reviewer_contracts.sh`
  (the D30 drift detector) and `scripts/smoke_mcp_runtime.sh` (pinning
  discipline + HTTP preflight). Reviewer-transport drift and MCP
  pinning regressions can no longer pass CI on the basis of "local
  validate_marketplace.sh catches it" alone. `smoke_mcp_capabilities.sh`
  remains local-only by design - it performs interactive session-based
  JSON-RPC initialize that requires auth unavailable in CI. Commit
  `dcbc7cc`.
- **Semgrep CI container digest-pinned (D35)** -
  closure of `2026-05-16T1859Z-61b913d` security F-1 (medium, 90, OWASP
  A03:2025 Software Supply Chain Failures). `.github/workflows/semgrep.yml`
  `container.image` changed from the mutable tag `semgrep/semgrep:1.163.0`
  to the immutable manifest-list digest
  `semgrep/semgrep:1.163.0@sha256:7cad2bc2d1e44f87f0bf4be6d1fa23aa90fb72015bebc89fb91385d813987a03`
  resolved 2026-05-16 via the Docker Hub v2 manifest API. The comment
  claim "SHA-pinned" is now structurally true. Re-resolution
  procedure is documented inline. Bumping the MCP `semgrep` pin in
  `plugins/rldyour-mcps/.mcp.json` should be paired with re-resolving
  this digest. Commit `dcbc7cc`.
- **Codebase-wide em-dash normalisation** - the global rldyour rule
  `No em dashes ( - ) - use only hyphens (-) everywhere` was previously
  violated in 603+ locations across docs, memories, skills, agents,
  references, commands, scripts, CHANGELOG, README, plugin.json
  descriptions, and config files. Every ` - ` (space + em-dash +
  space) and bare em-dash replaced with hyphen via a two-pass `sed`
  over the entire repository. Zero em-dashes remain at HEAD. No
  functional change: only typographic normalisation aligning practice
  with policy.
- **All marketplace and plugin versions bumped** - per the project
  release policy ("after any marketplace or plugin change, bump
  versions of both the marketplace and all touched plugins"). VERSION
  `0.2.2 -> 0.2.3`. `rldyour-flow` `0.2.2 -> 0.2.3`. All eight other
  plugins (`rldyour-mcps`, `rldyour-serena-mcp`, `rldyour-explore`,
  `rldyour-security`, `rldyour-browser`, `rldyour-design`,
  `rldyour-lsps`, `rldyour-rules`) bumped `0.2.0 -> 0.2.1` because
  the em-dash normalisation touched their `plugin.json` `description`
  fields and several of their `SKILL.md` / agent / command bodies,
  triggering the cache-refresh rule per AGENTS.md
  (`SKILL.md/agent.md/hooks.json/.mcp.json` changes trigger refresh).
  `marketplace.json` entries updated to match.

### Notes

- This release is a documentation, version-policy, and consistency
  consolidation. Every file change is auditable to a specific finding
  ID (D31 through D38) or to the explicit codebase-wide em-dash
  normalisation decision. No new features.
- Verification at HEAD: `bash scripts/validate_marketplace.sh` PASSES;
  `bash scripts/validate_reviewer_contracts.sh` reports `46 PASS / 0
  drift`; `python3 scripts/validate_plugin_versions.py` reports
  marketplace/manifest parity for all nine plugins;
  `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py`
  reports `is_current=true, memory_count=18,
  memory_match_reason=direct-head-reference`.
- Tag convention: `marketplace--v0.2.3` for the marketplace boundary
  and `<plugin-name>--v<version>` per plugin (nine plugin tags) via
  `claude plugin tag --push`. Tags should be created only after this
  release is pushed and validated.

## [0.2.2] - 2026-05-16

### Fixed

- **Reviewer output transport - wave-2 hardening (D29 follow-up)** -
  applied the medium-priority findings from the
  `2026-05-16T1433Z-e3d146b` self-bootstrap review wave. The
  `0.2.1` contract worked end-to-end (5 of 6 reviewers returned
  compact summaries through the parent context without truncation;
  `flow-verification-review` paused on a memories-not-yet-synced
  rumour, then resumed cleanly after the memory wave), but five
  documentation/contract gaps surfaced that could bite in adverse
  conditions.

### Changed

- **Heredoc EOF marker** (security medium 72, quality low 78):
  `plugins/rldyour-flow/references/reviewer-protocol.md` and all six
  reviewer agent bodies replaced the 2-character marker `MD` with the
  unique `RLDYOUR_REPORT_EOF`. Reports that legitimately contain
  short tokens (`MD hash`, `MD format`) can no longer close the
  heredoc early. Indented closing markers in the documentation
  examples were removed so the bash snippet is syntactically correct
  as written.
- **Explicit Bash write boundary** (security low 85): the contract in
  `reviewer-protocol.md` and every reviewer agent now states that the
  reviewer `Bash` write must target only
  `<report_dir>/<reviewer-name>.md`. `Edit`, `Write`, `NotebookEdit`
  remain absent from every reviewer `tools:` allowlist; `Bash`
  remains the only write-capable mechanism and is bounded by contract
  to the single report path.
- **Mandatory critical/high `Read` step** (security medium 65):
  `reviewer-protocol.md`, `plugins/rldyour-flow/skills/ry-start/SKILL.md`,
  and `plugins/rldyour-flow/skills/ry-review/SKILL.md` switched from
  "typically read critical/high" to "must read each report file for
  every critical and high finding before disposition".
  `flow-security-review` `Category` (OWASP/ASVS), `Attack path`,
  and `Verification` fields exist only in the report file, so the
  orchestrator now mandates the read.
- **Finding format severity enum** (integration F-2): `info` added to
  the documented severity list in `reviewer-protocol.md` so the
  summary `Counts:` field (`info=N`) maps to a documented severity
  class rather than an implicit one.
- **Terminology and citation alignment** (consistency medium 92,
  integration low 92/96): all six reviewer agents now quote Anthropic
  issue numbers as backticked inline-code matching
  `reviewer-protocol.md`, skills, `AGENTS.md`, `.claude/CLAUDE.md`,
  `CHANGELOG.md`. `run_id` label normalised to
  `<UTC-ISO-compact>-<git-short-sha>` (was a mix of three variants).
  One-liner cap wording normalised to `cap 30 entries`. `_summary.md`
  downgraded from "optionally writes" to "writes whenever any track
  reported one or more findings".
- **`RUNTIME_EXCLUDE_PATTERNS` alignment** (integration low 80):
  `plugins/rldyour-flow/scripts/fullrepo_sync.py` adds
  `.serena/diagnostics/**` and `.serena/reviews/**` so the runtime
  exclude list matches the `.gitignore` runtime-artefact block.
  `is_agent_path()` already returned `False` for these paths (they
  are not in `AGENT_ONLY_PATTERNS`); the addition is defensive
  consistency for future refactors.
- **Plugin version cache invalidation**: `rldyour-flow` plugin
  bumped `0.2.1 → 0.2.2`. Cache namespace becomes
  `~/.claude/plugins/cache/rldyour-claudecode/rldyour-flow/0.2.2/`.
  Marketplace `VERSION` and `.claude-plugin/marketplace.json`
  `rldyour-flow` entry bumped in lockstep. All other plugins stay at
  `0.2.0`.
- **Anthropic issue references upgraded to clickable markdown links**
  in `reviewer-protocol.md`, `ry-start`, `ry-review`, `AGENTS.md`,
  `.claude/CLAUDE.md` for easier human inspection of the regression
  context.

### Notes

- Read-only invariant for reviewer subagents unchanged. `Edit`,
  `Write`, `NotebookEdit` remain absent from every reviewer allowlist.
  `scripts/validate_agent_tools.py` continues to pass with all 8
  agent files validated.
- Wave-1 (`0.2.1`) tags `rldyour-flow--v0.2.1` and
  `marketplace--v0.2.1` are backfilled at commit `e3d146b` for
  `CHANGELOG.md` link integrity.
- Done criteria: `claude plugin validate plugins/rldyour-flow`
  passes; `validate_plugin_versions.py` reports `rldyour-flow 0.2.2`
  and all other plugins `0.2.0`; instruction docs remain under
  200-line cap; `bash scripts/validate_marketplace.sh` runs cleanly
  end-to-end; `marketplace--v0.2.1` and `marketplace--v0.2.2` tags
  pushed; `fullrepo` resynced.

## [0.2.1] - 2026-05-16

### Fixed

- **Reviewer subagent output transport (D29, R6)** - Claude Code 2.0.77+
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
  Fullrepo policy unchanged - `.serena/reviews/` is not in
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

- **Marketplace + all 9 plugins synchronised to `0.2.0`** - first
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

- **Wave 1-2 consolidation** - Conventional Commits discipline, strict-mode propagation
  to 14 utility/plugin scripts, prompt-injection markers expanded to 13+
  families with `re.IGNORECASE | re.UNICODE`, branch-name two-gate
  validation, agent `tools:` allowlist invariant via
  `scripts/validate_agent_tools.py`.
- **Wave 3 consolidation** - Serena memory base extended into the project brain: 8 new
  topic memories (`PHILOSOPHY-01-QUALITY-FIRST`, `PATTERNS-01-CANONICAL`,
  `BROWSER-01-WORKFLOW`, `DESIGN-01-WORKFLOW`, `EXPLORE-01-RESEARCH`,
  `LSPS-01-LANGUAGE-SERVERS`, `RULES-01-POLICY`, `SECURITY-01-OWASP`).
- **Wave 4 consolidation** - `bootstrap_check.sh` agent-only divergence guard (R5
  closure as `D19`), `.aider*` glob expansion at runtime, `WARN` to
  stderr for `RLDYOUR_FORCE_BOOTSTRAP=1` bypass and `git fetch`
  failures, `scripts/smoke_bootstrap_check.sh` with 7 assertions plus
  `AGENT_ONLY_PATHS` bash↔python drift detector, 18 memories
  cross-linked into a bidirectional `[[wikilinks]]` graph (≤2 hops from
  `CORE-01-INDEX`), OWASP Top 10:2025 (Final 2025-11-06) + ASVS 5.0.0
  precision, `TECHDEBT-01-NOW` Source Of Truth (11 anchors), D19-D23
  closures.
- **Wave 5 consolidation** - repository transferred from `rldyourmnd/rldyour-claude`
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
  tag boundary - same pattern Anthropic uses for minor-version bumps that
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
    `.github/workflows/**` changes) - the last green `actionlint` run
    is on `334fe09` where workflow YAML was last touched. This is
    intentional and documented; not a regression.
  - Fullrepo branch republished with `tracked_agent_paths: []` and
    R5 guard reporting `OK agent-only files match origin/fullrepo`.
  - Serena memories `RELEASE-01-VALIDATION` + `TECHDEBT-01-NOW` updated
    via `flow-memory-sync` subagent against the new HEAD SHA.

## [0.1.9] - 2026-05-16

### Changed

- **Wave 5 - CI hardening + org transfer** (repository moves from
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
  - **harden-runner egress audit** at the start of every job - surfaces
    unexpected outbound network calls in the GitHub Security tab.
  - **Claude Code CLI pinned**: `npm install -g @anthropic-ai/claude-code@2.1.143`
    (was unpinned). Closes Wave 4 security F-5 (INFO 35).
  - **New `.github/workflows/semgrep.yml`** - SAST via Semgrep OSS rules
    (Docker image `semgrep/semgrep:1.163.0`, matches the MCP server pin).
    Runs `semgrep scan --config=auto --error --metrics=off` on push, PR,
    and weekly schedule. Replaces an initial CodeQL workflow that required
    GitHub Advanced Security (paid add-on, not available for this repo's
    plan); Semgrep runs as a CLI without GHAS and fails CI on
    WARNING/ERROR-severity findings.
  - **New `.github/workflows/actionlint.yml`** - workflow YAML linter using
    `rhysd/actionlint` v1.7.12 binary, SHA256-verified against upstream
    `checksums.txt` (`8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8`).
  - **New `.github/dependabot.yml`** - monthly `github-actions` ecosystem
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

- **Wave 4 polish - R5 hardening + memory graph + research precision** (continues Wave 3
  vision: "Serena memories - мозг проекта" with quality-first / scalability-first
  defaults). Closes 6 deferred items from Wave 3 audit plus 21 findings from 6 parallel
  reviewer subagents (architecture, quality, consistency, integration, verification,
  security):
  - **R5 hardening (was open in TECHDEBT-01, now D19)**: `scripts/bootstrap_check.sh`
    new pre-`--bootstrap-init` divergence guard. For each agent-only path root,
    `git cat-file -e origin/fullrepo:$file` + `cmp -s $file <(git show ...)` detects
    content drift and refuses to proceed if local edits would be silently overwritten.
    Override via `RLDYOUR_FORCE_BOOTSTRAP=1` (now `WARN ... BYPASSED` to stderr, was
    `INFO` to stdout - closes Wave 4 security F-2, conf 70). `.aider*` glob expansion
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
    `--list-agent-only-patterns` CLI flag (deferred - smoke gate sufficient at
    current scale).
- **Deferred to Wave 5** (acknowledged, not blocking 0.1.8): GitHub Actions SHA
  pinning (security F-3, LOW 90 - `actions/checkout@v5` and `actions/setup-{node,
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

- **Wave 2 polish - "идеально выточенная система" (single seamless mechanism)**:
  - **Tier 1 (critical fixes)**: cross-plugin path in `flow-post-task-sync` SKILL replaced
    with `$(git rev-parse --show-toplevel)` (cwd-independent; `${CLAUDE_PROJECT_DIR}` is
    documented only for hook commands and stdio MCP env, not for skill execution context).
    New `scripts/validate_agent_tools.py` enforces agent `tools:` allowlist invariants
    (built-in tool names, MCP wildcard discipline, read-only-by-design MCP set).
    TECHDEBT-01-NOW.md gained R4 (non-Serena MCP wildcard future-proofing) and R5
    (bootstrap_check.sh footgun documentation).
  - **Tier 2 (consistency + observability)**: 14 utility/plugin scripts gained
    `IFS=$'\n\t'` + `unset CDPATH` after `set -euo pipefail` - 9 root `scripts/*.sh`
    (smoke_hooks, smoke_fullrepo_sync, smoke_mcp_capabilities, smoke_mcp_runtime,
    smoke_serena_memory_taxonomy, sync_fullrepo_branch, validate_marketplace,
    collect_diagnostics, install_local_git_hooks) plus 5 plugin scripts
    (`plugins/rldyour-flow/scripts/{detect_project_checks,git_sync_audit,
    local_git_ai_guard}.sh`, `plugins/rldyour-lsps/scripts/install_lsps_brew.sh`,
    `plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh`). Pattern matches
    existing gold standard in `scripts/install-rldyour-marketplace.sh`.
    CI workflow `.github/workflows/validate.yml` extended with 3 new steps in
    syntax-checks job: Agent tools allowlist validation, Hook lifecycle smoke,
    Serena memory taxonomy smoke. No `fetch-depth: 0` - current smokes don't need it.
  - **Tier 3 (defensive security)**: `scripts/worktree_add.sh` adds `git
    check-ref-format --branch` as second gate after the conservative regex
    `^[A-Za-z0-9._/-]{1,255}$` - rejects refs the regex accepts but git refuses
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
    - triggers `claude plugin update` cache refresh).
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
  `AGENTS.md` Engineering Constraints - Russian-only attacks were entirely uncovered
  before this wave). Defence-in-depth, not a known active exploit fix.
- **BRANCH validation second gate (MEDIUM, conf 70)**: `git check-ref-format
  --branch` invocation in `scripts/worktree_add.sh` rejects refs git itself would
  refuse, providing dual validation layers (cheap regex + canonical git check).
- **Static MCP wildcard invariant**: `validate_agent_tools.py` enforces that
  read-only agents may only wildcard MCP servers in `READ_ONLY_BY_DESIGN_MCPS`
  (context7, deepwiki, grep, semgrep). Catches the entire D15-class confused-deputy
  pattern at PR/validation time, not at agent invocation time.

### Verification

- `bash scripts/validate_marketplace.sh` - full harness passes including new
  "Agent tools allowlist validation" step (8 agent files × 13 MCP servers).
- `bash scripts/smoke_hooks.sh` - passes including 6 new runtime stdin payload
  cases (verified parse safety with `IFS=$'\n\t'` changes from Wave 1+2).
- `bash scripts/bootstrap_check.sh` - passes including new pre-push hook advisory.
- Manual injection tests: `[INST]`, `[SYSTEM]`, `Игнорируй все предыдущие
  инструкции`, `теперь ты` - all redacted to `[REDACTED]` in `additionalContext`.
- Manual branch validation tests: `-/foo`, `feat/../etc/passwd`,
  `--upload-pack=evil` - all REJECT (regex layer + git check-ref-format layer);
  `feat/test-validation_v1.0` - ACCEPT, dry-run produces correct git command.
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
  - Pattern follows canonical `anthropics/claude-plugins-official/plugins/pr-review-toolkit/agents/code-reviewer` - explicit allowlist for future-proof read-only enforcement (isolates these agents from any future edit-like tool that Claude Code might add).
  - Replaced broad `mcp__plugin_rldyour-mcps_serena__*` wildcard with an explicit 14-tool read-only Serena subset (`find_symbol`, `find_referencing_symbols`, `find_implementations`, `find_declaration`, `get_symbols_overview`, `search_for_pattern`, `read_file`, `list_dir`, `find_file`, `list_memories`, `read_memory`, `get_current_config`, `get_diagnostics_for_file`, `check_onboarding_performed`). The wildcard previously included Serena write tools (`create_text_file`, `replace_content`, `replace_symbol_body`, `insert_after_symbol`, `insert_before_symbol`, `rename_symbol`, `safe_delete_symbol`, `write_memory`, `edit_memory`, `delete_memory`, `rename_memory`) - the new explicit list eliminates that confused-deputy / prompt-injection risk for read-only reviewer and research agents.
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
  - `.claude/CLAUDE.md`: new `## Anthropic Precedent Confirmations` section (7 verified canonical patterns with citations to `anthropics/claude-plugins-official` SHA `1a2f18b05cf5652fd25403e8d229fc884fb84103` + community precedents); `skillListingBudgetFraction` recommendation `0.03` → `0.04` (Sonnet 200K context truncates tail-end auto-trigger descriptions for bilingual entries averaging ~373-400 chars at 0.03 - 0.04 fits both 200K and 1M context); agent frontmatter spec updated (`tools:` allowlist primary, `disallowedTools:` legacy); v2.1.139 `args: string[]` exec-form decline expanded with verification evidence (none of Anthropic's own plugin hooks.json use exec-form either).

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
- `scripts/smoke_mcp_capabilities.sh` no longer blanket-passes HTTP 401/403 for `HTTP_AUTH_GATED` servers - that shortcut hid the exact 403 entitlement-denial above. Now performs a real MCP `initialize` JSON-RPC handshake against HTTP endpoints, parses both `application/json` and `text/event-stream` response bodies, checks `result.serverInfo.name`, and classifies failures: 401 without auth → SKIP (reachable, no creds), 401 with auth → FAIL (token rejected), 403 → FAIL with explicit "switch to stdio github-mcp-server" hint, 200 without `serverInfo` → FAIL (silent-misconfig catch). Sends canonical `MCP-Protocol-Version` header. `figma` remains in `HTTP_AUTH_GATED` (accepts 200 without `serverInfo` until session id is established); `github` removed because it is now stdio.

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
  - `plugins/rldyour-flow/hooks/session_start_worktree_bootstrap.sh` -
    `SessionStart` hook (timeout 30s) that detects a fresh worktree
    (missing AGENTS.md / .claude/CLAUDE.md / .serena/project.yml marker)
    and auto-runs `fullrepo_sync.py --restore` to install the
    per-worktree `.git/info/exclude` block and check out agent-only
    paths from `origin/fullrepo`. Skip via
    `RLDYOUR_SKIP_WORKTREE_BOOTSTRAP=1`. The hook never publishes,
    never mutates origin.
  - `scripts/worktree_add.sh` - one-step helper for the manual
    `git worktree add` flow: detects whether the branch is local /
    remote / new, runs `git worktree add` with the right ref, then
    bootstraps agent-only context. Supports `RLDYOUR_DRY_RUN=1` and
    `RLDYOUR_WORKTREE_BASE_REF=HEAD` to mirror Claude Code's
    `worktree.baseRef: "head"` setting.
  - AGENTS.md "Worktree Workflow" section documenting the manual + auto
    flow, the Claude Code v2.1.139 `worktree.{baseRef,symlinkDirectories,
    sparsePaths}` settings, and the maintenance contract (per-worktree
    `.serena/memories/`, reconciled via `flow-post-task-sync` publish).
- `scripts/smoke_mcp_capabilities.sh` - capability-level smoke harness.
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
  citation per claim; removal-first principle; narrow tools - Serena memory
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

- Initial controlled Claude Code marketplace with nine first-party plugins -
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

[Unreleased]: https://github.com/NDDev-it-com/rldyour-claudecode/compare/1.0.0...HEAD
[1.0.0]: https://github.com/NDDev-it-com/rldyour-claudecode/compare/0.7.0...1.0.0
[0.7.0]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/0.7.0
[0.6.9]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/0.6.9
[0.6.8]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/0.6.8
[0.6.7]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.6.7
[0.6.6]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.6.6
[0.6.5]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.6.5
[0.6.4]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.6.4
[0.6.3]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.6.3
[0.6.2]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.6.2
[0.6.1]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.6.1
[0.6.0]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.6.0
[0.5.2]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.5.2
[0.4.0]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.4.0
[0.3.0]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.3.0
[0.2.3]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.2.3
[0.2.2]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.2.2
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
