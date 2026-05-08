# rldyour-claude

`rldyour-claude` is a personal Claude Code plugin marketplace. It is not a generic preset, not an automatic configuration takeover, and not a bundle of unrelated third-party opinions. It is a controlled catalog for the owner's own plugins, MCP servers, skills, subagents, slash commands, hooks, rules, and workflows.

Main principle: nothing is treated as enabled or correct unless the owner explicitly decides it.

## Control Model

- The active marketplace contains only plugins that are actually created and ready to install.
- Each plugin must have a clear responsibility boundary (one domain per plugin; no catch-all plugins).
- Each tool or workflow must describe its purpose, access model, risks, and usage rules.
- Repository documentation is written in English. User-facing communication with the owner is Russian unless explicitly requested otherwise.
- Technical identifiers stay stable, ASCII, and kebab-case where applicable.
- Every callable rldyour skill includes compact Russian and English trigger phrases in the `SKILL.md` frontmatter `description`. Claude Code uses descriptions as the primary routing surface; details belong in the skill body or references.
- Secrets, tokens, cookies, and private keys are never stored in this repository.

## Active Catalog

The active marketplace currently contains nine first-party plugins, all at `version: 0.1.0`:

- **`rldyour-mcps`** — single-owner MCP transport (13 pinned servers: Serena, Sequential Thinking, Playwright, Chrome DevTools, Context7, DeepWiki, Grep, Semgrep, shadcn, Dart/Flutter, Figma, OpenAI Docs, GitHub).
- **`rldyour-serena-mcp`** — Serena-first semantic code workflow, fact-only `.serena` memory sync via `flow-memory-sync` subagent, lifecycle hooks (UserPromptSubmit, PreToolUse:Bash, PostToolUse:Bash, Stop).
- **`rldyour-flow`** — autonomous SDLC orchestration with five slash commands (`ry-init`, `ry-start`, `ry-newp`, `ry-review`, `ry-deploy`), six reviewer subagents (architecture/quality/consistency/integration/verification/security tracks), advisory SessionStart and Stop hooks, scoped context packs, instruction docs sync, and post-task synchronization.
- **`rldyour-explore`** — deep multi-source research via `ry-explore` subagent (`model: opus[1m]`, `effort: max`) and tech/web research skills routing through Context7, DeepWiki, Grep, and authoritative web sources.
- **`rldyour-security`** — non-blocking OWASP Top 10 2026 secure-implementation guidance plus the `ry-sec-review` defensive review skill.
- **`rldyour-browser`** — browser validation, debugging, and tool-routing workflows for Playwright MCP and Chrome DevTools MCP.
- **`rldyour-design`** — Figma → code, centralized token-based design system, strict Feature-Sliced Design frontend architecture, shadcn/ui, ReactBits, and browser-validation workflows.
- **`rldyour-lsps`** — language-server routing, health checks, brew-first setup profiles, and Serena LSP integration guidance.
- **`rldyour-rules`** — quality-first engineering rules, architecture boundaries, implementation discipline, dependency compatibility (SLSA Level 2, SBOM, lockfile discipline), verification gates, project-instruction policy, MADR 4.0.0 ADR policy, and `ry-rules-review`.

## What Claude Code Reads

Claude Code reads:

- `.claude-plugin/marketplace.json` — active installable plugin catalog (`pluginRoot: ./plugins`, source form `./plugins/<name>`).
- `plugins/<plugin>/.claude-plugin/plugin.json` — plugin manifest. Each manifest declares `dependencies` as an array; `rldyour-mcps` is the base layer with no dependencies, all other plugins depend on it (and `rldyour-flow` additionally depends on `rldyour-serena-mcp`).
- Manifest-linked files: `skills/<skill>/SKILL.md`, `agents/<agent>.md`, `commands/<name>.md`, `hooks/hooks.json`, `.mcp.json`, references, scripts.

This README is for owner review and repository orientation. It explains the control model and active plugin catalog but does not enable tools by itself.

## Adding A Plugin

Before creating a new plugin, define:

- exact plugin name (kebab-case, namespaced under `rldyour-`);
- purpose and boundary (single domain, no catch-all);
- files it will contain;
- whether it provides MCP servers, skills, hooks, subagents, slash commands, or documentation only;
- what Claude Code can do through it;
- what actions require confirmation;
- what data must never be sent outside the machine or repository.

Only then create `plugins/<name>/` with the canonical layout (`.claude-plugin/plugin.json`, `skills/`, `agents/`, `commands/`, `hooks/`, `references/`, `scripts/` as needed) and add it to `.claude-plugin/marketplace.json`.

## Local Installation

```bash
claude plugin marketplace add /path/to/rldyour-claudecode
claude plugin install rldyour-mcps@rldyour-claude
claude plugin install rldyour-serena-mcp@rldyour-claude
claude plugin install rldyour-flow@rldyour-claude
# ...etc for each enabled plugin
```

After changing `marketplace.json`, a plugin manifest, hooks, skills, agents, or `.mcp.json`, restart Claude Code so the runtime reloads plugin definitions:

```bash
claude plugin validate .                     # validate marketplace
for p in plugins/*/; do
  claude plugin validate "$p"                # validate each plugin
done
scripts/validate_marketplace.sh              # full marketplace harness
```

`plugins/rldyour-mcps/.mcp.json` is the portable source of truth for MCP server definitions. Local MCP launcher packages are pinned in `.mcp.json` and additionally documented in `config/mcp-runtime-versions.env`. Do not use `@latest` or unpinned `uvx --from` package specs for local MCP runtime definitions; update versions intentionally and rerun capability smoke tests.

## Smoke Tests

The marketplace ships with smoke coverage for hooks, MCP runtime, fullrepo workflow, branch cleanup, bootstrap, and local git guard:

```bash
scripts/smoke_mcp_runtime.sh
scripts/smoke_mcp_capabilities.sh
scripts/smoke_hooks.sh
scripts/smoke_local_git_guard.sh
scripts/smoke_flow_branch_cleanup.sh
scripts/smoke_clean_bootstrap.sh
scripts/smoke_fullrepo_sync.sh
scripts/smoke_fullrepo_bootstrap_init.sh
```

Targeted state checks:

```bash
plugins/rldyour-flow/scripts/flow_post_task_state.py | python3 -m json.tool
plugins/rldyour-serena-mcp/scripts/serena_memory_state.py | python3 -m json.tool
plugins/rldyour-flow/scripts/instruction_docs_state.py --json | python3 -m json.tool
python3 scripts/validate_instruction_docs.py --require-agent-docs
python3 scripts/validate_plugin_versions.py
python3 scripts/validate_skill_routing.py
python3 scripts/check_mcp_runtime_versions.py
python3 scripts/release_manifest.py
```

GitHub Actions runs `claude plugin validate`, JSON/Python/shell syntax checks, and frontmatter verification on every push and pull request via `.github/workflows/validate.yml`. The scheduled `dependency-check.yml` workflow monitors pinned MCP runtime versions for upstream drift.

## Fullrepo Branch

`fullrepo` is the portable complete-state branch for agent-only files (e.g. `AGENTS.md`, `.claude/CLAUDE.md`, `.serena/project.yml`, `.serena/memories/**`). Normal project branches keep product history clean and exclude these files through `.git/info/exclude`.

```bash
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --bootstrap-init   # first-time setup on a fresh checkout
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json      # machine-readable sync state
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --restore          # restore agent-only files from origin/fullrepo
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --migrate-main     # git rm --cached agent-only files left in the index
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --publish          # refresh fullrepo with safe --force-with-lease
```

Customer-facing branch is `main`; the team works against `fullrepo`.

Local product repositories that consume this marketplace can install the rldyour Git pre-push guard:

```bash
scripts/install_local_git_hooks.sh --dry-run
scripts/install_local_git_hooks.sh --apply
```

The guard is branch-aware. Product branches keep strict protection against agent-only paths and AI-marker additions. The configured fullrepo branch (`fullrepo` by default, or `RLDYOUR_FULLREPO_BRANCH`) allows durable AI context while still blocking definite secrets, runtime markers, browser artifacts, and local env files.

## Release, Rollback, And Observability

Marketplace release version lives in `VERSION`. Per-plugin behavior versions stay in `plugins/<plugin>/.claude-plugin/plugin.json`. Release notes live in `CHANGELOG.md` (Keep-a-Changelog format).

```bash
python3 scripts/release_manifest.py            # build release metadata bundle
python3 scripts/check_mcp_runtime_versions.py  # detect drift against config/mcp-runtime-versions.env
scripts/collect_diagnostics.sh                 # local ignored diagnostics bundle for failure triage
```

Reference documents:

- `docs/release-process.md` — versioning, CHANGELOG, release evidence, `claude plugin tag --push` flow.
- `docs/rollback-restore.md` — safe restore from previous tags or fullrepo snapshots.
- `docs/dependency-updates.md` — pinned MCP runtime update policy.
- `docs/observability.md` — diagnostics, CI artifacts, hook lifecycle debugging, failure triage.

## Minimum Claude Code Version

**v2.1.111+** for `model: opus[1m]` bracketed extended-context syntax used by `ry-explore`. Earlier versions silently ignore the bracket suffix.
