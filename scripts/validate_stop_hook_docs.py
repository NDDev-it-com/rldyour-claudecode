#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FLOW_HOOKS = ROOT / "plugins" / "rldyour-flow" / "hooks" / "hooks.json"
SERENA_HOOKS = ROOT / "plugins" / "rldyour-serena-mcp" / "hooks" / "hooks.json"
DISPATCHER = "${CLAUDE_PLUGIN_ROOT}/hooks/stop_lifecycle_dispatcher.sh"
STALE_ACTIVE_PHRASES = (
    "both Stop hooks",
    "Serena Stop fires first",
    "Serena Stop still runs",
    "rldyour-serena-mcp Stop",
    "Serena Stop hook",
    "Stop hook to finish first",
)


class Failure(Exception):
    pass


def load_hooks(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Failure(f"{path.relative_to(ROOT)}: invalid JSON: {exc}") from exc
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        raise Failure(f"{path.relative_to(ROOT)}: hooks must be an object")
    return hooks


def command_hooks(event_items: Any) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    if not isinstance(event_items, list):
        return commands
    for item in event_items:
        if not isinstance(item, dict):
            continue
        for hook in item.get("hooks", []):
            if isinstance(hook, dict) and hook.get("type") == "command":
                commands.append(hook)
    return commands


def validate_registered_hooks() -> list[str]:
    flow = load_hooks(FLOW_HOOKS)
    serena = load_hooks(SERENA_HOOKS)
    if "Stop" in serena:
        raise Failure("rldyour-serena-mcp/hooks/hooks.json must not register Stop")

    stop_commands = command_hooks(flow.get("Stop"))
    dispatchers = [
        hook
        for hook in stop_commands
        if DISPATCHER in [str(arg) for arg in hook.get("args", [])]
    ]
    if len(dispatchers) != 1:
        raise Failure("rldyour-flow must register exactly one Stop dispatcher command")
    if len(stop_commands) != 1:
        raise Failure("rldyour-flow Stop event must contain only the dispatcher command")
    timeout = dispatchers[0].get("timeout")
    if not isinstance(timeout, int) or timeout < 40:
        raise Failure("Stop dispatcher timeout must preserve child-gate budget")
    return ["ok: Claude Stop hook registration uses one Flow dispatcher"]


def active_text_paths() -> list[Path]:
    paths = [
        ROOT / "AGENTS.md",
        ROOT / ".claude" / "CLAUDE.md",
        ROOT / "README.md",
        ROOT / "docs" / "runtime-env.md",
        ROOT / "docs" / "observability.md",
        ROOT / "docs" / "security" / "threat-model.md",
        ROOT / "docs" / "adr" / "0006-mcp-hook-ownership-boundaries.md",
        ROOT / "plugins" / "rldyour-flow" / "hooks" / "stop_post_task_sync.sh",
    ]
    return [path for path in paths if path.is_file()]


def validate_docs() -> list[str]:
    errors: list[str] = []
    for path in active_text_paths():
        text = path.read_text(encoding="utf-8", errors="replace")
        for phrase in STALE_ACTIVE_PHRASES:
            if phrase in text:
                errors.append(f"{path.relative_to(ROOT)}: stale Stop lifecycle phrase {phrase!r}")
    if errors:
        raise Failure("; ".join(errors))

    runtime_env = (ROOT / "docs" / "runtime-env.md").read_text(encoding="utf-8")
    required = {
        "`RLDYOUR_SKIP_STOP_GATES` | registered Flow Stop dispatcher",
        "`RLDYOUR_SKIP_FLOW_SYNC` | Flow Stop child gate",
        "`RLDYOUR_SKIP_SERENA_SYNC` | Serena memory child gate",
    }
    missing = sorted(item for item in required if item not in runtime_env)
    if missing:
        raise Failure("docs/runtime-env.md missing current skip-flag wording: " + ", ".join(missing))
    return ["ok: active Stop lifecycle docs match dispatcher architecture"]


def main() -> int:
    try:
        messages = validate_registered_hooks()
        messages.extend(validate_docs())
        print("\n".join(messages))
        return 0
    except Failure as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
