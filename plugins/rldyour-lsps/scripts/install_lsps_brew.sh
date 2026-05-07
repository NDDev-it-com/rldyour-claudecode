#!/usr/bin/env bash
set -euo pipefail

if ! command -v brew >/dev/null 2>&1; then
  printf 'Homebrew is required for this install profile.\n' >&2
  exit 1
fi

BREW_PACKAGES=(
  go
  gopls
  shellcheck
  vscode-langservers-extracted
  docker-language-server
  taplo
  marksman
  qtdeclarative
  qtlanguageserver
)

for package in "${BREW_PACKAGES[@]}"; do
  if brew list --formula "$package" >/dev/null 2>&1; then
    printf 'installed %s\n' "$package"
  else
    printf 'installing %s\n' "$package"
    brew install "$package"
  fi
done

if command -v rustup >/dev/null 2>&1; then
  rustup component add rust-src rust-analyzer
fi

printf 'brew-first LSP setup complete. Run scripts/check_lsps.sh to verify.\n'
