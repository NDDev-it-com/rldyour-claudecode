---
description: "Спроектировать новый проект через ry-newp: скептические вопросы → research → архитектура docs → optional scaffold."
argument-hint: <project-idea>
---

Дизайн нового проекта: **$ARGUMENTS**

Use the `ry-newp` skill to design a new project with enough rigor that implementation can start with clear architecture, technology choices, business logic, quality gates, and delivery plan.

The skill enforces:

1. Gather all context: prompt, requirements, screenshots, business constraints.
2. Skeptical Russian questions with options — product scope, users, business logic, data, integrations, security, deployment, observability, tests, constraints.
3. Research current best technologies and patterns via `rldyour-explore`.
4. Write planning docs under `.serena/newproj/<project>/`. Default 13 docs: HLO, REQUIREMENTS, ARCHITECTURE, ADRS, TECH_STACK, API, DATA, INFRA, SECURITY, TESTING, PROJECT_STRUCTURE, CONVENTIONS, DELIVERY_PLAN.
5. **Approval gate** before any scaffold code.
6. If approved — minimal useful scaffold + atomic commit + Serena memory init.

English project documents, Russian user-facing summaries.

Reply in Russian.
