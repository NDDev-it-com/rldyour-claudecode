---
name: lsp-setup
description: "Установка/обновление LSP-серверов через brew + toolchain (rustup, dart, npm). Только по явному запросу. Используй для: установи LSP, обнови лсп, поставь язык-серверы, почини language server."
---

# LSP Setup

## Purpose

Install or update LSP dependencies only after an explicit user request. Keep setup deterministic, brew-first, and safe for long-lived `stdio` language server use.

## Default Install Profile

Run from this repository when the user explicitly asks for setup:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/install_lsps_brew.sh
```

Then verify:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/check_lsps.sh
```

## Rules

- Prefer Homebrew for missing system tools.
- Use `rustup component add rust-src rust-analyzer` when `rustup` is installed.
- For npm-only LSPs (typescript-language-server, yaml-language-server, bash-language-server) install globally: `npm install -g <package>`. Or use existing project-local install when one exists.
- Do not reinstall already working non-brew commands just to standardize ownership.
- Do not put machine-local executable paths into committed project files.
- Do not auto-edit `.serena/project.yml`; propose or apply changes only on explicit setup request.
- After setup, run `lsp-health-check` and report exact remaining gaps.

## Install Profile Reference

Read `${CLAUDE_PLUGIN_ROOT}/references/install-profiles.md` before changing the install script or adding new LSPs.

## Anti-patterns

- Установка LSPs молча без явного запроса пользователя.
- `bunx package --stdio` / `uvx package --stdio` как long-lived runtime.
- Reinstall работающих executables просто для смены package manager.
- Auto-edit `.serena/project.yml` без явного setup request.
- Hardcode user-local пути (`/opt/homebrew/...`, `/home/user/...`) в committed plugin files.
