#!/usr/bin/env python3
"""validate_boundaries.py - plugin ownership boundary enforcement.

Reads `config/marketplace-policy.json` (the canonical invariant database)
and verifies at HEAD that the actual repository structure matches the
declared boundaries:

  1. mcp_owner: exactly one plugin owns a `.mcp.json` file, and its
     directory name matches `policy.mcp_owner`. The .mcp.json file is a
     transport-layer artifact; spreading it across multiple plugins
     defeats the single-source-of-truth contract that makes pinning,
     drift detection, and capability smoke meaningful.

  2. hook_owners: the set of plugins owning `hooks/hooks.json` matches
     `policy.hook_owners` exactly (no extras, no missing). Hooks are
     advisory enforcement gates that run in the user session; only the
     two flow-control plugins should ship them.

  3. plugin.json self-consistency: the `name` field matches the directory
     name (catches accidental copy-paste during plugin scaffolding).

  4. plugin.json dependencies parity: `data.get("dependencies", [])`
     matches `policy.plugin_dependencies[<plugin>]` exactly (sorted).
     Catches drift where a plugin gains/loses a dependency without
     updating the policy file, which is the source of truth for the
     dependency graph documented in ADR-0006.

Closes the ADR-0006 self-acknowledged gap: the Confirmation section
previously stated "a future validate_boundaries.py (not yet implemented)
will enforce them" - this script is that implementation.

SKIPs gracefully (exit 0) if config/marketplace-policy.json is absent so
the harness keeps moving forward on a fresh checkout that has not yet
shipped the policy file.

Exit codes: 0 clean (or SKIP), 1 on any boundary violation.

Companion to validate_plugin_versions.py (version parity) and
validate_release_state.py (release-cycle parity). This script covers
structural boundaries - what's where, not what version it is.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

POLICY_PATH = Path("config/marketplace-policy.json")


def _load_policy(root: Path) -> dict[str, object] | None:
    policy_file = root / POLICY_PATH
    if not policy_file.is_file():
        return None
    return json.loads(policy_file.read_text(encoding="utf-8"))


def _check_mcp_owner(root: Path, expected_owner: str | None, failures: list[str]) -> None:
    mcp_files = sorted((root / "plugins").glob("*/.mcp.json"))
    if len(mcp_files) != 1:
        failures.append(
            f".mcp.json ownership: expected exactly 1 file (owner: {expected_owner!r}), "
            f"found {len(mcp_files)} at {[str(f.relative_to(root)) for f in mcp_files]}"
        )
        return
    actual_owner = mcp_files[0].parent.name
    if expected_owner is not None and actual_owner != expected_owner:
        failures.append(
            f".mcp.json ownership: declared owner is {expected_owner!r} but file lives "
            f"under plugins/{actual_owner}/"
        )


def _check_hook_owners(
    root: Path, expected_owners: set[str], failures: list[str]
) -> None:
    hooks_files = sorted((root / "plugins").glob("*/hooks/hooks.json"))
    actual_owners = {f.parent.parent.name for f in hooks_files}
    extra = actual_owners - expected_owners
    missing = expected_owners - actual_owners
    if extra:
        failures.append(
            f"hooks.json ownership: unexpected owners {sorted(extra)} (not declared in "
            f"policy.hook_owners={sorted(expected_owners)})"
        )
    if missing:
        failures.append(
            f"hooks.json ownership: missing owners {sorted(missing)} (declared in "
            f"policy.hook_owners but no hooks/hooks.json found)"
        )


def _check_plugin_manifests(
    root: Path,
    plugin_dependencies: dict[str, list[str]],
    failures: list[str],
) -> None:
    for plugin_dir in sorted((root / "plugins").iterdir()):
        if not plugin_dir.is_dir():
            continue
        manifest = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest.is_file():
            failures.append(f"{plugin_dir.name}: missing .claude-plugin/plugin.json")
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{plugin_dir.name}: plugin.json is not valid JSON: {exc}")
            continue
        name = data.get("name")
        if name != plugin_dir.name:
            failures.append(
                f"{plugin_dir.name}: plugin.json name={name!r} differs from directory name"
            )
            continue
        # Per the 0.5.0 schema expansion, each dependency item may be either
        # a bare string ("rldyour-mcps") OR a {name, version} object. Normalize
        # both forms to the plugin name before comparison.
        raw_deps = data.get("dependencies", [])
        if isinstance(raw_deps, list):
            actual_names: list[str] = []
            for item in raw_deps:
                if isinstance(item, dict):
                    nm = item.get("name")
                    if isinstance(nm, str):
                        actual_names.append(nm)
                elif isinstance(item, str):
                    actual_names.append(item)
            actual_deps = sorted(actual_names)
        else:
            actual_deps = []
        expected_deps = sorted(plugin_dependencies.get(name, []))
        if actual_deps != expected_deps:
            failures.append(
                f"{name}: dependencies drift - plugin.json={actual_deps} vs "
                f"policy.plugin_dependencies={expected_deps}"
            )


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    policy = _load_policy(root)
    if policy is None:
        print(f"SKIP {POLICY_PATH} not present; boundary enforcement disabled")
        return 0

    failures: list[str] = []

    mcp_owner = policy.get("mcp_owner")
    if not isinstance(mcp_owner, str | type(None)):
        failures.append(
            f"policy.mcp_owner must be a string or null, got {type(mcp_owner).__name__}"
        )
        mcp_owner = None
    _check_mcp_owner(root, mcp_owner, failures)

    raw_hook_owners = policy.get("hook_owners", [])
    if not isinstance(raw_hook_owners, list):
        failures.append(
            f"policy.hook_owners must be a list, got {type(raw_hook_owners).__name__}"
        )
        raw_hook_owners = []
    hook_owners = {str(h) for h in raw_hook_owners}
    _check_hook_owners(root, hook_owners, failures)

    raw_plugin_deps = policy.get("plugin_dependencies", {})
    if not isinstance(raw_plugin_deps, dict):
        failures.append(
            f"policy.plugin_dependencies must be an object, "
            f"got {type(raw_plugin_deps).__name__}"
        )
        raw_plugin_deps = {}
    # Per `config/schemas/plugin.json` (0.5.0 expansion), each dependency item
    # may be either a bare string ("rldyour-mcps") OR a {name, version} object.
    # Normalize both forms to the plugin name for comparison against
    # policy.plugin_dependencies (which holds plain strings).
    def _dep_name(d: object) -> str:
        if isinstance(d, dict):
            name = d.get("name")
            return str(name) if isinstance(name, str) else ""
        return str(d)

    plugin_deps: dict[str, list[str]] = {
        str(k): [_dep_name(d) for d in v if _dep_name(d)] if isinstance(v, list) else []
        for k, v in raw_plugin_deps.items()
    }
    _check_plugin_manifests(root, plugin_deps, failures)

    if failures:
        for line in failures:
            print(f"FAIL {line}", file=sys.stderr)
        print(
            f"\nTotal: {len(failures)} boundary violation(s).", file=sys.stderr
        )
        return 1

    print(
        f"OK boundaries: mcp_owner={mcp_owner!r}, "
        f"hook_owners={sorted(hook_owners)}, "
        f"{len(plugin_deps)} plugin dependency contract(s) verified"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
