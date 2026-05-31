# ADR-0010: macOS runner egress trust gap and current cross-platform smoke

- **Status**: superseded
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd
- **Related**: [ADR-0008](./0008-ci-baseline-without-paid-addons.md) (CI security baseline without paid add-ons)

## Context and Problem Statement

This ADR records the historical trust gap around hosted `macos-latest` jobs
that existed before the current public-free CI model. The current owner policy
supersedes the old removal-only decision: public adapter CI/CD may use standard
public GitHub-hosted Ubuntu, Windows, and macOS runners, while larger,
self-hosted, runner-group, ARC, private organization, and paid-size runner
labels remain forbidden.

Every default workflow in the repo uses `step-security/harden-runner` with
`egress-policy: block` and an explicit `allowed-endpoints` list per OWASP
A02:2025 Security Misconfiguration. The previous macOS job shipped without
that egress block because `step-security/harden-runner` did not support that
runner family.

The reviewer wave 2026-05-17T1448Z flagged this as Security F-1
(MEDIUM, confidence 75): macOS jobs lack an enforced network egress policy.

Current evidence: `.github/workflows/cross-platform.yml` runs only lightweight
metadata/path smoke on standard public runner labels. Heavy runtime/release
jobs remain Ubuntu-hosted when the toolchain is OS-independent or Linux-only.

## Decision Drivers

- Owner policy now prioritizes maximum free public GitHub Actions coverage
  without paid/private runner labels.
- Platform-specific path/archive/metadata portability is validated in public CI
  through lightweight standard Ubuntu, Windows, and macOS smoke.

## Considered Options

### Option 1: Skip the macOS job entirely

Drop `macos-latest` from `cross-platform.yml`. Eliminates the egress gap
by eliminating the runner.

**Pros**: zero trust gap.

**Cons**: removes a real correctness check. BSD-userland regressions in
`scripts/smoke_*.sh` would only surface on a maintainer's machine, not
in CI. This contradicts the original purpose of the workflow.

### Option 2: Self-host a macOS runner with strict egress (firewall / pfctl)

Provision a maintained macOS runner under our control with `pfctl` rules
mirroring the harden-runner allowlist.

**Pros**: enforced egress.

**Cons**: self-hosted runners introduce a substantial security surface
of their own (runner registration tokens, persistent worker process,
auto-update reliability). Operational cost is high for a personal
marketplace. macOS host maintenance burden.

### Option 3: Accept the gap with documented mitigations (historical)

Keep the GitHub-hosted macOS job. Document the gap as a known trust
boundary. Apply non-egress mitigations:
- Job runs only on **schedule + workflow_dispatch** (Architecture F-3
  closure in 0.5.1; previous `pull_request: types: [labeled]` trigger
  removed). PR authors cannot influence the macOS job indirectly.
- Job permissions are `contents: read` only.
- Job runs only **read-only validators + smoke scripts** (no `git push`,
  no `gh` commands, no secret access).
- Job has `timeout-minutes: 10` so a runaway runner is bounded.
- All actions used by the job are SHA-pinned per OWASP A03:2025.

### Option 4: Wait for upstream runner-family support

Keep status quo until `step-security/harden-runner` ships macOS.

**Pros**: zero present work.

**Cons**: indefinite wait. Upstream has not committed to macOS support
since 2022.

### Option 5: Remove the hosted OS coverage gap with lightweight smoke (current)

Use standard public Ubuntu, Windows, and macOS runner labels only for a
lightweight smoke job. Keep heavy runtime/release jobs on Ubuntu unless there
is a concrete OS-specific validation need and a public-free implementation.

**Pros**: free public OS coverage without paid/private runner labels; minimal
macOS/Windows exposure because the job is read-only and metadata/path-focused.

**Cons**: hosted BSD/Windows regressions in heavy shell/runtime flows are still
not fully exercised by GitHub Actions and must be checked locally when needed.

## Decision Outcome

**Current choice: Option 5** - keep lightweight standard public OS smoke and
forbid paid/private runner classes.

## Consequences

- Public adapter workflows use only standard public GitHub-hosted runner labels.
- `cross-platform.yml` covers Ubuntu, Windows, and macOS with read-only
  metadata/path smoke.
- Platform-specific heavy runtime checks can still be run locally by the owner
  when a change touches shell/runtime portability.

## Confirmation

- `grep "macos-latest" .github/workflows/*.yml` returns only the lightweight
  cross-platform smoke workflow.
- Root `scripts/validate_public_ci_policy.py` allows standard public macOS and
  Windows labels while rejecting larger, self-hosted, runner-group, ARC,
  private organization, and paid-size labels.
