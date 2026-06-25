# rldyour Rules Policy

This reference is the source of truth for the user's general engineering rules.

## Priority Order

1. Safety and repository integrity.
2. Correctness and verified behavior.
3. Clean architecture and long-term scalability.
4. Project consistency and low semantic entropy.
5. Delivery speed.

## Advisory-First Behavior

Rules guide the agent and should be applied automatically inside the current scope. They should not block normal progress through hooks by default.

Hard bans are non-negotiable inside the touched scope:

- No hacks.
- No temporary workarounds.
- No fake implementations.
- No swallowed errors.
- No secrets in code, docs, logs, prompts, screenshots, memories, or commits.
- No fake green checks.

## Technical Debt Outside Scope

When serious technical debt is found outside the task scope:

1. Explain the issue in Russian.
2. Give 2-3 concrete options.
3. Do not expand scope until the user chooses.

## Sequential Thinking

Use Sequential Thinking MCP (`mcp__sequential-thinking__*`) for non-trivial decisions when available. Minimum 3 thoughts:

1. Understand the task and constraints.
2. Evaluate options and risks.
3. Decide and define verification.

Use more thoughts for architecture, migrations, security, deployment, and high-risk refactors.

## Semantic Entropy

Low semantic entropy means:

- One concept has one clear location.
- Similar behavior uses similar patterns.
- Names match domain language.
- Public contracts are explicit.
- Integration paths are synchronized.
- Generated artifacts, tests, docs, and memories match code.

## Source-Backed Decisions

Use current official docs and source-backed research for:

- New technologies and dependencies.
- Migrations and major upgrades.
- Framework behavior and compatibility.
- Security-sensitive implementation.
- Architecture decisions with long-term consequences.

## Conventional Commits

Use [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/). Eleven canonical types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

Subject ≤72 chars. Optional scope in parentheses (`feat(auth): ...`). Use `!` after type/scope or `BREAKING CHANGE:` footer for breaking changes.

Atomic commits per logical change. Split unrelated implementation, tests,
validators, docs/instructions, license/metadata, generated artifacts, and
Serena/tracked context sync when they are independently reviewable. Never amend after
pre-commit hook failure (commit did not happen, so amending modifies the
previous commit). Do not rewrite already-pushed history without explicit owner
approval; use a follow-up commit for published branches.

## Russian / English Discipline

- User-facing conversation: Russian by default.
- Repository artifacts (code, comments, commits, docs, ADRs, memories): English.
- Identifiers: ASCII kebab-case for plugin/skill names; project-native conventions otherwise.

## Implementation Discipline Checklist

- Understand existing implementation before editing (Serena-first).
- Trace integration points before finalizing.
- Preserve public contracts unless task requires breaking change.
- Atomic, readable commits. Separate refactors from behavior changes.
- Clean inspectable history. Separate unrelated concerns instead of dumping a
  whole task into one commit.
- Clear names > comments. Comments only for WHY, not WHAT.
- Remove obsolete code, stale flags, outdated tests in scope.
- Generated files synchronized or explicitly skipped.
- Reuse stable utilities; extract only on real repeated need.
- No premature abstractions for single hypothetical future case.
