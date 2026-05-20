#!/usr/bin/env python3
"""validate_plugin_versions.py - verify plugin.json vs marketplace.json version consistency.

Per Claude Code docs (code.claude.com/docs/en/plugins-reference#metadata-fields):
"If `version` is also set in the marketplace entry, the `plugin.json` value
takes precedence."

This script enforces the practical safer rule: if both are set, they must match.
Any drift between marketplace.json and plugin.json forces an explicit decision -
either drop the marketplace entry's version (rely on plugin.json) or update both.

Exit codes: 0 on success, 1 on any mismatch or missing version.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


EXPECTED_LICENSE = "AGPL-3.0-or-later"
EXPECTED_AUTHOR = "Danil Silantyev (github:rldyourmnd), CEO & Engineer NDDev"


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    if not marketplace_path.is_file():
        print(f"FAIL marketplace manifest missing: {marketplace_path}", file=sys.stderr)
        return 1

    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list):
        print("FAIL marketplace.json: 'plugins' is not a list", file=sys.stderr)
        return 1

    fail = 0
    seen_names: set[str] = set()
    for entry in entries:
        name = entry.get("name")
        if not name:
            print("FAIL marketplace entry missing 'name'", file=sys.stderr)
            fail = 1
            continue
        if name in seen_names:
            print(f"FAIL marketplace entry duplicate name: {name}", file=sys.stderr)
            fail = 1
            continue
        seen_names.add(name)

        source = entry.get("source", "")
        if not isinstance(source, str) or not source.startswith("./"):
            print(f"FAIL {name}: source must be a local relative path under ./plugins/, got {source!r}", file=sys.stderr)
            fail = 1
            continue

        plugin_dir = (root / source).resolve()
        plugin_manifest = plugin_dir / ".claude-plugin" / "plugin.json"
        if not plugin_manifest.is_file():
            print(f"FAIL {name}: plugin.json missing at {plugin_manifest}", file=sys.stderr)
            fail = 1
            continue

        plugin_data = json.loads(plugin_manifest.read_text(encoding="utf-8"))

        if plugin_data.get("name") != name:
            print(
                f"FAIL {name}: plugin.json name {plugin_data.get('name')!r} "
                f"does not match marketplace entry {name!r}",
                file=sys.stderr,
            )
            fail = 1
            continue

        marketplace_version = entry.get("version")
        plugin_version = plugin_data.get("version")

        if not plugin_version:
            print(f"FAIL {name}: plugin.json missing 'version'", file=sys.stderr)
            fail = 1
            continue

        if marketplace_version is not None and marketplace_version != plugin_version:
            print(
                f"FAIL {name}: marketplace.json version {marketplace_version!r} "
                f"differs from plugin.json {plugin_version!r}. "
                f"Per docs, plugin.json wins; align both or drop marketplace 'version'.",
                file=sys.stderr,
            )
            fail = 1
            continue

        if entry.get("license") != EXPECTED_LICENSE:
            print(
                f"FAIL {name}: marketplace license {entry.get('license')!r} "
                f"must be {EXPECTED_LICENSE!r}",
                file=sys.stderr,
            )
            fail = 1
            continue

        entry_author = entry.get("author")
        if not isinstance(entry_author, dict) or entry_author.get("name") != EXPECTED_AUTHOR:
            print(f"FAIL {name}: marketplace author must be {EXPECTED_AUTHOR!r}", file=sys.stderr)
            fail = 1
            continue

        if plugin_data.get("license") != EXPECTED_LICENSE:
            print(
                f"FAIL {name}: plugin.json license {plugin_data.get('license')!r} "
                f"must be {EXPECTED_LICENSE!r}",
                file=sys.stderr,
            )
            fail = 1
            continue

        plugin_author = plugin_data.get("author")
        if not isinstance(plugin_author, dict) or plugin_author.get("name") != EXPECTED_AUTHOR:
            print(f"FAIL {name}: plugin.json author must be {EXPECTED_AUTHOR!r}", file=sys.stderr)
            fail = 1
            continue

        print(f"OK {name}: version={plugin_version}")

    return fail


if __name__ == "__main__":
    sys.exit(main())
