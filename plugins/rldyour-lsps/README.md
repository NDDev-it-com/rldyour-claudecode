# rldyour-lsps

LSP routing, health checks, brew-first install profiles, Serena LSP integration, plus native Claude Code LSP server registration.

## What's inside

- `4` skills:
  - `lsp-routing` — picks the right language-server workflow (type-check, diagnostics, symbols, refactoring) for Python, Rust, Dart, TS/JS, Go, C++, Qt, YAML, Docker, HTML, CSS, Shell.
  - `lsp-health-check` — verify language servers and Serena prerequisites are available (`scripts/check_lsps.sh`).
  - `lsp-setup` — install/update LSPs via brew + toolchain (`scripts/install_lsps_brew.sh`). Only on explicit user request.
  - `serena-lsp-integration` — configure Serena MCP per project languages (`.serena/project.yml`, `ls_specific_settings`).
- `.lsp.json` — native Claude Code LSP server registration. Registers **15 language servers** matching the Codex `lsp-server-matrix.md`:
  - `python` (pyright-langserver `--stdio` for `.py`/`.pyi`/`.pyw`)
  - `typescript` (typescript-language-server `--stdio` for `.ts`/`.tsx`/`.js`/`.jsx`/`.mjs`/`.cjs`)
  - `rust` (rust-analyzer for `.rs`)
  - `dart` (dart `language-server --protocol=lsp` for `.dart`)
  - `go` (gopls for `.go`)
  - `cpp` (clangd for `.c`/`.h`/`.cc`/`.cpp`/`.cxx`/`.c++`/`.hh`/`.hpp`/`.hxx`/`.h++`/`.m`/`.mm`)
  - `qml` (qmlls for `.qml`)
  - `yaml` (yaml-language-server `--stdio` for `.yaml`/`.yml`)
  - `docker` (docker-language-server `start --stdio` for `.dockerfile` and `.hcl`/Bake — see caveat below)
  - `html` (vscode-html-language-server `--stdio` for `.html`/`.htm`)
  - `css` (vscode-css-language-server `--stdio` for `.css`/`.scss`/`.sass`/`.less`)
  - `bash` (bash-language-server `start` for `.sh`/`.bash`/`.zsh`)
  - `json` (vscode-json-language-server `--stdio` for `.json`/`.jsonc`)
  - `toml` (taplo `lsp stdio` for `.toml`)
  - `markdown` (marksman `server` for `.md`/`.mdx`/`.markdown`)

  Schema matches the canonical example from `Piebald-AI/claude-code-lsps` and `code.claude.com/docs/en/plugins-reference`. Each entry: `command` + `args` + `extensionToLanguage` + `transport: stdio` + `initializationOptions` + `settings` + `maxRestarts: 3`. This silences Claude Code's built-in recommendations to install per-language LSP plugins (like `pyright-lsp`) — CC uses the user's pre-installed servers directly. Servers must be installed locally; `scripts/install_lsps_brew.sh` handles brew-first install for the common set.
- `2` scripts: `check_lsps.sh`, `install_lsps_brew.sh`.
- `3` references: `lsp-server-matrix.md`, `install-profiles.md`, `serena-lsp-integration.md`.

## Coverage

All 15 LSPs from the matrix are registered in `.lsp.json` for native Claude Code support; the skills additionally route **any** of these languages through their canonical workflow patterns. Servers not on PATH are silently skipped by Claude Code (no error — just no LSP for that language until installed).

```
Python      pyright-langserver
Rust        rust-analyzer
Dart/Flutter dart language-server (system)
TypeScript  typescript-language-server (also handles JavaScript)
Go          gopls
C / C++     clangd (Qt C++ via correct compile_commands.json)
Qt QML      qmlls
YAML        yaml-language-server
Docker      docker-language-server
HTML        vscode-html-language-server
CSS         vscode-css-language-server (also SCSS/Sass/Less)
Shell       bash-language-server
JSON        vscode-json-language-server (also JSONC)
TOML        taplo
Markdown    marksman
```

Optional advanced TypeScript via `vtsls` is intentionally not registered (would conflict with `typescript-language-server` for the same `.ts`/`.tsx` extensions); use `lsp-routing` skill to invoke vtsls explicitly when a project requires it.

## Architectural caveats

- **`Dockerfile` (no extension)**: Claude Code's LSP-tool matches files via `extensionToLanguage` only. Files without an extension (canonical `Dockerfile`, `Containerfile`, `Makefile`) cannot be mapped through this schema — the docker-language-server entry only catches `*.dockerfile` and `*.hcl` (Bake). For plain `Dockerfile` the server runs on demand only when the file is opened with an explicit language ID via the editor.
- **MDX vs Markdown**: marksman parses `.mdx` as plain markdown — JSX expressions and front-matter tag-syntax are not understood. Install a dedicated `mdx-analyzer` LSP if MDX-aware features are required.
- **Compose files (`docker-compose.yml`, `compose.yaml`)**: handled by `yaml-language-server`, not by `docker-language-server` — both servers cannot claim the same extension. yaml-language-server provides schema-based validation; docker-language-server's compose-specific features are not exposed via this config.

## Dependencies

`rldyour-mcps` (Serena MCP server uses these LSP backends transparently).
