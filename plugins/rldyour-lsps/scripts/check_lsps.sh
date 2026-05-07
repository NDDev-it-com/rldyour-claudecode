#!/usr/bin/env bash
set -u

PROJECT_ROOT="${1:-$(pwd)}"
MISSING=0
WARNINGS=0

find_executable() {
  local name="$1"
  shift

  if command -v "$name" >/dev/null 2>&1; then
    command -v "$name"
    return 0
  fi

  local candidate
  for candidate in "$@"; do
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

require_command() {
  local label="$1"
  local command_name="$2"
  shift 2

  local resolved
  if resolved="$(find_executable "$command_name" "$@")"; then
    printf 'ok       %-28s %s\n' "$label" "$resolved"
  else
    printf 'missing  %-28s %s\n' "$label" "$command_name"
    MISSING=$((MISSING + 1))
  fi
}

warn_command() {
  local label="$1"
  local command_name="$2"
  shift 2

  local resolved
  if resolved="$(find_executable "$command_name" "$@")"; then
    printf 'ok       %-28s %s\n' "$label" "$resolved"
  else
    printf 'warn     %-28s %s\n' "$label" "$command_name"
    WARNINGS=$((WARNINGS + 1))
  fi
}

has_files() {
  local pattern="$1"
  find "$PROJECT_ROOT" \
    \( -path "$PROJECT_ROOT/.git" -o -path "$PROJECT_ROOT/node_modules" -o -path "$PROJECT_ROOT/.venv" -o -path "$PROJECT_ROOT/target" -o -path "$PROJECT_ROOT/build" -o -path "$PROJECT_ROOT/.dart_tool" \) -prune \
    -o -type f -name "$pattern" -print -quit | grep -q .
}

has_path() {
  local path="$1"
  [ -e "$PROJECT_ROOT/$path" ]
}

print_project_hint() {
  local label="$1"
  local status="$2"
  local detail="$3"
  printf '%-8s %-28s %s\n' "$status" "$label" "$detail"
}

printf 'rldyour-lsps health check\n'
printf 'project: %s\n\n' "$PROJECT_ROOT"

CLANGD_FALLBACKS=(
  "/opt/homebrew/opt/llvm/bin/clangd"
  "/usr/local/opt/llvm/bin/clangd"
  "/home/linuxbrew/.linuxbrew/opt/llvm/bin/clangd"
  "/home/linuxbrew/.linuxbrew/bin/clangd"
)
QMLLS_FALLBACKS=(
  "/opt/homebrew/opt/qtdeclarative/bin/qmlls"
  "/opt/homebrew/opt/qtdeclarative/libexec/bin/qmlls"
  "/usr/local/opt/qtdeclarative/bin/qmlls"
  "/home/linuxbrew/.linuxbrew/opt/qtdeclarative/bin/qmlls"
  "/home/linuxbrew/.linuxbrew/opt/qtdeclarative/libexec/bin/qmlls"
  "/home/linuxbrew/.linuxbrew/bin/qmlls"
)

printf 'Commands\n'
require_command "Python Pyright" "pyright-langserver"
require_command "Python Ruff" "ruff"
require_command "TypeScript/JS" "typescript-language-server"
require_command "Rust" "rust-analyzer"
require_command "Dart/Flutter" "dart"
require_command "Go" "gopls"
require_command "C/C++ clangd" "clangd" "${CLANGD_FALLBACKS[@]}"
require_command "YAML" "yaml-language-server"
require_command "Bash LSP" "bash-language-server"
require_command "ShellCheck" "shellcheck"
require_command "HTML" "vscode-html-language-server"
require_command "CSS" "vscode-css-language-server"
require_command "JSON" "vscode-json-language-server"
require_command "Docker" "docker-language-server"
require_command "TOML" "taplo"
require_command "Markdown" "marksman"

if has_files "*.qml"; then
  require_command "Qt QML" "qmlls" "${QMLLS_FALLBACKS[@]}"
else
  warn_command "Qt QML" "qmlls" "${QMLLS_FALLBACKS[@]}"
fi

printf '\nProject prerequisites\n'

if has_files "*.py"; then
  if has_path "pyproject.toml" || has_path "pyrightconfig.json"; then
    print_project_hint "Python config" "ok" "pyproject.toml or pyrightconfig.json found"
  else
    print_project_hint "Python config" "warn" "no pyproject.toml or pyrightconfig.json"
    WARNINGS=$((WARNINGS + 1))
  fi
fi

if has_files "*.ts" || has_files "*.tsx" || has_files "*.js" || has_files "*.jsx"; then
  if has_path "tsconfig.json" || has_path "jsconfig.json"; then
    print_project_hint "TS/JS config" "ok" "tsconfig.json or jsconfig.json found"
  else
    print_project_hint "TS/JS config" "warn" "no tsconfig.json or jsconfig.json"
    WARNINGS=$((WARNINGS + 1))
  fi
fi

if has_path "Cargo.toml"; then
  print_project_hint "Rust manifest" "ok" "Cargo.toml found"
fi

if has_path "pubspec.yaml"; then
  print_project_hint "Dart manifest" "ok" "pubspec.yaml found"
  if has_path "analysis_options.yaml"; then
    print_project_hint "Dart analysis" "ok" "analysis_options.yaml found"
  else
    print_project_hint "Dart analysis" "warn" "no analysis_options.yaml"
    WARNINGS=$((WARNINGS + 1))
  fi
fi

if has_path "go.mod" || has_path "go.work"; then
  print_project_hint "Go workspace" "ok" "go.mod or go.work found"
fi

if has_files "*.c" || has_files "*.cc" || has_files "*.cpp" || has_files "*.h" || has_files "*.hpp"; then
  if find "$PROJECT_ROOT" -name compile_commands.json -print -quit | grep -q .; then
    print_project_hint "C/C++ compile DB" "ok" "compile_commands.json found"
  else
    print_project_hint "C/C++ compile DB" "warn" "no compile_commands.json"
    WARNINGS=$((WARNINGS + 1))
  fi
fi

printf '\nSummary\n'
printf 'missing: %s\n' "$MISSING"
printf 'warnings: %s\n' "$WARNINGS"

if [ "$MISSING" -gt 0 ]; then
  exit 1
fi

exit 0
