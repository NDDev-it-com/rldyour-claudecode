from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_claude_surface_adoption.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_claude_surface_adoption", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_duplicate_required_runtime_fixes_are_rejected(tmp_path: Path, monkeypatch) -> None:
    module = load_module()
    baseline = tmp_path / "references" / "claude-baseline.json"
    adoption = tmp_path / "references" / "claude-surface-adoption.md"
    baseline.parent.mkdir()
    baseline.write_text(
        '{"baseline": {"claude_code": {"version": "2.1.177"}, '
        '"required_runtime_fixes": ["claude-code-2-1-177-runtime-rollup", '
        '"claude-code-2-1-177-runtime-rollup"]}}',
        encoding="utf-8",
    )
    adoption.write_text("2.1.177 runtime rollup\n", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "BASELINE", baseline)
    monkeypatch.setattr(module, "ADOPTION", adoption)

    assert module.main() == 1
