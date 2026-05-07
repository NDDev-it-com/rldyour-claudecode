#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
cd "$ROOT"

echo "Detected quality checks for: $ROOT"

if [ -f package.json ]; then
  echo "- JavaScript/TypeScript:"
  if command -v jq >/dev/null 2>&1; then
    jq -r '.scripts // {} | to_entries[] | "  script: \(.key) -> \(.value)"' package.json
  fi
  [ -f tsconfig.json ] && echo "  typecheck: package script or tsc --noEmit"
  echo "  lint: package script or eslint if configured"
fi

if [ -f pyproject.toml ] || [ -f requirements.txt ]; then
  echo "- Python:"
  command -v pyright >/dev/null 2>&1 && echo "  typecheck: pyright ." || echo "  typecheck: pyright missing"
  command -v ruff >/dev/null 2>&1 && echo "  lint: ruff check ." || echo "  lint: ruff missing"
fi

if [ -f Cargo.toml ]; then
  echo "- Rust:"
  echo "  typecheck: cargo check"
  echo "  lint: cargo clippy -- -D warnings"
  echo "  test: cargo test"
fi

if [ -f pubspec.yaml ]; then
  echo "- Dart/Flutter:"
  echo "  deps: dart pub get or flutter pub get"
  echo "  analyze: dart analyze or flutter analyze"
  echo "  test: dart test or flutter test"
fi

if [ -f go.mod ] || [ -f go.work ]; then
  echo "- Go:"
  echo "  vet: go vet ./..."
  echo "  test: go test ./..."
fi

if [ -f CMakeLists.txt ] || find . -maxdepth 3 \( -name '*.c' -o -name '*.cc' -o -name '*.cpp' -o -name '*.h' -o -name '*.hpp' \) -print -quit | grep -q .; then
  echo "- C/C++:"
  find . -name compile_commands.json -print -quit | grep -q . && echo "  clangd: compile_commands.json found" || echo "  clangd: compile_commands.json missing"
fi

if find . -maxdepth 3 \( -name 'Dockerfile' -o -name 'docker-compose.yml' -o -name 'compose.yml' \) -print -quit | grep -q .; then
  echo "- Docker:"
  echo "  validate: docker compose config when compose file exists"
fi
