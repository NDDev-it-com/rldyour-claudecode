"""Tests for scripts/validate_contract.py and contract matrix generation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _write_minimal_contract(repo: Path) -> None:
    (repo / "plugins" / "sample-plugin" / "skills" / "sample-skill").mkdir(parents=True)
    (repo / "plugins" / "sample-plugin" / "skills" / "sample-skill" / "SKILL.md").write_text(
        '---\nname: sample-skill\ndescription: "Fixture skill."\n---\n',
        encoding="utf-8",
    )
    (repo / "plugins" / "rldyour-flow" / "commands").mkdir(parents=True, exist_ok=True)
    (repo / "plugins" / "rldyour-flow" / "commands" / "ry-start.md").write_text(
        "# ry-start\n",
        encoding="utf-8",
    )
    (repo / "plugins" / "rldyour-flow" / "agents").mkdir(parents=True, exist_ok=True)
    (repo / "plugins" / "rldyour-flow" / "agents" / "flow-quality-review.md").write_text(
        "---\nname: flow-quality-review\ndescription: Fixture agent.\n---\n",
        encoding="utf-8",
    )
    (repo / "plugins" / "rldyour-flow" / "hooks" / "hooks.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PostToolUse": [
                        {
                            "matcher": "Bash",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "/bin/bash",
                                    "args": [
                                        "${CLAUDE_PLUGIN_ROOT}/hooks/post_tool_use_commit_advice.sh"
                                    ],
                                }
                            ],
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "validate.yml").write_text("name: validate\n", encoding="utf-8")

    contract = {
        "schema_version": 1,
        "verified_on": "2026-05-30",
        "owner_repo": "fixture",
        "adapters": ["claude", "codex", "opencode", "gemini", "mimocode"],
        "domains": [
            {
                "id": "sample",
                "description": "Fixture sample domain",
                "claude": {"plugin": "sample-plugin"},
                "codex": {"plugin": "sample-plugin"},
                "opencode": {"plugin": "sample-plugin"},
                "gemini": {"status": "fixture"},
                "mimocode": {"status": "fixture"},
            },
            {
                "id": "mcps",
                "description": "Fixture MCP domain",
                "claude": {"plugin": "rldyour-mcps"},
                "codex": {"plugin": "rldyour-mcps"},
                "opencode": {"plugin": "rldyour-mcps"},
                "gemini": {"status": "fixture"},
                "mimocode": {"status": "fixture"},
            },
            {
                "id": "flow",
                "description": "Fixture flow domain",
                "claude": {"plugin": "rldyour-flow"},
                "codex": {"plugin": "rldyour-flow"},
                "opencode": {"plugin": "rldyour-flow"},
                "gemini": {"status": "fixture"},
                "mimocode": {"status": "fixture"},
            },
        ],
        "public_flows": [
            {
                "id": "flow.start",
                "description": "Fixture public flow",
                "claude": {"path": "plugins/rldyour-flow/commands/ry-start.md"},
                "codex": {"name": "ry-start"},
                "opencode": {"name": "ry-start"},
                "gemini": {"status": "fixture"},
                "mimocode": {"status": "fixture"},
            }
        ],
        "skills": [
            {
                "id": "sample.skill",
                "description": "Fixture skill",
                "claude": {"path": "plugins/sample-plugin/skills/sample-skill/SKILL.md"},
                "codex": {"name": "sample-skill"},
                "opencode": {"name": "sample-skill"},
                "gemini": {"status": "fixture"},
                "mimocode": {"status": "fixture"},
            }
        ],
        "agent_roles": [
            {
                "id": "agent.review.quality",
                "description": "Fixture reviewer",
                "claude": {"path": "plugins/rldyour-flow/agents/flow-quality-review.md"},
                "codex": {"name": "quality-reviewer"},
                "opencode": {"name": "flow-quality-review"},
                "gemini": {"status": "fixture"},
                "mimocode": {"status": "fixture"},
            }
        ],
        "hook_lifecycle": [
            {
                "id": "tool.post.commit-advice",
                "description": "Fixture hook",
                "claude": {
                    "plugin": "rldyour-flow",
                    "event": "PostToolUse",
                    "script": "plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh",
                },
                "codex": {"status": "fixture"},
                "opencode": {"status": "fixture"},
                "gemini": {"status": "fixture"},
                "mimocode": {"status": "fixture"},
            }
        ],
        "ci_baseline": [
            {
                "id": "validate-contract",
                "description": "Fixture contract gate",
                "claude": {"workflow": ".github/workflows/validate.yml"},
                "codex": {"status": "fixture"},
                "opencode": {"status": "fixture"},
                "gemini": {"status": "fixture"},
                "mimocode": {"status": "fixture"},
            }
        ],
    }
    (repo / "config" / "rldyour-contract.json").write_text(
        json.dumps(contract, indent=2) + "\n",
        encoding="utf-8",
    )


def _run(repo: Path, script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo / "scripts" / script), *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=repo,
        timeout=30,
    )


class TestValidateContract:
    def test_minimal_contract_passes(self, patch_repo_root: Path) -> None:
        _write_minimal_contract(patch_repo_root)
        result = _run(patch_repo_root, "validate_contract.py")
        assert result.returncode == 0, result.stderr
        assert "OK rldyour contract" in result.stdout

    def test_missing_claude_skill_path_fails(self, patch_repo_root: Path) -> None:
        _write_minimal_contract(patch_repo_root)
        skill_path = patch_repo_root / "plugins" / "sample-plugin" / "skills" / "sample-skill" / "SKILL.md"
        skill_path.unlink()
        result = _run(patch_repo_root, "validate_contract.py")
        assert result.returncode == 1
        assert "sample.skill" in result.stderr
        assert "path does not exist" in result.stderr

    def test_hook_script_must_be_referenced_by_manifest(self, patch_repo_root: Path) -> None:
        _write_minimal_contract(patch_repo_root)
        hooks = patch_repo_root / "plugins" / "rldyour-flow" / "hooks" / "hooks.json"
        hooks.write_text('{"hooks": {"PostToolUse": []}}', encoding="utf-8")
        result = _run(patch_repo_root, "validate_contract.py")
        assert result.returncode == 1
        assert "tool.post.commit-advice" in result.stderr
        assert "not referenced" in result.stderr


class TestGenerateContractMatrix:
    def test_generate_then_check_passes(self, patch_repo_root: Path) -> None:
        _write_minimal_contract(patch_repo_root)
        output = patch_repo_root / "docs"
        output.mkdir(exist_ok=True)
        generate = _run(patch_repo_root, "generate_contract_matrix.py")
        assert generate.returncode == 0, generate.stderr

        check = _run(patch_repo_root, "generate_contract_matrix.py", "--check")
        assert check.returncode == 0, check.stderr
        assert "OK contract matrix" in check.stdout
