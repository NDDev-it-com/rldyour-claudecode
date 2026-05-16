<!-- Memory Metadata
Last updated: 2026-05-17
Last commit: 00d3f82 docs(config): add REVIEW.md template per global CLAUDE.md spec
Scope: plugins/rldyour-lsps/.lsp.json, plugins/rldyour-lsps/skills/lsp-routing/SKILL.md, plugins/rldyour-lsps/skills/lsp-health-check/SKILL.md, plugins/rldyour-lsps/skills/lsp-setup/SKILL.md, plugins/rldyour-lsps/skills/serena-lsp-integration/SKILL.md, plugins/rldyour-lsps/references/lsp-server-matrix.md, plugins/rldyour-lsps/references/install-profiles.md, plugins/rldyour-lsps/references/serena-lsp-integration.md, plugins/rldyour-lsps/scripts/check_lsps.sh, plugins/rldyour-lsps/scripts/install_lsps_brew.sh
Area: LSPS
-->

# LSPS-01-LANGUAGE-SERVERS

## Purpose

Language-server routing contract for `rldyour-lsps`. **15 LSP runtime entries** in `plugins/rldyour-lsps/.lsp.json` covering **16 documented language areas** across the matrix (Python, TS/JS, optional TS advanced via vtsls, Rust, Dart/Flutter, Go, C/C++, Qt C++, Qt QML, YAML, Docker, HTML, CSS, Bash, JSON, TOML, Markdown - `typescript_vts` is matrix-only, not present in `.lsp.json`). Drives accurate diagnostics, semantic navigation, and low-entropy implementation. Distinguishes Serena-native semantic support (11 keys) from external-only LSP areas (QML, Docker degraded, HTML, CSS) honestly.

`rldyour-lsps` is **skills-only** (4 skills + 3 references + 2 scripts + 1 `.lsp.json`, 0 agents, 0 hooks, 0 commands). Dependencies: `rldyour-mcps` only.

## Source Of Truth

- `plugins/rldyour-lsps/.lsp.json`: 15-key LSP runtime config (bash, cpp, css, dart, docker, go, html, json, markdown, python, qml, rust, toml, typescript, yaml). Each entry declares command, args, extensionToLanguage, transport, maxRestarts, startupTimeout.
- `plugins/rldyour-lsps/references/lsp-server-matrix.md`: canonical per-language matrix (Serena key, executable, startup shape, prerequisites, notes).
- `plugins/rldyour-lsps/references/install-profiles.md`: install paths per LSP.
- `plugins/rldyour-lsps/references/serena-lsp-integration.md`: Serena LSP keys + `.serena/project.yml` policy.
- `plugins/rldyour-lsps/skills/lsp-routing/SKILL.md`: routing decision tree.
- `plugins/rldyour-lsps/skills/lsp-health-check/SKILL.md`: verification workflow.
- `plugins/rldyour-lsps/skills/lsp-setup/SKILL.md`: install-only-on-explicit-request policy.
- `plugins/rldyour-lsps/skills/serena-lsp-integration/SKILL.md`: Serena integration policy.
- `plugins/rldyour-lsps/scripts/check_lsps.sh`: health-check script (idempotent).
- `plugins/rldyour-lsps/scripts/install_lsps_brew.sh`: brew-first install script.

## LSP Matrix (16 documented language areas, 15 `.lsp.json` runtime entries, May 2026)

| Area | Serena key | Executable | Project prerequisites | Notes |
|---|---|---|---|---|
| Python | `python` | `pyright-langserver` | `pyproject.toml` / `pyrightconfig.json` / venv | Pyright is Serena's Python default (replaces mypy). 2-5× faster than mypy, 98% spec coverage. |
| Python lint/format | external | `ruff` | `pyproject.toml` Ruff settings | Companion to Pyright, not replacement. `ruff server` if LSP client supports. |
| TypeScript | `typescript` | `typescript-language-server` | `tsconfig.json`, package manager lockfile | Default stable TS/JS LSP. |
| JavaScript | `typescript` | `typescript-language-server` | `jsconfig.json` or `allowJs` in `tsconfig.json` | JS handled via TS tooling. |
| TypeScript advanced | `typescript_vts` (matrix-only - not in `.lsp.json`) | `vtsls` | same as TypeScript | Optional alternative; use only when explicitly requested. Add to `.lsp.json` if/when a project needs it. |
| Rust | `rust` | `rust-analyzer` | Rust toolchain, `Cargo.toml`, `rust-src` | Prefer `rustup component add rust-src rust-analyzer`. |
| Dart | `dart` | `dart` (SDK) | `pubspec.yaml`, `analysis_options.yaml`, `dart pub get` | Use project SDK when possible. |
| Flutter | `dart` | `dart` / Flutter SDK | `pubspec.yaml`, `analysis_options.yaml`, `flutter pub get` | Flutter analysis is Dart-backed. |
| Go | `go` | `gopls` | `go.mod` or `go.work` | Do not treat random dirs as Go modules without module/workspace evidence. |
| C | `cpp` | `clangd` | `compile_commands.json` | Serena uses `cpp` for C. |
| C++ | `cpp` | `clangd` | `compile_commands.json` | `compile_commands.json` quality determines diagnostics quality. |
| Qt C++ | `cpp` | `clangd` | CMake build dir, Qt include paths in compile DB | Qt C++ = C++ + correct build metadata. |
| Qt QML | external | `qmlls` | QML imports / build metadata | Serena NOT QML-native - use external LSP + browser/app validation. |
| YAML | `yaml` | `yaml-language-server` | Schema associations | CI/Kubernetes/GitHub Actions/Compose schema mapping matters. |
| Dockerfile | external (degraded) | `docker-language-server` | Dockerfile/Compose/Bake files | **Degraded**: only `.dockerfile` extension routes - canonical `Dockerfile`/`Containerfile` filename does not (Claude Code #47748). |
| HTML | external | `vscode-html-language-server` | HTML files | Use browser validation for runtime truth ([[BROWSER-01-WORKFLOW]]). |
| CSS | external | `vscode-css-language-server` | CSS/PostCSS/Tailwind config | Pair with [[DESIGN-01-WORKFLOW]] for visual correctness. |
| Shell | `bash` | `bash-language-server` | Shell scripts, executable bits, shebangs | `shellcheck` required companion. |
| JSON | `json` | `vscode-json-language-server` | JSON schemas | Claude Code plugins/manifests use JSON. |
| TOML | `toml` | `taplo` | TOML files + schemas | Claude Code + Rust use TOML heavily. |
| Markdown | `markdown` | `marksman` | Markdown files | Useful for docs-heavy repos + plugin documentation. |

## Serena Language Key Map

Languages with native Serena semantic support (use `find_symbol`/`find_referencing_symbols`/etc):

- `python`, `typescript` (covers JS too), `rust`, `dart` (covers Flutter), `go`, `cpp` (covers C, C++, Qt C++), `yaml`, `bash`, `json`, `toml`, `markdown`.

External-only LSP areas (Serena NOT native - use direct reads + external LSP checks):

- `qml`, `dockerfile` (degraded), `html`, `css`.

## Routing Workflow (skill `lsp-routing`)

1. Detect language from files / manifests / lockfiles / build files (not extensions alone when project structure matters).
2. Read `plugins/rldyour-lsps/references/lsp-server-matrix.md` when exact command names, Serena keys, or prerequisites matter.
3. Use `serena-lsp-integration` skill when affecting Serena project languages / `.serena/project.yml` / `ls_specific_settings` / `serena project index`.
4. Use `lsp-health-check` skill when user asks whether LSPs work, project has missing diagnostics, or before non-trivial code work in newly-seen stack.
5. Use `lsp-setup` skill **only** after explicit user request to install or update.

## Default Decisions

- Python: Pyright (semantic) + Ruff (lint/format) - never mypy for new projects (per [[PHILOSOPHY-01-QUALITY-FIRST]] May 2026 defaults).
- TS/JS: `typescript-language-server` by default. `vtsls` only when project evidence requires.
- Rust: `rust-analyzer` + `rust-src`.
- Dart/Flutter: Dart SDK analyzer + Flutter SDK awareness.
- Go: `gopls` only inside real module/workspace.
- C/C++/Qt: `clangd` + `compile_commands.json` (critical for diagnostics quality).
- Qt QML: `qmlls` externally (not Serena-native).
- YAML: `yaml-language-server` + schemas.
- Docker: Docker Language Server externally (degraded - filename mapping gap).
- HTML/CSS/JSON: `vscode-langservers-extracted`.
- Shell: `bash-language-server` + `shellcheck`.
- TOML: Taplo.
- Markdown: Marksman.

## Health Check Workflow (skill `lsp-health-check`)

```bash
bash plugins/rldyour-lsps/scripts/check_lsps.sh           # current repo
bash plugins/rldyour-lsps/scripts/check_lsps.sh /path     # another project
```

Reports:
- Installed and missing commands (separately from project warnings).
- Project prerequisite warnings (missing `compile_commands.json`, `pubspec.yaml`, etc.).
- What must be installed or configured next.
- Whether Serena semantic work is safe for detected languages.

## Setup Workflow (skill `lsp-setup`, on explicit request only)

```bash
bash plugins/rldyour-lsps/scripts/install_lsps_brew.sh   # brew-first profile
bash plugins/rldyour-lsps/scripts/check_lsps.sh          # verify
```

Rules:
- Prefer Homebrew for missing system tools.
- `rustup component add rust-src rust-analyzer` when `rustup` installed.
- npm-only LSPs (`typescript-language-server`, `yaml-language-server`, `bash-language-server`) global install (`npm install -g`).
- Do not reinstall already-working non-brew commands just to standardize.
- Do not put machine-local executable paths in committed project files (`.serena/project.local.yml` for those).
- Do not auto-edit `.serena/project.yml` without explicit setup request.

## Serena Integration Policy

- Do not silently modify `.serena/project.yml`. Explain or apply changes only on explicit setup request. Full project initialization belongs to `rldyour-flow`.
- Use `.serena/project.local.yml` for machine-local executable paths. Committed `.serena/project.yml` for portable settings only.
- Recommend `serena project index` after language configuration changes.
- For supported code files, use Serena-first workflow: `check_onboarding_performed` → `list_memories` → `read_memory` → `get_symbols_overview` → `find_symbol(body=false)` → `find_symbol(body=true)` → `find_referencing_symbols` → `search_for_pattern`.
- For unsupported files (QML, HTML/CSS, Docker), state limitation and use direct reads + external LSP + browser/design validation.

## Runtime Safety

- **Never** start `stdio` language server manually (e.g., `pyright-langserver --stdio`, `bunx typescript-language-server --stdio`) - hangs without LSP client and corrupts protocol with stderr.
- **Never** use first-run `bunx package` or `uvx package` as long-lived LSP runtime - install logs can corrupt protocol handshakes.
- For validation, check command presence (`command -v <executable>`), versions, and project prerequisites.
- For C/C++/Qt, missing or stale `compile_commands.json` is **correctness blocker**, not cosmetic warning.

## Invariants

- `rldyour-lsps` plugin: 4 skills + 3 references + 2 scripts + 1 `.lsp.json`, 0 agents, 0 hooks, 0 commands. Dependencies: `rldyour-mcps`.
- 16 language areas documented in matrix (Python/TS/Rust/Dart/Go/C/C++/Qt/QML/YAML/Docker/HTML/CSS/Bash/JSON/TOML/Markdown). 15 of these have entries in `plugins/rldyour-lsps/.lsp.json`; `typescript_vts` is documented as optional alternative but not configured by default.
- Serena-native: 11 keys (`python`, `typescript`, `rust`, `dart`, `go`, `cpp`, `yaml`, `bash`, `json`, `toml`, `markdown`).
- External-only: QML, Docker (degraded), HTML, CSS.
- Pyright is Python default (mypy forbidden for new projects).
- `compile_commands.json` is correctness blocker for C/C++/Qt.
- `bunx`/`uvx` are explicit-setup tools only, not long-lived runtimes.
- `.serena/project.yml` not silently edited; `.serena/project.local.yml` for machine-local paths.

## Change Rules

- Add new LSP server: update `plugins/rldyour-lsps/.lsp.json` + `plugins/rldyour-lsps/references/lsp-server-matrix.md` + (optional) `plugins/rldyour-lsps/scripts/install_lsps_brew.sh` brew package.
- Update LSP version: bump in `.lsp.json` + matrix + verify via `bash plugins/rldyour-lsps/scripts/check_lsps.sh`.
- New project language: route through `serena-lsp-integration` skill before claiming Serena-native support.

## Verification

- `bash plugins/rldyour-lsps/scripts/check_lsps.sh`: proves LSP commands and project prerequisites available.
- `command -v <executable>`: per-LSP presence check.
- `python3 scripts/validate_agent_tools.py`: not LSP-specific, but proves Serena allowlist enforces read-only invariant ([[TECHDEBT-01-NOW]] R4).

## Cross-References

- Python/TS/Rust/Dart May 2026 type-check + lint defaults: [[PHILOSOPHY-01-QUALITY-FIRST]] Default Tooling table.
- Canonical FSD/VSA architecture using LSP feedback: [[DESIGN-01-WORKFLOW]] (frontend) + [[RULES-01-POLICY]] `architecture-boundaries` skill (backend).
- Serena semantic workflow: [[SERENA-01-MEMORY-SYNC]] + `plugins/rldyour-serena-mcp/skills/serena-code-workflow/SKILL.md`.
- Quality-first verification gates: [[RULES-01-POLICY]] `verification-quality-gates` skill.
