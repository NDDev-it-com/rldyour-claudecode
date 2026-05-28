#!/usr/bin/env python3
"""validate_instruction_docs.py - verify AGENTS.md and .claude/CLAUDE.md hygiene.

For the rldyour-claudecode marketplace these files are agent-only (live on the
`fullrepo` branch, excluded from `main` via `.git/info/exclude`). The validator
only inspects the worktree state - it does not require the files to be tracked
in the current branch.

Checks:
1. Both `AGENTS.md` and `.claude/CLAUDE.md` exist in the worktree (when
   --require-agent-docs is set).
2. Each file is non-empty and starts with a top-level heading.
3. Each file is under the Anthropic-recommended 200-line cap. Soft warning
   for 200..300 lines, hard fail at 300+ (Anthropic empirical guidance:
   adherence drops past ~200 lines).
4. Active version/count claims match package, baseline, runtime-env, and
   filesystem inventory.
5. No secret-looking strings in either file (lightweight scan against the
   patterns SECRET_RE in fullrepo_sync.py).

Exit codes: 0 success, 1 hard failure.
"""

from __future__ import annotations

import argparse
import json
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
FEATURE_FLOOR = "2.1.146"

ACTIVE_STALE_CLAIMS = (
    "claude_code_min_version:",
    "Minimum Claude Code: v2.1.145",
    "Current local CC: **v2.1.145**",
    "pins CI/local floor to 2.1.145",
)


def read_package_pin(root: Path) -> str:
    data = json.loads((root / "package.json").read_text(encoding="utf-8"))
    return data["devDependencies"]["@anthropic-ai/claude-code"]


def read_baseline_pin(root: Path) -> str:
    data = json.loads((root / "references" / "claude-baseline.json").read_text(encoding="utf-8"))
    return data["baseline"]["claude_code"]["version"]


def read_env_pin(root: Path) -> str:
    env_path = root / "config" / "mcp-runtime-versions.env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("CLAUDE_CODE_MIN_VERSION="):
            return line.split("=", 1)[1].strip()
    raise ValueError(f"missing CLAUDE_CODE_MIN_VERSION in {env_path}")


def inventory_counts(root: Path) -> dict[str, int]:
    return {
        "plugin_count": sum(1 for path in (root / "plugins").iterdir() if path.is_dir()),
        "skill_count": sum(1 for _ in root.glob("plugins/*/skills/*/SKILL.md")),
        "command_count": sum(1 for _ in root.glob("plugins/*/commands/*.md")),
        "subagent_count": sum(1 for _ in root.glob("plugins/*/agents/*.md")),
    }


def check_runtime_sources(root: Path) -> tuple[int, list[str], str]:
    issues: list[str] = []
    try:
        package_pin = read_package_pin(root)
        baseline_pin = read_baseline_pin(root)
        env_pin = read_env_pin(root)
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        issues.append(f"FAIL runtime pin source unreadable: {exc}")
        return 1, issues, ""
    pins = {
        "package.json": package_pin,
        "references/claude-baseline.json": baseline_pin,
        "config/mcp-runtime-versions.env": env_pin,
    }
    if len(set(pins.values())) != 1:
        for source, version in pins.items():
            issues.append(f"FAIL runtime pin mismatch: {source} -> {version}")
        return 1, issues, package_pin
    issues.append(f"OK runtime pin parity: Claude Code {package_pin}")
    return 0, issues, package_pin


def check_file(path: Path, root: Path, runtime_pin: str, counts: dict[str, int]) -> tuple[int, list[str]]:
    if not path.is_file():
        return 1, [f"FAIL missing: {path}"]

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    issues: list[str] = []
    fail = 0

    if not text.strip():
        issues.append(f"FAIL empty: {path}")
        fail = 1

    is_markdown_doc = path.suffix.lower() == ".md"

    if is_markdown_doc and not text.lstrip().startswith("#"):
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

    for stale in ACTIVE_STALE_CLAIMS:
        if stale in text:
            issues.append(f"FAIL {path}: stale active Claude Code claim {stale!r}")
            fail = 1

    if path.name in {"AGENTS.md", "CLAUDE.md"} and "sync_contract:" in text:
        expected_claims = {
            "claude_code_runtime_pin": runtime_pin,
            "claude_code_feature_floor": FEATURE_FLOOR,
        }
        for key, expected in expected_claims.items():
            if f'{key}: "{expected}"' not in text:
                issues.append(f"FAIL {path}: sync_contract missing {key}: {expected!r}")
                fail = 1
        for key, expected_count in counts.items():
            if f"{key}: {expected_count}" not in text:
                issues.append(f"FAIL {path}: sync_contract {key} does not match inventory ({expected_count})")
                fail = 1

    if path.match("*/.github/ISSUE_TEMPLATE/bug_report.yml"):
        if f'placeholder: "{runtime_pin}"' not in text:
            issues.append(f"FAIL {path}: bug-report Claude Code placeholder must match runtime pin {runtime_pin}")
            fail = 1

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
    active_templates = [root / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml"]

    counts = inventory_counts(root)
    rc, pin_issues, runtime_pin = check_runtime_sources(root)
    overall_fail = rc
    for line in pin_issues:
        stream = sys.stderr if line.startswith("FAIL") else sys.stdout
        print(line, file=stream)

    for target in targets:
        if not target.is_file():
            if args.require_agent_docs:
                print(f"FAIL missing required doc: {target}", file=sys.stderr)
                overall_fail = 1
            else:
                print(f"SKIP missing (not required): {target}")
            continue
        rc, issues = check_file(target, root, runtime_pin, counts)
        for line in issues:
            stream = sys.stderr if line.startswith("FAIL") else sys.stdout
            print(line, file=stream)
        overall_fail |= rc

    for target in active_templates:
        if not target.is_file():
            print(f"SKIP missing active template: {target}")
            continue
        rc, issues = check_file(target, root, runtime_pin, counts)
        for line in issues:
            stream = sys.stderr if line.startswith("FAIL") else sys.stdout
            print(line, file=stream)
        overall_fail |= rc

    return overall_fail


if __name__ == "__main__":
    sys.exit(main())
