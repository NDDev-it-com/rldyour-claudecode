# GitHub Actions Workflows

Ten workflows split into three classes by trigger policy. This split keeps
the GHEC monthly-minutes budget predictable and separates "repo is broken"
signals from "upstream published an update" signals.

## Required PR gates (run on every push to `main` and every PR)

These workflows must be green before any merge.

| Workflow | Job | Purpose |
| --- | --- | --- |
| `validate.yml` | `validate-marketplace`, `syntax-checks` | `claude plugin validate` + JSON schemas + Python AST + bash -n + frontmatter + plugin-version parity + ownership boundaries + agent tools + reviewer contracts + hook lifecycle smoke + docs canon + sync_contract drift + release state + inventory freshness + MCP runtime drift + smoke_mcp_runtime |
| `pytest.yml` | `pytest` | Unit tests under `tests/` with `-m "not integration"`. Live network probes run in `dependency-check.yml`. |
| `gitleaks.yml` | `gitleaks` | Defense-in-depth secret scanning. |
| `semgrep.yml` | `semgrep` | SAST via OSS rule packs. |
| `codeql.yml` | `analyze` | CodeQL semantic analysis for Python and GitHub Actions. |
| `actionlint.yml` | `actionlint` | Workflow YAML syntax + expression lint. PATH-filtered to `.github/workflows/**`. |

Branch protection on `main` should require these (and only these) status checks.

## Advisory scheduled gates (cron + workflow_dispatch only)

These workflows DO NOT run on push / PR. They surface drift without blocking
feature work.

| Workflow | Schedule | Purpose |
| --- | --- | --- |
| `claude-cli-drift.yml` | Mon 06:17 UTC | Compare pinned Claude Code CLI against npm latest. |
| `dependency-check.yml` | Mon 06:00 UTC | MCP runtime version drift + upstream probes (`probe_mcp_upstream.py`). Egress allowlist covers npm/PyPI/brew/Google Storage. |
| `cross-platform.yml` | Sun 04:00 UTC | Smoke tests on Linux **and** macOS (BSD vs GNU userland surface). |

Manual trigger: `gh workflow run claude-cli-drift.yml` (or via the GitHub UI).
Treat all three as **advisory**: a failure is a signal to act, not a merge
blocker.

## Release-only hard gates (tag push only)

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `release.yml` | tag push matching `marketplace--v*` or `rldyour-*--v*`, or `workflow_dispatch` | Validate release state + run full marketplace harness + emit `release-manifest.json` + create GitHub Release with evidence artefact. |

## Cost policy (GitHub Enterprise Cloud)

GitHub-hosted runner minute multipliers: Linux 1x, Windows 2x, **macOS 10x**.
GHEC plan ships 50,000 included minutes/month; private repo Actions usage is
billed to the owner.

To stay under budget:
- macOS runs only in `cross-platform.yml`, triggered only by the Sunday schedule
  or explicit `gh workflow run cross-platform.yml`. The default PR experience
  uses Ubuntu only. (Architecture F-3 closure: the prior `pull_request:
  types: [labeled]` trigger was removed in 0.5.1 because it created
  skipped-run noise on every unrelated label add; manual operator gestures
  remain available via `gh workflow run`.)
- `concurrency:` blocks cancel redundant runs on the same ref.
- PATH-filtered triggers (`actionlint` on `.github/**`, `pytest` on
  `scripts/`/`tests/`) avoid running jobs for irrelevant changes.
- Advisory workflows are scheduled off-peak (Sun/Mon early UTC) to spread
  API quota usage.

## Hardening (every workflow)

- Top-level `permissions: {}` (deny-all default per OWASP A01:2025).
- Per-job `permissions: contents: read` (write where strictly necessary, e.g. release).
- All third-party actions pinned by SHA, not by tag, per OWASP A03:2025.
- `step-security/harden-runner` with `egress-policy: block` and an explicit
  allowed-endpoints list on every Linux job. macOS skips harden-runner because
  the action does not support macOS runners.
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
