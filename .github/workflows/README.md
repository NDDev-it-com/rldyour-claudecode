# GitHub Actions Workflows

Twelve workflows split into four classes by trigger policy. The repository is
public, so standard GitHub-hosted runners do not consume the organization's
paid private-repository Actions minutes. The split still keeps CI signal clear:
required gates prove the repo is valid, while advisory gates surface upstream
drift separately.

## Required PR gates (run on every push to `main` and every PR)

These workflows must be green before any merge.

| Workflow | Job | Purpose |
| --- | --- | --- |
| `validate.yml` | `validate-marketplace`, `syntax-checks` | `claude plugin validate` + JSON schemas + Python AST + bash -n + frontmatter + plugin-version parity + ownership boundaries + cross-tool contract + agent tools + reviewer contracts + hook lifecycle smoke + docs canon + sync_contract drift + release state + inventory freshness + MCP runtime drift + smoke_mcp_runtime |
| `pytest.yml` | `pytest` | Unit tests under `tests/` with `-m "not integration"`. Live network probes run in `dependency-check.yml`. |
| `gitleaks.yml` | `gitleaks` | Defense-in-depth secret scanning. |
| `semgrep.yml` | `semgrep` | SAST via OSS rule packs. |
| `codeql.yml` | `analyze` | CodeQL semantic analysis for Python and GitHub Actions. |
| `dependency-review.yml` | `dependency-review` | Pull-request dependency diff review, failing on moderate-or-higher advisories. |
| `actionlint.yml` | `actionlint` | Workflow YAML syntax + expression lint. PATH-filtered to `.github/workflows/**`. |

Branch protection on `main` should require these (and only these) status checks.

## Public supply-chain gate

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `scorecard.yml` | push to `main`, weekly schedule, `workflow_dispatch`, `branch_protection_rule` | OpenSSF Scorecard SARIF for public supply-chain posture. |

## Advisory scheduled gates (cron + workflow_dispatch only)

These workflows DO NOT run on push / PR. They surface drift without blocking
feature work.

| Workflow | Schedule | Purpose |
| --- | --- | --- |
| `claude-cli-drift.yml` | Mon 06:17 UTC | Compare pinned Claude Code CLI against npm latest. |
| `dependency-check.yml` | Mon 06:00 UTC | MCP runtime version drift + upstream probes (`probe_mcp_upstream.py`). Egress allowlist covers npm/PyPI/brew/Google Storage. |
| `cross-platform.yml` | Sun 04:00 UTC | Advisory smoke tests for hook and validation harness portability on Ubuntu. |

Manual trigger: `gh workflow run claude-cli-drift.yml` (or via the GitHub UI).
Treat all three as **advisory**: a failure is a signal to act, not a merge
blocker.

## Release-only hard gates (tag push only)

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `release.yml` | numeric product tag push (`X.Y.Z`) or `workflow_dispatch` | Validate release state + run full marketplace harness + emit `release-manifest.json` + create GitHub Release with evidence artefact. |

## Cost policy (public repository)

Public repositories using standard GitHub-hosted runners are free under GitHub
Actions billing. Keep this repository public and avoid larger/self-hosted
runners to preserve the zero-paid-minutes adapter policy.

To keep runs useful and lightweight:
- All default, required, scheduled, and release workflows use Ubuntu standard
  runners only. Architecture F-3 remains preserved: the prior
  `pull_request: types: [labeled]` trigger for `cross-platform.yml` was removed
  in 0.5.1 because it created skipped-run noise on unrelated labels.
- `concurrency:` blocks cancel redundant runs on the same ref.
- PATH-filtered triggers (`actionlint` on `.github/**`, `pytest` on
  `scripts/`/`tests/`) avoid running jobs for irrelevant changes.
- Workflow artifacts set explicit short retention: diagnostics/SARIF keep 14
  days, release evidence keeps 30 days.
- Advisory workflows are scheduled off-peak (Sun/Mon early UTC) to spread
  API quota usage.

Private forks must review this workflow set before enabling Actions because
private-repository minutes and storage are billed to the repository owner.

## Hardening (every workflow)

- Top-level `permissions: {}` (deny-all default per OWASP A01:2025).
- Per-job `permissions: contents: read` (write where strictly necessary, e.g. release).
- All third-party actions pinned by SHA, not by tag, per OWASP A03:2025.
- `step-security/harden-runner` with `egress-policy: block` and an explicit
  allowed-endpoints list on every default adapter job.
- `concurrency: { group, cancel-in-progress: true }` on every workflow.

## Manual operator gestures

This repository's CI is **manual-first** from the agent's perspective: any
agent (Claude, Codex, etc.) working in the repo never triggers GitHub Actions
on its own. Workflow runs are initiated only by:
1. A human push or PR (covered by required PR gates above).
2. An explicit user instruction such as "запусти CI", "прогони на гитхабе",
   "сделай ci", "verify on GitHub Actions".
3. The cron schedule (advisory workflows).
4. A release tag push (release workflow).

Agents must NOT call `gh workflow run` proactively; if a user has not asked,
local validation (`bash scripts/validate_marketplace.sh`, `pytest`) is the
correct gate.
