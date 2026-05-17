"""Tests for scripts/validate_command_skill_drift.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(patch_repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(patch_repo_root / "scripts" / "validate_command_skill_drift.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=patch_repo_root,
        timeout=30,
    )


def _write_command(repo: Path, plugin: str, name: str, body: str) -> Path:
    path = repo / "plugins" / plugin / "commands" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _write_skill(repo: Path, plugin: str, name: str) -> Path:
    path = repo / "plugins" / plugin / "skills" / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
name: {name}
description: "Test skill."
---

# {name}

Skill body.
""",
        encoding="utf-8",
    )
    return path


class TestThinWrapper:
    """Commands that match a skill name must stay thin wrappers."""

    def test_thin_wrapper_passes(self, patch_repo_root: Path) -> None:
        _write_skill(patch_repo_root, "rldyour-test", "test-cmd")
        _write_command(
            patch_repo_root,
            "rldyour-test",
            "test-cmd",
            """---
description: "Test command."
argument-hint: <task>
---

Test: **$ARGUMENTS**

Use the `test-cmd` skill for this request. The skill body owns the workflow.

Reply in Russian.
""",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "OK" in result.stdout

    def test_body_too_long_blocks(self, patch_repo_root: Path) -> None:
        _write_skill(patch_repo_root, "rldyour-test", "test-cmd")
        bloat = "x" * 900
        _write_command(
            patch_repo_root,
            "rldyour-test",
            "test-cmd",
            f"""---
description: "Test."
---

Use the `test-cmd` skill for this request.

{bloat}
""",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "thin-wrapper cap" in result.stdout

    def test_missing_delegation_phrase_blocks(self, patch_repo_root: Path) -> None:
        _write_skill(patch_repo_root, "rldyour-test", "test-cmd")
        _write_command(
            patch_repo_root,
            "rldyour-test",
            "test-cmd",
            """---
description: "Test."
---

This command implements the workflow inline.

Step 1. Do this.
Step 2. Do that.
""",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "missing literal" in result.stdout

    def test_forbidden_heading_blocks(self, patch_repo_root: Path) -> None:
        _write_skill(patch_repo_root, "rldyour-test", "test-cmd")
        _write_command(
            patch_repo_root,
            "rldyour-test",
            "test-cmd",
            """---
description: "Test."
---

Use the `test-cmd` skill for this request.

## Workflow

Step 1.
""",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "forbidden heading" in result.stdout.lower()

    def test_long_numbered_list_blocks(self, patch_repo_root: Path) -> None:
        _write_skill(patch_repo_root, "rldyour-test", "test-cmd")
        _write_command(
            patch_repo_root,
            "rldyour-test",
            "test-cmd",
            """---
description: "Test."
---

Use the `test-cmd` skill for this request.

1. Step one.
2. Step two.
3. Step three.
4. Step four.
5. Step five.
""",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 1
        assert "numbered checklist" in result.stdout


class TestCommandOnlyPattern:
    """Commands without a matching skill (command + agent pattern) are skipped."""

    def test_command_without_matching_skill_skipped(self, patch_repo_root: Path) -> None:
        # ry-explore-style: command + agent, no skill with the same name.
        _write_command(
            patch_repo_root,
            "rldyour-test",
            "agent-cmd",
            """---
description: "Test command + agent pattern."
context: fork
agent: agent-cmd
---

Whatever body the command wants; it is the source of truth here.
""",
        )
        result = _run(patch_repo_root)
        assert result.returncode == 0
        assert "SKIP" in result.stdout
        assert "no matching skill" in result.stdout
