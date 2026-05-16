#!/usr/bin/env python3
"""validate_instruction_docs.py — verify AGENTS.md and .claude/CLAUDE.md hygiene.

For the rldyour-claudecode marketplace these files are agent-only (live on the
`fullrepo` branch, excluded from `main` via `.git/info/exclude`). The validator
only inspects the worktree state — it does not require the files to be tracked
in the current branch.

Checks:
1. Both `AGENTS.md` and `.claude/CLAUDE.md` exist in the worktree (when
   --require-agent-docs is set).
2. Each file is non-empty and starts with a top-level heading.
3. Each file is under the Anthropic-recommended 200-line cap. Soft warning
   for 200..300 lines, hard fail at 300+ (Anthropic empirical guidance:
   adherence drops past ~200 lines).
4. No secret-looking strings in either file (lightweight scan against the
   patterns SECRET_RE in fullrepo_sync.py).

Exit codes: 0 success, 1 hard failure.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SECRET_PATTERNS = [
    re.compile(r"\bctx7sk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]{20,}\b"),
]

LINE_SOFT_CAP = 200
LINE_HARD_CAP = 300


def check_file(path: Path) -> tuple[int, list[str]]:
    if not path.is_file():
        return 1, [f"FAIL missing: {path}"]

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    issues: list[str] = []
    fail = 0

    if not text.strip():
        issues.append(f"FAIL empty: {path}")
        fail = 1

    if not text.lstrip().startswith("#"):
        issues.append(f"FAIL no top-level heading: {path}")
        fail = 1

    n = len(lines)
    if n > LINE_HARD_CAP:
        issues.append(f"FAIL {path}: {n} lines exceeds hard cap {LINE_HARD_CAP}")
        fail = 1
    elif n > LINE_SOFT_CAP:
        issues.append(f"WARN {path}: {n} lines exceeds soft cap {LINE_SOFT_CAP} (Anthropic recommends < 200)")

    for pattern in SECRET_PATTERNS:
        match = pattern.search(text)
        if match:
            sample = match.group(0)[:8] + "..."
            issues.append(f"FAIL {path}: secret-looking string detected ({sample})")
            fail = 1
            break

    if fail == 0 and not issues:
        issues.append(f"OK {path}: {n} lines")

    return fail, issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-agent-docs",
        action="store_true",
        help="Fail when AGENTS.md or .claude/CLAUDE.md is missing from the worktree.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    targets = [root / "AGENTS.md", root / ".claude" / "CLAUDE.md"]

    overall_fail = 0
    for target in targets:
        if not target.is_file():
            if args.require_agent_docs:
                print(f"FAIL missing required doc: {target}", file=sys.stderr)
                overall_fail = 1
            else:
                print(f"SKIP missing (not required): {target}")
            continue
        rc, issues = check_file(target)
        for line in issues:
            stream = sys.stderr if line.startswith("FAIL") else sys.stdout
            print(line, file=stream)
        overall_fail |= rc

    return overall_fail


if __name__ == "__main__":
    sys.exit(main())
