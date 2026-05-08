---
name: architecture-boundaries
description: "Архитектурные границы: FSD/VSA/Hexagonal, modules, public APIs, imports. Используй для: архитектура, слои, FSD, VSA, hexagonal, frontend, backend, размещение кода, границы модуля, публичный API. EN triggers: architecture boundaries, module layers, public API design, import discipline, where to place code, ADR worthy, layer policy."
---

# Architecture Boundaries

## Purpose

Keep systems easy to understand, change, and scale by using stable architecture boundaries and project-consistent placement.

## Default Architecture (May 2026)

- Existing project architecture is the source of truth. Do not rewrite architecture just to satisfy a generic rule.
- New frontend, web UI, mobile UI, and desktop UI areas default to **Feature-Sliced Design** when the stack allows it.
- New backend areas default to **Vertical Slice Architecture** when the application is use-case, command, query, route, or handler oriented. Combine with **Hexagonal (Ports & Adapters)** for framework-agnostic durability and **Modular Monolith** as the organizational container for medium-scale systems.
- Important architecture or technology decisions require an ADR (MADR 4.0.0 format) or equivalent decision record.

## Frontend And Client UI (FSD)

- Prefer FSD layers: `app`, `pages`, `widgets`, `features`, `entities`, `shared`.
- Treat the deprecated `processes` layer as forbidden by default; route its responsibilities into `app`/`pages`/`widgets` depending on scope.
- Imports should point only to lower layers, except `app` and `shared` rules and explicit project exceptions.
- Use public APIs for slices. Avoid deep imports into slice internals.
- Keep `shared` business-agnostic. Business concepts belong in `entities`, `features`, `widgets`, or `pages`.

## Backend (VSA + Hexagonal + Modular Monolith)

- **VSA**: organize around use cases, commands, queries, routes, or handlers. Validation, handler logic, domain orchestration, persistence interaction, and response mapping must be easy to trace for one use case.
- **Hexagonal (Ports & Adapters)**: isolate domain core from infrastructure (DB, HTTP, queues). Ports define contracts, adapters implement them. Survives framework churn.
- **Modular Monolith**: module boundaries form the outer container; vertical slices organize features within; ports/adapters protect the core.
- Minimize cross-slice coupling. Shared backend code must be stable, genuinely reusable, and not a dumping ground.
- Avoid generic service/repository layers when they only pass data through and add no useful abstraction.
- Cross-cutting concerns such as auth, logging, observability, transactions, and error mapping must be explicit and consistently placed.
- Pure layered architecture is acceptable only for MVPs or small projects where speed matters more than sustainability.

## ADR Triggers

Create an ADR for:

- New architecture style or major boundary change.
- New framework, database, message broker, auth strategy, deployment model, or critical dependency.
- Intentional deviation from FSD/VSA defaults.
- Breaking public API or contract change.
- Long-lived tradeoff that future Claude Code sessions must understand.

Read `${CLAUDE_PLUGIN_ROOT}/references/architecture-policy.md` when deciding placement or documenting an ADR.

## Anti-patterns

- Forced FSD/VSA rewrite of coherent existing architecture.
- Pure Layered architecture для new backends в 2026 (use VSA+Hexagonal+Modular).
- Use deprecated FSD `processes` layer.
- Cross-slice internals imports вместо public APIs.
- Generic pass-through service/repository layers без abstraction value.
- Skip ADR для architecture decisions с long-term consequences.
