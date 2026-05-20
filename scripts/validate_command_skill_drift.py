#!/usr/bin/env python3
"""validate_command_skill_drift.py - enforce that skill-backed slash commands
stay thin wrappers.

Claude Code merged custom commands into skills (May 2026 docs). When a command
and a same-named skill ship together, the skill is the source of truth and the
command must be a thin delegation wrapper. Otherwise the two bodies drift and
the model receives contradictory guidance.

Invariants enforced when a command either:

  - has the same basename as an existing skill, OR
  - delegates to an existing skill through ``Use the `<skill-name>` skill``.

  1. Command file body (after frontmatter) is at most ``MAX_COMMAND_BODY`` chars.
  2. Command body contains the literal ``Use the `<skill-name>` skill`` so the
     model is routed to the delegated skill, not to inline instructions.
  3. Command body does not duplicate skill workflow with self-headings
     (``Workflow``, ``Rules``, ``Quality gates`` etc.).
  4. Command body does not contain numbered checklists longer than 3 items.

Commands that have NO matching/delegated skill (e.g. ``ry-explore`` is a
command + agent pattern, not command + skill) are skipped silently.

Exit code: 0 on PASS, 1 on FAIL, 2 on internal error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MAX_COMMAND_BODY = 800  # chars in the body (frontmatter excluded)
ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN_HEADINGS = (
    "Workflow",
    "Rules",
    "Quality gates",
    "Non-negotiables",
    "Anti-patterns",
    "Subagent Permission",
    "Review Phase",
    "Tracks",
    "Implementation",
    "Steps",
)
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
USE_SKILL_RE = re.compile(r"Use the `([a-z][a-z0-9-]*)` skill", re.IGNORECASE)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
NUMBERED_LIST_ITEM_RE = re.compile(r"^\s{0,3}\d+\.\s+\S", re.MULTILINE)


def strip_frontmatter(text: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if match:
        return text[match.end():]
    return text


def find_commands() -> list[Path]:
    return sorted(ROOT.glob("plugins/*/commands/*.md"))


def find_skills() -> set[str]:
    return {p.parent.name for p in ROOT.glob("plugins/*/skills/*/SKILL.md")}


def longest_consecutive_numbered_list(text: str) -> int:
    """Return the length of the longest run of consecutive numbered list items.

    A run is broken by ANY non-numbered-list line, including blank lines.
    Two adjacent numbered lists separated by a blank line count as two runs,
    not one merged streak. This matches Markdown's notion of a tight list
    block (per CommonMark: a blank line between list items terminates the
    block unless the next item is also a list item with deeper indentation).
    """
    longest = 0
    current = 0
    for line in text.splitlines():
        if NUMBERED_LIST_ITEM_RE.match(line):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def validate_command(path: Path, skill_names: set[str]) -> list[str]:
    """Return a list of failure messages for the command; empty = PASS."""
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    body = strip_frontmatter(text)
    name = path.stem

    skill_ref = USE_SKILL_RE.search(body)
    delegated_skill = skill_ref.group(1) if skill_ref else None
    target_skill = name if name in skill_names else delegated_skill

    if target_skill not in skill_names:
        # Command without a matching/delegated skill (e.g. command + agent pattern). Skip.
        return []

    if len(body) > MAX_COMMAND_BODY:
        failures.append(
            f"body is {len(body)} chars; thin-wrapper cap is {MAX_COMMAND_BODY}"
        )

    if not skill_ref:
        failures.append(
            f"missing literal 'Use the `{target_skill}` skill' delegation phrase"
        )
    elif skill_ref.group(1) != target_skill:
        failures.append(
            f"delegation phrase points to '{skill_ref.group(1)}' "
            f"but expected '{target_skill}'"
        )

    for heading_match in HEADING_RE.finditer(body):
        heading = heading_match.group(1).strip().rstrip(":")
        for forbidden in FORBIDDEN_HEADINGS:
            if heading.lower() == forbidden.lower():
                failures.append(
                    f"forbidden heading '{heading}' duplicates skill workflow"
                )

    longest_list = longest_consecutive_numbered_list(body)
    if longest_list > 3:
        failures.append(
            f"numbered checklist length {longest_list} exceeds limit 3 "
            f"(move detailed steps into the skill body)"
        )

    return failures


def main() -> int:
    try:
        skill_names = find_skills()
    except OSError as exc:
        print(f"FAIL internal error listing skills: {exc}", file=sys.stderr)
        return 2

    commands = find_commands()
    if not commands:
        print("SKIP no commands to validate")
        return 0

    any_failure = False
    skipped = 0
    for cmd in commands:
        name = cmd.stem
        rel = cmd.relative_to(ROOT)
        body = strip_frontmatter(cmd.read_text(encoding="utf-8"))
        skill_ref = USE_SKILL_RE.search(body)
        delegated_skill = skill_ref.group(1) if skill_ref else None
        target_skill = name if name in skill_names else delegated_skill
        if target_skill not in skill_names:
            print(f"SKIP {rel} (no matching skill - command-only pattern)")
            skipped += 1
            continue
        failures = validate_command(cmd, skill_names)
        if failures:
            any_failure = True
            # FAIL lines go to stderr for CI alert-channel consistency with
            # peer validators (security review F-5).
            for msg in failures:
                print(f"FAIL {rel}: {msg}", file=sys.stderr)
        else:
            print(
                f"OK {rel} (≤ {MAX_COMMAND_BODY} chars, "
                f"delegates to '{target_skill}' skill)"
            )

    if any_failure:
        return 1
    total = len(commands)
    validated = total - skipped
    print(f"\nOK {validated} thin-wrapper command(s) validated; {skipped} skipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
