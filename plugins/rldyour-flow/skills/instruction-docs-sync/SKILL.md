---
name: instruction-docs-sync
description: "Синхронизация AGENTS.md и .claude/CLAUDE.md из verified project facts. Используй для: project docs, AGENTS.md, CLAUDE.md, инструкции проекта, документация, sync docs, обнови инструкции."
---

# Instruction Docs Sync

## Purpose

Keep project instruction files current after meaningful work without creating a second source of truth or leaking agent-only files into normal branches.

This skill runs after Serena memory sync and before quality checks, commits, GitHub sync, and `fullrepo` publish.

## Required Files

- `AGENTS.md`: Codex-native project instructions.
- `.claude/CLAUDE.md`: Claude Code-native project memory.

Both files are agent-only in normal product repositories: keep them local, ignore them through `.git/info/exclude`, and publish them through `fullrepo`.

## Source Of Truth

Use only verified facts from:

- Current code, config, scripts, manifests, hooks, workflows, tests, and git diffs.
- Relevant Serena memories after they are current for the latest code.
- Commands that actually exist and checks that actually run.
- Official tool documentation when the file describes Codex or Claude Code behavior.

Do not copy chat history, future plans, speculation, secrets, tokens, cookies, or local credentials.

## Workflow

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/instruction_docs_state.py --json`.
2. Inspect changed files and recent commits to decide whether durable project facts changed.
3. Update `AGENTS.md` for Codex:
   - repository purpose and source-of-truth paths;
   - Codex-specific plugin/skill/tool routing;
   - setup, validation, release, deploy, git, and `fullrepo` commands;
   - concise engineering constraints and done criteria.
4. Update `.claude/CLAUDE.md` for Claude Code:
   - Claude Code project memory, commands, architecture, workflow, and diagnostics;
   - Claude-specific locations such as `.claude/settings.json`, `.claude/skills/`, `.claude-plugin/`, hooks, `/memory`, `/context`, `/hooks`, `/mcp`, `/doctor`, and `/status` when relevant;
   - no generic Codex-only instructions unless they also matter to Claude Code.
5. Keep both files independently useful. Do not reduce `.claude/CLAUDE.md` to only `@AGENTS.md`; shared facts may overlap, but each file must be optimized for its own CLI.
6. Let `flow-post-task-sync` commit normal tracked files, then publish agent-only instruction files through `fullrepo`.

## Freshness Rules

Review and update the files when any meaningful task changes durable facts:

- setup, install, bootstrap, doctor, validation, smoke, deploy, or release commands;
- project architecture, module boundaries, generated artifacts, quality gates, or security policy;
- plugins, skills, hooks, MCP definitions, LSP workflow, browser/design/security workflows, or git/fullrepo behavior;
- repository-specific conventions that future Codex or Claude Code sessions must know before editing.

Do not update for purely mechanical formatting, transient local state, temporary runtime markers, or facts already represented accurately.

## Output

Report:

- `Instruction docs state`: required files, missing files, durable-change candidates, and fullrepo policy.
- `Updated docs`: which instruction files changed and why.
- `Validation`: exact validation command and result, or "skipped because no validator yet".
- `Fullrepo`: whether updated agent-only docs still need `fullrepo` publish.

## Anti-patterns

- Reduce `.claude/CLAUDE.md` to a thin `@AGENTS.md` import.
- Copy chat history / future plans / speculation into instruction files.
- Update for mechanical formatting changes only.
- Skip Serena memory current-check before sync (memories first, instruction docs second).
- Commit instruction docs to normal branch when fullrepo policy requires they stay agent-only.
