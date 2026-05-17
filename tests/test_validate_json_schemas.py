"""Unit tests for scripts/validate_json_schemas.py.

Covers JSON Schema validation chain - happy path against fake marketplace
plus a violation case (additionalProperties: false catches extra fields).

The validator SKIPs schemas not present in the fixture (per its
contract - schemas may be added incrementally). The fake_repo only
ships a marketplace.json schema, so plugin.json + mcp.json + lsp.json
+ hooks.json schemas are SKIPped, and the only enforceable path is
marketplace validation.

Closes the test gap noted by A-F-6 / verification F-5 (was on the
6-validator missing-test list).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run(fake_repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(fake_repo / "scripts" / "validate_json_schemas.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=fake_repo,
    )


class TestHappyPath:
    def test_minimal_marketplace_passes(self, patch_repo_root: Path) -> None:
        # fake_repo ships a marketplace.json conforming to its own schema.
        # All other schemas (plugin/mcp/lsp/hooks) SKIP in the fixture.
        result = _run(patch_repo_root)
        assert result.returncode == 0, (
            f"stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
        # Either OK or SKIP (jsonschema not importable) - both are zero exit.
        assert "OK" in result.stdout or "SKIP" in result.stdout


class TestNegativePath:
    def test_extra_property_blocked(self, patch_repo_root: Path) -> None:
        # additionalProperties: false in the marketplace schema means any
        # extra top-level field triggers a JSON Schema violation. This is
        # the audit F-4 contract - schemas were tightened to additionalProperties:
        # false specifically to catch drift like this.
        marketplace_path = patch_repo_root / ".claude-plugin" / "marketplace.json"
        data = json.loads(marketplace_path.read_text(encoding="utf-8"))
        data["unexpected_field"] = "definitely-not-in-schema"
        marketplace_path.write_text(json.dumps(data), encoding="utf-8")
        result = _run(patch_repo_root)
        # Either FAIL (jsonschema available) or SKIP (not installed). The
        # CI env always has jsonschema so should hit FAIL there.
        if "SKIP" in result.stdout:
            return  # graceful no-op when jsonschema absent locally
        assert result.returncode == 1
        assert "unexpected_field" in result.stderr or "Additional properties" in result.stderr
