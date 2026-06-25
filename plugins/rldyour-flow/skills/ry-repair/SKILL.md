---
name: ry-repair
description: "Ремонт ry-repair: почини систему, semantic entropy, validators, docs/memory sync. EN: repo repair, contract normalization."
---

# ry-repair

## Purpose

Normalize a repository so Codex, Claude Code, OpenCode, Antigravity CLI, and MiMoCode can work from the same verified facts with minimal semantic entropy. This is a technical repair workflow; it is not permission to change business logic, product semantics, deployment targets, data contracts, security posture, or ADR meaning silently.

For rldyour AI CLI configuration repositories, `/ry-repair` also owns deterministic install/update/sync convergence: local repository state, system Claude/Codex/OpenCode/Gemini/MiMoCode configs, Serena memories, and GitHub state must be checked through the root `config/ry-repair-sync-contract.json` and `scripts/ry_repair_sync.py` contract before being reported as synchronized.

## Mode Selection

- **Work project**: run the full authoring repair workflow below.
- **rldyour control plane or adapter config repo, goal = converge the installed
  system**: run consumer mode instead - update the checkout FROM GitHub
  (`git pull --ff-only`, `git submodule update --init --recursive`), then
  `python3 scripts/ry_repair_sync.py --check` and `--apply-system`.
  In consumer mode do NOT author changes into the repository: no commits, no
  doc/contract/memory edits, no pushes. If fast-forward fails or
  validators reveal repository drift, report it and switch to authoring repair
  only on explicit owner instruction.

## Workflow

1. Detect repository type, active branch/worktree, submodules, CI surface, and effective project policy from `RLDYOUR_PROJECT_POLICY`, `.rldyour/project-policy.local.json`, `.rldyour/project-policy.json`, or built-in defaults.
2. Read project instructions and native AI-tool config: `AGENTS.md`, `.claude/CLAUDE.md`, `.codex`, `.claude`, `.opencode`, plugin/skill/command/agent manifests, and repository contracts when present.
3. Inspect Serena memories, plans, and research archives for stale facts, unsupported claims, missing taxonomy, duplicated instructions, or contradictions with current code.
4. Inspect GitHub issues, pull requests, and recent history through the GitHub connector, GitHub MCP, or `gh` when available. Verify every issue against current code before treating it as a fact.
5. Inspect MCP/LSP/tooling config, hook lifecycles, CI gates, release manifests, dependency baselines, and docs source-of-truth declarations.
6. When the root control plane is present, run `python3 scripts/ry_repair_sync.py --plan --target "$PWD"` and use `--check` before claiming sync. Use `--apply-system` only for owner-approved system convergence. For OS/mode work, pass explicit flags: `--os macos|linux|wsl|windows`, `--mode standard|orchestrator`, and `--cmux` only for macOS orchestrator mode.
7. Treat approved active inventories as system-wide: source repo surfaces, installed `$CODEX_HOME/config.toml`, Claude marketplace cache, OpenCode project config, generated tool references, CI workflows, runtime pins, docs, and release gates must match current MCP/provider policies. Do not keep permanent tool-specific absence gates for removed components.
8. Detect semantic entropy: duplicated docs, stale pins, conflicting instructions, dead config, unclear source-of-truth, missing ADR/CONTEXT/FUTURE facts, broken validators, adapter parity drift, and natural-language policy overrides that are not materialized in project policy JSON.
9. Produce a repair plan that separates technical repairs from owner-decision items.
10. Ask the owner in Russian before changing any business, functional, security-posture, deployment-target, data-model, or ADR decision. Use concise options with a recommended choice, reason, and impact.
11. Apply technical-only repairs using existing project patterns and native Codex surfaces. If the user explicitly states repository policy and no policy file exists, write `.rldyour/project-policy.json` or `.rldyour/project-policy.local.json` only from that explicit instruction; do not infer ownership/destructive permissions from chat tone.
12. Run matching validators, tests, schema checks, hook smoke, release/archive checks, installed-config checks, and instruction/memory freshness checks.
13. Synchronize durable docs and Serena memories from verified code/config state, then finish through `flow-post-task-sync` when durable artifacts changed.

## Non-Negotiables

- Current code, config, runtime checks, and verified GitHub state are the source of truth. Memories and docs are derived evidence.
- Hooks stay bounded and deterministic. They may mark state; `ry-repair` does the heavy repair work.
- Do not hide unresolved drift behind green summaries. Every blocked check names the blocker and next proof command.
- Do not report local repo, system config, Serena memory, or GitHub parity without evidence from `ry_repair_sync.py`, installed-config validators, current git state, and GitHub checks where applicable.

## Output

Report in Russian with scope, confirmed drift, repairs applied, owner-decision items, exact validation commands, and sync status.
