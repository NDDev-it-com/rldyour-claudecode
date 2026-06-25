---
name: serena-memory-sync
description: "Синхронизация Serena memories в .serena/memories: fact-only durable knowledge. Используй для: обнови memories. EN: sync memories, refresh project knowledge."
---

# Serena Memory Sync

## Purpose

Keep `.serena/` useful for future Codex, Claude Code, and other GPT-based coding agent sessions without creating hallucinated project lore. Memories must explain what the code actually does, where it lives, how it behaves, which invariants matter, and how to safely change and verify the area.

User-facing conversation stays in Russian. All stored `.serena/` knowledge files are written in English.

## When To Use

Use this skill without waiting for explicit invocation when:

- Meaningful code, plugin, workflow, architecture, design-system, security, integration, or configuration behavior changed.
- A Stop hook, commit-like action, or stale-memory marker indicates project knowledge should be synchronized.
- Durable facts were discovered while making or verifying project changes, and those facts are now encoded in code, configuration, workflow files, committed docs, or stable tests.
- `.serena/memories`, `.serena/plans`, or `.serena/research` may be stale or need a fact-only audit.
- A future Codex, Claude Code, or GPT-based agent session would need verified source-of-truth paths, invariants, contracts, entry points, or verification commands to implement confidently.

Do not auto-invoke this skill for read-only context discovery, log/server audits, report-only reviews, exploratory debugging, or current-status snapshots unless the user explicitly asked to update/synchronize memories or a Stop/stale-memory hook requires it. In those read-only workflows, list useful candidates in the user report and wait for permission before writing `.serena`.

Do not create memory noise for trivial formatting, purely mechanical edits, current runtime status, timestamped snapshots, server log summaries, health-check output, or unverified assumptions.

## Stored Locations

- `.serena/memories/`: durable project facts, conventions, architecture notes, implementation facts, and task completion requirements.
- `.serena/plans/`: non-trivial implementation plans that are worth preserving across sessions.
- `.serena/research/`: complex or long research results with source links and implementation impact.

These knowledge files are tracked normally on `main` as ordinary source, with no separate agent-only branch or overlay; the knowledge-only commit lands on `main` like any other source change.

Local/runtime files must not be committed or published by this plugin: `.serena/cache/`, `.serena/.gitignore`, `.serena/project.local.yml`, `.serena/.sync_marker`, `.serena/.serena_sync_state.json`, `.serena/.auto_sync_head`, `.serena/.active_workflow_intent.json`, `.serena/.dirty_stop_ack`, `.serena/.flow_sync_marker`, `.serena/.flow_post_task_state.json`.

## Memory Structure

Name memory files as `AREA-01-SLUG.md`.

Default cross-project areas: `CORE`, `BACKEND`, `FRONTEND`, `MOBILE`, `INFRA`, `API`, `AUTH`, `DATA`, `SEC`, `TEST`, `DESIGN`, `CLI`, `MCP`, `DOCS`, `RELEASE`, `TECHDEBT`. Agent-tooling repositories may add tool-specific areas such as `CODEX` when they are clearer than overloading `CORE`.

Create custom area prefixes only when the project needs a clearer domain boundary. Keep files narrow and split large memories instead of creating broad catch-all files.

Every project should maintain a compact index memory, normally `CORE-01-INDEX.md`, that lists the active memory areas, canonical file names, and which source-of-truth paths each memory owns. When adding a new memory, update the index in the same sync pass.

Numbering is stable:

- `01` is normally the area index or the first canonical topic.
- Add `02`, `03`, ... for new durable topics inside the same area.
- Do not renumber existing memories unless performing an explicit taxonomy migration.
- Use uppercase area codes and uppercase hyphenated slugs: `SERENA-01-MEMORY-SYNC.md`, `TECHDEBT-01-NOW.md`.

Split a memory when it starts covering more than one domain responsibility, when sections become hard to scan, or when a future agent would need to read many unrelated facts to answer one scoped question. Prefer adding a specific numbered file over appending unrelated content to an older broad memory.

Do not create timestamped snapshot memories such as `SYNC_YYYYMMDD_*`. If a runtime observation reveals a durable contract, update the relevant area memory with the stable contract and source paths instead of storing the observation as a snapshot.

Every memory starts with exactly this metadata block:

```html
<!-- Memory Metadata
Last updated: YYYY-MM-DD
Last commit: <sha> <message>
Scope: <files/dirs>
Area: <AREA>
-->
```

Do not add subjective confidence fields or unsupported metadata. If a fact is unresolved, put it in the body as an explicit unresolved gap.

## Memory Body Template

After the metadata block, use this body structure unless a section is truly irrelevant. Keep sections concise and factual.

```markdown
# <AREA-01-SLUG>

## Purpose

What this area is responsible for in the current project.

## Source Of Truth

- `path/to/file`: verified role of the file.
- `path/to/directory/`: verified role of the directory.

## Entry Points

- `symbol_or_command`: when it is used and what it controls.

## Current Behavior

Facts about runtime behavior, data flow, configuration flow, or lifecycle behavior that were verified from code, git diff, tests, or authoritative project files.

## Contracts And Data

File formats, config keys, environment variables, schemas, API shapes, command arguments, naming conventions, and persistence rules that future changes must preserve.

## Invariants

- Conditions that must remain true after changes.
- Boundaries that must not be crossed.

## Change Rules

- How to modify this area safely.
- Which tools or project patterns should be used first.

## Verification

- `command`: what it proves.
- Manual check: exact behavior to inspect if no command exists.

## Known Gaps

- Unverified or intentionally unresolved facts. Omit this section when there are no gaps.
```

Use exact file paths and symbol names. If a section would only contain generic advice, omit it rather than adding filler.

## What To Capture

Capture facts that materially improve future implementation confidence:

- Stable architecture boundaries and ownership of files/directories.
- Source-of-truth files for behavior, configuration, schemas, generated outputs, and public interfaces.
- Entry points: commands, hooks, routes, exported functions/classes, plugin manifests, MCP server definitions, and lifecycle scripts.
- Current behavior that affects implementation: startup order, data flow, side effects, fallback behavior, error handling, persistence, and external integrations.
- Contracts: file naming, metadata blocks, environment variables, API payloads, CLI flags, hook payload shape, and expected output shape.
- Invariants and constraints: safety boundaries, idempotency rules, no-secret rules, language/documentation policy, cross-plugin boundaries, and compatibility requirements.
- Verification: exact tests, linters, type checks, smoke checks, manual checks, and what each check proves.
- Recently changed decisions when they are now encoded in code or committed project configuration.

## What Not To Capture

Do not write:

- Conversation history, user preferences that are not project rules, or motivational text.
- Backlog items, speculative plans, TODO lists, or desired future architecture. Use `.serena/plans` for current non-trivial plans.
- Facts copied from old memories, README files, or comments unless verified against code.
- One-off init snapshots, server log excerpts, current health statuses, container/process lists, incident timestamps, or temporary audit observations.
- Obvious generic advice such as "write clean code" or "run tests" without project-specific commands or scope.
- Secrets, credentials, private cookies, raw tokens, local machine-only paths unless the project explicitly depends on that path.
- Large pasted code blocks. Reference exact paths and symbols instead.

## Sync Workflow

1. Resolve the concrete Git target:
   - Run `git rev-parse --show-toplevel`, `git rev-parse HEAD`, and `git rev-parse --short=7 HEAD` from the repository being synchronized.
   - Before any Serena MCP memory write, verify the active Serena project resolves to that Git root. If it does not, activate the intended repository path first.
   - In superprojects, process root and every nested repository with `.serena/memories/` separately; each memory set is synchronized against its own repository HEAD, not the superproject HEAD.
2. Read marker + impact analysis:
   - `python3 plugins/rldyour-serena-mcp/scripts/serena_memory_state.py` (state + stale marker)
   - `jq`/`python3` read `.serena/.serena_sync_state.json` if present; use `analysis.memory_taxonomy`, `analysis.memory_targets`, `analysis.areas`, and `analysis.areas_summary` as the first-pass scope.
   - Treat `analysis.schema_version` as the analyzer payload contract; if the field is missing, proceed conservatively from changed files.
3. Build the concrete sync scope:
   - Start from `sync_state.changed_files` when available.
   - If analysis exists, prioritize files and areas in `analysis.areas` and `analysis.memory_targets`.
   - If analysis is missing, fall back to `changed_files_since_sync` in state.
4. Use Serena first: `list_memories`, then read `CORE-01-INDEX` when present and every relevant memory target inferred from names. For code, use `get_symbols_overview`, targeted `find_symbol`, and `find_referencing_symbols` before raw reads when the language server supports the file type.
5. Update or create memory files with verified facts only, using the memory body template and the project taxonomy. Remove or correct stale statements instead of preserving outdated text.
6. Save non-trivial plans to `.serena/plans/` only when they will help future sessions continue work.
7. Save long research summaries to `.serena/research/` only when the research was complex, source-backed, and likely reusable.
8. Keep exact paths, symbol names, commands, contracts, invariants, verification checks, and behavior. Avoid generic advice.
9. Run the plugin's `commit_serena_knowledge.sh` script (path provided by the Stop hook message, or `${CLAUDE_PLUGIN_ROOT}/scripts/commit_serena_knowledge.sh` when the plugin is enabled). `.serena` knowledge is tracked normally on `main`, so this creates the knowledge-only commit and clears runtime sync markers.

## Quality Rules

Code is the source of truth. Never write a memory fact just because an old memory, plan, comment, or README says it.

Prefer small factual paragraphs over narratives. A future GPT-based coding agent should be able to quickly answer: what exists, where it is implemented, what conventions apply, what behavior and contracts matter, what must not break, how to safely change it, and what checks prove correctness.

Do not store secrets, tokens, private cookies, raw credentials, or sensitive runtime data.

Do not use `.serena/memories` as a backlog. Plans and TODOs belong in `.serena/plans` only when the plan is useful and current.

## Output

Report:

- `Freshness audit`: HEAD, newest synced commit, and changed scope.
- `Updated memories`: edited files.
- `New memories`: new files, if any.
- `Plans/research archived`: files written, if any.
- `Unresolved gaps`: anything that could not be verified from code.
- `Commit`: whether the Serena knowledge-only commit on `main` was created.
