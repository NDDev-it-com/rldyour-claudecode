---
name: serena-lsp-integration
description: "Конфигурация Serena MCP под languages проекта — LSP keys, .serena/project.yml, ls_specific_settings. Используй для: настрой Serena LSP, индексация, семантический анализ, serena project index."
allowed-tools:
  - mcp__plugin_rldyour-mcps_serena__*
  - Read
  - Write
  - Edit
  - Bash
---

# Serena LSP Integration

## Purpose

Keep Serena MCP usage aligned with real language-server support. Use Serena for semantic inspection and editing where supported, and fall back honestly where a file type is not Serena-native.

## Workflow

1. Inspect project evidence: manifests, build files, lockfiles, and source files.
2. Read `${CLAUDE_PLUGIN_ROOT}/references/serena-lsp-integration.md` when exact Serena keys or limitations matter.
3. Map supported languages to Serena keys: `python`, `typescript`, `rust`, `dart`, `go`, `cpp`, `yaml`, `bash`, `json`, `toml`, `markdown`.
4. Treat C and C++ as `cpp`; treat JavaScript as `typescript`.
5. Treat HTML, CSS, Docker, and QML as external LSP areas unless current Serena docs prove native support.
6. Check health and prerequisites through `lsp-health-check` before expecting reliable semantic behavior.
7. Recommend `serena project index` after language configuration changes.

## Configuration Policy

Do not silently modify `.serena/project.yml`. Explain or apply changes only when the user explicitly asks for setup. Full project initialization belongs to the `rldyour-flow` plugin.

Use `.serena/project.local.yml` for machine-local executable paths. Use committed `.serena/project.yml` only for portable project settings.

## Serena Tool Priority

For supported code files, use the existing Serena-first workflow:

1. `check_onboarding_performed`
2. `list_memories`
3. relevant `read_memory`
4. `get_symbols_overview`
5. targeted `find_symbol`
6. `find_referencing_symbols`
7. `search_for_pattern` only for broad text sweeps or unsupported file types

For unsupported files, state the limitation and use direct reads, search, external validation, or browser/design/security plugins as appropriate.

## Anti-patterns

- Автоматически редактировать `.serena/project.yml` без explicit setup request.
- Заявлять Serena-native поддержку для HTML/CSS/Docker/QML без upstream confirmation.
- Hardcode machine-local LSP paths (`/opt/homebrew/...`) в committed `.serena/project.yml` (use `.serena/project.local.yml`).
- Skip'нуть `serena project index` после изменения language configuration.
- Использовать `search_for_pattern` для symbol-level questions когда есть `find_symbol`.
