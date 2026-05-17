#!/usr/bin/env python3
"""validate_docs_canon.py - detect stale Claude Code terminology in docs.

Reads `config/cc-canon.json` (canonical terminology database) and flags any
file under docs/, README.md, AGENTS.md, .claude/CLAUDE.md, plugins/*/README.md,
or .serena/memories/*.md that contains a `forbidden_token` (deprecated name)
or asserts a wrong `version_floor` for a known knob.

Designed to catch drift like:
- `skillListingMaxDescChars` (forbidden; canonical: `maxSkillDescriptionChars`)
- `claude plugin tag --push" added in CC v2.1.119` (forbidden; correct: v2.1.118)

Graceful SKIP if `config/cc-canon.json` does not yet exist - the canon file
ships in G9 of release 0.3.0. After G9 the validator becomes enforcement.

Exit codes: 0 clean (or SKIP), 1 on any drift.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CANON_PATH = Path("config/cc-canon.json")

TARGET_GLOBS = (
    "README.md",
    "AGENTS.md",
    ".claude/CLAUDE.md",
    "docs/**/*.md",
    "plugins/*/README.md",
    ".serena/memories/*.md",
)


def discover_targets(root: Path) -> list[Path]:
    out: list[Path] = []
    for pattern in TARGET_GLOBS:
        for path in root.glob(pattern):
            if path.is_file():
                out.append(path)
    return sorted(set(out))


def check_forbidden(text: str, tokens: dict[str, str]) -> list[tuple[str, str]]:
    """Return (token, replacement) pairs for any forbidden token present."""
    return [(tok, repl) for tok, repl in tokens.items() if tok in text]


def check_version_floors(
    text: str, floors: dict[str, dict[str, str]]
) -> list[tuple[str, str, str]]:
    """Detect wrong "v2.1.XXX" assertions for a known knob.

    `floors` maps knob name -> {`floor`: "v2.1.105+", `wrong_floors`:
    ["v2.1.128", "v2.1.129"]}. Direct-association heuristic: flag only when
    a known wrong-floor token is *the immediately following parenthetical*
    after the knob (no other version token between them), or when the
    knob appears within 30 chars of the wrong-floor token.

    Tight matching avoids false positives in compatibility-floor paragraphs
    where many knobs and many versions co-occur in a long enumeration.
    """
    findings: list[tuple[str, str, str]] = []
    # Pattern: any "v2.1.XXX" token, possibly with trailing "+"
    version_token = re.compile(r"v\d+\.\d+\.\d+\+?")

    for knob, spec in floors.items():
        if knob not in text:
            continue
        correct = spec.get("floor", "")
        for wrong in spec.get("wrong_floors", []):
            wrong_pattern = re.escape(wrong) + r"\+?"
            for match in re.finditer(wrong_pattern, text):
                start = match.start()
                # Look back 30 chars for the knob; if any intervening
                # version token sits between the knob and `wrong`, the wrong
                # version is associated with the intervening token, not the
                # knob - skip it.
                window_start = max(0, start - 30)
                window = text[window_start:start]
                knob_pos = window.rfind(knob)
                if knob_pos == -1:
                    continue
                between = window[knob_pos + len(knob):]
                if version_token.search(between):
                    # Another version is between knob and wrong - not directly associated.
                    continue
                findings.append((knob, wrong, correct))
    return findings


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    canon_file = root / CANON_PATH
    if not canon_file.is_file():
        print(f"SKIP {CANON_PATH} not yet present (G9 will ship it); validator disabled")
        return 0
    try:
        canon = json.loads(canon_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL {CANON_PATH} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    forbidden_tokens: dict[str, str] = canon.get("forbidden_tokens", {})
    version_floors: dict[str, dict[str, str]] = canon.get("version_floors", {})

    failures: list[str] = []
    targets = discover_targets(root)

    for path in targets:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        rel = str(path.relative_to(root))

        for token, repl in check_forbidden(text, forbidden_tokens):
            failures.append(f"{rel}: forbidden token `{token}` (use `{repl}` instead)")
        for knob, wrong, correct in check_version_floors(text, version_floors):
            failures.append(
                f"{rel}: knob `{knob}` cited with wrong floor `{wrong}` "
                f"(canonical: `{correct}`)"
            )

    if failures:
        for line in failures:
            print(f"FAIL {line}", file=sys.stderr)
        print(f"\nTotal: {len(failures)} canon drift(s) across {len(targets)} target(s).",
              file=sys.stderr)
        return 1

    print(f"OK 0 canon drift(s) across {len(targets)} target file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
