---
description: "Задеплоить через ry-deploy: local↔GitHub↔server sync + проверки логов + fix-forward + docs/git финализация. Run the full deployment lifecycle with log verification and fix-forward."
argument-hint: <server>
---

Deploy на: **$ARGUMENTS**

Use the `ry-deploy` skill to synchronize local repository, GitHub, and server, then deploy safely with evidence.

The skill enforces:

1. Read deploy contract from `AGENTS.md` → `.claude/CLAUDE.md` → `.serena/deploy/*.md`. Required fields per `${CLAUDE_PLUGIN_ROOT}/references/deploy-contract.md`: Server, SSH, Path, Manager, Logs, Health, Tests, Rollback, Backup.
2. `bash ${CLAUDE_PLUGIN_ROOT}/scripts/deploy_readiness.sh <server>` for baseline state.
3. Verify local git, open PR, checks, Serena memories, docs, GitHub sync.
4. Inspect server baseline: git status, current commit, disk, logs **before restart**, process manager.
5. Sync code, migrations only after readiness is clear, restart/build services.
6. Verify logs, tests, health, business-critical flows.
7. **On failure**: RCA via logs + code + internet research → fix-forward → redeploy. Ask the user with options for risky/ambiguous decisions.
8. **DB rollback** only when explicit rollback command + verified backup/restore point.
9. Final: `flow-post-task-sync`.

**No fake success**: if auth/credentials/access/health-check unavailable, state the limitation and what evidence was still collected.

Reply in Russian.
