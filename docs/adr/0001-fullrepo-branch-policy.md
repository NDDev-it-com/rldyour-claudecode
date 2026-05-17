# ADR-0001: Fullrepo branch policy for agent-only files

- **Status**: accepted
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd
- **Informed**: future contributors and downstream marketplace consumers

## Context and Problem Statement

The repository ships two distinct artefact classes:

1. **Product**: marketplace manifest, plugin manifests, skills, agents,
   hooks, scripts, workflows, README, CHANGELOG, LICENSE. These are
   user-installable through `claude plugin install` and must live on `main`.
2. **Agent-only**: instruction files for AI tools (`AGENTS.md`,
   `.claude/CLAUDE.md`, `REVIEW.md`, `GEMINI.md`, `QWEN.md`), local AI tool
   directories (`.claude/**`, `.cursor/rules/**`, `.aider*`, `.gemini/**`,
   `.roo/**`, `.windsurf/**`, `.openhands/**`, `.agents/**`, `.github/copilot-instructions.md`,
   `.github/instructions/**`, `.github/prompts/**`), and Serena state
   (`.serena/project.yml`, `.serena/memories/**`, `.serena/plans/**`,
   `.serena/research/**`, `.serena/newproj/**`, `.serena/deploy/**`).

The Anthropic plugins-official marketplace (verified live snapshot at
2026-05-17) contains zero agent-only files at the root; their `main` is
strictly product. End-user consumers should see only the product when they
clone, but the maintainer wants persistent agent context across sessions
and worktrees.

Evidence: `plugins/rldyour-flow/scripts/fullrepo_sync.py:21-48` (AGENT_ONLY_PATTERNS),
`config/marketplace-policy.json` agent_only_path_globs.

## Decision Drivers

- Customer-facing branch must remain product-clean (parity with Anthropic).
- Maintainer needs durable AI context (memories, instructions) across
  sessions, worktrees, and machines.
- Branch protection on `main` must not block agent-only edits.

## Considered Options

- A: Keep everything in `main`. Pollutes product surface.
- B: Keep agent-only in a separate private branch with manual sync. High
  friction; easy to drift.
- C: Use `fullrepo` branch published from `main` via a controlled script.
  Two source-of-truth branches with explicit synchronization.

## Decision Outcome

Chosen option: **C**. `main` carries product. `fullrepo` carries `main`
content **plus** agent-only files; published via `python3
plugins/rldyour-flow/scripts/fullrepo_sync.py --publish` with
`--force-with-lease`. `.git/info/exclude` keeps agent-only files invisible
to git on `main` worktrees so they cannot leak into product commits.

### Consequences

- Good: zero pollution of `main`; product diff is always meaningful.
- Good: agent context survives across worktrees via `--restore`.
- Good: `--force-with-lease` allowed on `fullrepo` because it is intentionally
  rebuilt from `main`+local; never on `main`.
- Bad: discipline required - smoke_fullrepo_sync.sh, the R5 footgun, can
  overwrite in-flight agent-only edits. Mitigation: bootstrap_check.sh
  divergence guard (D19) refuses `--bootstrap-init` when local agent-only
  files differ from `origin/fullrepo`.
- Bad: branch governance must differ between `main` (PR + signed commits)
  and `fullrepo` (force-push allowed). See ADR-0008.

## Confirmation

- `python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --status-json`
  reports `tracked_agent_paths: []` on `main`.
- `bash scripts/smoke_bootstrap_check.sh` passes (7 assertion steps).
- `bash plugins/rldyour-flow/scripts/local_git_ai_guard.sh` blocks product
  branch pushes that contain agent-only paths.

## More Information

- Implementation: `plugins/rldyour-flow/scripts/fullrepo_sync.py`.
- Bootstrap guard: `scripts/bootstrap_check.sh` (D19/R5 closure).
- Related: ADR-0006 (boundaries), ADR-0008 (CI baseline).
