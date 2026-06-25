# Observability

How to inspect actual loaded state, debug hook lifecycle, triage failures.

## Built-in slash commands (run inside Claude Code session)

These commands surface what Claude Code has actually loaded - always trust them over assumptions about config files:

| Command | What it shows |
|---|---|
| `/status` | Active settings sources (managed → user → project → local) and their precedence |
| `/context` | Token-budget breakdown by category - system prompt, auto-memory, env info, MCP tools, skill descriptions, project CLAUDE.md, user CLAUDE.md, conversation history |
| `/memory` | Loaded `CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/*.md` files. Toggle auto-memory |
| `/skills` | Available skills with descriptions truncated per `skillListingBudgetFraction`. `/skills` menu can flip override states |
| `/agents` | Subagents available to invoke via the `Agent` tool |
| `/hooks` | Active hooks per event with their handler types |
| `/mcp` | Connected MCP servers, tool counts, status (since v2.1.122 marks "connected · tools fetch failed") |
| `/permissions` | Allow/deny rules from settings.json |
| `/doctor` | Auto-updater health + invalid keys + schema errors. Since v2.1.121 also warns about MCP servers overridden by higher-precedence scope |

## Plugin-loading debug

Run the CLI with `--debug` for detailed plugin loading output:

```bash
claude --debug
# Or filter to specific categories:
claude --debug api,hooks
claude --debug-file /tmp/claude-debug.log
```

Debug output shows manifest parse errors, component registration order, hook handler resolution, and MCP server startup logs.

## Machine-readable state (run from repo root)

These scripts emit JSON for scripting / dashboards / failure triage:

```bash
# Serena memory freshness vs HEAD
python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py

# Flow post-task state (dirty files, ahead/behind, tracked-context state, branch cleanup candidates)
python3 plugins/rldyour-flow/scripts/flow_post_task_state.py

# Instruction docs state (AGENTS.md, .claude/CLAUDE.md presence + review need)
python3 plugins/rldyour-flow/scripts/instruction_docs_state.py --json

# Tracked context sync status
plugins/rldyour-flow/scripts/flow_post_task_state.py

# Release manifest snapshot
python3 scripts/release_manifest.py
```

All emit valid JSON to stdout - pipe into `jq`, `python3 -m json.tool`, or your tool of choice.

## Hook lifecycle observability

### What hooks actually fire

The `/hooks` slash command shows registered hooks per event - but not whether they actually fired during the last turn. For lifecycle observability:

1. Run with `--debug api,hooks` - every hook firing logs handler type, command/prompt, exit code, stdout/stderr.
2. Hook stderr appears as `additionalContext` to Claude when `exit 2` blocks. Useful pattern: log diagnostic info to stderr unconditionally, even on success.
3. The `effort.level` JSON field (CC v2.1.133+) is in every hook payload - log it to confirm subagent/main session distinction.

### `hookSpecificOutput` JSON for advanced state

Hooks return discriminated-union JSON:

```json
{
  "continue": true,
  "stopReason": "string",
  "suppressOutput": false,
  "systemMessage": "string",
  "decision": "block",
  "reason": "string",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "additionalContext": "...",
    "permissionDecision": "allow|deny|ask|defer",
    "permissionDecisionReason": "...",
    "updatedInput": {},
    "updatedToolOutput": "..."
  }
}
```

`updatedToolOutput` works for **all** tools since v2.1.121 (was MCP-only before). Use it to inject context into Claude's view of tool results.

## Loop guards (Stop hook chain)

Both Stop hooks write fingerprint markers to detect "stop already attempted with this state" loops:

- `.serena/.sync_marker` - Serena memory sync: stores compound `${HEAD_SHA}:${NEWEST_SHA:-none}` fingerprint, capturing both project HEAD and the newest memory-sync commit (D32 fix). A partial memory sync that writes memories without advancing HEAD changes `NEWEST_SHA`, so the next Stop sees a different fingerprint and re-fires the advisory instead of silently passing.
- `.serena/.flow_sync_marker` - Flow post-task: stores SHA-256 content-hash fingerprint of a 10-field payload covering `(HEAD, dirty_files, ahead/behind, branch_cleanup, serena_current, doc_files_changed, tracked-context_needs_attention, instruction_docs_state.needs_instruction_docs_review)` (D31 fix added the last three fields so all contributors to `needs_flow_sync` enter the hash).

If `stop_hook_active=true` (from event payload, set when same Stop has fired before) AND the fingerprint matches, the hook exits 0 silently - letting Stop succeed without re-emitting the same advisory. This is what prevents infinite-loop "you must run X" prompts.

To debug a stuck loop:

```bash
ls -la .serena/.sync_marker .serena/.flow_sync_marker
cat .serena/.sync_marker .serena/.flow_sync_marker
# Reset:
rm -f .serena/.sync_marker .serena/.flow_sync_marker .serena/.serena_sync_state.json .serena/.flow_post_task_state.json
```

## Diagnostics bundle for off-machine review

`scripts/collect_diagnostics.sh` writes a timestamped tarball under `.serena/diagnostics/` (gitignored) containing CLI version, plugin list, manifest snapshots, MCP config, hook scripts inventory, current branch state, tracked-context state, runtime markers. Use when sharing a bug report or escalating triage:

```bash
scripts/collect_diagnostics.sh
# Returns path to .serena/diagnostics/diag-<UTC-ts>.tar.gz

# To also list the bundle contents on stdout:
scripts/collect_diagnostics.sh --print
```

The script never includes secrets or env values - only files from the repo. Verify before sharing externally.

## CI artifacts

GitHub Actions `validate.yml` runs on every push and PR - green CI is a precondition for tagging a release. Failed runs preserve logs for 90 days by default; download via the Actions tab or `gh run view <run-id> --log`. The scheduled `dependency-check.yml` job runs Mondays 06:00 UTC and produces a separate Actions run that pings on drift between `.mcp.json` pins and `config/mcp-runtime-versions.env`, plus catches unpinned `@latest` specs.

## Failure triage workflow

When a Claude Code session behaves unexpectedly:

1. **Run `/status`, `/context`, `/hooks`, `/mcp`** - confirm what's loaded.
2. **Run `claude --debug api,hooks`** for the failing turn - captures hook lifecycle.
3. **Run state scripts** - confirm machine-readable state (Serena/flow/instruction-docs).
4. **Run `scripts/collect_diagnostics.sh`** - bundle everything for archival.
5. **Run `scripts/validate_marketplace.sh`** - confirm marketplace itself is healthy (rules out drift in our manifests).
6. **Check `~/.claude/plugins/installed_plugins.json`** for stale `gitCommitSha` - restart Claude Code or `/plugin reload` to refresh from the directory marketplace.

The combination of `/doctor`, debug logs, state JSONs, and a diagnostic bundle covers ~95% of triage cases without needing to attach a debugger.
