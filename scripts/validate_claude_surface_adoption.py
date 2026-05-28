#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "references" / "claude-baseline.json"
ADOPTION = ROOT / "references" / "claude-surface-adoption.md"

REQUIRED_BASELINE_SURFACES = {
    "skill-and-slash-command-disallowed-tools-frontmatter": "`disallowed-tools`",
    "sessionstart-reloadskills-output": "`SessionStart.reloadSkills`",
    "message-display-hook-event": "`MessageDisplay`",
    "auto-mode-explicit-ask-user-question": "AskUserQuestion",
}

REQUIRED_2_1_153_SURFACES = (
    "`skipLfs`",
    "`/doctor`",
    "`COLUMNS`",
    "`claude agents`",
)

VALID_DECISIONS = ("Adopt", "Adopted", "Future", "Intentionally unused")


def main() -> int:
    errors: list[str] = []
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    version = baseline.get("baseline", {}).get("claude_code", {}).get("version")
    required = baseline.get("baseline", {}).get("required_runtime_fixes") or []
    text = ADOPTION.read_text(encoding="utf-8") if ADOPTION.is_file() else ""

    if not text:
        errors.append(f"{ADOPTION.relative_to(ROOT)} is missing")
    for key in required:
        expected = REQUIRED_BASELINE_SURFACES.get(key)
        if expected and expected not in text:
            errors.append(f"{ADOPTION.relative_to(ROOT)} missing decision for {key}")

    if version == "2.1.153":
        for marker in REQUIRED_2_1_153_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.153 surface {marker}")

    for line in text.splitlines():
        if not line.startswith("| `") and not line.startswith("| `/"):
            continue
        if not any(f"| {decision}" in line for decision in VALID_DECISIONS):
            errors.append(f"{ADOPTION.relative_to(ROOT)} row lacks an explicit adoption decision: {line}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Claude surface adoption decisions validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
