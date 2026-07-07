#!/usr/bin/env bash
# rldyour-rtk PreToolUse Bash hook.
#
# Delegates to rtk's native rewrite mode (`rtk hook claude`). rtk reads the
# PreToolUse JSON on stdin and, for supported commands, emits
# hookSpecificOutput.updatedInput so the command runs through `rtk <cmd>` and
# its output is compressed before it reaches the model context.
#
# Graceful degradation: if rtk is not installed, exit 0 with no output so Claude
# Code runs the original command unchanged. rtk itself exits 0 on any internal
# failure (filter error -> raw passthrough), so this hook never blocks a tool.
#
# Command scope (which commands rtk rewrites vs passes through) and the
# validator/verbatim exclusions are governed machine-globally by
# ~/.config/rtk/config.toml [hooks] exclude_commands (written by the
# rldyour-new-mac-or-ubuntu bootstrap; see config/token-economy-policy.json in
# the control plane). This script intentionally stays a thin, dependency-free
# delegator.
command -v rtk >/dev/null 2>&1 || exit 0
exec rtk hook claude
