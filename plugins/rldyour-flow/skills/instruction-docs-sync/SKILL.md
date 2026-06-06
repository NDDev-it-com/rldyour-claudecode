---
name: instruction-docs-sync
description: "Синхронизация AGENTS.md и .claude/CLAUDE.md из verified project facts. Используй для: AGENTS.md, CLAUDE.md, инструкции проекта, документация, обнови инструкции, документация устарела. EN triggers: update project instructions, refresh AGENTS.md, refresh CLAUDE.md, sync project docs, update durable docs, instructions sync."
---

# Instruction Docs Sync

## Purpose

Keep project instruction files current after meaningful work without creating a second source of truth or violating the effective project policy for agent files.

This skill runs after Serena memory sync and before quality checks, commits, GitHub sync, and `fullrepo` publish.

## Required Files

- `AGENTS.md`: concise root project-instruction file (cross-tool standard, see https://agents.md/).
- `.claude/CLAUDE.md`: Claude Code-native deep project memory.

By default these files are agent-only in rldyour-managed product repositories: keep them local, ignore them through `.git/info/exclude`, and publish them through `fullrepo`. If project policy sets `instruction_docs.mode=tracked-normal-branch` or `normal_branch_policy.agent_files=allowed`, treat them as normal tracked project files.

## Source Of Truth

Use only verified facts from:

- Current code, config, scripts, manifests, hooks, workflows, tests, and git diffs.
- Relevant Serena memories after they are current for the latest code.
- Commands that actually exist and checks that actually run.
- Official Claude Code documentation when the file describes Claude Code behavior.

Do not copy chat history, future plans, speculation, secrets, tokens, cookies, or local credentials.

## Workflow

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/instruction_docs_state.py --json`.
2. Inspect changed files and recent commits to decide whether durable project facts changed.
3. Update `AGENTS.md` as the concise root project-instruction file:
   - repository purpose and source-of-truth paths;
   - setup, validation, release, deploy, git, and `fullrepo` commands;
   - architecture map, plugin/skill/tool routing, and integration boundaries;
   - concise engineering constraints, hard rules, and done criteria.
4. Update `.claude/CLAUDE.md` for Claude Code:
   - Claude Code project memory, commands, architecture, workflow, and diagnostics;
   - Claude-specific locations such as `.claude/settings.json`, `.claude/skills/`, `.claude-plugin/`, hooks, `/memory`, `/context`, `/hooks`, `/mcp`, `/doctor`, and `/status` when relevant;
   - deep technical detail that complements the concise root file.
5. Keep both files independently useful. Do not reduce `.claude/CLAUDE.md` to only `@AGENTS.md`; shared facts may overlap, but each file must be optimized for its own role.
6. Let `flow-post-task-sync` commit tracked instruction files or publish agent-only instruction files through `fullrepo` according to effective project policy.

## Freshness Rules

Review and update the files when any meaningful task changes durable facts:

- setup, install, bootstrap, doctor, validation, smoke, deploy, or release commands;
- project architecture, module boundaries, generated artifacts, quality gates, or security policy;
- plugins, skills, hooks, MCP definitions, LSP workflow, browser/design/security workflows, or git/fullrepo behavior;
- repository-specific conventions that future Claude Code sessions must know before editing.

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
- Commit instruction docs to normal branch when fullrepo policy requires they stay agent-only. In tracked-normal-branch policy, committing them is expected.
