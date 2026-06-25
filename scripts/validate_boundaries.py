#!/usr/bin/env python3
"""Validate Claude marketplace structural boundaries.

The tracked-context model stores durable AI context on main. This validator
keeps ownership boundaries strict without depending on a secondary branch.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

POLICY_PATH = Path("config/marketplace-policy.json")
RETIRED_CONTEXT_BRANCH = "full" + "repo"
FORBIDDEN_POLICY_KEYS = {
    RETIRED_CONTEXT_BRANCH,
    f"{RETIRED_CONTEXT_BRANCH}_branch",
    "agent_only_path_globs",
}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not POLICY_PATH.is_file():
        print("SKIP config/marketplace-policy.json absent")
        return 0
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    forbidden = sorted(FORBIDDEN_POLICY_KEYS & set(policy))
    if forbidden:
        fail(f"legacy secondary-context policy key(s) present: {forbidden}")
    tracked = policy.get("tracked_context_globs")
    if not isinstance(tracked, list) or "AGENTS.md" not in tracked or ".serena/memories/**" not in tracked:
        fail("tracked_context_globs must include AGENTS.md and .serena/memories/**")
    if RETIRED_CONTEXT_BRANCH in policy.get("protected_branches", []):
        fail("protected_branches must not include retired secondary context branch")

    expected_mcp_owner = policy.get("mcp_owner")
    mcp_files = sorted(Path("plugins").glob("*/.mcp.json"))
    if len(mcp_files) != 1:
        fail(f".mcp.json ownership: expected exactly 1 file, found {len(mcp_files)}")
    actual_mcp_owner = mcp_files[0].parent.name
    if expected_mcp_owner and actual_mcp_owner != expected_mcp_owner:
        fail(f".mcp.json owner drift: expected {expected_mcp_owner}, found {actual_mcp_owner}")

    expected_hooks = set(policy.get("hook_owners", []))
    actual_hooks = {path.parent.parent.name for path in Path("plugins").glob("*/hooks/hooks.json")}
    if actual_hooks != expected_hooks:
        fail(f"hooks.json owner drift: expected {sorted(expected_hooks)}, found {sorted(actual_hooks)}")

    deps = policy.get("plugin_dependencies", {})
    failures: list[str] = []
    for plugin_dir in sorted(Path("plugins").iterdir()):
        if not plugin_dir.is_dir():
            continue
        manifest = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest.is_file():
            failures.append(f"{plugin_dir.name}: missing .claude-plugin/plugin.json")
            continue
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("name") != plugin_dir.name:
            failures.append(f"{plugin_dir.name}: manifest name drift {data.get('name')!r}")
        expected = sorted(deps.get(plugin_dir.name, []))
        actual = sorted(data.get("dependencies", []))
        if actual != expected:
            failures.append(f"{plugin_dir.name}: dependency drift expected={expected} actual={actual}")
    if failures:
        for item in failures:
            print(item, file=sys.stderr)
        return 1
    print("ok: marketplace boundaries valid; durable AI context tracked on main")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
