---
description: "Запустить scoped read-only инициализацию проекта через ry-init: Serena-first discovery + fullrepo bootstrap + verified context pack. Run scoped read-only project init."
argument-hint: <scope>
---

Scoped read-only инициализация проекта для: **$ARGUMENTS**

Use the `ry-init` skill for this request. The skill body owns the workflow (git audit, fullrepo bootstrap, Serena-first inspection, context-pack contract); `ry-init` is read-only for `.serena/memories` unless a stale-memory hook explicitly demands a sync pass.

Reply in Russian.
