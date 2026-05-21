<!-- Memory Metadata
Last updated: 2026-05-21
Last commit: 3b0ad53 chore(release): 0.6.4
Scope: AGENTS.md, .claude/CLAUDE.md, config/rldyour-contract.json, docs/contract-matrix.md, plugins/rldyour-rules/skills/project-instructions-policy/SKILL.md, plugins/rldyour-flow/scripts/instruction_docs_state.py, scripts/validate_instruction_docs.py, plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py
Area: DOCS
-->

# DOCS-01-INSTRUCTIONS

## Purpose

Durable instruction-file policy for the repository: what belongs in `AGENTS.md`, what belongs in `.claude/CLAUDE.md`, and how those files stay synchronized with code and memories.

## Source Of Truth

- `AGENTS.md`: concise cross-tool project instructions.
- `.claude/CLAUDE.md`: Claude Code-native deep memory for hook canon, subagents, budgets, diagnostics, and Don't/Done rules.
- `config/rldyour-contract.json` and `docs/contract-matrix.md`: cross-tool parity contract referenced from the instruction docs after 0.6.3.
- `plugins/rldyour-rules/skills/project-instructions-policy/SKILL.md`: instruction docs policy skill.
- `plugins/rldyour-rules/references/project-instructions-and-adrs.md`: AGENTS/CLAUDE/REVIEW/ADR policy reference.
- `plugins/rldyour-flow/scripts/instruction_docs_state.py`: detects when durable project facts changed and instruction docs need review.
- `scripts/validate_instruction_docs.py`: line-budget and presence validation.
- `plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py`: treats agent-instruction changes as memory-sync relevant and targets this memory.

## Current Behavior

- User-facing conversation with the owner is Russian unless explicitly requested otherwise.
- Repository artifacts are English: code, docs, comments, commits, AGENTS.md, CLAUDE.md, REVIEW.md, ADRs, Serena memories, plans, and research archives.
- `AGENTS.md` is the cross-tool concise instruction layer and is kept under the project line budget.
- `.claude/CLAUDE.md` is first-class Claude Code memory and must not be reduced to only an `@AGENTS.md` import.
- Both `AGENTS.md` and `.claude/CLAUDE.md` are agent-only in this fullrepo-managed repository and are excluded from `main` through `.git/info/exclude`.
- Current docs include the numbered Serena memory contract: `CORE-01-INDEX.md` is the memory map; topic files use `AREA-01-SLUG.md`.
- `config/REVIEW.md.template` (68 lines) exists at HEAD `00d3f82` - template for project-level `REVIEW.md`. Sections: Always Check, Architecture, Quality, Consistency, Tests, Security, Skip, Notes. Downstream projects copy to project root as `REVIEW.md`; reviewer agents (`flow-*-review`, `ry-rules-review`, `ry-sec-review`) auto-discover it. Verified at `config/REVIEW.md.template` at HEAD `00d3f82`.
- **Public-readiness community docs (0.6.0, commit `ad833b9`, follow-up `332e0e7`)**: `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` added at repo root. `.github/ISSUE_TEMPLATE/bug_report.yml`, `.github/ISSUE_TEMPLATE/feature_request.yml`, `.github/ISSUE_TEMPLATE/config.yml`, `.github/PULL_REQUEST_TEMPLATE.md` added. Verified at listed files at HEAD `b4e63ec`. SECURITY.md and CONTRIBUTING.md are English-only public-facing community policy files.
- **ADR count at HEAD**: 11 ADRs (docs/adr/0001 through 0011 + 0000-template + README). ADR-0011 added in 0.5.2 wave (`da432c6`); README ADR count updated to 11 in 0.6.0 wave (`332e0e7`). Verified at `docs/adr/` listing at HEAD `b4e63ec`.
- `AGENTS.md` routes memory writes through `flow-memory-sync` when Stop/post-task sync requires it and through `serena-memory-sync` as a manual/fallback workflow.
- `AGENTS.md` now lists `config/rldyour-contract.json` and `docs/contract-matrix.md` as source-of-truth files, and includes the contract validation command. `.claude/CLAUDE.md` points back to AGENTS.md for those cross-tool facts.
- Instruction-only commits are sync-relevant. They are not treated as knowledge-only no-ops by `mark_sync_required.sh` or `serena_memory_state.py`.

## Contracts And Data

- `AGENTS.md` should contain cross-tool facts: source-of-truth paths, plugin boundaries, validation/setup commands, SDLC routing, fullrepo policy, MCP transport summary, engineering constraints, and done criteria.
- `.claude/CLAUDE.md` should contain Claude Code-specific facts: subagent matrix, hook lifecycle/canon, skill-listing budget, changelog adoption, diagnostics, and Claude-specific Don't/Done rules.
- Current line counts at HEAD `fb1f4db` plus agent-only sync edits: `AGENTS.md` 200 lines; `.claude/CLAUDE.md` 199 lines (verified by `python3 scripts/validate_instruction_docs.py --require-agent-docs`). Both files declare a 200-line cap in HTML maintainer comments (stripped from Claude's context per CC v2.1.72).
- Do not put secrets, chat transcripts, raw tokens, private cookies, or local credentials into instruction docs.
- Do not store generic advice when a source path or command is more useful.
- Memory taxonomy changes require updates to `AGENTS.md`, `.claude/CLAUDE.md`, `serena-memory-sync` skill, `flow-memory-sync` agent, and `CORE-01-INDEX.md`.

## Change Rules

- Update `AGENTS.md` when durable cross-tool setup, architecture, validation, memory, fullrepo, or workflow rules change.
- Update `.claude/CLAUDE.md` when Claude Code-specific behavior changes: hooks, plugin frontmatter, skill listing, subagents, `/mcp`, `/hooks`, `/memory`, `/context`, `/doctor`, or Claude CLI facts.
- Run instruction-doc checks after any durable project behavior or workflow change.
- Keep both files concise. If a fact is too detailed for startup context, put it in a numbered Serena memory and link only the source-of-truth path or summary in docs.

## Cross-References

- Memory taxonomy (Serena memory naming, sync relevance): [[CORE-01-INDEX]] + [[SERENA-01-MEMORY-SYNC]].
- Claude Code-specific rules and frontmatter: [[CLAUDECODE-01-PLUGIN-CANON]].
- Hook lifecycle (instruction-only sync triggers stop gate): [[HOOKS-01-LIFECYCLE]].
- Patterns (file naming, commit messages): [[PATTERNS-01-CANONICAL]].
- Post-task sync workflow (docs state check): [[FLOW-01-SDLC]].
- Fullrepo branch policy: [[CORE-02-MARKETPLACE]].
- Quality philosophy (language, artifact rules): [[PHILOSOPHY-01-QUALITY-FIRST]].
- Release gate (validate_instruction_docs.py): [[RELEASE-01-VALIDATION]].

## Verification

- `python3 scripts/validate_instruction_docs.py --require-agent-docs`: validates instruction docs presence and line budgets.
- `python3 scripts/validate_contract.py && python3 scripts/generate_contract_matrix.py --check`: validates the cross-tool contract surfaced by AGENTS.md.
- `python3 plugins/rldyour-flow/scripts/instruction_docs_state.py --json | python3 -m json.tool`: explains whether docs need review and why.
- `bash scripts/smoke_serena_memory_taxonomy.sh`: asserts `AGENTS.md` changes require memory sync and target this memory.
- `git status --short`: should not show agent-only docs on `main` because they are fullrepo-managed.
