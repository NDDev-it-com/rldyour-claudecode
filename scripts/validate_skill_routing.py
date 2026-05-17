#!/usr/bin/env python3
"""validate_skill_routing.py - assert skill description coverage for routing policy.

Reads `config/skill-routing-policy.json` and for each test case verifies:
  1. The referenced skill exists at `plugins/<plugin>/skills/<skill>/SKILL.md`.
  2. The skill's frontmatter `description` (and optional `when_to_use`)
     contains every term in `description_terms` (case-insensitive substring).

This is the deterministic counterpart to model-based skill triggering: if a
user types a phrase from `prompt_terms`, the skill descriptions covering that
prompt must contain matching words. Drift here means Claude Code can no longer
reliably auto-trigger the skill for those Russian/English phrases.

Exit codes: 0 success, 1 on any missing skill or missing term.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def load_skill_text(plugin_skill: str, root: Path) -> str | None:
    """Read SKILL.md text for `plugin:skill` reference."""
    if ":" not in plugin_skill:
        return None
    plugin, skill = plugin_skill.split(":", 1)
    path = root / "plugins" / plugin / "skills" / skill / "SKILL.md"
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def extract_description(skill_text: str) -> str:
    """Return concatenated frontmatter description + when_to_use for term search."""
    match = FRONTMATTER_RE.search(skill_text)
    if not match:
        return ""
    frontmatter = match.group(1)
    parts: list[str] = []

    desc_match = re.search(r"^description:\s*(.+?)(?=\n\w|\Z)", frontmatter, re.DOTALL | re.MULTILINE)
    if desc_match:
        parts.append(desc_match.group(1).strip().strip('"').strip("'"))

    when_match = re.search(r"^when_to_use:\s*(.+?)(?=\n\w|\Z)", frontmatter, re.DOTALL | re.MULTILINE)
    if when_match:
        parts.append(when_match.group(1).strip().strip('"').strip("'"))

    return " ".join(parts).lower()


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    policy_path = root / "config" / "skill-routing-policy.json"
    if not policy_path.is_file():
        print(f"FAIL missing {policy_path}", file=sys.stderr)
        return 1

    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    cases = policy.get("cases", [])
    if not isinstance(cases, list):
        print("FAIL skill-routing-policy.json: 'cases' must be a list", file=sys.stderr)
        return 1

    fail = 0
    for case in cases:
        case_id = case.get("id", "<unknown>")
        expected = case.get("expected", [])
        if not isinstance(expected, list):
            print(f"FAIL {case_id}: 'expected' must be a list", file=sys.stderr)
            fail = 1
            continue

        for exp in expected:
            skill_ref = exp.get("skill")
            terms = exp.get("description_terms", [])
            if not skill_ref or not terms:
                print(f"FAIL {case_id}: skill or description_terms missing", file=sys.stderr)
                fail = 1
                continue

            skill_text = load_skill_text(skill_ref, root)
            if skill_text is None:
                print(f"FAIL {case_id}/{skill_ref}: SKILL.md not found", file=sys.stderr)
                fail = 1
                continue

            haystack = extract_description(skill_text)
            missing = [t for t in terms if t.lower() not in haystack]
            if missing:
                print(
                    f"FAIL {case_id}/{skill_ref}: description missing terms {missing}",
                    file=sys.stderr,
                )
                fail = 1
                continue

            print(f"OK {case_id}/{skill_ref}: all {len(terms)} terms matched")

    return fail


if __name__ == "__main__":
    sys.exit(main())
