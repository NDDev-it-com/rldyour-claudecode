---
name: ry-repair
description: "Нормализация репозитория: source-of-truth scan, semantic entropy audit, repair plan, technical-only fixes, validators, docs/memory sync. Используй для: /rldyour-flow:ry-repair, почини систему, нормализуй репозиторий, убери противоречия, repair repo. EN triggers: repository repair, semantic entropy cleanup, contract normalization, stale docs repair, AI-tool context repair."
argument-hint: "<scope or problem>"
---

# ry-repair

## Purpose

Normalize a repository so Claude Code, Codex, and OpenCode can operate from the same verified facts with minimal semantic entropy. This is a technical repair flow, not a permission to change business logic silently.

For rldyour AI CLI configuration repositories, `/ry-repair` also verifies deterministic install/update/sync convergence through the root `config/ry-repair-sync-contract.json` and `scripts/ry_repair_sync.py` contract when that control plane is present.

## Workflow

1. Detect repository type, active branch/worktree, submodules, CI surface, and agent-only/fullrepo policy.
2. Read project instructions (`AGENTS.md`, `.claude/CLAUDE.md`, OpenCode/Codex/Claude config when present) and identify the declared sources of truth.
3. Inspect Serena memories, plans, and research archives for stale facts, unsupported claims, missing taxonomy, or contradictions with current code.
4. Inspect GitHub issues/PRs/history when available through MCP/app/CLI, then verify every issue against current code before treating it as a fact.
5. Inspect MCP/LSP/tooling config, hook lifecycles, commands/skills/agents, CI gates, release manifests, and dependency baselines.
6. When the root control plane is present, run `python3 scripts/ry_repair_sync.py --plan --target "$PWD"` and use `--check` before claiming local repo, system AI CLI config, Serena memory, or GitHub/fullrepo sync.
7. Treat zero-active Semgrep policy as system-wide: installed Claude/Codex/OpenCode configs, active agent/tool surfaces, CI workflows, runtime pins, docs, and release gates must be clean. Keep only negative validators/tests and historical changelog entries.
8. Detect semantic entropy: duplicated docs, stale pins, conflicting instructions, dead config, unclear source-of-truth, missing ADR/CONTEXT/FUTURE facts, and broken validator contracts.
9. Produce a repair plan that separates:
   - technical repairs the agent may apply;
   - business, functional, security-posture, deployment-target, data-model, or ADR decisions that require the owner.
10. Ask the owner in Russian before changing any decision-class item. For Claude Code, use AskUserQuestion when available; otherwise present concise options with a recommendation and impact.
11. Apply technical-only repairs using existing project patterns and native adapter surfaces.
12. Run matching validators, tests, schema checks, hook smoke, release/archive checks, installed-config checks, and instruction/memory freshness checks.
13. Synchronize durable docs and Serena memories from verified code/config state, then finish through `flow-post-task-sync` when the repair changed durable artifacts.

## Non-Negotiables

- Code, current config, current runtime checks, and verified GitHub state are the source of truth. Memories and docs are derived facts.
- Do not edit ADR meaning, business logic, functional behavior, pricing, deployment targets, security posture, or data contracts without owner approval.
- Do not make hooks perform long-running repair work. Hooks may mark state; `ry-repair` performs the repair.
- Do not hide unresolved drift behind "green" summaries. Every blocked check must name the blocker and next proof command.
- Do not report local repo, system config, Serena memory, or GitHub parity without evidence from `ry_repair_sync.py`, installed-config validators, current git state, and fullrepo/GitHub checks where applicable.

## Output

Report in Russian:

- Scope and source-of-truth map.
- Confirmed drift, grouped by severity.
- Technical repairs applied.
- Decision-class items left for owner approval.
- Exact validation commands and results.
- Docs/memory/fullrepo/git synchronization status.
