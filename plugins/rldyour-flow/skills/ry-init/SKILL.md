---
name: ry-init
description: "Инициализация project scope с Serena-first discovery + fullrepo bootstrap, read-only по умолчанию. Используй для: /rldyour-flow:ry-init, инициализируй проект, изучи проект, контекст-пак, scope/sphere/module, разбери репозиторий. EN triggers: init project, scope discovery, project bootstrap, context pack, learn project, study repo, fullrepo init, onboard to repo."
---

# ry-init

## Purpose

Build a verified mental model of the requested project scope before implementation. If the scope is a sphere such as backend or mobile UI, inspect the entire sphere and all integration points needed to understand how it works end to end.

`ry-init` is read-only for project knowledge by default. It may restore or bootstrap agent-only context from `fullrepo`, but it must not create, edit, or delete Serena memories unless the user explicitly asks to update/synchronize memories or an active stale-memory hook requires synchronization.

## Workflow

1. Run `bash ${CLAUDE_PLUGIN_ROOT}/scripts/git_sync_audit.sh` when available.
2. Inspect dirty work, old branches, and worktrees. If code is correct and consistent, synchronize it into `main`, push, and remove merged branches/worktrees. If risky, explain the issue in Russian and ask the user with concrete options.
3. Resolve effective project policy with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/project_flow_policy.py --json` when available. Bootstrap project agent-only context only when `fullrepo.mode` allows it. `--bootstrap-init` restores existing fullrepo context; it must not create a missing fullrepo branch unless policy sets `create_if_missing=true` or the user explicitly asks in the current turn.
4. Read `${CLAUDE_PLUGIN_ROOT}/references/init-context-pack.md` and use it as the required context-pack contract.
5. Use `serena-code-workflow`: check onboarding, list memories, read relevant memories, and use Serena semantic tools before raw reads.
6. Map the requested scope deeply enough to understand modules, layers, symbols, DB fields, schemas, APIs, generated artifacts, configs, tests, and integration paths.
7. Use `lsp-routing` or `lsp-health-check` when language server support affects understanding.
8. Use `tech-research` or `web-research` only for unclear technology, architecture, or current best-practice questions.
9. Synthesize a Russian report with exact source-of-truth paths, current behavior, data/contracts, integration points, quality gates, risks, gaps, and what Claude Code can now safely change.
10. Do not run `serena-memory-sync` automatically. If initialization discovers useful durable facts that are missing from memories, report them under `Memory candidates (not written)` with exact source paths and ask before writing. Only run `serena-memory-sync` during `ry-init` when the user explicitly requested memory sync/update or a Stop/stale-memory hook requires it.

## Role Declaration (Orchestrator)

Session role is declarative, not auto-detected:

- If the user's init request explicitly declares this terminal the orchestrator
  (for example "я оркестратор", "this terminal is the orchestrator"), verify the
  preconditions: macOS, a cmux session (`CMUX_WORKSPACE_ID`/`CMUX_SURFACE_ID`
  present), and the `rldyour-orchestrator` plugin installed. When they hold,
  adopt the orchestrator duties from `rldyour-orchestrator:cmux-orchestrator`
  for the rest of the session: own user communication, task decomposition,
  delegation, final validation, and sync. When a precondition fails, say which
  one and continue in standard mode.
- Without that explicit declaration, always run in standard mode - never
  auto-activate orchestrator behavior from environment, policy, or guesswork.
- Worker terminals are not declared by the user: they are machine-identified by
  the launcher/layout environment (`RLDYOUR_AGENT_ROLE=worker`,
  `RLDYOUR_WORKER_ID`) and follow `rldyour-orchestrator:cmux-worker`.

## Scope Rules

- Empty scope means whole project.
- Sphere scope means the whole sphere plus integration points.
- Feature scope means trace all layers touched by that feature.
- Ambiguous scope means ask the user with 2-3 options.
- Do not stop at file lists. The initialized context must explain how relevant code works end to end.
- For database-backed or API work, include fields, schemas, migrations, payloads, and caller/client paths.
- For UI/client work, include routes/screens/components, state, API calls, design-system constraints, browser-visible behavior, and tests.
- If agent-only files such as `AGENTS.md`, `CLAUDE.md`, `.serena/*`, `.claude/*`, `.cursor/rules/*`, or `.agents/skills/*` are needed for context, first read project policy. Restore `fullrepo` before treating them as missing only when policy allows restore; in tracked-normal-branch projects, treat them as normal source files.
- Runtime snapshots, server log summaries, health-check timestamps, current container status, and one-off audit observations are report material, not Serena memory material, unless they reveal a stable code/config contract.

## Output

Report in Russian:

- Scope initialized.
- Git/GitHub/worktree state.
- Architecture and data flow.
- Key files and symbols.
- Data models, DB fields, schemas, API contracts, config/env keys, and generated artifacts.
- Integration points.
- Tests, LSP/check commands, browser/security/design evidence when relevant.
- Known risks and gaps.
- Memory candidates (not written), only when useful durable facts were found and memory sync was not explicitly requested.
- Ready-for tasks.

## Anti-patterns

- Запускать `serena-memory-sync` автоматически без user request или stale-memory хука.
- Останавливаться на file listings без понимания end-to-end behavior.
- Do not run `--bootstrap-init` when project policy disables fullrepo. If `AGENTS.md`/`CLAUDE.md` are missing and policy allows fullrepo restore, restore before treating them as absent.
- Treat'ить runtime snapshots как memory material.
- Editing scope-detection ambiguous prompts без 2-3 concrete option questions.
