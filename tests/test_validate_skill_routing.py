"""Integration test for scripts/validate_skill_routing.py.

The validator reads `config/skill-routing-policy.json` and verifies that
each routing case's expected skills contain the required description
terms. Coverage strategy: run against the real repository state (which
is the actual contract being protected) plus a synthetic mutation test
that builds a minimal fixture in tmp_path.

The synthetic test exercises both the happy path (terms match) and the
negative path (term missing) without depending on the live repo's
exact skill content drifting over time.

Closes the test gap noted by A-F-6 / verification F-5.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run_in(cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(cwd / "scripts" / "validate_skill_routing.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
        timeout=30,
    )


@pytest.mark.integration
def test_real_repo_passes() -> None:
    """End-to-end smoke against the live repository.

    The harness ships a `config/skill-routing-policy.json` plus all
    referenced skills - this asserts that contract holds at HEAD.
    Marked integration because it depends on the live repo state.
    """
    repo_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "validate_skill_routing.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=repo_root,
        timeout=30,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"


class TestSyntheticPolicy:
    def _setup_policy(self, fake_repo: Path, skill_text: str) -> None:
        """Write minimal skill-routing-policy + matching skill in fake_repo."""
        policy_dir = fake_repo / "config"
        policy_dir.mkdir(exist_ok=True)
        (policy_dir / "skill-routing-policy.json").write_text(
            json.dumps(
                {
                    "cases": [
                        {
                            "id": "test-case",
                            "expected": [
                                {
                                    "skill": "sample-plugin:test-skill",
                                    "description_terms": ["footerm", "barterm"],
                                }
                            ],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        skill_dir = fake_repo / "plugins" / "sample-plugin" / "skills" / "test-skill"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")

    def test_matching_terms_pass(self, patch_repo_root: Path) -> None:
        self._setup_policy(
            patch_repo_root,
            "---\nname: test-skill\n"
            "description: 'Skill with footerm and barterm in description'\n---\n\nbody\n",
        )
        result = _run_in(patch_repo_root)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "all 2 terms matched" in result.stdout

    def test_missing_term_blocks(self, patch_repo_root: Path) -> None:
        # Description omits 'barterm' - validator catches the gap.
        self._setup_policy(
            patch_repo_root,
            "---\nname: test-skill\n"
            "description: 'Skill with only footerm here'\n---\n\nbody\n",
        )
        result = _run_in(patch_repo_root)
        assert result.returncode == 1
        assert "barterm" in result.stderr

    def test_missing_skill_blocks(self, patch_repo_root: Path) -> None:
        # Policy references a skill that does not exist on disk.
        policy_dir = patch_repo_root / "config"
        (policy_dir / "skill-routing-policy.json").write_text(
            json.dumps(
                {
                    "cases": [
                        {
                            "id": "missing-skill",
                            "expected": [
                                {
                                    "skill": "sample-plugin:nonexistent-skill",
                                    "description_terms": ["any"],
                                }
                            ],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        result = _run_in(patch_repo_root)
        assert result.returncode == 1
        assert "not found" in result.stderr
