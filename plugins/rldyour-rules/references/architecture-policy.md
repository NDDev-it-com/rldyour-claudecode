# Architecture Policy

## Existing Projects

Existing project architecture is the source of truth. Apply these defaults to new areas and refactors, but do not force a rewrite when the project already has a coherent architecture.

## Frontend And Client UI Default: FSD

Use Feature-Sliced Design for new frontend, web UI, mobile UI, and desktop UI areas when practical.

Default layers:

- `app`: application setup, providers, routing, global styles.
- `pages`: route-level composition.
- `widgets`: large reusable UI blocks composed from features and entities.
- `features`: user actions and business interactions.
- `entities`: business entities and entity model/UI.
- `shared`: business-agnostic UI, lib, config, API clients, assets.

Rules:

- Treat the deprecated `processes` layer as forbidden by default. Although still present in some FSD docs, this project routes its responsibilities into `app`/`pages`/`widgets` depending on scope.
- Lower layers must not import higher layers.
- Slices should expose public APIs (usually `index.ts` barrel files).
- Avoid deep imports into slice internals.
- Keep `shared` free of business-specific concepts.
- Use separate public APIs for `shared/ui` and `shared/lib` components when a single barrel would harm tree-shaking or clarity.
- Use `@x` cross-imports only when an entity relationship needs it and the project accepts the pattern.

Alternative for medium-scale FE projects: **Modular Monolith + VSA** - module boundaries form the outer container, vertical slices organize features within. Documented in an ADR.

## Backend Default (May 2026): VSA + Hexagonal + Modular Monolith

The 2026 consensus combines three patterns for sustainable backends:

### Vertical Slice Architecture (VSA) - primary

Use VSA for backend features when practical:

- Organize around use cases, commands, queries, routes, or handlers.
- Keep validation, handler logic, domain orchestration, persistence interaction, and response mapping easy to trace for one use case.
- Pairs naturally with CQRS and the REPR pattern (Request-Endpoint-Response).
- Minimize coupling between slices.

### Hexagonal Architecture (Ports & Adapters) - for durability

Layer Hexagonal under VSA for framework-agnostic durability:

- Domain core defines ports (interfaces).
- Adapters implement ports for HTTP, DB, queues, external services.
- Domain core never depends on infrastructure. Survives framework churn.
- Apply when long-lived business logic justifies the ceremony.

### Modular Monolith - as the organizational container

For medium-scale systems, modules form the outer boundary; vertical slices organize features within; ports/adapters protect the core. Pragmatic default for teams migrating from monoliths.

### When to use what

- **Pure Layered**: only for MVPs or small projects where speed > sustainability.
- **Clean Architecture**: for large-scale, long-lived systems where ceremony is justified.
- **Onion Architecture**: similar to Hexagonal but stricter; choose Hexagonal as the modern equivalent.

## ADR Triggers

Create an ADR (MADR 4.0.0 format) for:

- New architecture style or major boundary change.
- New framework, database, message broker, auth strategy, deployment model, or critical dependency.
- Intentional deviation from FSD/VSA/Hexagonal/Modular-Monolith defaults.
- Breaking public API or contract change.
- Long-lived tradeoff that future Claude Code sessions must understand.

## Common Concerns

- **Cross-cutting concerns** (auth, logging, observability, transactions, error mapping) must be explicit and consistently placed.
- **Anti-Corruption Layer (ACL)** when integrating with external systems whose model differs from the domain.
- **Composition Root** centralizes wiring for adapters and dependencies.
- **Generic pass-through services and repositories** that add no abstraction value should be avoided.
