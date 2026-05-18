"""Unit tests for plugins/rldyour-serena-mcp/scripts/serena_memory_state.py.

Covers:
- SERENA_KNOWLEDGE_PREFIXES (canonical knowledge directories)
- AGENT_INSTRUCTION_PATHS (D77 closure: agent-instruction-equivalent canon)
- _is_knowledge_path classification
- _non_knowledge_paths filtering
- Drift detection between serena_memory_state.AGENT_INSTRUCTION_PATHS
  and the inline mirror in mark_sync_required.sh (single source of truth invariant).

These tests guard the structural conflict closure documented in ADR-0011
and TECHDEBT-01-NOW D77.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_MODULE_PATH = (
    REPO_ROOT
    / "plugins"
    / "rldyour-serena-mcp"
    / "scripts"
    / "serena_memory_state.py"
)
HOOK_SCRIPT_PATH = (
    REPO_ROOT
    / "plugins"
    / "rldyour-serena-mcp"
    / "hooks"
    / "mark_sync_required.sh"
)
EXCLUDE_FILE = REPO_ROOT / ".git" / "info" / "exclude"


def _load_state_module():
    spec = importlib.util.spec_from_file_location(
        "serena_memory_state_test", STATE_MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def state_module():
    return _load_state_module()


class TestSerenaKnowledgePrefixes:
    """SERENA_KNOWLEDGE_PREFIXES recognises .serena/* knowledge directories."""

    def test_memories_directory_is_knowledge(self, state_module):
        assert state_module._is_knowledge_path(".serena/memories/CORE-01-INDEX.md")

    def test_plans_directory_is_knowledge(self, state_module):
        assert state_module._is_knowledge_path(".serena/plans/wave-plan.md")

    def test_research_directory_is_knowledge(self, state_module):
        assert state_module._is_knowledge_path(".serena/research/notes.md")

    def test_newproj_directory_is_knowledge(self, state_module):
        assert state_module._is_knowledge_path(".serena/newproj/foo.md")

    def test_deploy_directory_is_knowledge(self, state_module):
        assert state_module._is_knowledge_path(".serena/deploy/bar.md")


class TestAgentInstructionPaths:
    """AGENT_INSTRUCTION_PATHS recognises agent-instruction-equivalent files.

    Coverage matches the canonical "rldyour fullrepo agent-only files" block
    in .git/info/exclude. Each test case corresponds to one path glob.
    """

    @pytest.mark.parametrize(
        "path",
        [
            "AGENTS.md",
            "CLAUDE.md",
            "REVIEW.md",
            "GEMINI.md",
            "QWEN.md",
        ],
    )
    def test_root_instruction_files(self, state_module, path):
        assert state_module._is_knowledge_path(path), f"{path} should be knowledge"

    @pytest.mark.parametrize(
        "path",
        [
            ".cursorrules",
            ".windsurfrules",
        ],
    )
    def test_root_dotfile_instructions(self, state_module, path):
        assert state_module._is_knowledge_path(path)

    @pytest.mark.parametrize(
        "path",
        [
            ".aider",
            ".aiderignore",
            ".aider.conf.yml",
            ".aider.chat.history.md",
        ],
    )
    def test_aider_prefix_match(self, state_module, path):
        """`.aider` prefix matches all .aider* files (canonical exclude glob)."""
        assert state_module._is_knowledge_path(path)

    @pytest.mark.parametrize(
        "path",
        [
            ".claude/CLAUDE.md",
            ".claude/agents/foo.md",
            ".codex/config.yml",
            ".cursor/rules/x.md",
            ".gemini/foo.md",
            ".windsurf/bar.md",
            ".roo/baz.md",
            ".openhands/qux.md",
        ],
    )
    def test_agent_root_directories(self, state_module, path):
        assert state_module._is_knowledge_path(path)

    @pytest.mark.parametrize(
        "path",
        [
            ".github/copilot-instructions.md",
            ".github/instructions/x.md",
            ".github/prompts/y.md",
        ],
    )
    def test_github_agent_paths(self, state_module, path):
        assert state_module._is_knowledge_path(path)

    @pytest.mark.parametrize(
        "path",
        [
            ".agents/skills/a.md",
            ".agents/commands/b.md",
            ".agents/hooks/c.md",
        ],
    )
    def test_dot_agents_paths(self, state_module, path):
        assert state_module._is_knowledge_path(path)

    @pytest.mark.parametrize(
        "path",
        [
            ".serena/project.yml",
            ".serena/project.local.yml",
        ],
    )
    def test_serena_metadata_files(self, state_module, path):
        """`.serena/project.yml` is metadata, not knowledge directory, but is
        still agent-instruction-equivalent (lives only on fullrepo branch)."""
        assert state_module._is_knowledge_path(path)


class TestNotKnowledgePaths:
    """Negative cases: real code, config, and product files must NOT be knowledge."""

    @pytest.mark.parametrize(
        "path",
        [
            "src/main.py",
            "plugins/rldyour-flow/scripts/fullrepo_sync.py",
            "config/cc-canon.json",
            "config/marketplace-policy.json",
            "package.json",
            "pyproject.toml",
            "VERSION",
            "CHANGELOG.md",
            "README.md",
            "scripts/validate_marketplace.sh",
            ".github/workflows/validate.yml",  # workflows are product, not agent-instruction
            ".github/dependabot.yml",
        ],
    )
    def test_real_code_paths_not_knowledge(self, state_module, path):
        assert not state_module._is_knowledge_path(path), (
            f"{path} should NOT be classified as knowledge"
        )


class TestNonKnowledgePathsFilter:
    """_non_knowledge_paths drops knowledge paths and RUNTIME_IGNORED markers."""

    def test_mixed_input_filters_correctly(self, state_module):
        paths = [
            "src/main.py",
            ".serena/memories/X.md",
            "AGENTS.md",
            "config/foo.json",
            ".serena/.sync_marker",
            ".serena/.serena_sync_state.json",
        ]
        result = state_module._non_knowledge_paths(paths)
        assert result == ["src/main.py", "config/foo.json"]

    def test_empty_input(self, state_module):
        assert state_module._non_knowledge_paths([]) == []

    def test_all_knowledge_returns_empty(self, state_module):
        paths = ["AGENTS.md", ".claude/CLAUDE.md", ".serena/memories/X.md"]
        assert state_module._non_knowledge_paths(paths) == []


class TestExcludeBlockParity:
    """AGENT_INSTRUCTION_PATHS must cover the .git/info/exclude canonical
    agent-only block. Drift between exclude file and AGENT_INSTRUCTION_PATHS
    is a structural inconsistency (ADR-0011)."""

    @staticmethod
    def _extract_exclude_paths() -> set[str]:
        if not EXCLUDE_FILE.exists():
            pytest.skip(".git/info/exclude missing - not a fresh repo")
        text = EXCLUDE_FILE.read_text(encoding="utf-8")
        match = re.search(
            r"# >>> rldyour fullrepo agent-only files >>>\n(.*?)\n# <<<",
            text,
            re.DOTALL,
        )
        if not match:
            pytest.skip("agent-only block markers absent from exclude file")
        paths = set()
        for line in match.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith("!") or line.startswith("#"):
                continue
            # exclude entries are like /AGENTS.md or /.claude/**
            stripped = line.lstrip("/")
            # Normalise glob suffix to prefix form for matching.
            stripped = stripped.removesuffix("/**").removesuffix("*")
            paths.add(stripped)
        return paths

    def test_no_missing_agent_paths(self, state_module):
        """Every agent-only path in .git/info/exclude must be recognised as
        knowledge. Semantic match: exclude `.cursor/rules` is covered by
        canon `.cursor/` (we're broader by design)."""
        exclude_paths = self._extract_exclude_paths()
        # Probe each exclude path with a synthetic file under it; if
        # _is_knowledge_path() returns True the canon covers it.
        missing = []
        for excl in exclude_paths:
            probe = excl if excl.endswith(".md") or excl.endswith(".yml") else f"{excl}/dummy.md"
            if not state_module._is_knowledge_path(probe):
                # Special case: bare `.aider` prefix-match handles dotfile families.
                if excl.startswith(".aider") and state_module._is_knowledge_path(".aider.test"):
                    continue
                missing.append(excl)
        assert not missing, (
            f"Agent-only paths from .git/info/exclude not covered "
            f"by knowledge classification: {sorted(missing)}"
        )


class TestInlineHookCanonDrift:
    """mark_sync_required.sh has an inline mirror of AGENT_INSTRUCTION_PATHS
    (heredoc Python cannot import the plugin module). This test asserts both
    canonical lists stay in sync; drift would cause inconsistent hook behavior.
    """

    @staticmethod
    def _extract_inline_canon() -> set[str]:
        text = HOOK_SCRIPT_PATH.read_text(encoding="utf-8")
        match = re.search(
            r"AGENT_INSTRUCTION_PATHS\s*=\s*\((.*?)\)",
            text,
            re.DOTALL,
        )
        assert match, "mark_sync_required.sh missing AGENT_INSTRUCTION_PATHS canon"
        items = re.findall(r'"([^"]+)"', match.group(1))
        return set(items)

    def test_inline_hook_path_canon_matches(self, state_module):
        inline = self._extract_inline_canon()
        module = set(state_module.AGENT_INSTRUCTION_PATHS)
        only_in_inline = inline - module
        only_in_module = module - inline
        assert not only_in_inline, (
            f"Paths in mark_sync_required.sh inline canon but NOT in "
            f"serena_memory_state.AGENT_INSTRUCTION_PATHS: {sorted(only_in_inline)}"
        )
        assert not only_in_module, (
            f"Paths in serena_memory_state.AGENT_INSTRUCTION_PATHS but NOT in "
            f"mark_sync_required.sh inline canon: {sorted(only_in_module)}"
        )
