---
name: implementation-discipline
description: "Дисциплинированная реализация: код, API, schemas, configs, tests, naming, errors, reuse, sync. Используй для: реализация, доработка, рефакторинг, нейминг, реюз, контракты, integration sync."
---

# Implementation Discipline

## Purpose

Make every change precise, synchronized, maintainable, and consistent with the system around it.

## Workflow

- Understand the current implementation before editing. Use Serena semantic tools first when available (`get_symbols_overview` → `find_symbol(body=false)` → `find_symbol(body=true)` → `find_referencing_symbols`).
- Trace all affected integration points before finalizing: routes, clients, schemas, DTOs, migrations, generated types, config, docs, and tests.
- Preserve existing public contracts unless the task explicitly requires a breaking change.
- Keep changes atomic and readable. Separate mechanical refactors from behavior changes.
- Prefer clear names over comments. Use comments only for why, constraints, non-obvious algorithms, or external contract reasons.
- Remove obsolete code, stale branches, stale docs, dead feature flags, and outdated tests when they are in scope.
- Keep generated files synchronized with their source commands or state why generation is unavailable.

## Reuse And Abstraction

- Reuse existing stable utilities, primitives, domain types, and patterns.
- Extract common code when there is real duplication or a stable concept, not just because two lines look similar.
- Do not introduce a broad abstraction for a single speculative future case.
- If two areas solve the same problem differently, choose the project-consistent pattern or ask before normalizing wider scope.

Read `${CLAUDE_PLUGIN_ROOT}/references/rules-policy.md` for the full implementation discipline checklist.

## Anti-patterns

- Edit без understanding existing implementation (use Serena first).
- Mix mechanical refactors с behavior changes в одном коммите.
- Premature abstraction для single speculative future case.
- Skip integration tracing — забыть про clients, schemas, generated types.
- Comments объясняющие WHAT (имена должны это делать), а не WHY.
- Leave dead code / stale flags / outdated tests в touched scope.
