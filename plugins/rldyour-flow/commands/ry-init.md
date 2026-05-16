---
description: "Запустить scoped read-only инициализацию проекта через ry-init: Serena-first discovery + fullrepo bootstrap + verified context pack. Run scoped read-only project init."
argument-hint: <scope>
---

Scoped read-only инициализация проекта для: **$ARGUMENTS**

Use the `ry-init` skill to build a verified mental model of the requested scope. The skill enforces:

1. `bash ${CLAUDE_PLUGIN_ROOT}/scripts/git_sync_audit.sh` - git/branch/worktree state.
2. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fullrepo_sync.py --bootstrap-init` - restore agent-only context (AGENTS.md, .claude/CLAUDE.md, .serena/* etc.) from `fullrepo` before treating them as missing.
3. Read `${CLAUDE_PLUGIN_ROOT}/references/init-context-pack.md` as the contract for the context-pack output.
4. Serena-first inspection: `check_onboarding_performed` → `list_memories` → `read_memory` (relevant) → `get_symbols_overview` → targeted `find_symbol` → `find_referencing_symbols` → `search_for_pattern` (only for broad sweeps).
5. Map architecture, data models, integration points, tests, quality gates.
6. Russian report with `Memory candidates (not written)` section when durable facts are found.

`ry-init` is **read-only** for `.serena/memories` by default - does not write memories unless the user explicitly asked or a stale-memory hook requires it.

If `$ARGUMENTS` is empty - initialize the whole project. If `$ARGUMENTS` is a sphere (backend/frontend/mobile/etc.) - initialize the whole sphere plus integration points. If ambiguous - ask the user with 2-3 concrete options.

Reply in Russian.
