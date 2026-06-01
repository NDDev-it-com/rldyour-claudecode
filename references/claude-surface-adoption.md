# Claude Code Surface Adoption

Verified: 2026-06-01

Source of truth:
- Runtime baseline: `references/claude-baseline.json`
- Runtime package pin: `package.json`
- Official changelog: `https://code.claude.com/docs/en/changelog`

## Decisions

| Surface | Introduced | Decision | Implementation | Validator |
| --- | --- | --- | --- | --- |
| `disallowed-tools` skill/slash-command frontmatter | 2.1.152 | Adopt selectively | Use only for read-only/review/reporting routes where removing mutation tools reduces accidental capability. Keep positive `allowed-tools` routing as the default because it is easier to validate against plugin MCP namespaces. | `scripts/validate_skill_allowed_tools.py` |
| `/reload-skills` | 2.1.152 | Adopt operationally | Document as the operator command after plugin, skill, or marketplace updates. Do not call it from static validators. | `scripts/validate_claude_surface_adoption.py` |
| `SessionStart.reloadSkills` hook output | 2.1.152 | Future | Adopt only when a startup hook can cheaply prove that skill directories changed. Blind reload on every session start is unnecessary churn. | `scripts/validate_claude_surface_adoption.py` |
| `MessageDisplay` hook event | 2.1.152 | Intentionally unused | No current redaction or display-observability requirement justifies adding a high-volume hook. | `scripts/validate_claude_surface_adoption.py` |
| `/code-review --fix` and `/simplify` integration | 2.1.152 | Future | Keep rldyour reviewer tracks as the canonical review workflow until parity with file-first reviewer reports is designed and validated. | `scripts/validate_claude_surface_adoption.py` |
| `skipLfs` for `github`/`git` plugin marketplace sources | 2.1.153 | Future | This adapter does not currently use Git LFS-heavy plugin marketplace sources. Add only when marketplace source installs prove LFS download cost or failures. | `scripts/validate_claude_surface_adoption.py` |
| npm auto-update diagnostics and `/doctor` update reporting | 2.1.153 | Adopt operationally | Keep the package pin in `package.json`; use `/doctor` and `claude --version` in installed-runtime checks when local update failures are suspected. | `scripts/validate_release_state.py` |
| status line `COLUMNS`/`LINES` env | 2.1.153 | Future | No custom status-line integration currently depends on terminal dimensions. | `scripts/validate_claude_surface_adoption.py` |
| `claude agents` native command and bundled skill autocomplete | 2.1.153 | Adopt implicitly | Existing agent names remain explicit. No config migration is required. | `scripts/validate_agent_tools.py` |
| Opus 4.8 via `opus` and `opus[1m]` aliases | 2.1.154 | Adopted | Keep `ry-explore` on `model: opus[1m]`; on Anthropic API the alias resolves to Opus 4.8, and Claude Code v2.1.154+ is the minimum runtime for that target. | `scripts/validate_claude_surface_adoption.py` |
| Dynamic workflows and `/workflows` | 2.1.154 | Hybrid pending native workflow | Keep `/rldyour-flow:ry-start` as the stable plugin command and route workflow-capable Claude Code sessions to the project `ry-start-workflow` boundary only when a saved `.claude/workflows/` artifact exists and installed-runtime smoke proves it. `plugins/rldyour-flow/skills/ry-start/SKILL.md` remains the fallback because official docs expose saved-workflow creation through the interactive `/workflows` view, not a stable file-format generator. | `scripts/validate_claude_surface_adoption.py`; root `scripts/smoke_claude_ry_start_workflow.py` |
| Streaming tool execution enabled by default | 2.1.154 | Adopt implicitly | No config migration is required; existing hooks and reviewer file-first output must continue to treat tool output as bounded evidence. | `scripts/validate_claude_surface_adoption.py` |
| Piped `claude mcp list`/`get` pending-approval reporting | 2.1.154 | Adopt operationally | Keep MCP approval checks in installed-runtime diagnostics; do not auto-approve `.mcp.json` from static validators. | `scripts/validate_claude_surface_adoption.py` |
| Plugin `defaultEnabled: false` metadata | 2.1.154 | Future | All first-party rldyour plugins remain enabled by the owner marketplace installer; add this only for optional plugins with explicit owner approval. | `scripts/validate_claude_surface_adoption.py` |
| Opus 4.8 thinking-block API hotfix | 2.1.156 | Adopted | Preserve the hotfix introduced in `2.1.156`; pin package/runtime surfaces to Claude Code `2.1.159` and require installed-runtime smoke to report `claude --version` `2.1.159` or newer before declaring Opus 4.8 release readiness. | `scripts/validate_claude_surface_adoption.py` |
| `.claude/skills` direct loading, `claude plugin init`, and `/plugin` autocomplete | 2.1.157 | Adopt operationally | Treat these as compatible with the existing marketplace model; keep first-party release artifacts in marketplace plugins and use `.claude/skills` only for generated/runtime discovery bridges where the control plane owns them. | `scripts/validate_claude_surface_adoption.py` |
| `settings.json` `agent` field honored | 2.1.157 | Adopt implicitly | Keep agent routing explicit in first-party command and skill metadata; no config migration is required because the existing settings surface can now be trusted when installed-runtime smoke exercises it. | `scripts/validate_agent_tools.py`; `scripts/validate_claude_surface_adoption.py` |
| `EnterWorktree` and background-agent worktree fixes | 2.1.157 | Adopt implicitly | Treat as runtime correctness for worktree-aware tasks; keep rldyour worktree cleanup and fullrepo publishing policy in Flow rather than inventing adapter-specific worktree orchestration. | `scripts/validate_claude_surface_adoption.py` |
| `tool_decision` tool parameters with `OTEL_LOG_TOOL_DETAILS` | 2.1.157 | Future | Do not enable high-detail OpenTelemetry tool-parameter logging by default; use only for explicit diagnostics where logs are treated as sensitive evidence and never committed. | `scripts/validate_claude_surface_adoption.py` |
| workflow keyword trigger setting | 2.1.157 | Future | Keep `/rldyour-flow:ry-start` and skill routing as the stable owner entrypoint until native saved workflows are created by Claude Code and installed-runtime smoke proves the trigger behavior. | `scripts/validate_claude_surface_adoption.py` |
| `CLAUDE_CODE_ENABLE_AUTO_MODE=1` provider Auto mode for Bedrock, Vertex, and Foundry | 2.1.158 | Hybrid | Document the environment variable for cloud-provider sessions using current provider-supported Opus Auto mode targets such as Opus 4.8, but keep the owner-local default launcher on `--dangerously-skip-permissions`; no local workflow may require provider Auto mode to be enabled. | `scripts/validate_claude_surface_adoption.py` |
| Claude Code 2.1.159 infrastructure-only release | 2.1.159 | Adopted | Official changelog records internal infrastructure improvements with no user-facing changes; update package/runtime pins and keep existing feature decisions unchanged. | `scripts/validate_runtime_baselines.py`; `scripts/validate_model_baselines.py` |

## AskUserQuestion And Owner Full-Auto

The owner-standard Claude launcher remains `claude --dangerously-skip-permissions`.
That bypasses permission prompts by design. Claude Code Auto mode is a separate
native mode where a classifier model can reduce permission prompts, but it has
plan/account/model requirements and does not create a repository-controlled way
to answer semantic `AskUserQuestion` prompts on the owner's behalf.

For rldyour workflows, semantic ambiguity is handled by the main model or the
reviewer/research agents before mutation. Permission prompts are handled by the
owner-standard bypass launcher. Do not add a custom auto-answer hook that
fabricates owner decisions.

## Validation

`scripts/validate_claude_surface_adoption.py` requires this file to contain an
explicit decision for every runtime surface listed in
`references/claude-baseline.json`, every Claude Code `2.1.154` workflow/model
surface, and every pinned `2.1.159` runtime surface that affects this
adapter's plugin, skill, hook, or marketplace behavior.
