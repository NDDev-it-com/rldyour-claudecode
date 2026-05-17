<!-- Memory Metadata
Last updated: 2026-05-17
Last commit: 1937f65 docs(adr-0010): macOS egress trust gap accepted
Scope: .claude/CLAUDE.md, AGENTS.md, plugins/*/.claude-plugin/plugin.json, plugins/rldyour-mcps/.mcp.json, plugins/*/skills/*/SKILL.md, plugins/*/agents/*.md, plugins/*/hooks/hooks.json, plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py
Area: CLAUDECODE
-->

# CLAUDECODE-01-PLUGIN-CANON

## Purpose

Current Claude Code plugin/runtime facts that this marketplace relies on. These facts are source-backed by Claude Code documentation and encoded in repository manifests, hooks, and instruction docs.

## Source Of Truth

- `.claude/CLAUDE.md`: Claude Code-native project memory with hook canon, subagent matrix, skill-listing budget, and changelog adoption notes.
- `AGENTS.md`: cross-tool project instructions and current Claude Code compatibility floor.
- `plugins/*/.claude-plugin/plugin.json`: plugin metadata and dependency declarations.
- `plugins/*/skills/*/SKILL.md`: skill frontmatter and trigger descriptions.
- `plugins/*/agents/*.md`: subagent frontmatter and tool permissions.
- `plugins/rldyour-flow/hooks/hooks.json` and `plugins/rldyour-serena-mcp/hooks/hooks.json`: hook declarations.
- `plugins/rldyour-serena-mcp/scripts/analyze_sync_scope.py`: analyzer mapping that targets this memory for plugin component and Claude Code instruction contract changes.

## Current Behavior

- `claude plugin validate` is the canonical manifest validator and is run through `scripts/validate_marketplace.sh`.
- Agent `tools:` allowlist invariants are enforced by `scripts/validate_agent_tools.py` (added Wave 2, commit `b4234c2`), wired unconditionally into `scripts/validate_marketplace.sh` at line 117. The script enforces: (1) built-in tool names in `KNOWN_BUILTIN_TOOLS`; (2) MCP pattern `mcp__plugin_<plugin>_<server>__<tool>` references real plugins and servers; (3) wildcards (`__*`) for non-Serena MCP servers must be in `READ_ONLY_BY_DESIGN_MCPS` (`context7`, `deepwiki`, `grep`, `semgrep`); (4) `SERVERS_WITH_WRITE_TOOLS` (`serena`) must use explicit tool lists, not wildcards, in read-only agent frontmatter. This is the canonical deterministic enforcement point for the TECHDEBT-01-NOW R4 invariant.
- Plugin manifests use SchemaStore `$schema` URLs, but Claude Code validates actual fields through its own plugin validator.
- `dependencies` in `plugin.json` are plugin names OR `{name, version}` objects. The schema was expanded in 0.5.0 commit `7048dbc feat(schema)`: `dependencies` items accept `string` OR `{name, version}` object; component paths (`skills`/`commands`/`agents`/`hooks`) accept `string` OR `array of strings`. Verified at `config/schemas/plugin.json` at HEAD `b5e78d4`. The repo enforces marketplace/manifest version alignment through `scripts/validate_plugin_versions.py`.
- Skills are the primary routing surface; descriptions are Russian-leading with English triggers appended.
- Plugin-shipped subagents use frontmatter for `model`, `effort`, `maxTurns 90 (security 100, ry-explore 90)` in user settings. `0.04` (4%) is chosen over the Anthropic/claudekit-cli baseline `0.03` to accommodate bilingual Russian-leading + English-triggers descriptions averaging ~400 chars per entry across 32 skills (verified in `.claude/CLAUDE.md` line 82 at HEAD).
- `claude plugin tag --push` uses `<plugin-name>--v<version>` tag convention and refuses dirty worktrees or pre-existing tags. Available from v2.1.118+. Verified at `AGENTS.md` line 70 at HEAD `a506526`.
- `claude plugin details <name>` is available from v2.1.139+; v2.1.142 adds LSP visibility.
- Hook `if` filter (v2.1.118+) scopes Bash lifecycle hooks to specific git command patterns. In the 0.5.0 canonical-form rewrite (commit `614bdcf`), the `if` filter was moved from matcher-group level into each inner hook handler (sibling to `type`/`command`/`args`). Both `plugins/rldyour-flow/hooks/hooks.json` and `plugins/rldyour-serena-mcp/hooks/hooks.json` now use exec-form `command: "/bin/bash"` (absolute path, PATH-independent) + `args: ["${CLAUDE_PLUGIN_ROOT}/hooks/X.sh"]` per CC v2.1.139+ recommendation. In the 0.5.1 perf hardening (commit `24d2290`), Serena `PreToolUse:Bash` and `PostToolUse:Bash` changed from 1 broad `Bash(git *)` handler each to 5 narrow handlers per event (`git commit*`, `git merge*`, `git cherry-pick*`, `git rebase*`, `git am*`). Flow uses `Bash(git commit*)` for PostToolUse and 3 `Bash(gh *)` patterns for the new `pre_tool_use_ci_advisory.sh`. Verified at both `hooks.json` files at HEAD `24d2290` (flow with ci_advisory handlers at `22dc9d9`). Total handler count: 12 Serena + 7 flow = 19 handlers in 2 manifests.
- JSON schema validation: 5 schemas in `config/schemas/` (`hooks.json`, `lsp.json`, `marketplace.json`, `mcp.json`, `plugin.json`). Enforced by `scripts/validate_json_schemas.py`, wired into `scripts/validate_marketplace.sh`. At HEAD `b5e78d4` all 5 schemas have `format: "uri-reference"` on `$schema` property (changed from `"uri"` in 0.5.0 commit `7048dbc` so repo-relative `$schema` paths validate per RFC 3986). `config/schemas/hooks.json` rewritten with `$defs` (`matcherGroup`, `hookHandler`); `if` is a `hookHandler` property; full v2.1.142 field set added (`args`, `async`, `asyncRewake`, `shell`, `continueOnBlock`, `url`, `headers`, `allowedEnvVars`, `server`, `tool`, `input`, `prompt`, `model`, `agent`, `once`); `additionalProperties: false` keeps schema drift surfaced. Verified at `config/schemas/hooks.json` and `config/schemas/plugin.json` at HEAD `b5e78d4`.
- `sync_contract` YAML block added to both `AGENTS.md` (line 9) and `.claude/CLAUDE.md` (line 5) at HEAD `a506526`. 14 shared claims enforced by `scripts/validate_instruction_sync.py` (reports 0 drift). `CONTRACT_BLOCK_RE` regex at `scripts/validate_instruction_sync.py:45` tolerates `\s*` before closing `-->` (pattern: `r"<!--\s*sync_contract:\s*\n(.*?)\n\s*-->"`, added in `e9d5424`, closes INFO-3). Verified via `python3 scripts/validate_instruction_sync.py` at HEAD `a506526`.
- Additional validators wired into `scripts/validate_marketplace.sh`: `validate_docs_canon.py` (0 drift across 46 target files), `validate_text_hygiene.py`, `validate_skill_allowed_tools.py`, `validate_release_state.py`, `validate_instruction_sync.py`. `generate_inventory.py` is a standalone reporting script. Verified at HEAD `a506526` (commit `test(harness): add 6 validators`).
- `config/text-hygiene-allowlist.json` (added `f02235a`, wave 0.4.4): externalises em-dash / en-dash / BIDI exemption sets from `scripts/validate_text_hygiene.py`. `load_allowlists(root)` function loads from the JSON file with malformed-JSON fallback to `_DEFAULT_ALLOWLIST_EM/EN/BIDI`. Config absent means compiled-in defaults apply (backward-compat for fresh checkouts). Verified at `config/text-hygiene-allowlist.json` and `scripts/validate_text_hygiene.py:66-93` at HEAD `6f07fe8`.
- `.github/workflows/validate.yml` Claude CLI install step reads version dynamically from `package.json` `devDependencies['@anthropic-ai/claude-code']` via a dedicated step with `$GITHUB_OUTPUT` (changed in `8a26e5a`); Dependabot npm bumps now auto-propagate without a manual hardcoded string update. Verified at `.github/workflows/validate.yml` lines 55-65 at HEAD `a04c6eb`.
- `scripts/validate_instruction_sync.py` and `scripts/validate_json_schemas.py` SKIP messages print to stdout (not stderr) for stream consistency with sibling validators (changed in `8b9a6c6`). Verified at `scripts/validate_instruction_sync.py:83,87,94` and `scripts/validate_json_schemas.py:61` at HEAD `a04c6eb`.
- `scripts/validate_docs_canon.py` uses `max(30, len(knob) + 15)` window heuristic (changed from fixed `start - 30` in `8b9a6c6`) to correctly detect long knob names like `maxSkillDescriptionChars` in context. Regression covered by `tests/test_validate_docs_canon.py::TestValidateDocsCanon::test_long_knob_window_expands_dynamically`. Verified at `scripts/validate_docs_canon.py:88` at HEAD `a04c6eb`.
- `scripts/validate_boundaries.py` enforces 4 structural invariants against `config/marketplace-policy.json`: (1) exactly one plugin owns `.mcp.json` (mcp_owner match); (2) `hooks/hooks.json` owners match policy `hook_owners` set exactly; (3) `plugin.json` `name` field matches directory name; (4) `plugin.json` `dependencies` matches `plugin_dependencies[<plugin>]` in policy. SKIPs gracefully when `config/marketplace-policy.json` is absent. Closes ADR-0006 gap (the "not yet implemented" language in the Confirmation section was retired at HEAD `924256c`). Wired into `scripts/validate_marketplace.sh` and `.github/workflows/validate.yml` as a mandatory (non-advisory) step. Verified at `scripts/validate_boundaries.py` at HEAD `924256c`.
- `.github/workflows/validate.yml` `syntax-checks` job gained 2 advisory steps at HEAD `924256c` (commit `72c5665`): "Ruff lint (advisory)": `ruff check scripts/ plugins/` with `continue-on-error: true`; "Pyright type check (advisory)": project-wide `pyright` with `continue-on-error: true`. `pip install` step expanded to include `ruff>=0.7`, `pyright>=1.1`, `pyyaml>=6`, `pytest>=8` (resolves runtime/test imports under static analysis). At HEAD `924256c` both gates pass: 0 ruff errors and 0 pyright errors/warnings across `scripts/`, `plugins/`, `tests/`. Verified at `.github/workflows/validate.yml` lines 215-230 at HEAD `924256c`.
- `scripts/_mcp_parse.py` shared module (added commit `cd13d0a`): single source of truth for parsing `mcp__plugin_<plugin>_<server>__<tool_or_star>` references. `split_mcp_ref(ref, plugins) -> tuple[str, str, str] | None` uses longest-known-prefix match (handles hyphen-separated plugin names) with `rpartition('_')` fallback for unknown plugins. Imported by both `scripts/validate_skill_allowed_tools.py` and `scripts/validate_agent_tools.py`. `pyproject.toml` sets `extraPaths = ["scripts"]` so Pyright resolves `from _mcp_parse import ...`. `tests/test_mcp_parse.py` (9 tests) covers the shared parser directly. Verified at `scripts/_mcp_parse.py` at HEAD `924256c`.
- Official Claude Code MCP docs still show the GitHub remote MCP endpoint as an example; this repository uses local stdio `github-mcp-server` to keep the marketplace self-contained without dependence on `api.githubcopilot.com/mcp/`. A standard GitHub PAT with `repo` + `read:org` scopes is sufficient; no Copilot subscription is required. Rationale source: `plugins/rldyour-mcps/README.md` line 28 at HEAD.
- Repository transferred from `rldyourmnd/rldyour-claude` to `NDDev-it-com/rldyour-claudecode` (private) in Wave 5. Marketplace slug renamed from `rldyour-claude` to `rldyour-claudecode` in `.claude-plugin/marketplace.json`. All 9 plugin `plugin.json` files updated with new `homepage` and `repository` URLs pointing to `github.com/nddev-it-com/rldyour-claudecode`. Local origin remote is now `git@github.com:NDDev-it-com/rldyour-claudecode.git`. Verified at `.claude-plugin/marketplace.json` and `plugins/rldyour-mcps/.claude-plugin/plugin.json` at HEAD `334fe09`.

## Invariants

- Keep Claude Code-deep facts in `.claude/CLAUDE.md`; keep cross-tool concise rules in `AGENTS.md`.
- Do not reduce `.claude/CLAUDE.md` to only `@AGENTS.md`; both are first-class and optimized for different CLIs.
- Do not add undocumented `.mcp.json` keys such as `startup_timeout_sec` or `tool_timeout_sec`; use documented env vars where needed.
- When current Claude Code behavior changes, update `.claude/CLAUDE.md`, relevant plugin docs, and this memory from verified docs or runtime evidence.
- Reviewer protocol hardening is treated as a compatibility-sensitive convention: any change to marker text, report directory paths, severity enums, or required orchestrator reads must update `reviewer-protocol.md`, `flow-*` skills, and this memory atomically.

## Cross-References

- Marketplace plugin boundaries and dependency graph: [[CORE-02-MARKETPLACE]].
- MCP server registry (13 pinned servers): [[MCP-01-TRANSPORT]].
- Hook lifecycle canon: [[HOOKS-01-LIFECYCLE]].
- Memory sync agent (flow-memory-sync frontmatter): [[SERENA-01-MEMORY-SYNC]].
- Instruction docs policy: [[DOCS-01-INSTRUCTIONS]].
- Agent tools patterns (explicit allowlist): [[PATTERNS-01-CANONICAL]] Agent Frontmatter.
- Open risks (R4 wildcard, R5 divergence): [[TECHDEBT-01-NOW]].
- Release validation (validate_marketplace.sh): [[RELEASE-01-VALIDATION]].

## Verification

- `bash scripts/validate_marketplace.sh`: validates plugin manifests, skill/agent/command frontmatter, and the Serena taxonomy smoke.
- `python3 scripts/validate_instruction_docs.py --require-agent-docs`: validates `AGENTS.md` and `.claude/CLAUDE.md` presence and line budgets.
- `claude plugin validate .`: validates marketplace manifest through the Claude Code CLI.
- `bash scripts/smoke_serena_memory_taxonomy.sh`: verifies that plugin component and agent-instruction changes target this memory.
