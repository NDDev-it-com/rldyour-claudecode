---
name: serena-memory-sync
description: "Синхронизация .serena/memories — fact-only заметки из кода/диффов/тестов. Используй для: обнови memories, синхронизируй память, после коммита, после Stop-хука, fact-only audit, .serena/plans, .serena/research, durable changes."
allowed-tools:
  - mcp__plugin_rldyour-mcps_serena__*
  - Read
  - Bash
---

# Serena Memory Sync

## Purpose

Keep `.serena/` useful for future Claude Code sessions without creating hallucinated project lore. Memories must explain what the code actually does, where it lives, how it behaves, which invariants matter, and how to safely change and verify the area.

User-facing conversation stays in Russian. All stored `.serena/` knowledge files are written in English.

## When To Use

Use this skill without waiting for explicit invocation when:

- Meaningful code, plugin, workflow, architecture, design-system, security, integration, or configuration behavior changed.
- A Stop hook, commit-like action, or stale-memory marker indicates project knowledge should be synchronized.
- Durable facts were discovered while making or verifying project changes, and those facts are now encoded in code, configuration, workflow files, committed docs, or stable tests.
- `.serena/memories`, `.serena/plans`, or `.serena/research` may be stale or need a fact-only audit.
- A future Claude Code session would need verified source-of-truth paths, invariants, contracts, entry points, or verification commands to implement confidently.

Do not auto-invoke this skill for read-only context discovery, log/server audits, report-only reviews, exploratory debugging, or current-status snapshots unless the user explicitly asked to update/synchronize memories or a Stop/stale-memory hook requires it. In those read-only workflows, list useful candidates in the user report and wait for permission before writing `.serena`.

Do not create memory noise for trivial formatting, purely mechanical edits, current runtime status, timestamped snapshots, server log summaries, health-check output, or unverified assumptions.

## Stored Locations

- `.serena/memories/`: durable project facts, conventions, architecture notes, implementation facts, and task completion requirements.
- `.serena/plans/`: non-trivial implementation plans that are worth preserving across sessions.
- `.serena/research/`: complex or long research results with source links and implementation impact.

In normal product repositories, these knowledge files are agent-only context. They are restored from and published to `fullrepo`, then ignored through `.git/info/exclude` instead of being committed to `main`. Repositories that are themselves agent tooling may intentionally track selected `.serena` knowledge files when they are part of the product source of truth.

Local/runtime files must not be committed or published by this plugin: `.serena/cache/`, `.serena/.gitignore`, `.serena/project.local.yml`, `.serena/.sync_marker`, `.serena/.serena_sync_state.json`, `.serena/.auto_sync_head`, `.serena/.active_workflow_intent.json`, `.serena/.dirty_stop_ack`.

## Memory Structure

Name memory files as `AREA_NN_slug.md`.

Default areas: `CORE`, `BACKEND`, `FRONTEND`, `MOBILE`, `INFRA`, `API`, `AUTH`, `DATA`, `SEC`, `TEST`, `DESIGN`, `CLI`, `MCP`.

Create custom area prefixes only when the project needs a clearer domain boundary. Keep files narrow and split large memories instead of creating broad catch-all files.

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
# <AREA_NN_slug>

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

1. Inspect git state: current HEAD, recent commits, changed files, and non-memory diffs.
2. Use Serena first: `list_memories`, `read_memory` for relevant files, then `get_symbols_overview`, targeted `find_symbol`, and `find_referencing_symbols` for changed code.
3. Update or create memory files with verified facts only, using the memory body template. Remove or correct stale statements instead of preserving outdated text.
4. Save non-trivial plans to `.serena/plans/` only when they will help future sessions continue work.
5. Save long research summaries to `.serena/research/` only when the research was complex, source-backed, and likely reusable.
6. Keep exact paths, symbol names, commands, contracts, invariants, verification checks, and behavior. Avoid generic advice.
7. Run the plugin's `commit_serena_knowledge.sh` script (path provided by the Stop hook message, or `${CLAUDE_PLUGIN_ROOT}/scripts/commit_serena_knowledge.sh` when the plugin is enabled). In repositories where `.serena` knowledge is still tracked, this creates the knowledge-only commit. In fullrepo-managed repositories, it acknowledges current memories and clears runtime sync markers without committing AI files to the current branch; `flow-post-task-sync` publishes the final `fullrepo` snapshot.

## Quality Rules

Code is the source of truth. Never write a memory fact just because an old memory, plan, comment, or README says it.

Prefer small factual paragraphs over narratives. A future Claude Code session should be able to quickly answer: what exists, where it is implemented, what conventions apply, what behavior and contracts matter, what must not break, how to safely change it, and what checks prove correctness.

Do not store secrets, tokens, private cookies, raw credentials, or sensitive runtime data.

Do not use `.serena/memories` as a backlog. Plans and TODOs belong in `.serena/plans` only when the plan is useful and current.

## Output

Report:

- `Freshness audit`: HEAD, newest synced commit, and changed scope.
- `Updated memories`: edited files.
- `New memories`: new files, if any.
- `Plans/research archived`: files written, if any.
- `Unresolved gaps`: anything that could not be verified from code.
- `Commit`: whether the Serena knowledge-only auto-commit was created or fullrepo-managed knowledge was acknowledged for later `fullrepo` publish.
