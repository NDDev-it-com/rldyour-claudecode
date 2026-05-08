---
name: lsp-health-check
description: "Проверка LSP и Serena prerequisites для Python/Rust/Dart/Flutter/TS/JS/Go/C++/Qt/YAML/Docker/HTML/CSS/Shell. Используй для: проверь LSP, проверь язык-серверы, диагностики LSP, доступны ли LSP в проекте. EN triggers: check LSP, language server health, LSP diagnostics, verify LSP setup, are LSP installed, LSP project prerequisites, LSP doctor."
allowed-tools:
  - Bash
  - Read
---

# LSP Health Check

## Purpose

Verify that language servers and project prerequisites are available before relying on diagnostics, semantic navigation, or Serena symbol tools.

## Command

Run from a repository root:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/check_lsps.sh
```

For another project:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/check_lsps.sh /path/to/project
```

## Workflow

1. Run the health-check script when available.
2. If the script is not available in the current environment, check commands manually using stable executable names from `${CLAUDE_PLUGIN_ROOT}/references/lsp-server-matrix.md`.
3. Report missing commands separately from project prerequisite warnings.
4. Do not start raw `stdio` LSP sessions as a test — they hang waiting for a real LSP client.
5. For C, C++, and Qt C++, treat missing `compile_commands.json` as a serious warning because diagnostics may be wrong.
6. For TypeScript and JavaScript, verify `tsconfig.json` or `jsconfig.json`.
7. For Python, verify `pyproject.toml`, `pyrightconfig.json`, or virtual environment expectations.
8. For Dart and Flutter, verify `pubspec.yaml`, `analysis_options.yaml`, and dependency resolution.

## Output

In Russian, summarize:

- Installed and missing commands.
- Project prerequisite warnings.
- What must be installed or configured next.
- Whether Serena semantic work is safe for the detected languages.

## Anti-patterns

- Запускать `pyright-langserver --stdio` без LSP-клиента (зависает).
- Игнорировать project prerequisite warnings (`compile_commands.json` для C/C++ критично).
- Объявлять "LSPs работают" без verification через скрипт или `command -v`.
- Reinstall'ить уже работающие executables только для package manager standardization.
