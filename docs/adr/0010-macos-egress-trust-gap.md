# ADR-0010: Former macOS runner egress trust gap

- **Status**: superseded
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd
- **Related**: [ADR-0008](./0008-ci-baseline-without-paid-addons.md) (CI security baseline without paid add-ons)

## Context and Problem Statement

This ADR records the historical decision that allowed a scheduled/manual
`macos-latest` smoke job for BSD-vs-GNU shell portability. The current owner
policy supersedes that decision: public adapter CI/CD must use Ubuntu standard
runners only for default, required, scheduled, and release workflows.

Every default workflow in the repo uses `step-security/harden-runner` with
`egress-policy: block` and an explicit `allowed-endpoints` list per OWASP
A02:2025 Security Misconfiguration. The previous macOS job shipped without
that egress block because `step-security/harden-runner` did not support that
runner family.

The reviewer wave 2026-05-17T1448Z flagged this as Security F-1
(MEDIUM, confidence 75): macOS jobs lack an enforced network egress policy.

Current evidence: `.github/workflows/cross-platform.yml` now runs only on
`ubuntu-latest` and applies `step-security/harden-runner` unconditionally.

## Decision Drivers

- Owner policy now prioritizes a uniform zero-paid-risk public adapter CI
  surface over hosted OS parity in GitHub Actions.
- Platform-specific shell portability remains a local maintainer validation
  concern rather than a public required/scheduled CI concern.

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

### Option 5: Remove the runner-family gap (current)

Remove the non-Ubuntu runner from public adapter CI and keep default checks on
Ubuntu standard runners.

**Pros**: uniform egress hardening, no runner-family ambiguity, simpler branch
protection.

**Cons**: hosted BSD-userland regressions are no longer caught by GitHub
Actions and must be checked locally when needed.

## Decision Outcome

**Current choice: Option 5** - remove the runner-family gap.

## Consequences

- All public adapter workflow jobs in this repository use Ubuntu standard
  runner labels.
- The former egress trust gap is closed by removing the affected hosted runner
  family from CI.
- Platform-specific checks can still be run locally by the owner when a change
  touches shell portability.

## Confirmation

- `grep "macos-latest" .github/workflows/*.yml` returns no workflow hits.
- `grep -A2 "egress-policy" .github/workflows/cross-platform.yml` shows the
  default hardened Ubuntu job.
