# Project Instructions And ADRs

## AGENTS.md

`AGENTS.md` is the cross-tool standard root project-instruction file (see https://agents.md/). Create or update it when durable root-level project facts change:

- Setup commands.
- Quality gates.
- Architecture constraints.
- Project-specific coding rules.
- Deploy contracts.
- Review rules.
- Tooling and generated artifact rules.

Keep it concise. It is loaded as a high-signal entry point at session start, so it should contain high-signal project rules only.

For default rldyour-managed product repositories, project-root `AGENTS.md` is agent-only context. Keep it local and in the `tracked context` branch, and add it to `.git/info/exclude` through the rldyour tracked context workflow instead of tracking it in normal branches. Project policy may explicitly set `normal_branch_policy.agent_files=allowed` or `instruction_docs.mode=tracked-normal-branch`; then `AGENTS.md` is a normal tracked project file.

## .claude/CLAUDE.md

Create or update `.claude/CLAUDE.md` in every tracked context-managed project. This file is Claude Code project memory and must be optimized for Claude Code, not treated as a thin wrapper around `AGENTS.md`.

Include:

- Project commands and checks Claude Code should know every session.
- Project architecture, source-of-truth paths, naming conventions, and common workflows.
- Claude-specific diagnostics and controls when relevant: `/memory`, `/context`, `/hooks`, `/mcp`, `/permissions`, `/doctor`, `/status`.
- Claude-specific file locations when relevant: `.claude/settings.json`, `.claude/skills/`, `.claude/hooks/`, `.claude/agents/`, `.claude-plugin/`.

Keep it concise and first-class. Do not make the file only `@AGENTS.md`. Do not create root `CLAUDE.md` by default; it is a legacy location in the rldyour workflow.

For default rldyour-managed product repositories, `.claude/CLAUDE.md` is agent-only context and follows the same `tracked context` branch policy as project-root `AGENTS.md`. In tracked-normal-branch projects, it may be committed as a first-class project instruction file.

## REVIEW.md

Create or update `REVIEW.md` when review-specific rules are durable:

- Always-check areas.
- Architecture boundaries.
- Security-sensitive paths.
- Test expectations.
- Known generated files to ignore.
- Project-specific false positives.

## ADRs (MADR 4.0.0 - May 2026 canonical)

Use the **MADR 4.0.0** template from [adr.github.io/madr](https://adr.github.io/madr/). Released September 2024, stable in 2026.

Store ADRs in the project-standard location when one exists. Otherwise prefer `docs/adr/`.

### MADR 4.0.0 fields

- **Title** (`# <ADR number>: <short noun phrase>`).
- **Status**: proposed / rejected / accepted / deprecated / superseded by [...].
- **Date**: when the decision was last updated.
- **Decision-Makers**: list of people involved.
- **Consulted**: list of people whose opinions were sought.
- **Informed**: list of people kept up to date.
- **Context and Problem Statement**: describe the problem and constraints.
- **Decision Drivers**: list of forces / requirements / quality attributes.
- **Considered Options**: list of options.
- **Decision Outcome**: chosen option and justification.
- **Consequences**: positive and negative consequences in one combined section (changed in MADR 3.0.0).
- **Confirmation**: how the decision is confirmed (tests, monitoring, review).
- **Pros and Cons of the Options** (optional).
- **More Information** (optional, links).

Use the **bare** template variant for minimal overhead, **full** variant for important decisions.

### When to write an ADR

- New architecture style or major boundary change.
- New framework, database, message broker, auth strategy, deployment model.
- Critical dependency choice or version pin.
- Intentional deviation from project defaults (FSD/VSA/Hexagonal).
- Breaking public API or contract change.
- Long-lived tradeoff that future agents must preserve.

## Agent-Only Files And Tracked context

Default rldyour-managed policy keeps agent-only files that reveal or preserve AI workflow state out of normal project branches. Store them locally, ignore them through `.git/info/exclude`, and publish them to the `tracked context` branch through `rldyour-flow` (`python3 ${CLAUDE_PLUGIN_ROOT}/../rldyour-flow/scripts/tracked context_sync.py`). Foreign or colleague-owned repositories may opt into tracked AI instruction files through `.rldyour/project-policy.json`.

Default agent-only paths include:

- `AGENTS.md`, `.claude/CLAUDE.md`, root `CLAUDE.md` when migrating legacy projects, `REVIEW.md`, `GEMINI.md`, and `QWEN.md`.
- `.serena/project.yml`, `.serena/memories/`, `.serena/plans/`, `.serena/research/`, `.serena/newproj/`, and `.serena/deploy/`.
- `.claude/`, `.cursor/rules/`, `.agents/skills/`, `.agents/commands/`, `.agents/hooks/`, `.github/instructions/`, and `.github/prompts/`.

Never publish runtime markers, caches, local env files, browser evidence, secrets, tokens, cookies, or credentials to `main` or `tracked context`.
