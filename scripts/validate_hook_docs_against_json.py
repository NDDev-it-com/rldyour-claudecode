#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLOW_HOOKS = ROOT / "plugins" / "rldyour-flow" / "hooks" / "hooks.json"
SERENA_HOOKS = ROOT / "plugins" / "rldyour-serena-mcp" / "hooks" / "hooks.json"
DOCS = (ROOT / "AGENTS.md", ROOT / ".claude" / "CLAUDE.md")


class Failure(Exception):
    pass


def load_hooks(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Failure(f"{path.relative_to(ROOT)} is not valid JSON: {exc}") from exc


def stop_handlers(plugin: str, hooks_path: Path) -> list[tuple[str, int]]:
    data = load_hooks(hooks_path)
    handlers: list[tuple[str, int]] = []
    for group in data.get("hooks", data).get("Stop", []) or []:
        for handler in group.get("hooks", []) or []:
            args = handler.get("args") or []
            script = str(args[0]) if args else str(handler.get("command", ""))
            timeout = int(handler.get("timeout", 0))
            if script:
                handlers.append((f"{plugin}:{script}", timeout))
    return handlers


def validate_doc(path: Path, expected_script: str, timeout: int) -> list[str]:
    if not path.is_file():
        raise Failure(f"{path.relative_to(ROOT)} is missing")
    text = path.read_text(encoding="utf-8")
    stale = (
        "`hooks/stop_memory_sync.sh`",
        "`hooks/stop_post_task_sync.sh`",
        "| Stop | rldyour-serena-mcp |",
    )
    for needle in stale:
        if needle in text:
            raise Failure(f"{path.relative_to(ROOT)} contains stale registered Stop hook claim: {needle}")
    expected_row = f"| Stop | rldyour-flow | `{expected_script}` | {timeout}s |"
    if expected_row not in text:
        raise Failure(f"{path.relative_to(ROOT)} missing current Stop dispatcher row: {expected_row}")
    if not re.search(r"single registered Claude Stop hook|single registered Stop", text):
        raise Failure(f"{path.relative_to(ROOT)} must explain that Stop uses one registered dispatcher")
    return [f"ok: {path.relative_to(ROOT)} Stop hook table matches hooks.json"]


def main() -> int:
    try:
        flow_stop = stop_handlers("rldyour-flow", FLOW_HOOKS)
        serena_stop = stop_handlers("rldyour-serena-mcp", SERENA_HOOKS)
        if serena_stop:
            raise Failure(f"{SERENA_HOOKS.relative_to(ROOT)} must not register Stop handlers: {serena_stop}")
        if len(flow_stop) != 1:
            raise Failure(f"{FLOW_HOOKS.relative_to(ROOT)} must register exactly one Stop handler: {flow_stop}")
        handler, timeout = flow_stop[0]
        expected_script = "hooks/stop_lifecycle_dispatcher.sh"
        if not handler.endswith("${CLAUDE_PLUGIN_ROOT}/" + expected_script):
            raise Failure(f"unexpected Flow Stop handler: {handler}")
        messages = [f"ok: hooks.json registers one Flow Stop dispatcher at {timeout}s"]
        for doc in DOCS:
            messages.extend(validate_doc(doc, expected_script, timeout))
        print("\n".join(messages))
        return 0
    except Failure as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
