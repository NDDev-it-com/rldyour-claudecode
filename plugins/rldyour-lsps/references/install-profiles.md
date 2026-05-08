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

## Note on Claude Code LSP plugin registration

As of May 2026, Claude Code v2.1.x auto-loads `.lsp.json` from each installed plugin's root directory and registers the listed servers natively (verified empirically via `/reload-plugins` output reporting plugin LSP server count). Schema: `code.claude.com/docs/en/plugins-reference#lsp-servers`. The user must still install the LSP binaries locally (via `install_lsps_brew.sh` or equivalent) — `.lsp.json` only registers the server with Claude Code; if the binary is not on PATH, registration silently no-ops for that language. Anthropic's own `claude-plugins-official` LSP plugins try to declare `lspServers` in the central `marketplace.json`, but that propagation path is broken (Issue #15148, OPEN on v2.1.x) — per-plugin `.lsp.json` files in plugin root directly avoid that bug.

## Known limitations

- **Filename-only files do not route**: Claude Code uses `path.extname()` to map files to language servers. Files without an extension (`Dockerfile`, `Containerfile`, `Makefile`, `CMakeLists.txt`, `Gemfile`, `Rakefile`, `Procfile`, `Jenkinsfile`, `Vagrantfile`) cannot be associated with an LSP server through the current `.lsp.json` schema, which only supports `extensionToLanguage`. Tracked in [anthropics/claude-code#47748](https://github.com/anthropics/claude-code/issues/47748) (OPEN, `area:lsp` + `enhancement`, filed 2026-04-14). For Dockerfile specifically, the `docker` entry in our `.lsp.json` only catches files with the non-canonical `.dockerfile` extension; bare `Dockerfile`/`Containerfile` falls back to plain text until Anthropic ships filename-based matching.
- **Compound extensions are also unsupported**: e.g. `.spec.ts`, `.tfcomponent.hcl` resolve only to the last segment. Closed `not_planned` in [anthropics/claude-code#15785](https://github.com/anthropics/claude-code/issues/15785) (closed 2026-02-14).
- **Watch-list**: if Anthropic merges the filename-routing PR, add a `filenameToLanguage` block to `.lsp.json` for Docker / Make / etc. and remove this limitation note.
