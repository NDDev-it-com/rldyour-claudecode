# Context Sufficiency Gate

`ry-start` must pass this gate before writing or editing code. The gate is informational and self-correcting: if evidence is missing, collect more context or ask the user. It should not create fake blockers, but it must prevent blind implementation.

## Gate Questions

Before planning, answer these questions from verified code, memories, research, or explicit user input:

- What exact behavior or bug is being implemented or fixed?
- Which modules, layers, files, and symbols are in scope?
- Which data models, DB fields, schemas, API payloads, generated types, or config keys are touched?
- Which entry points call into this behavior and which downstream systems are affected?
- Which existing patterns must be followed for naming, errors, validation, state, UI placement, tests, and logging?
- Which tests, linters, type checks, LSP diagnostics, browser checks, or security checks prove correctness?
- Which current docs, framework/library APIs, migration notes, or production usage patterns are relevant?
- What unknowns remain, and are they safe to resolve by investigation or do they require user input?

## Minimum Context Pack

For every non-trivial implementation, capture this in the plan before editing:

| Area | Required evidence |
| --- | --- |
| Scope | Task summary, affected layers, files, symbols, and integration path |
| Code | Serena memories, symbol overview, targeted bodies, references/callers |
| Data | DB fields, schemas, API shapes, config/env keys, generated artifacts |
| Patterns | Similar implementations, conventions, error handling, validation style |
| Research | Official docs through Context7, repo architecture through DeepWiki, GitHub patterns through Grep by Vercel when technical uncertainty exists |
| Quality | Detected checks, tests to add/update, LSP diagnostics, manual/browser/security evidence |
| Risks | Edge cases, compatibility risks, migration risks, security-sensitive paths, unresolved gaps |

## Decision Rules

- If the implementation depends on external API/framework behavior, run technical research before planning.
- If the task changes security-sensitive behavior, include OWASP guidance and schedule security review.
- If UI/browser-visible behavior changes, schedule browser validation and screenshot evidence under `browser/`.
- If a plan item cannot be tied to a real file, symbol, contract, or documented decision, verify it before editing.
- If an unknown can cause wrong architecture, data loss, auth bypass, broken deployment, or incompatible dependency choice, ask the user with options.

## Progress Checkpoints

During implementation, provide concise Russian progress updates after meaningful milestones:

- What changed.
- What evidence was used.
- What remains.
- Whether the plan still matches the code.
- Any new risk or scope expansion.

For long tasks, checkpoint after every 2-3 completed plan groups or whenever a verified fact contradicts the plan.

## Final Evidence

Before final delivery, the model must be able to state:

- Context gathered.
- Research used.
- Files and symbols changed.
- Quality gates run or blocked.
- Reviewer/browser/security evidence when relevant.
- Serena memories/docs/git synchronization status.
