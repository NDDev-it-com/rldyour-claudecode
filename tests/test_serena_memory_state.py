"""Unit tests for plugins/rldyour-serena-mcp/scripts/serena_memory_state.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_MODULE_PATH = REPO_ROOT / "plugins" / "rldyour-serena-mcp" / "scripts" / "serena_memory_state.py"


def _load_state_module():
    spec = importlib.util.spec_from_file_location("serena_memory_state_test", STATE_MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def state_module():
    return _load_state_module()


@pytest.mark.parametrize(
    "path",
    [
        ".serena/memories/CORE-01-INDEX.md",
        ".serena/plans/wave-plan.md",
        ".serena/research/notes.md",
        ".serena/newproj/foo.md",
        ".serena/deploy/bar.md",
    ],
)
def test_durable_serena_context_is_knowledge(state_module, path: str) -> None:
    assert state_module._is_knowledge_path(path)


@pytest.mark.parametrize(
    "path",
    [
        "AGENTS.md",
        ".claude/CLAUDE.md",
        ".serena/project.yml",
        ".serena/project.local.yml",
        ".serena/cache/document_symbols.pkl",
        ".serena/reviews/report.md",
        "plugins/rldyour-flow/scripts/flow_post_task_state.py",
        "config/marketplace-policy.json",
        "README.md",
    ],
)
def test_non_memory_paths_are_not_serena_knowledge(state_module, path: str) -> None:
    assert not state_module._is_knowledge_path(path)


def test_non_knowledge_paths_filter(state_module) -> None:
    paths = [
        ".serena/memories/CORE-01-INDEX.md",
        ".serena/research/notes.md",
        "AGENTS.md",
        "src/main.py",
        "config/foo.json",
    ]
    assert state_module._non_knowledge_paths(paths) == ["AGENTS.md", "src/main.py", "config/foo.json"]


def test_all_knowledge_returns_empty(state_module) -> None:
    paths = [".serena/memories/X.md", ".serena/plans/Y.md"]
    assert state_module._non_knowledge_paths(paths) == []
