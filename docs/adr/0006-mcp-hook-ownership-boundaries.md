# ADR-0006: MCP and hook ownership boundaries

- **Status**: accepted
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd

## Context and Problem Statement

Claude Code plugins can each declare their own `.mcp.json` and
`hooks/hooks.json`. With 9 plugins in this marketplace, unrestricted
ownership would create:

- **MCP conflicts**: two plugins pinning incompatible Serena versions, or
  two plugins both registering the same MCP server with different flags.
- **Hook chaos**: stop-hook chains where the order is unpredictable; the
  Stop gate advisory pattern (exit 2 + loop-guard fingerprint) depends on
  exactly one Stop hook per layer running per cycle.
- **Cache key drift**: any plugin component change bumps its plugin
  version; if MCP transport lives in 5 plugins, every MCP pin bump
  invalidates 5 caches.

Evidence: AGENTS.md:38-43, README.md:33-41, `config/marketplace-policy.json`
mcp_owner + hook_owners fields.

## Decision Drivers

- One source of truth per transport / hook event chain.
- Cache invalidation locality.
- Predictable Stop-hook chain ordering.

## Considered Options

- A: Free-for-all. Any plugin can declare anything.
- B: All MCP + hooks in one mega-plugin. Defeats domain separation.
- C: Single MCP owner (`rldyour-mcps`); single hook owner per concern
  family (sync/memory vs SDLC orchestration). Other plugins consume via
  `dependencies`.

## Decision Outcome

Chosen option: **C**. Hard invariants:

- **Only `rldyour-mcps` declares `.mcp.json`**. The 11 pinned MCP servers
  (Serena, Sequential Thinking, Chrome DevTools, Context7, DeepWiki, Grep,
  shadcn, Dart/Flutter, Figma, OpenAI Docs, GitHub) live in
  `plugins/rldyour-mcps/.mcp.json`. Every browser action is first gated by
  exact `$HOME/.local/bin/cloakbrowser-cdp-health`; execution is limited to
  exact `$HOME/.local/bin/playwright-cli` outside MCP and the exact managed
  Chrome DevTools MCP wrapper. `webwright-task` is compatibility routing only;
  the Webwright runtime and all fallbacks are forbidden.
- **Only `rldyour-flow` and `rldyour-serena-mcp` declare `hooks/hooks.json`**.
  `rldyour-serena-mcp` owns memory-sync lifecycle (UserPromptSubmit,
  PreToolUse:Bash with `if` filter, PostToolUse:Bash with `if` filter).
  `rldyour-flow` owns SDLC orchestration lifecycle (SessionStart×2,
  PostToolUse:Bash with `if` filter, Stop).
- **Stop chain ordering**: Claude registers one Stop hook, the
  `rldyour-flow` dispatcher. The dispatcher invokes the Serena memory child
  gate first, then the Flow post-task child gate. Flow still calls
  `serena_memory_state.py` directly for current-state checks rather than
  depending on child gate stdout.

All other plugins:

- Consume MCP transport via `dependencies: ["rldyour-mcps"]` in
  `plugin.json`.
- Cannot declare their own MCP servers or hooks (validator would catch).

### Consequences

- Good: clear ownership; one place to bump pins, one place to debug hook
  ordering.
- Good: cache invalidation localized (MCP bump → `rldyour-mcps` cache
  only).
- Good: Stop chain ordering deterministic through one registered dispatcher.
- Bad: cross-plugin dependency lookups required (e.g.,
  `flow_post_task_state.py` reaches into `rldyour-serena-mcp` via
  `$(git rev-parse --show-toplevel)/plugins/rldyour-serena-mcp/scripts/...`).
  Mitigation: cross-plugin path patterns documented in
  PATTERNS-01-CANONICAL memory.
- Bad: introducing a new transport requires touching `rldyour-mcps` even
  if the consumer is a single plugin. Acceptable trade-off.

## Confirmation

- `bash scripts/validate_marketplace.sh` step
  "Plugin ownership boundaries (mcp_owner + hook_owners + dependencies)"
  runs `python3 scripts/validate_boundaries.py` which reads
  `config/marketplace-policy.json` and enforces all four invariants
  documented in this ADR:
  1. exactly one plugin owns `.mcp.json` (matches `policy.mcp_owner`),
  2. only declared plugins own `hooks/hooks.json` (matches
     `policy.hook_owners` set exactly - no extras, no missing),
  3. each plugin.json `name` field matches its directory name,
  4. each plugin.json `dependencies` array matches
     `policy.plugin_dependencies[<plugin>]` exactly (sorted).
- CI mirror: `.github/workflows/validate.yml` runs the same validator
  as a dedicated step in the `validate-plugins` job.
- Closure added 2026-05-17 in wave 0.4.3 commit; the older
  "(not yet implemented)" wording was retired with `scripts/validate_boundaries.py`.

## More Information

- Related: ADR-0005 (local stdio github MCP), ADR-0007 (runtime pinning).
