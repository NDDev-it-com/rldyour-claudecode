# ADR-0010: macOS runner egress trust gap is an accepted upstream limitation

- **Status**: accepted
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd
- **Related**: [ADR-0008](./0008-ci-baseline-without-paid-addons.md) (CI security baseline without paid add-ons)

## Context and Problem Statement

`.github/workflows/cross-platform.yml` runs a smoke matrix on
`ubuntu-latest` AND `macos-latest` to verify that shell scripts behave
consistently on GNU userland (Linux) and BSD userland (macOS) - `sed -i`,
`find`, `date`, and `readlink` differ between the two and have surfaced
real bugs in earlier waves.

Every other workflow in the repo uses `step-security/harden-runner` with
`egress-policy: block` and an explicit `allowed-endpoints` list per OWASP
A02:2025 Security Misconfiguration. On `cross-platform.yml`, the macOS job
ships without that egress block because **`step-security/harden-runner`
does not support macOS runners** (per the action's upstream documentation
at `https://github.com/step-security/harden-runner`; macOS support has
been open since 2022 and remains "not on our roadmap").

The reviewer wave 2026-05-17T1448Z flagged this as Security F-1
(MEDIUM, confidence 75): macOS jobs lack an enforced network egress policy.

Evidence: `.github/workflows/cross-platform.yml` lines 42-58 (Harden Runner
step guarded by `if: runner.os == 'Linux'`); upstream limitation documented
in `step-security/harden-runner` README "Supported Platforms" table.

## Decision Drivers

- Cross-platform smoke coverage is a real correctness gain (BSD vs GNU
  userland differences are observed bugs, not theoretical).
- macOS-runner egress enforcement is not currently available from any
  GitHub Actions ecosystem alternative we trust.
- Cost: GitHub-hosted macOS runners are 10x Linux multiplier; the
  matrix already runs only on schedule + workflow_dispatch.
- Threat model: this is a **personal-marketplace** repository; the macOS
  job runs read-only validators + smoke scripts that do not write to any
  external sink. The hijack surface is small.

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

### Option 3: Accept the gap with documented mitigations (chosen)

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

### Option 4: Wait for upstream macOS support

Keep status quo until `step-security/harden-runner` ships macOS.

**Pros**: zero present work.

**Cons**: indefinite wait. Upstream has not committed to macOS support
since 2022.

## Decision Outcome

**Chosen: Option 3** - accept the gap with documented mitigations.

Rationale: cross-platform smoke coverage delivers concrete value; the
trust gap is bounded (read-only validators, no secret access, no PR
trigger, 10-minute timeout); the alternative options either remove the
coverage or take on a larger security surface.

## Consequences

- macOS smoke runs without enforced egress allowlist. Documented in
  `.github/workflows/README.md` and in this ADR.
- If `step-security/harden-runner` ships macOS, revisit and adopt within
  one release.
- If a real macOS-runner compromise occurs, this ADR is the audit trail.
- This ADR is referenced from `.serena/memories/TECHDEBT-01-NOW.md`
  R6.macOS-egress entry for cross-tool discoverability.

## Confirmation

- `grep -A2 "egress-policy" .github/workflows/cross-platform.yml`
  shows the Linux-only conditional.
- `grep "macos-latest" .github/workflows/*.yml` confirms macOS appears
  only in `cross-platform.yml`.
- `gh workflow view cross-platform.yml --json` shows triggers limited
  to `schedule + workflow_dispatch` post-0.5.1.
