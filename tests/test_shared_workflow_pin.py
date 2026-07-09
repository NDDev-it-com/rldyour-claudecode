from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github/workflows"
WORKFLOW_DOC = WORKFLOWS / "README.md"
SHARED_REPO = "NDDev-it-com/nddev-ci-workflows"
SHARED_SHA = "ac4d1f469f5974741c7449305ffcbd5f05a5a47f"
SHARED_VERSION = "0.5.1"
PIN_RE = re.compile(
    rf"^\s*(?:-\s*)?uses:\s*{re.escape(SHARED_REPO)}/[^@\s]+@{SHARED_SHA}"
    rf"\s+#\s*{re.escape(SHARED_VERSION)}\s*$"
)


def test_all_shared_workflow_callers_use_one_verified_pin() -> None:
    callers: list[tuple[Path, int, str]] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if f"{SHARED_REPO}/" in line:
                callers.append((path, line_number, line))

    assert callers, "no nddev-ci-workflows reusable callers found"
    drift = [
        f"{path.relative_to(ROOT)}:{line_number}: {line.strip()}"
        for path, line_number, line in callers
        if PIN_RE.fullmatch(line) is None
    ]
    assert not drift, "shared workflow pin drift:\n" + "\n".join(drift)


def test_shared_workflow_pin_is_documented() -> None:
    text = WORKFLOW_DOC.read_text(encoding="utf-8")
    assert f"release `{SHARED_VERSION}`" in text
    assert f"`{SHARED_SHA}`" in text
