---
name: ry-newp
description: "Дизайн нового проекта: скептические вопросы, research, архитектура docs, опциональный scaffold после approval. Используй для: /ry-newp, новый проект, новый стартап, ТЗ, проект с нуля, project from scratch."
disable-model-invocation: true
---

# ry-newp

## Purpose

Design a new project with enough rigor that implementation can start with clear architecture, technology choices, business logic, quality gates, and delivery plan.

## Workflow

1. Gather all provided context: prompt, docs, chats, requirements, screenshots, business constraints.
2. Ask skeptical Russian questions with options. Cover product scope, users, business logic, data, integrations, security, deployment, observability, tests, and constraints.
3. Research current best technologies and architecture patterns with `rldyour-explore` (`tech-research` + `web-research`).
4. Write planning docs under `.serena/newproj/<project>/` using `${CLAUDE_PLUGIN_ROOT}/references/flow-lifecycle.md` (the `## ry-newp` section lists default artifacts).
5. Ask for approval before creating any scaffold code.
6. If scaffold is approved, create the minimal useful project structure, commit atomically, and initialize Serena memories.

## Output

Produce English project documents and Russian user-facing summaries.

Default docs:

- `01_HLO.md` (high-level overview)
- `02_REQUIREMENTS.md`
- `03_ARCHITECTURE.md`
- `04_ADRS.md`
- `05_TECH_STACK.md`
- `06_API.md`
- `07_DATA.md`
- `08_INFRA.md`
- `09_SECURITY.md`
- `10_TESTING.md`
- `11_PROJECT_STRUCTURE.md`
- `12_CONVENTIONS.md`
- `13_DELIVERY_PLAN.md`

## Anti-patterns

- Scaffold без approval.
- Generic architecture без проверки project constraints.
- Skip skeptical questions — accept все assumptions of the prompt as-is.
- Plan без research current best practices через rldyour-explore.
- Initialize Serena memories до того как scaffold approved и commit'нулся.
