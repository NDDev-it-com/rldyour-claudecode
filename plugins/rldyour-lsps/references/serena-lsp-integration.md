# Serena LSP Integration

Serena MCP provides semantic code intelligence through language-server backed language keys. The `rldyour-lsps` plugin must keep this boundary explicit.

## Serena-Native Keys For This System

Use these keys when generating or checking `.serena/project.yml`:

- `python` for Python through Pyright.
- `typescript` for TypeScript and JavaScript.
- `typescript_vts` only when explicitly selecting VTSLS.
- `rust` for Rust through rust-analyzer.
- `dart` for Dart and Flutter.
- `go` for Go through gopls.
- `cpp` for C, C++, and Qt C++ through clangd.
- `yaml` for YAML.
- `bash` for Bash shell scripts.
- `json` for JSON.
- `toml` for TOML.
- `markdown` for Markdown.

## Non-Native Or External Areas

Serena should not be described as fully semantic for these areas unless upstream support is confirmed in the current Serena release:

- HTML
- CSS
- Dockerfile, Docker Compose, Docker Bake
- QML and Qt Quick
- Non-Bash shell dialects

For those areas, use external LSP health checks, project file checks, browser/design/security validation where relevant, and Claude Code-native text tools when needed.

## Project Configuration Policy

This plugin does not silently mutate `.serena/project.yml`. It may inspect the file, explain needed changes, or apply changes only when the user explicitly asks for setup. Full project initialization belongs to the `rldyour-flow` plugin.

When a project needs Serena language coverage, prefer this order:

1. Detect project evidence: files, manifests, lockfiles, build files, and tool configs.
2. Map detected technologies to Serena language keys.
3. Verify LSP executables and project prerequisites through `lsp-health-check`.
4. Propose `.serena/project.yml` changes only for supported Serena keys.
5. Run or recommend `serena project index` after project configuration changes.
6. Use Serena semantic tools for supported files and fallback honestly for unsupported files.

## `ls_specific_settings`

Use `ls_specific_settings` only when the default managed server is insufficient or a stable local executable must be pinned. Common cases:

```yaml
ls_specific_settings:
  python:
    ls_path: "/absolute/path/from/command -v pyright-langserver"
  cpp:
    ls_path: "/absolute/path/from/command -v clangd"
    compile_commands_dir: "build"
  typescript:
    ls_path: "/absolute/path/from/command -v typescript-language-server"
```

Do not add machine-local paths to committed project files unless the repository intentionally depends on that machine layout. macOS Homebrew, Linuxbrew, SDK, Snap, and user-local executable paths are all machine projections; prefer `.serena/project.local.yml` for local overrides.

## C, C++, And Qt

For `cpp`, the language server is only as correct as the compile database:

- CMake projects should enable `CMAKE_EXPORT_COMPILE_COMMANDS=ON`.
- Non-CMake projects should provide a generated `compile_commands.json`.
- Qt C++ needs Qt include paths, generated headers, and build flags in the compile database.
- Qt QML should be handled by `qmlls` externally; do not claim Serena symbol operations are QML-aware unless upstream support is verified.

## JavaScript

Use `typescript` for JavaScript. A JavaScript-only project should still provide `jsconfig.json` or TypeScript configuration that lets the language server understand module resolution.

## How this plugin registers LSP servers with Claude Code

This plugin ships `plugins/rldyour-lsps/.lsp.json` at the plugin root. Claude Code v2.1.x auto-loads `.lsp.json` from each installed plugin and registers the listed servers natively (verified empirically via `/reload-plugins` output: "15 plugin LSP servers"). Schema: `code.claude.com/docs/en/plugins-reference#lsp-servers`. Each entry maps a language key to `command + args + extensionToLanguage + transport=stdio + initializationOptions + settings + maxRestarts` (plus optional `startupTimeout`).

Anthropic's `claude-plugins-official` LSP plugin folders (typescript-lsp, pyright-lsp, rust-analyzer-lsp, gopls-lsp, clangd-lsp, jdtls-lsp, etc.) ship only LICENSE + README because they declare `lspServers` in the central marketplace.json — but that propagation path is broken in CC v2.1.x (Issue #15148, still OPEN as of May 2026). Per-plugin `.lsp.json` directly avoids that bug and is the canonical workaround used by `Piebald-AI/claude-code-lsps` and `boostvolt/claude-code-lsps` production marketplaces. Local executable installation is still the user's responsibility — `.lsp.json` only registers the server with CC; the binary must already be on PATH.
