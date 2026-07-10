"""Regression tests for the mandatory CloakBrowser skill boundary."""

from __future__ import annotations

import pytest
import validate_browser_provider_policy as policy


def test_live_repository_browser_policy_passes() -> None:
    policy.validate()


@pytest.mark.parametrize("skill", sorted(policy.REQUIRED_SKILLS))
def test_every_browser_skill_has_exact_boundary(skill: str) -> None:
    path = policy.ROOT / "plugins/rldyour-browser/skills" / skill / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    assert text.count(policy.MANDATORY_SKILL_BOUNDARY) == 1


def test_missing_boundary_fails_closed() -> None:
    with pytest.raises(policy.Failure, match="must appear exactly once"):
        policy.validate_skill_contract("browser-validation", "# Browser Validation\n")


def test_unqualified_cli_command_is_rejected() -> None:
    text = (
        policy.MANDATORY_SKILL_BOUNDARY
        + "\n\n```bash\nplaywright-cli open https://example.test\n```\n"
    )
    with pytest.raises(policy.Failure, match=r"exact \$HOME/.local/bin/playwright-cli"):
        policy.validate_skill_contract("browser-validation", text)


@pytest.mark.parametrize(
    ("alternate", "message"),
    [
        ("/tmp/playwright-cli", "playwright-cli must use exact"),
        ("/tmp/chrome-devtools-mcp", "chrome-devtools-mcp must use exact"),
    ],
)
def test_alternate_provider_path_is_rejected(alternate: str, message: str) -> None:
    text = policy.MANDATORY_SKILL_BOUNDARY + f"\n\n{alternate}\n"
    with pytest.raises(policy.Failure, match=message):
        policy.validate_skill_contract("browser-validation", text)


def test_action_without_immediate_health_gate_is_rejected() -> None:
    text = (
        policy.MANDATORY_SKILL_BOUNDARY
        + "\n\n```bash\n"
        + "$HOME/.local/bin/playwright-cli open https://example.test\n"
        + "```\n"
    )
    with pytest.raises(policy.Failure, match="immediately health-gated"):
        policy.validate_skill_contract("browser-validation", text)
