# ADR-0008: CI security baseline without paid add-ons

- **Status**: accepted
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd

## Context and Problem Statement

The repository is hosted on GitHub Enterprise Cloud (private). GHEC
includes 50,000 Linux runner-minutes/month for private repos but does
**not** include GitHub Advanced Security (GHAS, paid add-on, required for
private-repo code scanning to upload SARIF to the Security tab) or GitHub
Secret Protection (paid add-on, required for push protection).

CI must achieve a real security baseline without these paid features:
SAST coverage, supply-chain hardening, secret scanning, and least-privilege
workflow permissions.

Evidence: `.github/workflows/semgrep.yml:1-13` (explicit "Semgrep replaces
CodeQL because GHAS is not enabled"), `.github/workflows/validate.yml:16`
(top-level `permissions: {}`), `.github/workflows/gitleaks.yml` (G11).

## Decision Drivers

- Zero paid GitHub add-ons.
- Strong supply-chain hardening (OWASP A03:2025).
- Predictable minute spend within 50K/month included quota.

## Considered Options

- A: Use CodeQL with SARIF upload. Requires GHAS, paid for private repos.
- B: Use Semgrep with SARIF upload. SARIF still requires GHAS.
- C: Semgrep OSS as CLI without SARIF upload; gitleaks as CLI without
  SARIF upload; pin all actions to commit SHAs; harden-runner egress
  block; least-privilege permissions.

## Decision Outcome

Chosen option: **C**. The CI baseline:

- **`validate.yml`**: claude plugin validate + JSON Schema + Python AST +
  shell `bash -n` + frontmatter + 6 custom validators + reviewer contract
  drift + MCP runtime smoke + Serena taxonomy smoke + bootstrap divergence
  smoke. 19 steps total.
- **`semgrep.yml`**: Semgrep OSS via digest-pinned Docker image
  (`semgrep/semgrep:1.163.0@sha256:7cad2bc2d1e44f87f0bf4be6d1fa23aa90fb72015bebc89fb91385d813987a03`,
  matches the MCP pin). 6 OSS rule packs (`p/python`, `p/github-actions`,
  `p/security-audit`, `p/secrets`, `p/owasp-top-ten`, `p/ci`). `--error`
  fails CI on WARNING/ERROR findings. Findings surface in job log; no
  SARIF upload.
- **`gitleaks.yml`** (G11; bumped to v8.30.1 in 0.4.0): defence-in-depth
  secret scanner via official Docker image (`zricethezav/gitleaks:v8.30.1`,
  digest-pinned), `detect --redact` with full git history (fetch-depth: 0).
  Findings surface in job log + SARIF report archived on failure (always:,
  retained 30 days).
- **`actionlint.yml`**: workflow YAML linter with checksum-verified
  install.
- **`dependency-check.yml`** + **`claude-cli-drift.yml`** (G11): weekly
  drift detection for MCP runtime pins and Claude Code CLI version.

Cross-cutting:

- **SHA-pinned actions** (OWASP A03:2025): every `uses:` references a
  40-char commit SHA + trailing tag comment. `scripts/refresh_actions_pins.sh`
  (G7) re-resolves tags to fresh SHAs via `gh api`.
- **harden-runner egress block**: every job uses
  `step-security/harden-runner@<sha>` with `egress-policy: block` and
  explicit `allowed-endpoints`.
- **Top-level `permissions: {}`**: deny-all default; per-job permissions
  grant minimum scope (`contents: read` for validators,
  `contents: write` only for release.yml `gh release create`).
- **Concurrency**: `cancel-in-progress: true` on validate/semgrep/actionlint;
  `cancel-in-progress: false` on release (releases must complete).

### Consequences

- Good: real security baseline at $0 add-on cost.
- Good: 19 validators give deep coverage of marketplace invariants.
- Bad: no SARIF upload means findings live in job logs, not the GitHub
  Security tab. Mitigation: release-blocking CI gate forces findings to
  surface before tag push.
- Bad: GHAS Dependabot security alerts not available; relying on
  Dependabot version-update PRs (free tier) for dependency drift.
- Bad: no GHAS push protection on the repo. Mitigation: local pre-push
  guard (`plugins/rldyour-flow/scripts/local_git_ai_guard.sh`) scans for
  secrets before push.

## Confirmation

- `.github/workflows/*.yml` audited: every `uses:` line is a 40-char SHA
  pin with trailing tag comment.
- `permissions: {}` at workflow top level in every workflow.
- `step-security/harden-runner@ab7a9404c0f3da075243ca237b5fac12c98deaa5`
  consistently used.
- `bash scripts/validate_marketplace.sh` exits 0; CI mirrors most steps.

## More Information

- Related: ADR-0009 (release tag convention).
- Future option: if the project upgrades to GHEC + GHAS, migrate Semgrep
  to SARIF upload + CodeQL companion; add push protection.

## Amendment 2026-05-18 (release 0.6.0): public repository unlocks CodeQL

Decision: when the repository visibility toggles to **public** (release
0.6.0 public-readiness wave), CodeQL becomes free per GitHub billing -
the GHAS paywall does NOT apply to public repositories. The "no CodeQL,
no SARIF upload" framing in this ADR was correct for the private-repo
configuration that originally drove it; on public repos, CodeQL is
available at no cost and SARIF results upload to the Security tab.

Action taken in release 0.6.0:

- **Added** `.github/workflows/codeql.yml` running CodeQL on `python`
  and `actions` language matrix with `security-and-quality` query pack.
- **Retained** Semgrep OSS, gitleaks, harden-runner, SHA pins,
  `permissions: {}` baseline: CodeQL is additive, not a replacement.
  Defence in depth via three complementary security workflows
  (CodeQL = semantic, Semgrep = pattern SAST, gitleaks = secret scan)
  is the new public-repo baseline.
- **Threat-model document update**: `docs/security/threat-model.md`
  Section 4 to reflect CodeQL availability and add reference to
  ADR-0008 amendment.

The original decision (no paid add-ons, no GHAS) still applies for
contributors who fork this repository into a private repository -
they will need to disable CodeQL or accept the GHAS billing surface.
