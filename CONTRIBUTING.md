# Contributing

Thanks for your interest in `rldyour-claudecode`. This is the rldyour AI CLI configuration for Claude Code: plugin marketplace, MCP/LSP, Serena memory, security review, browser/design workflows, and reviewer agents. It is maintained by Danil Silantyev
(github:rldyourmnd), CEO NDDev; PRs and Issues are welcome, but the bar is
"consistency with the existing architecture and quality-first invariants" -
drive-by patches that don't fit the philosophy will be redirected or closed.

If you want a workflow without these constraints, **fork and tailor**.
That's the canonical way to extend this marketplace.

## Quick start

```bash
# Required env (boostrap_check.sh enforces both before any MCP starts):
export CONTEXT7_API_KEY=<your-context7-key>
export GITHUB_PERSONAL_ACCESS_TOKEN=<your-github-pat-repo+read:org>

# Local install:
git clone https://github.com/NDDev-it-com/rldyour-claudecode.git
cd rldyour-claudecode
bash scripts/install-rldyour-marketplace.sh

# Required pre-flight check for env vars (bootstrap_check.sh, not boostrap):
bash scripts/bootstrap_check.sh

# Run the full validation harness before submitting any change:
bash scripts/validate_marketplace.sh

# Run the unit test suite:
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/ -m "not integration"
```

## What contributions fit

- **Bug fixes** with clear repro + regression test.
- **Hook hardening** (defensive resolver patterns, injection-marker
  coverage, exit semantics).
- **Validator improvements** (new invariant checks in `scripts/validate_*`
  with unit tests in `tests/test_validate_*`).
- **Smoke test coverage** for edge cases or new platforms.
- **Documentation clarifications** in `README.md`, `docs/adr/`,
  `docs/runtime-env.md`, ADR additions or corrections.
- **Reviewer agent improvements** (`plugins/rldyour-flow/agents/`)
  aligned with the canonical Anthropic `pr-review-toolkit` pattern.

## What does NOT fit

- **Third-party plugins** outside the `rldyour-*` namespace. This is a
  personal marketplace by design. Catalog additions: open an Issue
  describing the use case first.
- **Architecture rewrites** without an ADR. The plugin boundaries
  (`config/marketplace-policy.json`) are intentionally narrow.
- **Catch-all helpers** that violate single-domain-per-plugin invariant.
- **`disallowedTools` denylists** on read-only agents (the canonical
  pattern is explicit `tools:` allowlist - see
  `scripts/validate_agent_tools.py`).
- **Memory edits outside `flow-memory-sync` subagent**. Memories live
  on the `fullrepo` branch and follow the `AREA-NN-SLUG.md` taxonomy.

## Engineering invariants

### Code style

- See `.claude/CLAUDE.md` for project-local Claude Code style and
  invariants (deep memory, hook canon, subagent matrix).
- Russian for user-facing prose, English for code/docs/commits/comments.
- No `latest` pins; every dependency has an explicit version (npm @ tag,
  uvx `--from package==version`, container digest).

### Commits

- **Conventional Commits v1.0.0**: `type(scope): subject` (lowercase,
  imperative, ≤72 chars). Types: `feat`, `fix`, `docs`, `refactor`,
  `perf`, `test`, `build`, `ci`, `chore`, `style`, `revert`.
- **Atomic commits**: one logical change per commit. Separate mechanical
  refactors from behavior changes. Separate source / docs / Serena
  knowledge. Split license/metadata, validators/tests, generated artifacts,
  and fullrepo/Serena sync when they are independently reviewable.
- **Published history**: do not rewrite already-pushed history without explicit
  maintainer approval; use a follow-up commit instead.
- **No** `--no-verify` unless explicitly requested by the maintainer.

### Quality gates

Before opening a PR, run:

```bash
bash scripts/validate_marketplace.sh
```

This runs the full harness (~10 sub-validators + smoke tests + 14+
unit-test files). It must pass on `ubuntu-latest`. CI re-runs the same
gates on every PR.

For matrix-relevant changes (shell scripts, sed/find/awk patterns,
hook scripts):

```bash
# Trigger cross-platform.yml manually:
gh workflow run cross-platform.yml --ref <branch>
```

### Branch policy

- `main`: product code + docs + tests. No agent-only files. Protected.
- `fullrepo`: `main` + agent-only files (AGENTS.md, .claude/, .serena/,
  IDE configs). Force-push allowed only via `fullrepo_sync.py --publish`
  (`--force-with-lease`).
- `feat/*`, `fix/*`, `chore/*`: feature branches. Open a PR to `main`.

### Versions

- Marketplace `VERSION` and all 9 plugins bump together on every wave
  that touches plugin/marketplace files (owner-set rule, 2026-05-17).
- Tags: `marketplace--v<X.Y.Z>` plus 9 `<plugin>--v<X.Y.Z>` per release.
- See ADR-0009 and `docs/release-process.md`.

## Issue templates

- **Bug report**: concrete repro + expected vs actual + environment.
- **Feature request**: use case + alternatives considered + acceptance
  criteria. Often "no, this would violate boundary X" is the answer;
  please don't take it personally.
- **Security**: do NOT use the public Issue template. Open a private
  Security Advisory instead (see `SECURITY.md`).

## Reviewing

When a PR lands:

1. The CI matrix (`validate.yml`, `pytest.yml`, `cross-platform.yml`,
   `gitleaks.yml`, `semgrep.yml`, `codeql.yml`) gates merge.
2. The maintainer applies the `ry-review` reviewer track (6 parallel
   subagents covering architecture / quality / consistency / integration
   / verification / security). Findings get triaged: must-fix / should-fix
   / defer / accept.
3. Memory and instruction-doc impact assessment via `flow-memory-sync`
   subagent on the `fullrepo` branch (does NOT touch `main`).

## License

By contributing, you agree your contributions are licensed under the
[GNU Affero General Public License v3.0 or later](./LICENSE).

## Code of Conduct

This project follows the [Contributor Covenant 2.1](./CODE_OF_CONDUCT.md).
Be kind, be specific, criticize the code not the person.
