#!/usr/bin/env python3
"""validate_json_schemas.py - JSON Schema validation for marketplace artifacts.

Validates each JSON manifest in the repo against its local config/schemas/*
schema using the `jsonschema` Python package. Mappings:

  .claude-plugin/marketplace.json           -> config/schemas/marketplace.json
  plugins/*/.claude-plugin/plugin.json      -> config/schemas/plugin.json
  plugins/*/.mcp.json                       -> config/schemas/mcp.json
  plugins/*/.lsp.json                       -> config/schemas/lsp.json
  plugins/*/hooks/hooks.json                -> config/schemas/hooks.json

The check is additive to `claude plugin validate` (which already verifies
marketplace + plugin manifests) and to the existing `json.load()` parse step
- this validator catches structural drift in `.mcp.json`, `.lsp.json`, and
`hooks.json`, none of which are covered by Claude CLI validation.

Graceful SKIP when `jsonschema` is not importable (broken local install,
missing `attrs` transitive dep, etc.). CI installs `jsonschema attrs` in
the validate.yml job. Failure mode: print one line per failing file with
the validator path, stop on first error per file (`validate` raises).

Exit codes: 0 success / SKIP, 1 on validation failures.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema  # type: ignore[import-not-found]
    import jsonschema.validators  # type: ignore[import-not-found]
except ImportError as exc:
    print(f"SKIP jsonschema not importable ({exc}); install via `pip install jsonschema`")
    sys.exit(0)


SCHEMA_MAP: tuple[tuple[str, str], ...] = (
    (".claude-plugin/marketplace.json", "config/schemas/marketplace.json"),
    ("plugins/*/.claude-plugin/plugin.json", "config/schemas/plugin.json"),
    ("plugins/*/.mcp.json", "config/schemas/mcp.json"),
    ("plugins/*/.lsp.json", "config/schemas/lsp.json"),
    ("plugins/*/hooks/hooks.json", "config/schemas/hooks.json"),
)


def load_schema(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    failures: list[str] = []
    checked = 0

    for instance_glob, schema_rel in SCHEMA_MAP:
        schema_path = root / schema_rel
        if not schema_path.is_file():
            print(f"SKIP schema missing: {schema_rel}")
            continue
        schema = load_schema(schema_path)
        validator_cls = jsonschema.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        validator = validator_cls(schema, format_checker=jsonschema.FormatChecker())

        for instance_path in sorted(root.glob(instance_glob)):
            if not instance_path.is_file():
                continue
            checked += 1
            try:
                instance = json.loads(instance_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"{instance_path.relative_to(root)}: JSON parse error: {exc}")
                continue

            errors = list(validator.iter_errors(instance))
            if errors:
                # Report up to 3 errors per file to keep output focused.
                for err in errors[:3]:
                    path = "/".join(str(p) for p in err.absolute_path) or "<root>"
                    failures.append(
                        f"{instance_path.relative_to(root)} [{path}]: {err.message}"
                    )
                if len(errors) > 3:
                    failures.append(
                        f"{instance_path.relative_to(root)}: ... +{len(errors) - 3} more"
                    )
            else:
                print(f"OK {instance_path.relative_to(root)} -> {schema_rel}")

    if failures:
        print(f"\nFAIL {len(failures)} schema violation(s):", file=sys.stderr)
        for line in failures:
            print(f"  {line}", file=sys.stderr)
        return 1

    print(f"\nOK {checked} JSON manifest(s) validated against {len(SCHEMA_MAP)} schema(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
