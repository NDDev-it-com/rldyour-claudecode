# Threat Model

OWASP Top 10:2025 mapping for `rldyour-claudecode`. The marketplace itself
is metadata + Bash/Python scripts + hook handlers + workflow YAML; there is
no runtime application code. The threat surface is therefore the set of
executable boundaries an attacker (or a careless contributor) can use to
exfiltrate secrets, mutate the host, or poison AI context.

Scope: this document covers the marketplace as shipped from
`github.com/nddev-it-com/rldyour-claudecode`. It does not cover threats
introduced by the user's personal Claude Code session or by other plugins
the user installs.

## Executable surfaces

| Surface | Owner | Privileges | Mitigations |
|---|---|---|---|
| `plugins/rldyour-flow/hooks/*.sh` | `rldyour-flow` | Bash, runs in user session | Strict mode trio (`set -euo pipefail` + IFS + unset CDPATH); advisory-only (no push/merge/publish); `if` filters limit invocation to `Bash(git commit*)` family. |
| `plugins/rldyour-serena-mcp/hooks/*.sh` | `rldyour-serena-mcp` | Bash, runs in user session | Same strict mode; Stop hook exits 2 advisory (no destructive ops); fingerprint loop guard. |
| `plugins/rldyour-flow/scripts/fullrepo_sync.py` | `rldyour-flow` | Filesystem + git plumbing | `bootstrap_check.sh` divergence guard refuses `--bootstrap-init` when local agent-only files differ from `origin/fullrepo`; `--publish` uses `--force-with-lease` (not `--force`); `local_git_ai_guard.sh` pre-push blocks agent-only paths on product branches. |
| `plugins/rldyour-mcps/.mcp.json` | `rldyour-mcps` | Spawns MCP servers (stdio + HTTP) | All 13 servers pinned (`==X.Y.Z` / `@X.Y.Z` / exact URL / host-binary version); `scripts/check_mcp_runtime_versions.py` enforces parity; `scripts/smoke_mcp_runtime.sh` HOST_BINARY_ALLOWLIST fails pin=None for unknown servers; `scripts/probe_mcp_upstream.py` weekly drift check. |
| `.github/workflows/*.yml` | CI | runs-on GitHub-hosted runners | SHA-pinned actions; `permissions: {}` top-level (deny-all); harden-runner egress block + explicit allowlist per workflow; `concurrency.cancel-in-progress` to bound minute spend. |
| `scripts/*.{sh,py}` | repo root | Runs in local validation context | Strict mode trio in all shell scripts; Python scripts use stdlib only where possible (no pip dependency to validate locally except jsonschema for G9 schemas - graceful SKIP if unavailable). |

## OWASP 2025 mapping

### A01:2025 Broken Access Control

**Threat**: contributor (or compromised CI token) gains write to `main`
without review, pushes a malicious plugin manifest or hook.

**Mitigations**:
- ADR-0001 (fullrepo) keeps agent-only context out of `main`; product
  changes on `main` are scoped.
- ADR-0008 (CI baseline): `permissions: {}` top-level + per-job
  least-privilege; release.yml is the only workflow with
  `contents: write`, and it requires a signed tag.
- Solo maintainer model (resolved during 28-question intake, raunda 1):
  no CODEOWNERS required at present; signed commits via local git config
  as self-discipline.
- `plugins/rldyour-flow/scripts/local_git_ai_guard.sh` pre-push hook
  blocks product-branch pushes that introduce agent-only paths or
  definite secrets.

### A02:2025 Security Misconfiguration

**Threat**: workflow YAML or `.mcp.json` accidentally grants
overly-broad permissions or unpins a runtime.

**Mitigations**:
- `scripts/validate_marketplace.sh` (19 steps) plus CI mirror in
  `.github/workflows/validate.yml`.
- `config/schemas/{marketplace,plugin,mcp,lsp,hooks}.json` JSON Schema
  validation via `scripts/validate_json_schemas.py` (additive to
  `claude plugin validate`; covers `.mcp.json`, `.lsp.json`, `hooks.json`
  which Claude CLI does not validate).
- `config/marketplace-policy.json` centralizes invariants
  (mcp_owner, hook_owners, skill listing budget, agent-only globs, runtime
  excludes, tag conventions).
- `scripts/smoke_mcp_runtime.sh` HOST_BINARY_ALLOWLIST: pin=None FAILs
  for unknown servers (audit F-TEST-02 closure).

### A03:2025 Software Supply Chain Failures

**Threat**: third-party action / MCP runtime / Docker image upgraded
silently to a malicious version.

**Mitigations**:
- SHA-pinned GitHub Actions (`uses: owner/repo@<40-hex-sha>  # tag`).
- `scripts/refresh_actions_pins.sh` re-resolves tags to fresh SHAs via
  `gh api`.
- Docker images digest-pinned (`semgrep/semgrep:1.164.0@sha256:2079836...`).
- All 13 MCP servers pinned per ADR-0007.
- `actions/dependabot` + `.github/dependabot.yml` for github-actions and
  npm ecosystems.
- `.github/workflows/claude-cli-drift.yml` weekly check for the Claude
  Code CLI npm pin.
- `scripts/probe_mcp_upstream.py` weekly check for MCP upstream releases
  via npm / PyPI / Homebrew JSON.

### A04:2025 Cryptographic Failures

**Threat**: secrets in transit or at rest unprotected; weak signing.

**Mitigations**:
- HTTPS-only for HTTP MCP servers (`config/schemas/mcp.json` enforces
  `pattern: "^https://"`).
- Signed git tags for releases (`git tag -s`; ADR-0009);
  `gh release create --verify-tag` refuses unsigned tags.
- No secrets in committed files (verified by `gitleaks.yml` + Semgrep
  p/secrets pack + manual review).

### A05:2025 Injection

**Threat**: user-controlled text (commit message, prompt, file path) is
echoed into LLM context or shell command without sanitization.

**Mitigations**:
- `plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh`:
  - `INJECTION_MARKERS` regex covers 13+ marker families (system tags,
    chat templates, role-play prefixes, Russian-language equivalents,
    2026 tool-call XML tags).
  - `BIDI_CONTROLS` regex covers Unicode U+202A-U+202E + U+2066-U+2069
    (Trojan Source attack family) - replaced with `[REDACTED-BIDI]`.
  - `sanitize_for_advisory()` helper applied at 4 sites (commit subject
    plus 3 path warning sites).
- `scripts/validate_text_hygiene.py` repo-wide check: em-dashes,
  en-dashes, BIDI controls absent from committed files (G8).

### A06:2025 Insecure Design

**Threat**: design encourages destructive automation (hooks that push,
merge, publish without human approval).

**Mitigations**:
- ADR-0001 + ADR-0004 + ADR-0006: hooks are advisory-only by contract.
  `Edit`, `Write`, `NotebookEdit` are absent from every reviewer
  agent allowlist; `Bash` write is contractually bounded to one
  report path per reviewer.
- Stop hooks use exit 2 to block + loop-guard fingerprint to avoid
  infinite loops without doing the work themselves; the orchestrator
  (`ry-start` / `flow-post-task-sync` skill) makes high-blast-radius
  decisions.

### A07:2025 Authentication Failures

**Threat**: PAT / API key leaked to logs, browsing surfaces, or shared
caches.

**Mitigations**:
- `${CONTEXT7_API_KEY}` and `${GITHUB_PERSONAL_ACCESS_TOKEN}` are
  `${VAR}` expansion only - never literals.
- `plugins/rldyour-mcps/.env.example` documents required vars without
  any value.
- `.gitignore` excludes `.env*` except `.env.example`; runtime markers
  excluded.
- `gitleaks.yml` workflow scans full history with `--redact`.

### A08:2025 Software or Data Integrity Failures

**Threat**: malicious commit replaces a plugin manifest or memory file
without detection.

**Mitigations**:
- Signed tags + `--verify-tag` (ADR-0009).
- `scripts/validate_release_state.py` enforces VERSION / CHANGELOG /
  manifests parity before release.
- Local pre-push guard (`local_git_ai_guard.sh`) blocks agent-only paths
  on product branches.
- Semgrep narrowly excludes only `.serena/cache/**` + runtime markers;
  `.serena/memories/**` is in scope (G12 closure).

### A09:2025 Security Logging & Alerting Failures

**Threat**: security-relevant events (override bypass, capability smoke
failure, tag drift) happen silently.

**Mitigations**:
- `RLDYOUR_FORCE_BOOTSTRAP=1` bypass writes to
  `.serena/.bootstrap_overrides.log` with timestamp + HEAD + user +
  cwd (D41).
- CI workflow logs preserved 90 days; failed runs surface in PR checks.
- `scripts/probe_mcp_upstream.py` emits `::warning::` for drift; CI
  job summary surfaces them.
- `scripts/validate_release_state.py` INFO for tag mismatch (release
  workflow can grep for FAIL without false positives on feature branches).

### A10:2025 Mishandling of Exceptional Conditions

**Threat**: failed validator / smoke / capability probe silently passes
because of a bare `pass` or swallowed exception.

**Mitigations**:
- PHILOSOPHY-01-QUALITY-FIRST "no swallowed errors" hard ban.
- D33 closure: `serena_memory_state.py` no longer has bare `pass` on
  malformed analysis payload; logs to stderr and continues with
  documented fallback.
- All shell scripts use strict mode trio (`set -euo pipefail`).
- `bash -n` syntax check in CI + validate_marketplace.sh.

## Trust boundaries

Three boundaries exist:

1. **Maintainer ↔ marketplace**: maintainer pushes signed commits and
   tags; pre-push guard catches obvious mistakes; CI enforces structural
   correctness.
2. **Marketplace ↔ Claude Code runtime**: Claude Code installs the
   marketplace via `claude plugin install`; plugin code runs in the
   maintainer's session. Pinned MCP runtimes + hooks confine the surface.
3. **Claude Code runtime ↔ external services**: HTTP MCP servers
   (DeepWiki, grep.app, Figma, OpenAI Docs) traverse the network; PATs
   leave the local machine for GitHub. Egress block + harden-runner
   confines CI; local sessions trust user environment.

## Known acceptable risks

- **Code Scanning availability** (updated 2026-05-18, release 0.6.0):
  the repository is now public. CodeQL is free for public repos per
  GitHub billing and uploads SARIF to the Security tab via
  `.github/workflows/codeql.yml`. Dependabot security updates are
  enabled. The previous "no GHAS, no SARIF" framing applied to the
  private-repo configuration that drove the original CI baseline -
  see ADR-0008 amendment 2026-05-18. CodeQL + Semgrep + gitleaks are
  now three complementary security workflows; CodeQL covers semantic
  taint flows + Actions workflow analysis, Semgrep covers pattern-based
  SAST (OSS rule packs), gitleaks covers secret scanning. The repo's
  defence-in-depth security stack is markedly stronger than the
  pre-public baseline.
- **Public secret transition monitoring** (updated 2026-05-31): GitHub-native
  public-repository secret scanning and push protection are expected live
  settings and are checked from the private root control plane when an owner
  token is available. The adapter keeps workflow-layer coverage through
  gitleaks weekly/on-push/on-PR full-history scans, Semgrep `p/secrets`, and
  the local pre-push guard (`plugins/rldyour-flow/scripts/local_git_ai_guard.sh`).
  The 90-day post-private monitoring window is a local conservative transition
  control, not a GitHub platform limitation.
- **fullrepo `--force-with-lease`**: intentional per ADR-0001. Cannot
  share `main`'s no-force-push rule.

## Update policy

- Add a new row to "Executable surfaces" when a new plugin owns hooks /
  MCP / scripts.
- Add a new OWASP 2025 mapping entry when a new mitigation lands.
- Cite ADR IDs for irreversible decisions, validator script paths for
  enforcement points, and CHANGELOG D-numbers for closed audit findings.
