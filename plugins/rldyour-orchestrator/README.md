# rldyour-orchestrator

macOS-only cmux orchestrator plugin: one user-facing orchestrator terminal
delegates scoped tasks to worker terminals inside a single cmux workspace.

## Skills

- `cmux-orchestrator` - orchestrator duties: policy read, task decomposition,
  delegation via `cmux send --surface` with per-task `RLDYOUR_TASK_ID` and
  `RLDYOUR_WORKER_ALLOWED_PATHS`, observation via `cmux read-screen`/`cmux events`,
  report collection, final validation and sync ownership.
- `cmux-worker` - worker role: scoped work only, JSON report plus the mandatory
  `cmux notify` exit-code completion signal, no push/fullrepo/system installs.

## Activation Model

The orchestrator role is declarative: the user states the role explicitly when
initializing the session (`/ry-init` with an orchestrator declaration). Without
that declaration, and on sessions without this plugin, everything runs in
standard mode - nothing breaks and no orchestrator behavior activates.

Worker terminals stay machine-identified through the launcher/layout
environment (`RLDYOUR_EXECUTION_MODE=orchestrator`, `RLDYOUR_AGENT_ROLE=worker`,
`RLDYOUR_WORKER_ID`) because worker restrictions are enforced by flow state
scripts, not by conversation context.

## Platform

cmux is a macOS application (`manaflow-ai/cmux`). This plugin is installed only
on macOS; Linux, WSL, and Windows installs skip it entirely.

## Dependencies

Depends on `rldyour-flow` for the Stop-lifecycle state machinery that enforces
worker scope and post-task synchronization.
