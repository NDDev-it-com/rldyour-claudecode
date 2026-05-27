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
    (tmp_path / "package.json").write_text(
        '{"name": "fixture-marketplace", "version": "0.4.0", '
        '"license": "AGPL-3.0-or-later", '
        '"author": {"name": "Danil Silantyev (github:rldyourmnd), CEO NDDev"}, '
        '"devDependencies": {"@anthropic-ai/claude-code": "2.1.152"}}',
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\n'
        'name = "fixture-marketplace"\n'
        'version = "0.4.0"\n'
        'license = "AGPL-3.0-or-later"\n'
        'authors = [{ name = "Danil Silantyev", email = "rldyourmnd@users.noreply.github.com" }]\n',
        encoding="utf-8",
    )
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
        '{"name": "fixture-marketplace", "plugins": ['
        '{"name": "sample-plugin", "source": "./plugins/sample-plugin", "version": "0.4.0",'
        '"license": "AGPL-3.0-or-later",'
        '"author": {"name": "Danil Silantyev (github:rldyourmnd), CEO NDDev"}},'
        '{"name": "rldyour-mcps", "source": "./plugins/rldyour-mcps", "version": "0.4.0",'
        '"license": "AGPL-3.0-or-later",'
        '"author": {"name": "Danil Silantyev (github:rldyourmnd), CEO NDDev"}},'
        '{"name": "rldyour-flow", "source": "./plugins/rldyour-flow", "version": "0.4.0",'
        '"license": "AGPL-3.0-or-later",'
        '"author": {"name": "Danil Silantyev (github:rldyourmnd), CEO NDDev"}}'
        ']}',
        encoding="utf-8",
    )

    plugin_dir = tmp_path / "plugins" / "sample-plugin" / ".claude-plugin"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.json").write_text(
        '{"name": "sample-plugin", "version": "0.4.0",'
        '"license": "AGPL-3.0-or-later",'
        '"author": {"name": "Danil Silantyev (github:rldyourmnd), CEO NDDev"}}',
        encoding="utf-8",
    )

    mcps_plugin_dir = tmp_path / "plugins" / "rldyour-mcps" / ".claude-plugin"
    mcps_plugin_dir.mkdir(parents=True)
    (mcps_plugin_dir / "plugin.json").write_text(
        '{"name": "rldyour-mcps", "version": "0.4.0",'
        '"license": "AGPL-3.0-or-later",'
        '"author": {"name": "Danil Silantyev (github:rldyourmnd), CEO NDDev"}}',
        encoding="utf-8",
    )
    # Add both a stdio write-capable server (serena) and an HTTP
    # read-only-by-design server (context7) so agent-tools tests can exercise
    # both wildcard-blocked and wildcard-passes branches of validate_agent_tools.
    (tmp_path / "plugins" / "rldyour-mcps" / ".mcp.json").write_text(
        '{"mcpServers": {'
        '"serena": {"command": "uvx", "args": ["serena-agent==1.5.3"]},'
        '"context7": {"type": "http", "url": "https://example.com"}'
        '}}',
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

    # text-hygiene allowlist (wave 0.4.4 externalisation) plus a hook stub
    # matching the BIDI exempt path so test_bidi_allowlist_skips_documented_file
    # can exercise the exemption end-to-end in fake_repo isolation.
    (config_dir / "text-hygiene-allowlist.json").write_text(
        '{"em_dash": [], "en_dash": [],'
        ' "bidi": ["plugins/rldyour-flow/hooks/post_tool_use_commit_advice.sh"]}',
        encoding="utf-8",
    )
    hook_dir = tmp_path / "plugins" / "rldyour-flow" / "hooks"
    hook_dir.mkdir(parents=True)
    # U+202E RLO embedded via Python escape so this conftest.py source stays
    # ASCII-clean (text-hygiene scan of conftest source must not trip).
    # Python decodes the escape at module load, write_text writes the actual
    # BIDI char to disk; validator must exempt the written file per allowlist.
    bidi_rlo = chr(0x202E)
    (hook_dir / "post_tool_use_commit_advice.sh").write_text(
        f"#!/usr/bin/env bash\n# BIDI char in regex char class: {bidi_rlo} detection target\n",
        encoding="utf-8",
    )
    # plugin.json stub so validate_release_state.py (which iterates plugins/*
    # and requires plugin.json in every subdir) does not FAIL on the new
    # rldyour-flow stub directory.
    flow_plugin_dir = tmp_path / "plugins" / "rldyour-flow" / ".claude-plugin"
    flow_plugin_dir.mkdir(parents=True)
    (flow_plugin_dir / "plugin.json").write_text(
        '{"name": "rldyour-flow", "version": "0.4.0",'
        '"license": "AGPL-3.0-or-later",'
        '"author": {"name": "Danil Silantyev (github:rldyourmnd), CEO NDDev"}}',
        encoding="utf-8",
    )
    flow_scripts_dir = tmp_path / "plugins" / "rldyour-flow" / "scripts"
    flow_scripts_dir.mkdir(parents=True)
    (flow_scripts_dir / "fullrepo_sync.py").write_text(
        'AGENT_ONLY_PATTERNS = ("AGENTS.md", ".codex/**")\n'
        'RUNTIME_EXCLUDE_PATTERNS = (".serena/.gitignore",)\n',
        encoding="utf-8",
    )
    (config_dir / "marketplace-policy.json").write_text(
        '{'
        '"mcp_owner": "rldyour-mcps",'
        '"hook_owners": [],'
        '"plugin_dependencies": {'
        '"sample-plugin": [], "rldyour-mcps": [], "rldyour-flow": []'
        '},'
        '"agent_only_path_globs": ["AGENTS.md", ".codex/**"],'
        '"runtime_exclude_globs": [".serena/.gitignore"]'
        '}',
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
    # `_mcp_parse.py` is the shared module imported by both
    # validate_skill_allowed_tools.py and validate_agent_tools.py - copy it
    # so the `from _mcp_parse import split_mcp_ref` resolves at test runtime.
    # Alphabetized so future additions land in the obvious slot (consistency F-1).
    for name in [
        "_mcp_parse.py",
        "check_mcp_runtime_versions.py",
        "generate_inventory.py",
        "generate_contract_matrix.py",
        "probe_mcp_upstream.py",
        "release_manifest.py",
        "validate_agent_tools.py",
        "validate_boundaries.py",
        "validate_command_skill_drift.py",
        "validate_contract.py",
        "validate_docs_canon.py",
        "validate_instruction_docs.py",
        "validate_instruction_sync.py",
        "validate_json_schemas.py",
        "validate_plugin_versions.py",
        "validate_release_state.py",
        "validate_skill_allowed_tools.py",
        "validate_skill_routing.py",
        "validate_text_hygiene.py",
    ]:
        src = SCRIPTS_DIR / name
        if src.is_file():
            shutil.copy(src, scripts_link / name)

    monkeypatch.chdir(fake_repo)
    return fake_repo
