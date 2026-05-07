# Init Context Pack

`ry-init` must build a verified context pack for the requested scope. The goal is not to read every file. The goal is to make future implementation safe by mapping the code, data, contracts, and integration paths that matter for the scope.

## Scope Resolution

Classify the requested scope before investigation:

- Project: whole repository, monorepo, or unknown scope.
- Sphere: backend, frontend, mobile, desktop, infra, API, auth, data, design, or another project-specific area.
- Module: named package, app, service, feature slice, library, or bounded context.
- Feature: user-facing behavior, business flow, bug, migration, or cross-cutting concern.

If the scope is ambiguous, ask the user in Russian with 2-3 concrete options. If the scope is a sphere, inspect the whole sphere and the integration points that connect it to the rest of the system.

## Required Evidence

Use Serena first for supported code:

1. `check_onboarding_performed`.
2. `list_memories`.
3. `read_memory` for relevant memories.
4. `get_symbols_overview` for entry files and important modules before reading bodies.
5. `find_symbol` with body disabled to discover children and public surface.
6. `find_symbol` with body enabled only for implementation that must be understood.
7. `find_referencing_symbols` to trace callers, data flow, and impact.
8. `search_for_pattern` for cross-cutting names, routes, schemas, config keys, DB fields, migrations, generated artifacts, tests, and unsupported file types.

Use raw `rg` or direct reads only for manifests, Markdown, config files, shell scripts, generated metadata, unsupported language files, or broad text sweeps.

## Context Pack Sections

The final `ry-init` report must include these sections when relevant:

- Scope: exact scope, classification, and why it was chosen.
- Git and sync: branch, upstream, dirty files, ahead/behind, worktrees, open PRs if available.
- Architecture map: layers, modules, dependency direction, public interfaces, and boundaries.
- Entry points: commands, app roots, routes, handlers, screens, components, jobs, migrations, and deploy hooks.
- Key symbols: functions, classes, types, modules, services, repositories, state stores, and exported APIs.
- Data model: database tables, fields, migrations, schemas, ORM models, API payloads, generated types, and invariants.
- Integration graph: upstream callers, downstream dependencies, external services, queues, browser flows, CLI commands, and server contracts.
- Configuration: env variables, config files, feature flags, build/runtime settings, secrets policy, and deployment assumptions.
- Tests and quality gates: test files, coverage areas, detected commands, LSP diagnostics, linters, type checks, browser/security checks when relevant.
- Existing patterns: naming, error handling, logging, validation, API shape, state management, UI placement, dependency style, and commit/doc conventions.
- Risks and gaps: unknowns that must be resolved before implementation.
- Memory candidates (not written): durable facts missing from `.serena` that would help future sessions, only when memory sync was not explicitly requested.
- Ready-for: concrete tasks the model can now safely perform with this context.

## Deep Coverage Rules

- For database-backed work, trace every touched DB field from schema/migration/model to API/service/UI/test usage.
- For API work, trace request validation, authorization, handler, service/domain logic, persistence, response shape, client usage, and tests.
- For frontend or mobile UI work, trace routing, state, API calls, design tokens/components, browser-visible behavior, accessibility/responsive constraints, and tests.
- For auth, payments, admin, file upload, secrets, or external integrations, include security-sensitive paths and trigger security guidance.
- For migrations and dependency changes, include current version, compatibility constraints, release notes or official docs, and real usage patterns when needed.

## Output Discipline

Keep the report dense and useful. Prefer exact paths and symbol names over prose. Separate verified facts from inferences. Do not store secrets, raw credentials, cookies, private tokens, speculative notes, one-off log snapshots, current health statuses, or server audit timestamps in memories.
