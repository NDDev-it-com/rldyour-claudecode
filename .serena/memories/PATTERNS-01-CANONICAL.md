<!-- Memory Metadata
Last updated: 2026-05-17
Last commit: bf19b44 docs(readme): update versions to 0.2.3 + add Support/Feedback section
Scope: .claude/CLAUDE.md (Engineering Conventions), AGENTS.md (Engineering Constraints), plugins/rldyour-flow/agents/flow-*-review.md, plugins/rldyour-explore/agents/ry-explore.md, plugins/rldyour-serena-mcp/agents/flow-memory-sync.md, plugins/*/skills/*/SKILL.md, plugins/*/hooks/*.sh, plugins/*/hooks/hooks.json, scripts/validate_agent_tools.py, scripts/worktree_add.sh, scripts/install-rldyour-marketplace.sh
Area: PATTERNS
-->

# PATTERNS-01-CANONICAL

## Purpose

Catalog of canonical implementation patterns used throughout this marketplace. When adding a new skill, agent, command, hook, script, or memory, use these patterns as the **copy-from-here template** to keep the system uniform and free of semantic entropy. Drift from these patterns is a consistency-review FAIL.

## File Naming

- All files and directories: **kebab-case** (`flow-post-task-sync.md`, `validate-agent-tools.py`).
- Shell scripts: `kebab-case.sh`.
- Python scripts: `snake_case.py` (Python identifier conformance overrides kebab-case for module names).
- Test files: `*.test.<ext>` or `*.spec.<ext>` colocated with source.
- Configuration files: lowercase with dots (`tsconfig.json`, `eslint.config.js`).

## Identifier Conventions

| Context | Style | Example |
|---|---|---|
| Shell exported / config vars | `SCREAMING_SNAKE_CASE` | `RLDYOUR_SKIP_STOP_GATES` |
| Shell local vars | `snake_case` | `script_dir`, `head_sha` |
| Python module-level constants | `SCREAMING_SNAKE_CASE` | `KNOWN_BUILTIN_TOOLS` |
| Python functions / variables | `snake_case` | `validate_agent_file` |
| Python classes | `PascalCase` | `MemoryWriter` |
| TS/JS functions / variables | `camelCase` | `parseAgent` |
| TS/JS classes / types / interfaces / enums | `PascalCase` | `AgentDefinition` |
| Constants (all languages) | `SCREAMING_SNAKE_CASE` | `MAX_SUBJECT_LEN` |

Boolean prefixes: `is_`, `has_`, `should_`, `can_` (Python/Rust/Shell) and `is`, `has`, `should`, `can` (TS/JS).

## SKILL.md Frontmatter

```yaml
---
name: <kebab-case-skill-name>
description: "<RU-leading text>. Используй для: <RU trigger phrases>. EN triggers: <EN trigger phrases>."
# Optional fields:
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - mcp__plugin_rldyour-mcps_<server>__<tool_or_*>
disable-model-invocation: true     # slash-only invocation (slash-command-driven workflows)
argument-hint: "<scope>"
---
```

Rules:
- **Description is Russian-leading**. EN triggers appended after `EN triggers:` (per AGENTS.md Engineering Constraints).
- **Average 350-400 chars per description** (entire frontmatter description field).
- `allowed-tools` removes per-call permission prompts during work without touching the listing budget.
- `disable-model-invocation: true` makes the skill slash-only (4 skills currently: `ry-deploy`, `ry-newp`, `ry-rules-review`, `ry-sec-review`).

## Agent Frontmatter

```yaml
---
name: <kebab-case-agent-name>
description: <one-line orchestration-focused; reviewer agents avoid "use when..." triggers>
model: sonnet                       # canonical short form
# or:
# model: opus[1m]                   # canonical bracketed form, CC v2.1.111+, account-gated
effort: high                        # | low | medium | high | max
maxTurns: 36                        # 36 for standard reviewer; 42 for security (+6 variant-hunt); 90 for ry-explore
tools:                              # explicit allowlist (canonical Anthropic pattern)
  - Read
  - Grep
  - Glob
  - Bash
  - mcp__plugin_rldyour-mcps_serena__find_symbol
  - mcp__plugin_rldyour-mcps_serena__find_referencing_symbols
  - mcp__plugin_rldyour-mcps_serena__find_implementations
  - mcp__plugin_rldyour-mcps_serena__find_declaration
  - mcp__plugin_rldyour-mcps_serena__get_symbols_overview
  - mcp__plugin_rldyour-mcps_serena__search_for_pattern
  - mcp__plugin_rldyour-mcps_serena__read_file
  - mcp__plugin_rldyour-mcps_serena__list_dir
  - mcp__plugin_rldyour-mcps_serena__find_file
  - mcp__plugin_rldyour-mcps_serena__list_memories
  - mcp__plugin_rldyour-mcps_serena__read_memory
  - mcp__plugin_rldyour-mcps_serena__get_current_config
  - mcp__plugin_rldyour-mcps_serena__get_diagnostics_for_file
  - mcp__plugin_rldyour-mcps_serena__check_onboarding_performed
  - mcp__plugin_rldyour-mcps_context7__*
  - mcp__plugin_rldyour-mcps_deepwiki__*
  - mcp__plugin_rldyour-mcps_grep__*
color: blue                         # blue, green, purple, orange, pink, red, cyan, yellow
---
```

Rules:
- **Explicit `tools:` allowlist beats `disallowedTools` denylist**. Pattern from `anthropics/claude-plugins-official/plugins/pr-review-toolkit/agents/code-reviewer.md`. Provides future-proof read-only isolation if Claude Code adds new edit-like tools.
- **`mcp__plugin_rldyour-mcps_serena__*` wildcard is FORBIDDEN** for read-only agents (D15 closure): Serena has 11 write tools. Use the explicit 14-tool read-only subset above.
- Wildcards allowed only for `READ_ONLY_BY_DESIGN_MCPS` (context7, deepwiki, grep, semgrep) per `scripts/validate_agent_tools.py`.
- `flow-memory-sync` is the **only exception** retaining `disallowedTools: [Edit, Write, NotebookEdit]` - its job requires Serena memory write tools, so a wider allowlist plus the denylist provides defence-in-depth against project-file mutation.
- Plugin-shipped subagents silently ignore `hooks`, `mcpServers`, `permissionMode`.
- Reviewer subagent maxTurns is ×3 of naive limit (36/42 instead of 12-14) - MCP-rich toolsets consume 5-8 turns on tool plumbing before useful work begins.

## Slash Command Frontmatter

```yaml
---
description: "Запустить <RU action>. Run <EN action>."
argument-hint: <scope>
# Optional:
# context: fork              # isolated context window per invocation
# agent: <agent-name>        # delegate body execution to named agent
---

<RU body text with $ARGUMENTS substitution>

Use the `<skill-name>` skill to ...

Reply in Russian.
```

Rules:
- Bare `model:` is silently ignored without `context: fork`. Pair them or delegate via `agent:`.
- Slash commands reference internal files via `${CLAUDE_PLUGIN_ROOT}/scripts/...` and `${CLAUDE_PLUGIN_ROOT}/references/...`.
- Cross-plugin references use `${CLAUDE_PROJECT_DIR}` (hooks only) or `$(git rev-parse --show-toplevel)` (skill body invocation context).

## Hook Script (Bash)

```bash
#!/usr/bin/env bash
# <hook-name>.sh - <one-line purpose>.
#
# <Multi-line description: what triggers it, what it does, what it does NOT do.>
#
# Skip flag: RLDYOUR_SKIP_<NAME>=1 → exit 0 immediately.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

if [ "${RLDYOUR_SKIP_<NAME>:-0}" = "1" ]; then
  exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Read stdin payload (JSON from Claude Code).
INPUT=$(cat 2>/dev/null || true)
PARSED=$(printf "%s" "$INPUT" | python3 -c '
import json, sys
try:
    payload = json.load(sys.stdin)
except Exception:
    raise SystemExit(0)
# Extract fields safely.
print(payload.get("field", ""))
' 2>/dev/null || true)

# ... main logic ...

# Emit JSON additionalContext if applicable.
python3 - "$CONTEXT" <<'PY'
import json, sys
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "<EventName>",
        "additionalContext": sys.argv[1],
    }
}))
PY
```

Rules:
- **Shell strict mode trio**: `set -euo pipefail` + `IFS=$'\n\t'` + `unset CDPATH` always together, right after shebang + comment block.
- Defensive guards: `RLDYOUR_SKIP_*` env-var short-circuit + outside-git short-circuit.
- Stdin JSON parsed via `python3 -c` heredoc, not shell awk/sed.
- `additionalContext` JSON emitted via second `python3 - <<'PY'` heredoc using `json.dumps`.
- Stop hooks exit `2` to block, all other hooks exit `0` (advisory).
- No push, no merge, no fullrepo publish, no branch deletion in hooks - high-blast-radius operations belong to orchestrator skills/subagents.

## Reviewer Report Heredoc Marker

Canonical EOF marker for reviewer agent report writes: `RLDYOUR_REPORT_EOF`.

```bash
cat > "${report_dir}/<reviewer-name>.md" <<'RLDYOUR_REPORT_EOF'
<full markdown report body>
RLDYOUR_REPORT_EOF
```

Rationale: short generic tokens (`MD`, `EOF`, `END`) can appear legitimately inside a reviewer's markdown report body and cause premature heredoc termination - an Anthropic-acknowledged regression in reviewer `task.output` handling (issues #16789, #20531, #23463, all closed "not planned"). `RLDYOUR_REPORT_EOF` is sufficiently unique to avoid collision. Closing marker must be at column 0 (bash heredoc rule). Canonical example: `plugins/rldyour-flow/references/reviewer-protocol.md` lines 62-67 at HEAD `e5a7694`. Applied to all 6 reviewer agents (`flow-architecture-review.md`, `flow-quality-review.md`, `flow-consistency-review.md`, `flow-integration-review.md`, `flow-verification-review.md`, `flow-security-review.md`) in `plugins/rldyour-flow/agents/`. Drift detection: `scripts/validate_reviewer_contracts.sh` asserts the marker + 4 sibling invariants across all 6 reviewer agents and the protocol; wired into `scripts/validate_marketplace.sh` after the "Agent tools allowlist validation" step (lines 123-126 at HEAD `00d3f82`). Script (180 lines at HEAD `00d3f82`) checks 9 invariant types: 7 PASS per agent × 6 agents = 42, plus 4 protocol-level PASS = 46 PASS total (verified by `bash scripts/validate_reviewer_contracts.sh` at HEAD `00d3f82`). Header corrected to list all 9 invariants in commit `6f0c70d`. Behavior asserted by automated test at `scripts/validate_reviewer_contracts.sh`.

## Cross-Plugin Path Patterns

| Context | Pattern |
|---|---|
| In-plugin script in skill body | `${CLAUDE_PLUGIN_ROOT}/scripts/<file>` |
| In-plugin reference in skill body | `${CLAUDE_PLUGIN_ROOT}/references/<file>.md` |
| Cross-plugin path in skill body | `$(git rev-parse --show-toplevel)/plugins/<other-plugin>/scripts/<file>` |
| In-hook command in `hooks.json` | `bash ${CLAUDE_PLUGIN_ROOT}/hooks/<script>.sh` (Claude Code expands before passing to shell) |
| In-hook stdio MCP env | `${CLAUDE_PROJECT_DIR}` (v2.1.139+ - passed to subprocess env, NOT skill-body-visible) |

**Anti-pattern**: hardcoded relative paths (`plugins/rldyour-serena-mcp/scripts/...`). They break when cwd ≠ repo root.

## Input Validation Patterns

### Branch / ref names (worktree, git tooling)

```bash
# Layer 1: conservative regex (cheap, rejects option-injection like --upload-pack=evil)
if ! [[ "${BRANCH}" =~ ^[A-Za-z0-9._/-]{1,255}$ ]]; then
  echo "FAIL invalid branch name '${BRANCH}'" >&2
  exit 1
fi

# Layer 2: git's own check-ref-format (canonical, rejects refs git itself refuses)
if ! git check-ref-format --branch "${BRANCH}" >/dev/null 2>&1; then
  echo "FAIL branch name '${BRANCH}' rejected by git check-ref-format" >&2
  exit 1
fi

# Layer 3: '--' separator before path arguments in git commands
git "${GIT_ARGS[@]} -- ${PATH_ARG} ${COMMIT_ISH}"
```

### Prompt-injection markers (commit subjects, user-controllable text echoed into LLM context)

Use `INJECTION_MARKERS` regex covering 13+ families (see `plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh`):
- Anthropic/OpenAI/Llama/Mistral system tags (`[SYSTEM]`, `<|im_start|>`, `[INST]`, `<<SYS>>`)
- Chat-template tags (`<|user|>`, `<|assistant|>`, `<|system|>`)
- Markdown system prefix (`---system---`)
- Role-play prefixes (`you are now`, `from now on`)
- Russian-language equivalents (`[СИСТЕМА]`, `игнорируй ... инструкции`, `забудь ... команды`, `теперь ты`)
- Use `re.IGNORECASE | re.UNICODE` flags. Replace matches with `[REDACTED]` (canonical sanitization marker for this marketplace).
- Truncate to 200 chars after sanitization to avoid extending injection beyond expected payload length.

## Memory File Pattern

```markdown
<!-- Memory Metadata
Last updated: YYYY-MM-DD
Last commit: <short-sha> <commit-subject>
Scope: <files/dirs>
Area: <AREA>
-->

# AREA-NN-SLUG

## Purpose
<2-4 sentences: what this memory captures and when to read it.>

## Source Of Truth
- `path/to/file`: why it's the canonical source for this topic.

## Current Behavior / Patterns / Contracts / Invariants
<Fact-only content. Cite file:line or commit SHA for every claim.>

## Change Rules
<When this memory must be updated; what change waves trigger updates.>

## Verification
- `command`: what it proves.

## Cross-References
- Related: `[[AREA-NN-SLUG]]` (use double-brackets; resolves via Serena memory listing). Example: `[[CORE-01-INDEX]]`.
```

Filename: `AREA-NN-SLUG.md` (e.g., `FLOW-01-SDLC.md`). Memory name in Serena: `AREA-NN-SLUG` (without `.md`).

`CORE-01-INDEX.md` is the map and must be updated when a memory is added, deleted, renamed, or split. Numbering is stable - add the next number in an area; do not renumber existing memories unless the task is an explicit taxonomy migration.

## Tag Conventions

- **Plugin tag format**: `<plugin-name>--v<version>` (e.g., `rldyour-flow--v0.2.0`). Created via `claude plugin tag --push` per plugin. `claude plugin tag --push` refuses dirty worktrees or pre-existing tags.
- **Marketplace boundary tag format**: `marketplace--v<version>` (e.g., `marketplace--v0.2.0`). Introduced in 0.2.0 release; pushed manually (not via `claude plugin tag --push`). Marks the aggregate release boundary in `CHANGELOG.md` reference-links block as `[0.2.0]: https://github.com/NDDev-it-com/rldyour-claudecode/releases/tag/marketplace--v0.2.0`. Verified at `CHANGELOG.md` line 576 at HEAD `ebeb062`.
- Tags should be created only after tracked files are clean and `bash scripts/validate_marketplace.sh` passes.

## Commit Message Pattern (Conventional Commits v1.0.0)

```
<type>(<scope>)[!]: <subject - imperative mood, lowercase, no period, ≤72 chars>

<body - wrap at 72 chars; explain WHY, not WHAT. Reference issues/PRs.>

<footers - BREAKING CHANGE: ..., Refs: #N, Co-authored-by: ...>
```

Canonical types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

Scope: component or module name, lowercase (e.g., `scripts`, `hooks`, `agents`, `skill`, `release`).

Use `!` after type/scope or `BREAKING CHANGE:` footer for breaking changes.

**Atomic commits**: one logical change per commit. Separate mechanical refactors from behavior changes. Separate source / docs / Serena knowledge commits when it improves history clarity.

## Verification

- `python3 scripts/validate_agent_tools.py`: proves agent `tools:` allowlist invariants (D15 closure + R4 mitigation).
- `python3 scripts/validate_plugin_versions.py`: proves marketplace ↔ plugin.json version parity.
- `python3 scripts/validate_skill_routing.py`: proves trigger-phrase coverage in SKILL.md descriptions.
- `bash scripts/smoke_hooks.sh`: proves hook script parse + skip flags + outside-git + runtime stdin payload safety.
- `bash scripts/validate_marketplace.sh`: full harness covering all of the above plus frontmatter/JSON/Python/shell syntax checks and MCP runtime drift.

## Cross-References

- Quality philosophy: [[PHILOSOPHY-01-QUALITY-FIRST]].
- Per-rule policy: [[RULES-01-POLICY]].
- Claude Code-specific frontmatter canon: [[CLAUDECODE-01-PLUGIN-CANON]].
- Memory taxonomy: [[CORE-01-INDEX]], [[SERENA-01-MEMORY-SYNC]].
