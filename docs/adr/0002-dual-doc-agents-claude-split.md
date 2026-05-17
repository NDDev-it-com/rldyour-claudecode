# ADR-0002: Two-file AGENTS.md and .claude/CLAUDE.md split

- **Status**: accepted
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd

## Context and Problem Statement

AI tools that consume instruction files diverge in conventions: the
Linux-Foundation-stewarded `AGENTS.md` spec (60k+ adopting repos as of
May 2026, https://agents.md/) is read by OpenAI Codex CLI, GitHub Copilot,
Cursor, Aider, Devin, Windsurf, Roo, OpenHands, Gemini Code Assist, and
others. Claude Code instead reads `.claude/CLAUDE.md` for project-deep
context (subagent matrix, hook canon, skill-listing budget, Claude Code
changelog adoption notes).

A naive single-file approach forces a choice: lose Claude Code-specific
depth (if writing only AGENTS.md) or lose cross-tool reach (if writing
only `.claude/CLAUDE.md`). A thin `.claude/CLAUDE.md` that just imports
`AGENTS.md` (`@AGENTS.md`) was explicitly considered and rejected -
Anthropic memory docs confirm `@import` does not reduce token cost (content
loads at launch either way) and adds indirection without information gain.

Evidence: `.claude/CLAUDE.md:1-5`, `AGENTS.md:1-18`, `~/.claude/CLAUDE.md`
"Don't reduce this file to `@AGENTS.md` import".

## Decision Drivers

- Cross-tool ambition (30+ tools per agents.md spec).
- Claude Code-specific depth (subagents, hooks, skill budget tuning).
- Token-budget realism (no `@import` magic).
- Drift containment (semantic sync must be machine-verified).

## Considered Options

- A: Single `AGENTS.md`, no Claude Code-specific file. Loses depth.
- B: Single `.claude/CLAUDE.md`, no cross-tool file. Loses reach.
- C: Thin `.claude/CLAUDE.md` with `@AGENTS.md` import. Anthropic-recommended
  in some contexts but adds zero token saving and creates "two-truth"
  ambiguity (which file does the model actually load?).
- D: Two first-class files, dual-sourced, with semantic drift validator.

## Decision Outcome

Chosen option: **D**. Both files exist. Each is optimized for its consumer
class. Both files are agent-only (fullrepo-managed - see ADR-0001).
`scripts/validate_instruction_sync.py` parses `<!-- sync_contract: ... -->`
YAML blocks from both files and fails on key-value drift for shared claims.
Each file may carry depth claims unique to its scope (e.g., only
`.claude/CLAUDE.md` declares the hook event canon; only `AGENTS.md`
declares the Codex compatibility section).

### Consequences

- Good: each AI tool loads the deepest applicable file without indirection.
- Good: drift between the two is caught in CI via sync_contract YAML.
- Good: line cap of 200 lines each keeps each file scannable.
- Bad: controlled duplication of cross-tool claims. Mitigation: sync_contract
  validator enforces parity.
- Bad: two locations to update when a shared claim changes. Mitigation: the
  drift validator forces both to update together.

## Confirmation

- `python3 scripts/validate_instruction_docs.py --require-agent-docs`
  enforces presence, heading, line cap, no-secrets.
- `python3 scripts/validate_instruction_sync.py` enforces semantic parity
  for shared `sync_contract:` claims (introduced in G15).
- Both files visible only on `fullrepo` branch (excluded from `main` via
  `.git/info/exclude`).

## More Information

- Cross-tool spec: https://agents.md/ (Linux Foundation AAIF, 2025-12-09).
- Related: ADR-0001 (fullrepo), ADR-0008 (CI baseline that runs the
  validators).
