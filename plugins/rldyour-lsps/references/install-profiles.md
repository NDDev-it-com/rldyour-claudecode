# Install Profiles

The default setup policy is brew-first, explicit, and non-silent.

## Brew-First Packages

Install these through Homebrew when missing. This applies to macOS Homebrew and Linuxbrew when `brew` is available on Linux:

```bash
brew install go gopls shellcheck vscode-langservers-extracted docker-language-server taplo marksman qtdeclarative qtlanguageserver
```

These packages cover:

- Go and `gopls`.
- ShellCheck for Bash validation.
- HTML, CSS, and JSON LSP commands through `vscode-langservers-extracted`.
- Dockerfile, Compose, and Bake language server.
- TOML through Taplo.
- Markdown through Marksman.
- Qt QML language-server tooling through Qt packages.

## Existing Non-Brew Executables Are Acceptable

If these already exist as stable local commands, do not reinstall them just to change package manager ownership:

- `pyright-langserver` (often via npm or pipx)
- `ruff` (via pipx, cargo, or brew)
- `rust-analyzer` (via rustup component)
- `typescript-language-server` (via npm)
- `yaml-language-server` (via npm)
- `bash-language-server` (via npm)
- `dart` (via Dart SDK / Flutter SDK)
- `clangd` (via brew llvm or system Xcode CLT)

The health check should report the actual executable path. A future cleanup can standardize paths if needed.

Platform-specific command paths are runtime projections, not committed project contracts. Prefer `command -v <tool>` in checks and use explicit fallback paths only for common Homebrew and Linuxbrew locations.

## Toolchain-Specific Exceptions

- Rust: if `rustup` is present, run `rustup component add rust-src rust-analyzer` because it matches the active Rust toolchain.
- Dart and Flutter: prefer the SDK that belongs to the project.
- Python: prefer the project virtual environment for runtime packages, but Pyright itself can be a stable global executable.
- C/C++/Qt: install tools globally, but project diagnostics depend on local build metadata.

## npm-Installable LSPs (when brew formula is missing)

```bash
npm install -g typescript-language-server typescript
npm install -g yaml-language-server
npm install -g bash-language-server
npm install -g pyright              # alternative to pipx install pyright
```

## Do Not Do This

- Do not run `bunx package --stdio` or `uvx package --stdio` as a long-lived language server runtime. First-run install logs corrupt the LSP protocol handshake.
- Do not install global tools silently without an explicit user request.
- Do not store user tokens, credentials, or private paths in committed plugin files.
- Do not modify `.serena/project.yml` automatically during normal code inspection.

## Note on Claude Code LSP plugins

As of May 2026, Anthropic's `claude-plugins-official` ships per-language LSP plugin folders (typescript-lsp, pyright-lsp, rust-analyzer-lsp, etc.) but each one contains only LICENSE + README — they document the install command for the user. Claude Code does not expose a `.lsp.json` schema or `lspServers` plugin field that would auto-load LSPs. LSPs remain local executables consumed by Serena MCP, IDE clients, and our health-check scripts.
