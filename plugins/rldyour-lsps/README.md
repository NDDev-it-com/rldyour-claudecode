# rldyour-lsps

LSP routing, health checks, brew-first install profiles, Serena LSP integration, plus native Claude Code LSP server registration.

## What's inside

- `4` skills:
  - `lsp-routing` — picks the right language-server workflow (type-check, diagnostics, symbols, refactoring) for Python, Rust, Dart, TS/JS, Go, C++, Qt, YAML, Docker, HTML, CSS, Shell.
  - `lsp-health-check` — verify language servers and Serena prerequisites are available (`scripts/check_lsps.sh`).
  - `lsp-setup` — install/update LSPs via brew + toolchain (`scripts/install_lsps_brew.sh`). Only on explicit user request.
  - `serena-lsp-integration` — configure Serena MCP per project languages (`.serena/project.yml`, `ls_specific_settings`).
- `.lsp.json` — native Claude Code LSP server registration. Currently registers `pyright-langserver` for `.py`/`.pyi`/`.pyw` files, matching the canonical schema from `code.claude.com/docs/en/plugins-reference#lsp-servers`. This silences the built-in CC recommendation to install the `pyright-lsp` Anthropic plugin when Python files are detected — Claude Code now uses the user's pre-installed pyright (typically at `~/.local/bin/pyright-langserver`) directly.
- `2` scripts: `check_lsps.sh`, `install_lsps_brew.sh`.
- `3` references: `lsp-server-matrix.md`, `install-profiles.md`, `serena-lsp-integration.md`.

## Coverage

The skills route **any** of the languages below through their canonical LSP. Only Python is currently registered with native Claude Code via `.lsp.json` (since the marketplace itself contains Python scripts). To register additional language servers natively, append entries to `.lsp.json` matching the pattern from `plugins/rldyour-lsps/.lsp.json`:

```
Python      pyright-langserver        (registered in .lsp.json)
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
