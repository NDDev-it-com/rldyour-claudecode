# rldyour-lsps

LSP routing, health checks, brew-first install profiles, Serena LSP integration.

## What's inside

- `4` skills:
  - `lsp-routing` — picks the right language-server workflow (type-check, diagnostics, symbols, refactoring) for Python, Rust, Dart, TS/JS, Go, C++, Qt, YAML, Docker, HTML, CSS, Shell.
  - `lsp-health-check` — verify language servers and Serena prerequisites are available (`scripts/check_lsps.sh`).
  - `lsp-setup` — install/update LSPs via brew + toolchain (`scripts/install_lsps_brew.sh`). Only on explicit user request.
  - `serena-lsp-integration` — configure Serena MCP per project languages (`.serena/project.yml`, `ls_specific_settings`).
- `2` scripts: `check_lsps.sh`, `install_lsps_brew.sh`.
- `3` references: `lsp-server-matrix.md`, `install-profiles.md`, `serena-lsp-integration.md`.

## Coverage

```
Python      pyright (or basedpyright)
Rust        rust-analyzer
Dart/Flutter dart language-server (system)
TypeScript  typescript-language-server
Go          gopls
C++         clangd
Qt          clangd with Qt-aware compile commands
YAML/JSON   yaml-language-server / vscode-json-languageserver
Docker      docker-langserver
HTML/CSS    vscode-html-languageserver / vscode-css-languageserver
Shell       bash-language-server
```

## Dependencies

`rldyour-mcps` (Serena MCP server uses these LSP backends transparently).
