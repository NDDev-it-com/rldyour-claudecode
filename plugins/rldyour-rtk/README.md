# rldyour-rtk

rtk token-economy core for the rldyour Claude Code adapter.

- **Hook** (`hooks/hooks.json` → `hooks/rtk_rewrite.sh`): a guaranteed
  `PreToolUse` Bash hook that delegates to rtk's native `rtk hook claude`,
  transparently rewriting supported shell commands to `rtk <cmd>` so their
  output is compressed before it reaches context. Graceful passthrough (exit 0)
  when rtk is absent.
- **Skill** (`skills/token-economy`): when to prefer rtk vs Serena/LSP symbol
  reads, plus scope limits (Bash-tool only; excludes validator/verbatim
  commands).
- **Command** (`/rtk-gain`): report token savings (`rtk gain`).

## rtk

rtk (Rust Token Killer, https://github.com/rtk-ai/rtk, Apache-2.0) is an
external single binary - install with `brew install rtk` (homebrew-core). It is
**not** an MCP server and is not vendored here. Machine-global config lives at
`~/.config/rtk/config.toml` (macOS: `~/Library/Application Support/rtk/`),
including `[hooks] exclude_commands` for validator/JSON-verbatim safety. The
control-plane source of truth for the rtk pin and exclusion baseline is
`config/token-economy-policy.json` in `rldyour-ai-cli-tools`.

Owner: Danil Silantyev (github:rldyourmnd), CEO NDDev. License:
AGPL-3.0-or-later.
