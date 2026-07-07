---
name: token-economy
description: "Экономия токенов через rtk и Serena/LSP: shell-команды идут через rtk (сжатие вывода), код читается символами Serena, а не целыми файлами. Используй для: запуск команд, чтение вывода git/тестов/сборки/линта, экономия контекста, большие файлы. EN triggers: token economy, rtk, compress command output, reduce context, avoid whole-file reads, run commands efficiently, rtk gain."
allowed-tools:
  - Bash
---

# Token economy (rtk + Serena/LSP)

Keep the model's context small. Two non-overlapping layers:

- **rtk = shell-output compression.** The `rldyour-rtk` PreToolUse Bash hook
  transparently rewrites supported commands (`git`, `pytest`/`jest`/`cargo test`,
  `tsc`/`eslint`/`ruff`, `ls`/`grep`/`find`, `docker`/`kubectl`, ...) to
  `rtk <cmd>` so only signal reaches context. You do not type `rtk` yourself -
  the hook does it.
- **Serena/LSP = symbol-level code reads.** Navigate and edit code through
  `find_symbol` / `find_referencing_symbols` / `insert_after_symbol`, not by
  reading whole files.

## Rules

1. Run shell commands normally; the hook routes supported ones through rtk.
   Never defeat it by demanding raw output for git/test/build/lint/ls/grep/find.
2. For large files prefer `rtk read <file>` or `rtk read <file> -l aggressive`
   (signatures only); for code understanding prefer Serena symbol tools.
3. Do not duplicate layers: rtk compresses command output; Serena/LSP handles
   symbol reads and edits.
4. Do not wrap interactive commands (editors, REPLs); the hook already skips
   unknown/interactive commands (graceful passthrough).
5. On a failing command rtk saves full output to a tee log - read that log
   instead of re-running the command.
6. Check savings with `/rtk-gain`.

## Scope limits

- The hook fires only on the **Bash tool**. Native Read/Grep/Glob and MCP tool
  output do not pass through rtk. To compress those, use shell equivalents
  (`rtk grep`, `rtk read`).
- Commands whose output must be parsed byte-for-byte (control-plane validators,
  `git commit`/`merge`/`rebase` watched by other hooks, `gh api`, `jq`) are
  excluded from rewriting via `~/.config/rtk/config.toml` `[hooks]
  exclude_commands`. Never rely on rtk to reshape output a script must parse.

## Requirement

rtk (Rust Token Killer, github.com/rtk-ai/rtk, Apache-2.0) is an external single
binary: `brew install rtk`. Without it, this layer is a no-op and commands run
raw - nothing breaks.
