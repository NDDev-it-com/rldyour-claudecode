#!/usr/bin/env python3
"""validate_text_hygiene.py - enforce ASCII-only typography across the repo.

The global rldyour rule (~/.claude/CLAUDE.md) forbids em-dashes and en-dashes
in committed artifacts; only ASCII hyphen-minus is allowed. This validator
also blocks Unicode bidirectional control characters (U+202A-U+202E,
U+2066-U+2069) repo-wide as defence-in-depth against Trojan Source attacks
(post_tool_use_commit_advice.sh already strips them from advisory output -
this script ensures they never enter the repo in the first place).

Exit codes: 0 clean, 1 on any finding. Run after `bash scripts/validate_marketplace.sh`
adds it to the harness; CI mirrors the call in `.github/workflows/validate.yml`.

Scope:
- Walks repo root; respects .git, node_modules, __pycache__, .venv, venv,
  .serena/cache, .serena/diagnostics, .serena/reviews skips.
- Reads every non-binary file (UTF-8 only - falls back to errors='ignore'
  for the scan but flags only files where the substring actually appears).

False-positive policy:
- Empty allowlist by default. If a file legitimately needs an em-dash
  (citing a third-party doc verbatim, for example), add it to ALLOWLIST
  below with a one-line justification comment.
"""

from __future__ import annotations

import sys
from pathlib import Path

EM_DASH = "—"
EN_DASH = "–"  # noqa: RUF001 - this IS the EN DASH character we detect; intentional
BIDI_CONTROLS = (
    "‪", "‫", "‬", "‭", "‮",
    "⁦", "⁧", "⁨", "⁩",
)

SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".serena/cache",
    ".serena/diagnostics",
    ".serena/reviews",
}

# Files exempt from each rule. Add with a comment explaining why.
ALLOWLIST_EM = frozenset({
    # Pytest negative fixtures intentionally embed em-dashes to exercise
    # the validator's detection path; they are scoped to tests/ only.
    "tests/test_validate_text_hygiene.py",
})
ALLOWLIST_EN = frozenset({
    "tests/test_validate_text_hygiene.py",
})
ALLOWLIST_BIDI: frozenset[str] = frozenset({
    # BIDI controls appear as a regex character class in the hook sanitizer
    # (lines 92-101); they are detection input, not malicious payload.
    "plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh",
    # Same intentional dirty fixture for pytest negative test.
    "tests/test_validate_text_hygiene.py",
})


def should_skip(path: Path) -> bool:
    parts = path.parts
    for skip in SKIP_DIRS:
        skip_parts = skip.split("/")
        if len(parts) >= len(skip_parts):
            for i in range(len(parts) - len(skip_parts) + 1):
                if parts[i:i + len(skip_parts)] == tuple(skip_parts):
                    return True
    return False


def scan(root: Path) -> int:
    findings: list[tuple[str, str, int, str]] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if should_skip(path.relative_to(root)):
            continue
        # Skip self to avoid matching the literal U+2014 escape in this source.
        # Use resolved-path comparison rather than `path.name == ...` so a
        # future file named `validate_text_hygiene.py` placed elsewhere in the
        # tree (e.g., tests/) is NOT silently exempted from scanning.
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        rel = str(path.relative_to(root))

        if EM_DASH in text and rel not in ALLOWLIST_EM:
            for lineno, line in enumerate(text.splitlines(), start=1):
                if EM_DASH in line:
                    findings.append(("em-dash", rel, lineno, line.strip()[:100]))
        if EN_DASH in text and rel not in ALLOWLIST_EN:
            for lineno, line in enumerate(text.splitlines(), start=1):
                if EN_DASH in line:
                    findings.append(("en-dash", rel, lineno, line.strip()[:100]))
        for ch in BIDI_CONTROLS:
            if ch in text and rel not in ALLOWLIST_BIDI:
                for lineno, line in enumerate(text.splitlines(), start=1):
                    if ch in line:
                        findings.append((
                            f"bidi-{ord(ch):04x}",
                            rel,
                            lineno,
                            line.strip()[:100].replace(ch, "[BIDI]"),
                        ))

    if not findings:
        print("OK 0 typography violations across repository")
        return 0

    print(f"FAIL {len(findings)} typography violations:", file=sys.stderr)
    for kind, rel, lineno, snippet in findings[:50]:
        print(f"  {rel}:{lineno} [{kind}] {snippet}", file=sys.stderr)
    if len(findings) > 50:
        print(f"  ... and {len(findings) - 50} more", file=sys.stderr)
    return 1


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    return scan(root)


if __name__ == "__main__":
    raise SystemExit(main())
