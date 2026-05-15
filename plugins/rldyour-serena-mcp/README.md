# rldyour-serena-mcp

Serena-first semantic code workflow + fact-only memory sync + lifecycle hooks.

## What's inside

- `2` skills: `serena-code-workflow` (semantic inspection patterns), `serena-memory-sync` (memory write rules).
- `1` subagent: `flow-memory-sync` (`model: sonnet`, `effort: high`, `maxTurns: 36`, `color: yellow`, `disallowedTools: [Edit, Write, NotebookEdit]`) — the canonical handler for `.serena/memories/*.md` updates with anti-hallucination contract (citation per claim, source-of-truth hierarchy code > tests > git diff > existing memories, removal-first principle).
- `4` hooks: `UserPromptSubmit`, `PreToolUse:Bash` (auto-sync baseline), `PostToolUse:Bash` (mark sync required), `Stop` (memory-sync gate — emits advisory + `exit 2` when memories are stale).
- `3` scripts: `analyze_sync_scope.py` (commit-range/file-list impact analysis for focused sync), `serena_memory_state.py` (machine-readable freshness check), `commit_serena_knowledge.sh` (acknowledge sync state, used by hooks and the `flow-memory-sync` subagent).

## Coordination contract

Serena owns memory freshness. The flow plugin's Stop hook derives `serena_current` from `serena_memory_state.py` before checking git/docs/fullrepo state — so memory sync runs first, then post-task pipeline.

## Loop guard

`.serena/.sync_marker` carries the current HEAD SHA. If `stop_hook_active=true` and the marker matches, the hook allows Stop without re-running.

## Dependencies

`rldyour-mcps` (Serena MCP server lives there).
