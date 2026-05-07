# LSP Server Matrix

This matrix is the source of truth for the `rldyour-lsps` plugin. User-facing conversation stays Russian, but stored plugin documentation stays English.

## Core Matrix

| Area | Serena language key | Primary executable | Startup shape | Project prerequisites | Notes |
| --- | --- | --- | --- | --- | --- |
| Python | `python` | `pyright-langserver` | `pyright-langserver --stdio` | `pyproject.toml`, `pyrightconfig.json`, or clear virtual environment | Pyright is Serena's Python default. Use `ruff` for linting and formatting, not as a replacement for Pyright semantic analysis. |
| Python lint/format | external | `ruff` | `ruff server` when an LSP client supports it | `pyproject.toml` with Ruff settings when project-specific behavior matters | Keep Ruff diagnostics practical and non-blocking unless the project treats them as gates. |
| TypeScript | `typescript` | `typescript-language-server` | `typescript-language-server --stdio` | `tsconfig.json`, workspace `typescript`, package manager lockfile | Default stable TypeScript/JavaScript LSP. |
| JavaScript | `typescript` | `typescript-language-server` | `typescript-language-server --stdio` | `jsconfig.json` or `allowJs` in `tsconfig.json` | JavaScript is handled through TypeScript tooling. |
| TypeScript advanced | `typescript_vts` | `vtsls` | `vtsls --stdio` | same as TypeScript | Optional alternative only when a project needs VS Code-like TypeScript behavior. |
| Rust | `rust` | `rust-analyzer` | `rust-analyzer` | Rust toolchain, `Cargo.toml`, `rust-src` | Prefer `rustup component add rust-src rust-analyzer` when rustup manages the toolchain. |
| Dart | `dart` | `dart` | Dart SDK language server | `pubspec.yaml`, `analysis_options.yaml`, `dart pub get` | Use the project SDK when possible. |
| Flutter | `dart` | `dart` or Flutter SDK analyzer | Dart/Flutter analysis server | `pubspec.yaml`, `analysis_options.yaml`, `flutter pub get` | Flutter analysis is Dart-backed; use Flutter SDK for Flutter projects. |
| Go | `go` | `gopls` | `gopls` | `go.mod` or `go.work`, build tags/env | Do not treat random directories as Go modules without module/workspace evidence. |
| C | `cpp` | `clangd` | `clangd` | `compile_commands.json` | Serena uses `cpp` for C. |
| C++ | `cpp` | `clangd` | `clangd` | `compile_commands.json` | `compile_commands.json` quality determines diagnostics quality. |
| Qt C++ | `cpp` | `clangd` | `clangd` | CMake build dir, Qt include paths in compile database | Qt C++ is C++ plus correct build metadata. |
| Qt QML | external | `qmlls` | `qmlls` | QML imports/build metadata, generated qml LS config when available | Serena is not QML-native; use external LSP checks and browser/app validation as appropriate. |
| YAML | `yaml` | `yaml-language-server` | `yaml-language-server --stdio` | Schema associations, SchemaStore, or project-local schemas | For CI, Kubernetes, GitHub Actions, Docker Compose, and app config, schema mapping matters. |
| Dockerfile/Compose/Bake | external | `docker-language-server` | Docker LSP command | Dockerfile, Compose, Bake files | Serena is not Docker-native; use external diagnostics and project checks. |
| HTML | external | `vscode-html-language-server` | `vscode-html-language-server --stdio` | HTML files and framework conventions | Use browser validation for runtime truth. |
| CSS | external | `vscode-css-language-server` | `vscode-css-language-server --stdio` | CSS/PostCSS/Tailwind config when relevant | Pair with design/browser plugins for visual correctness. |
| Shell | `bash` | `bash-language-server` | `bash-language-server start` | Bash scripts, executable bits, shebangs | `shellcheck` is required companion validation. |
| JSON | `json` | `vscode-json-language-server` | `vscode-json-language-server --stdio` | JSON schemas where possible | Included because Claude Code plugins and manifests use JSON. |
| TOML | `toml` | `taplo` | `taplo lsp stdio` | TOML files and schemas where available | Included because Claude Code and Rust projects use TOML heavily. |
| Markdown | `markdown` | `marksman` | `marksman server` | Markdown files | Useful for docs-heavy repositories and plugin documentation. |

## Runtime Rules

- Use stable local executables for long-lived LSP `stdio` sessions.
- Do not use first-run `bunx`, `uvx`, or package-installing commands as long-lived LSP runtime commands because install logs can corrupt protocol handshakes.
- `bunx`, `uvx`, `brew`, `rustup`, `go install`, and package managers are acceptable for explicit setup or health checks.
- Do not start an interactive language server manually unless the caller is an LSP client. For validation, check command presence, versions, and project prerequisites instead.
- For C/C++/Qt, missing or stale `compile_commands.json` is a correctness blocker, not a cosmetic warning.

## Source Pointers

- Serena language support and configuration: `https://oraios.github.io/serena/01-about/020_programming-languages.html`, `https://oraios.github.io/serena/02-usage/050_configuration.html`
- LSP specification: `https://github.com/Microsoft/language-server-protocol/blob/gh-pages/_specifications/lsp/3.17/specification.md`
- Pyright: `https://github.com/microsoft/pyright`
- Ruff: `https://docs.astral.sh/ruff/editors/`
- TypeScript Language Server: `https://github.com/typescript-language-server/typescript-language-server`
- rust-analyzer: `https://rust-analyzer.github.io/book/`
- gopls: `https://go.dev/gopls/`
- clangd: `https://clangd.llvm.org/`
- Qt QML Language Server: `https://doc.qt.io/qt-6/qtqml-tooling-qmlls.html`
- YAML Language Server: `https://github.com/redhat-developer/yaml-language-server`
- Docker Language Server: `https://github.com/docker/docker-language-server`
- vscode-langservers-extracted: `https://github.com/hrsh7th/vscode-langservers-extracted`
- Bash Language Server: `https://github.com/bash-lsp/bash-language-server`
- Taplo: `https://taplo.tamasfe.dev/`
- Marksman: `https://github.com/artempyanykh/marksman`
- Anthropic LSP plugins (per-language READMEs only, no auto-load schema): `https://github.com/anthropics/claude-plugins-official/tree/main/plugins`
