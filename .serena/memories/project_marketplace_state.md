# rldyour-claude marketplace state

Last commit: 5e1c3d4 (feat(commands): bilingual descriptions for /help discoverability, 2026-05-08).
Four May-2026 best-practice waves applied:
- optimize/may-2026-best-practices: 6 commits 3fe9005..2e22652 (merged to main)
- docs/canonical-may2026: 1 commit ca13470 (merged to main)
- polish/deferred-findings: 3 commits 3ce7970..f23765d (merged to main)
- feat/memory-sync-subagent: 1 commit 772f6e8 (current branch, NOT YET merged)
First three feature branches deleted after fast-forward merge.
Marketplace name: `rldyour-claude`. Repo: github.com/rldyourmnd/rldyour-claude (private).

## Layered architecture (verified)

1. Transport — `rldyour-mcps` (single owner of `.mcp.json`, 13 pinned servers).
2. Semantic code — `rldyour-serena-mcp` (depends on `rldyour-mcps`).
3. SDLC orchestrator — `rldyour-flow` (depends on `rldyour-mcps`, `rldyour-serena-mcp`).
4. Domain — `rldyour-explore`, `rldyour-security`, `rldyour-browser`, `rldyour-design`,
   `rldyour-lsps` (each depends on `rldyour-mcps`).
5. Engineering rules — `rldyour-rules` (depends on `rldyour-mcps`).

Cross-plugin `dependencies` declared in plugin.json `dependencies: [...]` array.

## Hard boundaries

- Only `rldyour-mcps` declares `.mcp.json`.
- Only `rldyour-flow` and `rldyour-serena-mcp` declare `hooks.json`.
- One domain per plugin; cross-plugin overlap forbidden.
- `rldyour-browser` is a skills-only consumer of transport (depends on `rldyour-mcps` only).
- `rldyour-design` depends on `rldyour-mcps` and `rldyour-browser` (declared in `plugins/rldyour-design/.claude-plugin/plugin.json` since commit 25624e5 — design-validation skill delegates to rldyour-browser:browser-validation).

## Hooks lifecycle (coordination contract)

| Event | Owner | Script |
|---|---|---|
| UserPromptSubmit | rldyour-serena-mcp | hooks/user_prompt_submit.sh |
| PreToolUse:Bash | rldyour-serena-mcp | hooks/prepare_auto_sync.sh |
| PostToolUse:Bash | rldyour-serena-mcp | hooks/mark_sync_required.sh |
| PostToolUse:Bash | rldyour-flow | hooks/post_tool_use_commit_advice.sh |
| SessionStart | rldyour-flow | hooks/session_start_context.sh |
| Stop | rldyour-serena-mcp | hooks/stop_memory_sync.sh |
| Stop | rldyour-flow | hooks/stop_post_task_sync.sh |

`flow.stop_post_task_sync.sh` waits for `serena_current=true` from the Serena Stop hook
before running. Loop guard: `.serena/.flow_sync_marker` fingerprint of (HEAD, dirty,
ahead/behind, branch, Serena freshness). If `stop_hook_active=true` and same fingerprint,
hook allows stop.

All hooks advisory: emit `hookSpecificOutput.additionalContext`, exit 0 on errors.
Skip flags: `RLDYOUR_SKIP_FLOW_SESSION_CONTEXT`, `RLDYOUR_SKIP_STOP_GATES`,
`RLDYOUR_SKIP_FLOW_SYNC`.

## Subagent matrix (8 total)

Reviewer (rldyour-flow/agents/flow-*-review.md): `model: sonnet`, `effort: high`,
`maxTurns: 36` (security: `42`), `disallowedTools: [Edit, Write, NotebookEdit]`.
6 agents with distinct colors:

| Agent | maxTurns | color |
|---|---|---|
| flow-architecture-review | 36 | blue |
| flow-quality-review | 36 | green |
| flow-consistency-review | 36 | purple |
| flow-integration-review | 36 | orange |
| flow-verification-review | 36 | pink |
| flow-security-review | 42 | red |

`maxTurns` was raised from 12-14 to 36/42 (×3) after observing that MCP-rich
toolsets (Serena+Context7+DeepWiki+Grep) consume turns on tool plumbing.
Tight 12-14 limits effectively gave only 4-7 reasoning turns.

Research (rldyour-explore/agents/ry-explore.md): `model: opus[1m]`, `effort: max`,
`maxTurns: 90` (was 30), `disallowedTools: [Edit, Write, NotebookEdit]`, `color: cyan`.
Triggered via `/rldyour-explore:ry-explore` slash command (`context: fork`).

Memory sync (rldyour-serena-mcp/agents/flow-memory-sync.md, added 772f6e8): `model: sonnet`,
`effort: high`, `maxTurns: 36`, `disallowedTools: [Edit, Write, NotebookEdit]`, `color: yellow`.
Plugin-shipped subagent invoked from main session via Agent tool (subagent_type
`rldyour-serena-mcp:flow-memory-sync`). Narrow tool access — Serena memory tools
(write_memory, edit_memory, etc.) + read-only Bash/Read/Grep/Glob; cannot mutate
arbitrary files. Anti-hallucination guards in body: source-of-truth hierarchy
(code > tests > git diff > existing memories), citation requirement per claim,
removal-first principle for unverifiable claims. Receives diff context as Agent
prompt and runs commit_serena_knowledge.sh internally. Plugin agents on Claude
Code v2.1.x are loaded at session start — after creating/updating an agent file,
restart the session for the agent to appear in `Agent` tool subagent_type list.

## MCP transport (rldyour-mcps/.mcp.json)

13 pinned servers (8 stdio, 5 HTTP); all dead `startup_timeout_sec`/`tool_timeout_sec`
keys removed (commit 0d78443). HTTP servers: deepwiki, grep, figma, openai-docs, github.

- serena: `serena-agent==1.2.0`, `--context=agent`, web dashboard disabled,
  `alwaysLoad: true` (v2.1.121+) — eager startup since Serena drives every
  UserPromptSubmit hook.
- sequential-thinking: `@modelcontextprotocol/server-sequential-thinking@2025.12.18`.
- playwright: `@playwright/mcp@0.0.74` headless.
- chrome-devtools: `chrome-devtools-mcp@0.25.0` headless isolated.
- context7: `@upstash/context7-mcp@2.2.4`. Requires `CONTEXT7_API_KEY`.
- deepwiki: HTTP `mcp.deepwiki.com/mcp`.
- grep: HTTP `mcp.grep.app`.
- semgrep: `semgrep==1.161.0`.
- shadcn: `shadcn@4.7.0`.
- dart-flutter: `dart mcp-server --force-roots-fallback`.
- figma: HTTP `mcp.figma.com/mcp`.
- openai-docs: HTTP `developers.openai.com/mcp`.
- github: HTTP `api.githubcopilot.com/mcp/`, `Authorization: Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}`.
  Switched from stdio (`github-mcp-server stdio`) to HTTP transport in commit 47387ee;
  matches `anthropics/claude-plugins-official` canonical pattern (commit 76b35e9).

Timeouts via env: `MCP_TIMEOUT`, `MCP_TOOL_TIMEOUT`, `MAX_MCP_OUTPUT_TOKENS`,
`MCP_CONNECTION_NONBLOCKING`.

## Serena MCP context

`--context=agent` is canonical for Claude Code in Serena 1.2.0 (set in commit 482c421).
Exposes 45 of 46 Serena tools (only excludes the redundant `initial_instructions`
tool that Claude Code loads via ToolSearch).

Serena 1.2.0 has no `claude-code` context. The `serena prompts print-cc-system-prompt-override`
command prints a Claude Code-specific system prompt that maps Read/Edit/Glob/Grep
to Serena's symbolic tools as PRIMARY — used when running Claude Code with
`--system-prompt` flag.

Serena memory location: project-level via `.serena/memories/` (managed by
`rldyour-serena-mcp`).

## Fullrepo branch policy

Agent-only files live on `fullrepo` only. `AGENT_ONLY_PATTERNS` in
`plugins/rldyour-flow/scripts/fullrepo_sync.py`:

- root: AGENTS.md, CLAUDE.md, REVIEW.md, GEMINI.md, QWEN.md, .cursorrules,
  .windsurfrules, .aider*
- directories: .claude/**, .cursor/rules/**, .gemini/**, .roo/**, .windsurf/**,
  .openhands/**, .agents/{skills,commands,hooks}/**
- .github: copilot-instructions.md, instructions/**, prompts/**
- .serena: project.yml, memories/**, plans/**, research/**, newproj/**, deploy/**

All other-CLI agent-only directory globs were trimmed in commit 5feae39; this
marketplace targets Claude Code only.

`fullrepo_sync.py` subcommands: `--bootstrap-init`, `--restore`, `--migrate-main`,
`--publish` (uses `--force-with-lease`), `--status-json`.

## LSP known limitations (added afabf41, 2026-05-08)

- `extensionToLanguage` only: Claude Code `.lsp.json` schema does not support filename-based
  routing. Files without extension (`Dockerfile`, `Containerfile`, `Makefile`, `CMakeLists.txt`,
  `Gemfile`, `Procfile`, `Jenkinsfile`) cannot route to any LSP server.
  Tracked: anthropics/claude-code#47748 (OPEN `area:lsp` + `enhancement`, filed 2026-04-14).
- Compound extensions unsupported (e.g. `.spec.ts` routes only to last segment).
  Closed `not_planned` in anthropics/claude-code#15785 (2026-02-14).
- docker entry in `.lsp.json` is marked **Degraded** in lsp-server-matrix.md:
  only `.dockerfile` extension routes; bare `Dockerfile`/`Containerfile` falls back to text.
  (Source: `plugins/rldyour-lsps/references/lsp-server-matrix.md` and
  `plugins/rldyour-lsps/references/install-profiles.md` Known limitations section.)

## CI

`.github/workflows/validate.yml` (commit bbb934b) runs on push, pull_request, and
workflow_dispatch:
1. `claude plugin validate .` + per-plugin validation via `npm install -g @anthropic-ai/claude-code`.
2. Syntax checks: JSON manifests, Python AST, bash -n, frontmatter presence.

## Conventions

- User-facing Russian; English repo artifacts.
- Skill `description` Russian-leading; explicit bilingual pattern since wave 12 (ef1b819):
  `"<purpose>. Используй для: <RU triggers>. EN triggers: <EN triggers>."` applied to all 32 skills.
  Slash command descriptions also bilingual since 5e1c3d4 (7 commands updated).
- Conventional Commits, ≤72 chars, single scope `(scope):`.
- Atomic commits; secrets/runtime/browser artifacts never committed.
- All MCP server versions pinned (stdio `==X.Y.Z`; HTTP by URL).
- Min Claude Code: **v2.1.111+** for `model: opus[1m]` bracket syntax in agents.

## Skill-listing optimizations (2026-05-08)

- 15 skills declare explicit `allowed-tools` (verified at HEAD via grep): serena-code-workflow,
  serena-memory-sync, tech-research, web-research, browser-validation, browser-debug,
  lsp-routing, lsp-health-check, lsp-setup, serena-lsp-integration, figma-to-code,
  design-validation, design-system-implementation, ry-design (added Serena wildcard in 1d33c25),
  flow-post-task-sync (added Bash/Read/Grep/Glob in 1d33c25). MCP wildcard form
  `mcp__plugin_rldyour-mcps_<server>__*` validated via `claude plugin validate`.
- 2 skills marked `disable-model-invocation: true` (slash-only): ry-deploy, ry-newp.
- User-side fix in `~/.claude/settings.json`: `skillListingBudgetFraction: 0.03`
  (v2.1.129+) — default 1% truncated 37/70 skill descriptions.
- Plugin.json `$schema` URL switched to `json.schemastore.org/claude-code-plugin-manifest.json`
  (canonical per docs).

## Recent commit history (a115b86..HEAD)

main (a115b86..bbb934b):
- 482c421 feat(mcps): switch Serena MCP --context to agent
- 5feae39 refactor(flow,serena-mcp): trim other-CLI globs and rename agents-doc constant
- 131c57b docs: reframe AGENTS.md as cross-tool root file
- 0d78443 chore(mcps): drop unsupported timeout fields from .mcp.json
- bcfa726 feat: declare cross-plugin dependencies in plugin.json
- bbb934b ci: add claude plugin validate workflow

May-2026 best-practices wave (bbb934b..2e22652, merged 2026-05-08):
- 3fe9005 refactor(agents): unify reviewer effort/maxTurns/colors and triple ry-explore turns
- 2631322 chore(plugins): switch plugin.json $schema to schemastore canonical
- db18b8a feat(mcps): mark serena MCP server alwaysLoad
- 0f7362b feat(skills): add allowed-tools to skills with explicit toolset
- 652a49d feat(flow): mark ry-deploy and ry-newp as slash-only
- 2e22652 docs(flow): align reviewer-protocol with new effort/maxTurns/color matrix

Canonical docs wave (2e22652..ca13470, merged 2026-05-08, agent-only files
not in git history but published to fullrepo):
- AGENTS.md trimmed: removed Skill Listing Budget section (Claude Code-specific),
  added cross-ref + maintainer/living-doc HTML comments. 150 → 152 lines.
- .claude/CLAUDE.md aggressively rewritten: removed Slash Commands table,
  MCP Transport, Architecture Layers, Fullrepo Branch Policy (full duplicates
  with AGENTS.md). Kept Plugins And Components, Subagent Frontmatter Matrix,
  Hooks Lifecycle (with Timeout column), Skill Listing Budget, Hook Events Canon,
  Engineering Conventions, Don't, Done Criteria. 206 → 123 lines (-40%).
- ca13470 fix(explore): align ry-explore body maxTurns:90 with frontmatter
  (caught by flow-integration-review).
- All 5 RLDYOUR_SKIP_* flags now documented (was 3).

Polish wave (ca13470..f23765d, merged 2026-05-08):
- 3ce7970 feat(design): allowed-tools added to 4 of 5 design skills
  (figma-to-code, design-system-implementation, design-validation, ry-design).
  fsd-frontend-architecture intentionally without — pure reference skill.
- 7e32688 feat(audit): disable-model-invocation:true on ry-rules-review and
  ry-sec-review (audit operations are deliberate). Now 4 skills are slash-only:
  ry-deploy, ry-newp, ry-rules-review, ry-sec-review. ry-init/ry-start/ry-review/
  ry-design intentionally retain auto-trigger as orchestrators.
- f23765d docs(flow): documented maxTurns:36/42 rationale in reviewer-protocol.md
  (security gets +6 turns for variant-hunt sweep).
- .claude/CLAUDE.md grew by 1 line (124 total) documenting the validated pattern
  of mixing built-in tools and MCP wildcards in allowed-tools.

Memory-sync subagent wave (f23765d..772f6e8, merged 2026-05-08):
- 772f6e8 feat(serena-mcp): add flow-memory-sync subagent for fact-only sync.
  NEW plugins/rldyour-serena-mcp/agents/flow-memory-sync.md (sonnet/high/36/yellow,
  anti-hallucination contract in body — citation per claim, source-of-truth
  hierarchy code > tests > git diff > existing memories, removal-first principle).

LSP registration wave (8123e46..36a1788, branches feat/lsp-pyright-registration
+ feat/lsp-full-matrix):
- 941e179 feat(lsps): register pyright via .lsp.json for native CC LSP support
  — bootstrap fix for the original pyright-lsp recommendation.
- 36a1788 feat(lsps): register full LSP matrix in .lsp.json (15 languages).
  - plugins/rldyour-lsps/.lsp.json now contains 15 entries verified against
    user's PATH (~/.local/bin,
    /opt/homebrew/bin, ~/.bun/bin, ~/.cargo/bin paths):
    python (pyright-langserver), typescript (typescript-language-server,
    handles js/jsx/mjs/cjs too), rust (rust-analyzer), dart
    (dart language-server --protocol=lsp), go (gopls), cpp (clangd for
    .c/.h/.cc/.cpp/.cxx/.c++/.hh/.hpp/.hxx/.h++/.m/.mm), qml (qmlls),
    yaml (yaml-language-server), docker (docker-language-server start),
    html (vscode-html-language-server), css (vscode-css-language-server,
    handles scss/sass/less), bash (bash-language-server start), json
    (vscode-json-language-server, handles jsonc), toml (taplo lsp stdio),
    markdown (marksman server).
  - Each entry uses canonical schema: command + args + extensionToLanguage
    + transport=stdio + initializationOptions + settings + maxRestarts=3.
  - Schema sourced from Piebald-AI/claude-code-lsps and
    code.claude.com/docs/en/plugins-reference.
  - Intentional omissions: vtsls (would conflict with typescript-language-server
    for same extensions; invoke explicitly via lsp-routing skill if needed),
    ruff (lint companion, not full LSP; invoke via lsp-routing skill when
    applicable). basedpyright not installed locally; pyright is sufficient.
  - Result: CC stops recommending per-language LSP plugins (pyright-lsp etc)
    for any of the 15 covered languages — uses user's pre-installed servers
    directly. Servers not on PATH are silently skipped (no error).
- 38f4cc6 fix(lsps): canonical alignment after cross-check vs Piebald-AI and
  boostvolt reference marketplaces. Two surgical fixes:
  - dart: add "startupTimeout": 60000 (Piebald-AI canonical) for slow Dart/Flutter
    boot.
  - bash: add ".ksh": "shellscript" to extensionToLanguage (boostvolt canonical).
  Other 13 entries verified exact match with canonical (pyright/html/css/rust/
  go/cpp/typescript/yaml plus 5 unique-but-correct: docker/json/toml/markdown/qml).
  Live startup tested for marksman, taplo, bash-language-server,
  docker-language-server, vscode-json-language-server.
- 750a798 fix(lsps): align typescript/docker/cpp with canonical extensions
  after ry-explore deep verify against Anthropic Official marketplace,
  Helix languages.toml, nvim-lspconfig, Piebald-AI, boostvolt configs:
  - typescript: add .cts and .mts (Anthropic Official has both; modern
    ESM/CommonJS TypeScript module variants).
  - docker: add `.hcl`: "dockerbake" (docker-language-server Bake language ID; removed in
    ba2592a as mis-routing fix — see plugin-dev validation wave below).
  - cpp: add --background-index arg (Anthropic Official clangd config has
    it for performance); add .C/.H uppercase variants (Unix/macOS convention),
    .cu/.cuh (CUDA), .cppm (C++20 modules).
  README.md amended with architectural caveats:
  - Dockerfile (no extension) cannot be mapped via extensionToLanguage
    schema — it's a fundamental Claude Code LSP-tool limitation.
  - MDX parsed as plain markdown by marksman; JSX features need dedicated
    mdx-analyzer.
  - Compose files (.yml/.yaml) handled by yaml-language-server, not docker —
    extensionToLanguage cannot map one extension to two LSPs.
  Final verdict: 12/15 entries exact-match canonical; 3 received functional
  fixes; 0 broken. Sources cross-checked: Anthropic Official, SchemaStore,
  Helix, nvim-lspconfig, Piebald-AI, boostvolt, plus per-server official
  docs (microsoft/pyright, dart-lang/sdk, golang/tools, clangd/clangd,
  qt/qtdeclarative, redhat-developer/yaml-language-server,
  docker/docker-language-server, bash-lsp, artempyanykh/marksman,
  tamasfe/taplo, vscode-langservers-extracted).

Operations harness wave (a851d99..8123e46, branch feat/codex-port-wave):
- adb0bc1 docs: root public files (README.md, CHANGELOG.md, VERSION 0.1.0, LICENSE MIT).
- ff14160 feat(ops): operations harness — scripts/{validate_marketplace.sh,
  validate_plugin_versions.py, validate_instruction_docs.py,
  validate_skill_routing.py, check_mcp_runtime_versions.py, release_manifest.py,
  collect_diagnostics.sh, sync_fullrepo_branch.sh} + config/{mcp-runtime-versions.env,
  skill-routing-policy.json with 15 deterministic Russian/English routing tests}.
- 22b8d5b feat(ci): scheduled dependency-check.yml workflow + statusMessage on
  every hook handler in both plugins + extended validate.yml (now runs
  validate_plugin_versions, check_mcp_runtime_versions, validate_skill_routing).
- 4005831 docs(plugins): per-plugin README.md across all 9 plugins.
- 2082b5d docs: docs/{release-process, rollback-restore, dependency-updates,
  observability}.md reference set.
- 8123e46 feat(ops): smoke tests — scripts/{smoke_hooks.sh, smoke_mcp_runtime.sh,
  smoke_fullrepo_sync.sh, bootstrap_check.sh, install_local_git_hooks.sh}.
- All scripts pass validate_marketplace.sh full harness on current HEAD.
- Wave validated against ry-explore deep research findings (Anthropic
  claude-plugins-official patterns + EveryInc + MadAppGang + tractorjuice/arc-kit).
- Tag convention canonical: {plugin-name}--v{version} per docs/en/plugin-dependencies.

Wave 12 — bilingual trigger surface (ef1b819..5e1c3d4, 2026-05-08):
- ef1b819 feat(skills): bilingual trigger surface across all 32 skills. All 8 plugins
  (rldyour-browser, rldyour-design, rldyour-explore, rldyour-flow, rldyour-lsps,
  rldyour-rules, rldyour-security, rldyour-serena-mcp) follow the explicit pattern:
  `"<purpose>. Используй для: <RU triggers>. EN triggers: <EN triggers>."` 32 SKILL.md
  files changed (1 insertion, 1 deletion each). Plugin-qualified slash literals
  (e.g. `/rldyour-flow:ry-start`) replace bare `/ry-start` refs in descriptions.
- 5e1c3d4 feat(commands): bilingual descriptions for 7 slash commands. Files:
  plugins/rldyour-design/commands/ry-design.md, plugins/rldyour-flow/commands/ry-deploy.md,
  ry-init.md, ry-newp.md, ry-review.md, ry-start.md, plugins/rldyour-rules/commands/ry-rules-review.md.
  Each description now contains both Russian sentence and English sentence.

Wave 11 — plugin-validator + skill-reviewer + ry-explore audit fixes (c76487a..3066e7f, 2026-05-08):
- c76487a fix(flow): ry-start argument-hint + canonical slash `/rldyour-flow:ry-start` + EN keywords.
  Added `argument-hint: "<task description>"` to SKILL.md frontmatter.
- 336fb9f fix(security): ry-sec-review When To Use now states "slash-only" instead of
  "Use this skill without waiting for explicit invocation" (contradicted disable-model-invocation).
- 1d33c25 fix(skills): allowed-tools alignment for orchestrator skills:
  - ry-design: added `mcp__plugin_rldyour-mcps_serena__*` (body step 7 invokes Serena).
  - flow-post-task-sync: added `allowed-tools: [Bash, Read, Grep, Glob]`;
    description expanded with Stop hook advisory triggers.
- afabf41 docs(lsps): install-profiles.md gained "Known limitations" section:
  - Filename-only files (Dockerfile, Containerfile, Makefile, etc.) cannot route via
    extensionToLanguage; tracked in anthropics/claude-code#47748 (OPEN, enhancement, filed 2026-04-14).
  - Compound extensions unsupported (#15785, closed not_planned).
  - lsp-server-matrix.md: docker entry marked "Degraded" referencing #47748.
- 47387ee feat(mcps): github MCP switched stdio → HTTP (`type: http`,
  `url: https://api.githubcopilot.com/mcp/`, `Authorization: Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}`).
  Matches anthropics/claude-plugins-official canonical (commit 76b35e9). Server count still 13.
  smoke_mcp_runtime.sh:110 — env-coverage probe now extracts `${VAR}` from both `env` (stdio)
  and `headers` (HTTP) blocks.
- 3066e7f feat(ops): bootstrap_check.sh — Dart SDK >=3.9 gate: fail-fast if MAJOR<3 or
  MAJOR==3 && MINOR<9. INFO line if dart absent. rldyour-mcps/README.md gains "Runtime SDK
  requirements" section and Special-notes line for github HTTP transport.
  Dart 3.9+ requirement source: docs.flutter.dev/ai/mcp-server (2026-05).

Plugin-dev validation wave (ba2592a..29586bd, branch audit/plugin-dev-validation):
- ba2592a fix(lsps): drop `.hcl` from docker entry in `.lsp.json` (was mis-routing Terraform/Packer
  .hcl; docker-language-server uses Bake-only .hcl support). Corrected install-profiles.md and
  serena-lsp-integration.md: CC v2.1.x auto-loads plugin .lsp.json files directly (canonical
  workaround for Issue #15148); `/reload-plugins` reports "15 plugin LSP servers".
- 25624e5 fix(design): `rldyour-design/plugin.json` dependencies now `["rldyour-mcps", "rldyour-browser"]`;
  design-validation skill body delegates to rldyour-browser:browser-validation.
- a432f26 fix(serena-mcp): `flow-memory-sync` agent gains positive `tools:` allowlist (Serena memory
  tools + Read/Grep/Glob/Bash); serena-memory-sync SKILL.md allowed-tools reduced to
  `[mcp__*serena__*, Read, Bash]` (Write/Edit removed); stop_memory_sync.sh IS_CURRENT
  parse-failure default flipped to `"false"` (fails closed).
- e60037e docs: README corrections — OWASP Top 10 2026→2025 in rldyour-security; removed reference
  to nonexistent `implementation-discipline.md (implicit)` in rldyour-rules; clarified 2-of-3
  skills declare MCP wildcards in rldyour-browser (browser-tool-routing is intentional pure prose).
- 29586bd docs: 12 files updated across rldyour-browser, rldyour-design, rldyour-explore,
  rldyour-security — unscoped `mcp__<server>__*` references in prose changed to canonical scoped
  form `mcp__plugin_rldyour-mcps_<server>__*` matching actual runtime tool IDs.

Advisory enforcement gates restored (refactor/restore-advisory-hooks):
- Stop hooks are advisory enforcement gates, not executors. Hooks compute
  machine-readable state via serena_memory_state.py / flow_post_task_state.py,
  block Stop with exit 2 when work remains, never perform high-blast-radius
  operations themselves.
- stop_memory_sync.sh: advisory exit 2 when memories stale, points orchestrator
  at flow-memory-sync subagent (preferred) or fallback Serena workflow.
- stop_post_task_sync.sh: advisory exit 2 when needs_flow_sync=true after
  Serena is current. Emits 9-step plan summary referencing flow-post-task-sync
  skill which handles: checks → atomic commits → push → ff-merge into default →
  push default → fullrepo publish → cleanup merged branches/worktrees.
- Orchestrator (ry-start, flow-post-task-sync skill, main session) is the
  executor of merge/push/publish/cleanup under model judgement.
- Loop guard preserved: same fingerprint + stop_hook_active=true → exit 0.
- Flow lifecycle when ry-start finishes a task wave:
    1. Task work commits land on feature branch.
    2. Stop fires.
    3. Serena hook checks memory freshness; blocks Stop if stale.
    4. Orchestrator invokes flow-memory-sync subagent (or fallback workflow).
    5. After Serena is current, Flow hook checks git/docs/fullrepo/cleanup
       state; blocks Stop if needs_flow_sync=true.
    6. Orchestrator runs flow-post-task-sync skill which executes the full
       pipeline.
    7. needs_flow_sync=false, Stop allowed.
