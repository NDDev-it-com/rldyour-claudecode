# Security Policy

## Supported Versions

This is the Claude Code plugin marketplace for rldyour SDLC flows: MCP/LSP,
Serena memory, security review, browser/design workflows, and reviewer agents.
Only the latest
marketplace release boundary tag (`marketplace--v<MAJOR>.<MINOR>.<PATCH>`)
receives security fixes. Each plugin carries its own `<plugin>--v<X.Y.Z>`
tag aligned with the marketplace boundary.

| Version | Supported |
|---------|-----------|
| Latest `marketplace--v0.6.x` | yes |
| Earlier minor / patch | no |

When a security issue lands, the wave bumps every plugin to the same
patch release (see `docs/release-process.md` and ADR-0009 for the
versioning contract).

## Reporting a Vulnerability

Please use **GitHub Security Advisories** as the primary channel:

- Open a private advisory at
  `https://github.com/NDDev-it-com/rldyour-claudecode/security/advisories/new`.
- GitHub notifies the maintainer privately; the advisory stays embargoed
  until a fix is published.

Do **not** open a public Issue for security reports. Public Issues are for
non-security bugs, regressions, and missing-component requests.

## What counts as a security issue here

This is a Claude Code plugin marketplace, not a production runtime. The
threat model focuses on:

- **Prompt injection via hook output**: hook scripts that echo untrusted
  text into Claude's context window. See `plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh`
  for the canonical sanitization helper (`sanitize_for_advisory()` -
  redacts BiDi control characters, injection markers, role-play prefixes
  in 13+ marker families across EN/RU).
- **Supply chain integrity**: MCP runtime version pins
  (`config/mcp-runtime-versions.env`), GitHub Actions SHA pins, npm
  pins. Dependabot tracks drift; `scripts/check_mcp_runtime_versions.py`
  enforces parity locally and in CI.
- **Boundary leakage**: agent-only files (`AGENTS.md`, `.claude/**`,
  `.serena/memories/**`) must stay on the `fullrepo` branch and never
  reach `main`. The `fullrepo_sync.py` script enforces this; ADR-0001
  documents the policy.
- **Hook freshness invariants for branch-split projects**: see ADR-0011.

## What does NOT count

- Issues that require executing untrusted plugins. By design, this
  marketplace catalogues only the owner's own plugins. Third-party plugin
  trust is the user's responsibility.
- Issues that require credentials leaks from your own environment. The
  repo does not store any credentials; `bootstrap_check.sh` enforces that
  required env vars (`CONTEXT7_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`)
  are present locally before any MCP server starts.

## Defensive Tooling

- **gitleaks** (`.github/workflows/gitleaks.yml`): secret scanner runs on
  every push to `main`, every PR, and a weekly schedule (Tue 06:00 UTC).
  Full git-history scan via `fetch-depth: 0` checkout. Container pinned
  by digest.
- **Semgrep** (`.github/workflows/semgrep.yml`): SAST with OWASP Top 10
  + secrets + GitHub Actions rule packs, container pinned by digest.
- **CodeQL** (`.github/workflows/codeql.yml`): semantic analysis for
  Python and GitHub Actions workflows, free for public repos.
- **Dependabot** (`.github/dependabot.yml`): version drift detection for
  Actions and npm.
- **harden-runner**: egress-policy `block` on every workflow with
  explicit allowlist per workflow.
- **OWASP A03:2025 supply-chain hygiene**: every third-party Action is
  SHA-pinned; container images are digest-pinned where supported.

## Acknowledgements

Security findings credited in `CHANGELOG.md` under the relevant release
entry. Wave history with `D<N>` debt-closure IDs in
`.serena/memories/TECHDEBT-01-NOW.md` (agent-only, not on `main`).
