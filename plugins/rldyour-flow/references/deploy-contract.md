# Deploy Contract

`ry-deploy` reads deploy configuration from:

1. `AGENTS.md`
2. `.claude/CLAUDE.md`
3. `.serena/deploy/*.md`

Use the first complete contract found. If multiple contracts conflict, ask the user.

## Minimum Fields

| Field | Meaning |
| --- | --- |
| Server | Logical target name such as `production` or `staging` |
| SSH | SSH target such as `user@host` |
| Path | Project path on the server |
| Manager | Restart/build manager such as `docker compose`, `systemd`, `pm2`, or custom command |
| Logs | Log command |
| Health | Optional health command or URL |
| Tests | Optional server-side test command |
| Rollback | Optional rollback command |
| Backup | Optional backup/restore point command |

## Safety

- Never deploy without verifying git state and target server.
- Read logs before restart to establish baseline.
- Run migrations before restart only after backup/rollback readiness is known.
- Prefer fix-forward. DB rollback requires verified rollback and backup/restore point.
- If the server breaks, inspect logs, code, and current internet/docs before changing code.
