# Claude Code Surface Adoption

Verified: 2026-06-08

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
| `settings.json` `statusLine` command and status line `COLUMNS`/`LINES` env | 2.1.153 | Adopted | `scripts/install-rldyour-marketplace.sh` stage 8 writes the managed `~/.claude/rldyour-statusline.sh` script and sets `settings.json` `statusLine` so every owner session shows model name, `context_window` used/left percentage, `rate_limits` five-hour/seven-day remaining percentage, and session cost. The script tolerates absent fields (rate limits appear only on subscription accounts after the first API response) and does not depend on `COLUMNS`/`LINES` terminal dimensions. | `scripts/validate_claude_surface_adoption.py` |
| `claude agents` native command and bundled skill autocomplete | 2.1.153 | Adopt implicitly | Existing agent names remain explicit. No config migration is required. | `scripts/validate_agent_tools.py` |
| Opus 4.8 via `opus` and `opus[1m]` aliases | 2.1.154 | Adopted | Keep `ry-explore` on `model: opus[1m]`; on Anthropic API the alias resolves to Opus 4.8, and Claude Code v2.1.154+ is the minimum runtime for that target. | `scripts/validate_claude_surface_adoption.py` |
| Dynamic workflows and `/workflows` | 2.1.154 | Hybrid pending native workflow | Keep `/rldyour-flow:ry-start` as the stable plugin command and route workflow-capable Claude Code sessions to the project `ry-start-workflow` boundary only when a saved `.claude/workflows/` artifact exists and installed-runtime smoke proves it. `plugins/rldyour-flow/skills/ry-start/SKILL.md` remains the fallback because official docs expose saved-workflow creation through the interactive `/workflows` view, not a stable file-format generator. | `scripts/validate_claude_surface_adoption.py`; root `scripts/smoke_claude_ry_start_workflow.py` |
| Streaming tool execution enabled by default | 2.1.154 | Adopt implicitly | No config migration is required; existing hooks and reviewer file-first output must continue to treat tool output as bounded evidence. | `scripts/validate_claude_surface_adoption.py` |
| Piped `claude mcp list`/`get` pending-approval reporting | 2.1.154 | Adopt operationally | Keep MCP approval checks in installed-runtime diagnostics; do not auto-approve `.mcp.json` from static validators. | `scripts/validate_claude_surface_adoption.py` |
| Plugin `defaultEnabled: false` metadata | 2.1.154 | Future | All first-party rldyour plugins remain enabled by the owner marketplace installer; add this only for optional plugins with explicit owner approval. | `scripts/validate_claude_surface_adoption.py` |
| Opus 4.8 thinking-block API hotfix | 2.1.156 | Adopted | Preserve the hotfix introduced in `2.1.156`; pin package/runtime surfaces to Claude Code `2.1.169` and require installed-runtime smoke to report `claude --version` `2.1.169` or newer before declaring Opus 4.8 release readiness. | `scripts/validate_claude_surface_adoption.py` |
| `.claude/skills` direct loading, `claude plugin init`, and `/plugin` autocomplete | 2.1.157 | Adopt operationally | Treat these as compatible with the existing marketplace model; keep first-party release artifacts in marketplace plugins and use `.claude/skills` only for generated/runtime discovery bridges where the control plane owns them. | `scripts/validate_claude_surface_adoption.py` |
| `settings.json` `agent` field honored | 2.1.157 | Adopt implicitly | Keep agent routing explicit in first-party command and skill metadata; no config migration is required because the existing settings surface can now be trusted when installed-runtime smoke exercises it. | `scripts/validate_agent_tools.py`; `scripts/validate_claude_surface_adoption.py` |
| `EnterWorktree` and background-agent worktree fixes | 2.1.157 | Adopt implicitly | Treat as runtime correctness for worktree-aware tasks; keep rldyour worktree cleanup and fullrepo publishing policy in Flow rather than inventing adapter-specific worktree orchestration. | `scripts/validate_claude_surface_adoption.py` |
| `tool_decision` tool parameters with `OTEL_LOG_TOOL_DETAILS` | 2.1.157 | Future | Do not enable high-detail OpenTelemetry tool-parameter logging by default; use only for explicit diagnostics where logs are treated as sensitive evidence and never committed. | `scripts/validate_claude_surface_adoption.py` |
| ultracode keyword trigger setting | Current baseline | Future | Keep `/rldyour-flow:ry-start` and skill routing as the stable owner entrypoint until native saved workflows are created by Claude Code and installed-runtime smoke proves the ultracode trigger behavior. | `scripts/validate_claude_surface_adoption.py` |
| `CLAUDE_CODE_ENABLE_AUTO_MODE=1` provider Auto mode for Bedrock, Vertex, and Foundry | 2.1.158 | Hybrid | Document the environment variable for cloud-provider sessions using current provider-supported Opus Auto mode targets such as Opus 4.8, but keep the owner-local default launcher on `--dangerously-skip-permissions`; no local workflow may require provider Auto mode to be enabled. | `scripts/validate_claude_surface_adoption.py` |
| Claude Code 2.1.159 infrastructure-only release | 2.1.159 | Adopted | Official changelog records internal infrastructure improvements with no user-facing changes; update package/runtime pins and keep existing feature decisions unchanged. | `scripts/validate_runtime_baselines.py`; `scripts/validate_model_baselines.py` |
| Claude Code 2.1.161 secret-redaction and parallel-call isolation | 2.1.161 | Adopt implicitly | Runtime redacts sensitive `claude mcp` command output and isolates parallel tool-call failures. Repository repair scripts still redact captured command output before state logging instead of relying only on runtime behavior. | `scripts/validate_runtime_baselines.py`; `scripts/validate_model_baselines.py`; root `scripts/ry_repair_sync.py --plan --json` |
| Claude Code 2.1.162 agents/tooling and permission fixes | 2.1.162 | Adopted | Treat optional `waitingFor` in `claude agents --json` as runtime output data, allow native `Grep`/`Glob` tool listings on embedded-search builds, keep WebFetch permission rules explicit, and use installed-runtime smoke to prove the local binary. | `scripts/validate_runtime_baselines.py`; `scripts/validate_model_baselines.py`; root `scripts/smoke_claude_ry_start_workflow.py` |
| Managed runtime version bounds | 2.1.163 | Future | `requiredMinimumVersion` and `requiredMaximumVersion` are enterprise/admin managed settings. Do not write them into normal user or project config until this repository owns a managed settings surface; validate only when such a surface exists. | `scripts/validate_claude_surface_adoption.py` |
| `/plugin list` inventory command | 2.1.163 | Adopt operationally | Treat `/plugin list --enabled` and `/plugin list --disabled` as installed-runtime diagnostics. Static release truth remains marketplace and plugin manifests in this repository. | `scripts/validate_claude_surface_adoption.py` |
| Stop/SubagentStop `hookSpecificOutput.additionalContext` | 2.1.163 | Future | Keep Stop hook continuation owned by rldyour-flow until a specific hook needs to add feedback without surfacing as an error. Do not use this as a generic retry channel. | `scripts/validate_claude_surface_adoption.py` |
| Skills literal dollar escape before digits | 2.1.163 | Adopt operationally | When command bodies need a literal `$` before a digit, use the `\$` escape syntax and keep generated skill text ASCII-stable. No current command body migration is required. | `scripts/validate_claude_surface_adoption.py` |
| stdio MCP `CLAUDE_CODE_SESSION_ID` parity on resume | 2.1.163 | Adopt implicitly | Runtime now aligns resumed stdio MCP servers with hook/Bash session IDs; keep MCP config unchanged and rely on installed-runtime smoke when debugging resumed sessions. | `scripts/validate_claude_surface_adoption.py` |
| Claude Code 2.1.165 reliability rollup | 2.1.165 | Adopted | Official changelog records Bug fixes and reliability improvements only. Keep this as historical adopted runtime evidence; the current package/runtime baseline is `2.1.169`. | `scripts/validate_runtime_baselines.py`; `scripts/validate_live_runtime_latest.py` |
| `fallbackModel`, `--fallback-model`, deny rule glob, `SendMessage`, thinking disable, and managed MCP predicates | 2.1.166 | Adopt operationally | Document `fallbackModel` as owner/managed/user runtime policy without committing fallback model IDs; deny rule tool-name globs may include `"*"` while allow rules reject non-MCP globs; relayed `SendMessage` permission requests do not carry user authority; `MAX_THINKING_TOKENS=0` and `--thinking disabled` stay explicit operator overrides; future managed settings validation must cover `allowedMcpServers`, `deniedMcpServers`, and `${VAR}` matching. | `scripts/validate_claude_surface_adoption.py`; root `config/model-policy.json` |
| Claude Code 2.1.167 reliability rollup | 2.1.167 | Adopted | Official changelog records Bug fixes and reliability improvements only. Keep this as historical adopted runtime evidence; the current package/runtime baseline is `2.1.169`. | `scripts/validate_runtime_baselines.py`; `scripts/validate_live_runtime_latest.py` |
| Claude Code 2.1.168 reliability rollup | 2.1.168 | Adopted | Official changelog records Bug fixes and reliability improvements only. Keep this as historical adopted runtime evidence; the current package/runtime baseline is `2.1.169`. | `scripts/validate_runtime_baselines.py`; `scripts/validate_live_runtime_latest.py` |
| Claude Code 2.1.169 package/runtime rollup | 2.1.169 | Adopted | npm registry `latest` and local `claude update` report `2.1.169`; official changelog may lag. Adopt `2.1.169` as the current package/runtime baseline with no new adapter-owned config surface. | `scripts/validate_runtime_baselines.py`; `scripts/validate_live_runtime_latest.py` |

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
surface, and every pinned `2.1.169` runtime surface that affects this
adapter's plugin, skill, hook, or marketplace behavior.
