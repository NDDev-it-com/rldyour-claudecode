---
name: instruction-docs-sync
description: "Синхронизация AGENTS.md и CLAUDE.md из verified facts. Используй для: инструкции, docs устарели. EN: update project instructions, docs sync."
---

# Instruction Docs Sync

## Purpose

Keep project instruction files current after meaningful work without creating a second source of truth or violating the effective project policy for agent files.

This skill runs after Serena memory sync and before quality checks, commits, and GitHub sync.

## Required Files

- `AGENTS.md`: Codex-native project instructions.
- `.claude/CLAUDE.md`: Claude Code-native project memory.

These files are tracked normally on the `main` branch as ordinary source. Project policy may set `instruction_docs.mode=disabled` to skip review, but by default they are tracked project files.

## Source Of Truth

Use only verified facts from:

- Current code, config, scripts, manifests, hooks, workflows, tests, and git diffs.
- Relevant Serena memories after they are current for the latest code.
- Commands that actually exist and checks that actually run.
- Official tool documentation when the file describes Codex or Claude Code behavior.

Do not copy chat history, future plans, speculation, secrets, tokens, cookies, or local credentials.

## Workflow

1. Run `plugins/rldyour-flow/scripts/instruction_docs_state.py --json` or the cache copy when working outside this repository.
2. Inspect changed files and recent commits to decide whether durable project facts changed.
3. Update `AGENTS.md` for Codex:
   - repository purpose and source-of-truth paths;
   - Codex-specific plugin/skill/tool routing;
   - setup, validation, release, deploy, and git commands;
   - concise engineering constraints and done criteria.
4. Update `.claude/CLAUDE.md` for Claude Code:
   - Claude Code project memory, commands, architecture, workflow, and diagnostics;
   - Claude-specific locations such as `.claude/settings.json`, `.claude/skills/`, hooks, `/memory`, `/context`, `/hooks`, `/mcp`, `/doctor`, and `/status` when relevant;
   - no generic Codex-only instructions unless they also matter to Claude Code.
5. Keep both files independently useful. Do not reduce `.claude/CLAUDE.md` to only `@AGENTS.md`; shared facts may overlap, but each file must be optimized for its own CLI.
6. Run `python3 scripts/validate_instruction_docs.py --require-agent-docs` when the repository tracks agent instruction docs. In clones that do not, run it without `--require-agent-docs`.
7. Let `flow-post-task-sync` commit the tracked instruction files on `main` according to effective project policy.

## Freshness Rules

Review and update the files when any meaningful task changes durable facts:

- setup, install, bootstrap, doctor, validation, smoke, deploy, or release commands;
- project architecture, module boundaries, generated artifacts, quality gates, or security policy;
- plugins, skills, hooks, MCP definitions, LSP workflow, browser/design/security workflows, or git behavior;
- repository-specific conventions that future Codex or Claude Code sessions must know before editing.

Do not update for purely mechanical formatting, transient local state, temporary runtime markers, or facts already represented accurately.

## Output

Report:

- `Instruction docs state`: required files, missing files, and durable-change candidates.
- `Updated docs`: which instruction files changed and why.
- `Validation`: exact validation command and result.
- `Commit`: which tracked instruction files `flow-post-task-sync` will commit on `main`.
