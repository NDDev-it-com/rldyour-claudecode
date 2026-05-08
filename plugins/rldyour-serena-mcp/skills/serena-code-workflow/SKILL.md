---
name: serena-code-workflow
description: "Семантический воркфлоу для кода через Serena MCP — приоритет перед raw reads и grep. Используй для: изучи код, проиндексируй проект, найди символы, найди ссылки на символ, рефакторинг, проследи реализацию, инспектируй файл. EN triggers: navigate code, find symbol, find references, semantic refactor, trace usages, inspect file, code lookup, symbol search, where is X defined."
allowed-tools:
  - mcp__plugin_rldyour-mcps_serena__*
  - Read
  - Grep
  - Glob
---

# Serena Code Workflow

## Purpose

Use Serena MCP as the primary semantic layer for code work. The goal is low semantic entropy: understand structure before reading bodies, edit symbols instead of brittle line ranges, keep project knowledge synchronized, and prefer scalable patterns over quick text surgery.

User-facing conversation stays in Russian unless the user asks otherwise. Repository documentation, code comments, commit messages, memory files, plan files, and research archive files are written in English.

## When To Use

Use this skill without waiting for explicit invocation when the task asks to:

- Inspect, index, explore, understand, map, review, edit, refactor, or trace repository code.
- Analyze projects, directories, files, symbols, classes, functions, references, call sites, dependencies, or implementation scope.
- Find where a feature is implemented, how code is connected, what can be deleted, or what will be affected by a change.
- Make non-trivial code changes where semantic structure matters more than raw text matching.
- Use or prefer Serena MCP, LSP-aware tools, symbol navigation, or project memories.

If Serena is unavailable or the file type is not supported, state the fallback and continue with Claude Code-native tools (Read, Grep, Glob, Edit). Do not block progress just because a preferred MCP tool is missing.

## Serena Tool Order (read)

For reading code, follow this order unless the task is trivial or the current session lacks a listed tool:

1. `activate_project` when the active project is unclear.
2. `check_onboarding_performed` to verify whether Serena project onboarding exists.
3. `list_memories` to discover durable project knowledge.
4. `read_memory` only for relevant memories inferred from names.
5. `get_symbols_overview` to map top-level file structure without reading full files.
6. `find_symbol` with `include_body=false` to discover children, overloads, and symbol paths.
7. `find_symbol` with `include_body=true` only for the exact implementation needed.
8. `find_referencing_symbols` to trace callers, usages, dead code risk, and refactor impact.
9. `search_for_pattern` only for broad text sweeps, non-symbol text, or fallback coverage.

## Serena Tool Order (edit)

For editing code, prefer:

1. `find_symbol(include_body=true)` to read the current implementation.
2. `replace_symbol_body` for whole-symbol replacement.
3. `insert_before_symbol` or `insert_after_symbol` for structured additions.
4. `rename_symbol` for LSP-aware symbol renames.
5. `safe_delete_symbol` if available and suitable.

Use raw `rg`, direct file reads, and line patches only when Serena cannot answer the question, when the task is text-level rather than symbol-level, or when the needed edit is a tiny known-location change.

## Indexing And Project Discovery

For Serena project setup and indexing, follow Serena's project workflow. The official indexing operation is the Serena project command `serena project index`; MCP tools then use the resulting project and language-server state for semantic navigation. Do not invent a nonexistent MCP "index directory" tool.

When a project is not onboarded, use Serena onboarding patterns and memory tools as the source of durable project context. Full project initialization commands belong to the `rldyour-flow` plugin; this skill only defines the Serena-first rule and the correct tool priority.

## Quality Rules

Code is the source of truth. Memories, plans, and docs must be checked against actual code, git diff, and task-specific verification.

Do not read entire files when `get_symbols_overview` plus targeted `find_symbol` is enough. Do not use grep as the first move for symbol-level questions.

For non-trivial decisions, make a short explicit plan before editing. If the task requires external technical research, use the `rldyour-explore` plugin first and then return to Serena for local code impact.

After meaningful project changes, use the `serena-memory-sync` skill before final stop so `.serena/memories` stays accurate.

## Output

For investigation-only work, report:

- `Scope`: what code was inspected.
- `Evidence`: Serena tools or fallback sources used.
- `Findings`: concrete facts with file paths or symbol names.
- `Next steps`: implementation or verification actions.

For implementation work, keep the final concise: what changed, how it was verified, and any residual risk.

## Anti-patterns

- Reading whole files for symbol-level questions
- Using grep before `get_symbols_overview` for symbol search
- Editing line ranges when `replace_symbol_body` would do
- Skipping memories before exploring
- Assuming Serena is unavailable without checking
