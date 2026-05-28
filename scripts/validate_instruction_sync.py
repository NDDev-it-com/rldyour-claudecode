#!/usr/bin/env python3
"""validate_instruction_sync.py - semantic drift validator for dual-doc split.

Repo intentionally keeps both AGENTS.md (cross-tool) and .claude/CLAUDE.md
(Claude Code-deep) as first-class instruction files (no thin @import). The
existing validate_instruction_docs.py checks only presence + heading + line
cap + secret-like strings. This validator catches semantic drift between the
two files for a curated set of shared claims.

Contract: each file may contain one or more HTML-comment YAML blocks marked
with `sync_contract:`:

    <!-- sync_contract:
    claims:
      mcp_owner: rldyour-mcps
      hook_owners: [rldyour-flow, rldyour-serena-mcp]
      reviewer_transport_marker: RLDYOUR_REPORT_EOF
    -->

The validator extracts every `sync_contract` block from both files,
flattens claim keys, and asserts that for each key present in BOTH files
the values match exactly. Keys only present in one file are allowed (each
file can carry its own deep facts).

Graceful SKIP when neither file contains a `sync_contract` block (G15 ships
the initial blocks). After G15 the validator becomes enforcement.

Exit codes: 0 clean (or SKIP), 1 on any drift.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

AGENTS = Path("AGENTS.md")
CLAUDE = Path(".claude/CLAUDE.md")

CONTRACT_BLOCK_RE = re.compile(
    # `\s*` before `-->` tolerates indented closing tags (rare but valid
    # HTML-comment style); ensures docs with `  -->` still parse cleanly.
    r"<!--\s*sync_contract:\s*\n(.*?)\n\s*-->",
    re.DOTALL,
)


def extract_claims(text: str) -> dict[str, object]:
    """Extract and merge all sync_contract YAML blocks from `text`."""
    if yaml is None:
        return {}
    claims: dict[str, object] = {}
    for match in CONTRACT_BLOCK_RE.finditer(text):
        block = match.group(1)
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as exc:
            # Surface malformed sync_contract blocks to stderr per security
            # review F-5 (PHILOSOPHY-01-QUALITY-FIRST "no swallowed errors"
            # hard ban). The block is still skipped (control flow unchanged)
            # but the operator gets a diagnostic instead of silent failure.
            print(
                f"validate_instruction_sync: malformed sync_contract YAML "
                f"block (offset {match.start()}): {exc}",
                file=sys.stderr,
            )
            continue
        if not isinstance(data, dict):
            continue
        raw_claims = data.get("claims")
        if isinstance(raw_claims, dict):
            for key, value in raw_claims.items():
                claims[str(key)] = value
            continue
        for key, value in data.items():
            claims[str(key)] = value
    return claims


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    agents_path = root / AGENTS
    claude_path = root / CLAUDE

    if not agents_path.is_file() or not claude_path.is_file():
        print(f"SKIP {AGENTS} or {CLAUDE} missing (agent-only files may not be restored yet)")
        return 0

    if yaml is None:
        print("SKIP PyYAML not installed; install via `pip install pyyaml` to enable")
        return 0

    agents_claims = extract_claims(agents_path.read_text(encoding="utf-8"))
    claude_claims = extract_claims(claude_path.read_text(encoding="utf-8"))

    if not agents_claims and not claude_claims:
        print(f"SKIP no sync_contract blocks found in {AGENTS} or {CLAUDE} (G15 ships initial blocks)")
        return 0

    shared = set(agents_claims) & set(claude_claims)
    drift: list[str] = []
    for key in sorted(shared):
        a = agents_claims[key]
        c = claude_claims[key]
        if a != c:
            drift.append(f"{key}: AGENTS.md={a!r} vs .claude/CLAUDE.md={c!r}")

    if drift:
        print("FAIL semantic drift between AGENTS.md and .claude/CLAUDE.md:", file=sys.stderr)
        for line in drift:
            print(f"  {line}", file=sys.stderr)
        return 1

    print(
        f"OK {len(shared)} shared claim(s) match; "
        f"{len(agents_claims) - len(shared)} AGENTS-only; "
        f"{len(claude_claims) - len(shared)} CLAUDE-only"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
