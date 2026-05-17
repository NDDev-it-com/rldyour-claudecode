"""Shared pytest fixtures for rldyour-claudecode validator tests.

Tests under `tests/` are unit + integration tests for the Python validators
in `scripts/`. Each test isolates filesystem state via tmp_path and patches
the validator's `Path(__file__).resolve().parent.parent` anchor so the
validator scans the tmp tree instead of the real repository.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Make scripts importable as modules in tests
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    """Build a minimal fake marketplace repo under tmp_path.

    Returns the repo root. Layout:
      tmp_path/
        VERSION                   (0.4.0)
        CHANGELOG.md              (one [0.4.0] entry)
        README.md                 (markers + minimal text)
        AGENTS.md                 (sync_contract block)
        .claude/CLAUDE.md         (sync_contract block)
        .claude-plugin/marketplace.json  (1 plugin entry)
        plugins/sample-plugin/.claude-plugin/plugin.json
        plugins/rldyour-mcps/.mcp.json   (1 stdio server)
        config/cc-canon.json
        config/schemas/marketplace.json  (minimal schema)
    """
    (tmp_path / "VERSION").write_text("0.4.0\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n## [0.4.0] - 2026-05-17\n\nTest fixture.\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "# fixture\n\n<!-- inventory:begin -->\n<!-- inventory:end -->\n",
        encoding="utf-8",
    )
    (tmp_path / "AGENTS.md").write_text(
        "# AGENTS\n\n<!-- sync_contract:\nclaims:\n  shared: 'value-a'\n-->\n",
        encoding="utf-8",
    )
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "CLAUDE.md").write_text(
        "# CLAUDE\n\n<!-- sync_contract:\nclaims:\n  shared: 'value-a'\n-->\n",
        encoding="utf-8",
    )
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "marketplace.json").write_text(
        '{"name": "fixture-marketplace", "plugins": [{"name": "sample-plugin",'
        ' "source": "./plugins/sample-plugin", "version": "0.4.0"}]}',
        encoding="utf-8",
    )

    plugin_dir = tmp_path / "plugins" / "sample-plugin" / ".claude-plugin"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.json").write_text(
        '{"name": "sample-plugin", "version": "0.4.0"}',
        encoding="utf-8",
    )

    mcps_dir = tmp_path / "plugins" / "rldyour-mcps"
    mcps_dir.mkdir(parents=True)
    (mcps_dir / ".mcp.json").write_text(
        '{"mcpServers": {"serena": {"command": "uvx", "args": ["serena-agent==1.3.0"]}}}',
        encoding="utf-8",
    )

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "cc-canon.json").write_text(
        '{"forbidden_tokens": {"oldName": "newName"},'
        ' "version_floors": {"foo": {"floor": "v2.0+", "wrong_floors": ["v1.9"]}}}',
        encoding="utf-8",
    )

    schemas_dir = config_dir / "schemas"
    schemas_dir.mkdir()
    (schemas_dir / "marketplace.json").write_text(
        '{"$schema": "https://json-schema.org/draft/2020-12/schema",'
        ' "type": "object", "required": ["name", "plugins"],'
        ' "additionalProperties": false,'
        ' "properties": {"$schema": {"type": "string"}, "name": {"type": "string"},'
        ' "plugins": {"type": "array"}}}',
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture
def patch_repo_root(monkeypatch: pytest.MonkeyPatch, fake_repo: Path) -> Path:
    """Make scripts' `Path(__file__).resolve().parent.parent` point at fake_repo.

    Scripts compute the repo root as `Path(__file__).resolve().parent.parent`
    because they live under `scripts/`. Tests need that computation to land on
    fake_repo rather than the real repository.

    Implementation: symlink fake_repo/scripts/<validator>.py to the real
    scripts/<validator>.py, then chdir into fake_repo so any `Path(".")`
    calls also resolve correctly. The validator import will pick up the
    symlinked location and compute root = fake_repo.
    """
    scripts_link = fake_repo / "scripts"
    scripts_link.mkdir(exist_ok=True)
    # Copy real scripts so __file__ inside the script resolves to fake_repo/scripts/<name>.
    for name in [
        "validate_text_hygiene.py",
        "validate_skill_allowed_tools.py",
        "validate_release_state.py",
        "validate_docs_canon.py",
        "validate_instruction_sync.py",
        "generate_inventory.py",
        "validate_json_schemas.py",
        "release_manifest.py",
        "validate_plugin_versions.py",
    ]:
        src = SCRIPTS_DIR / name
        if src.is_file():
            shutil.copy(src, scripts_link / name)

    monkeypatch.chdir(fake_repo)
    return fake_repo
