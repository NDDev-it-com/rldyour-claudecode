#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "references" / "claude-baseline.json"
ADOPTION = ROOT / "references" / "claude-surface-adoption.md"

REQUIRED_BASELINE_SURFACES = {
    "skill-and-slash-command-disallowed-tools-frontmatter": "`disallowed-tools`",
    "sessionstart-reloadskills-output": "`SessionStart.reloadSkills`",
    "message-display-hook-event": "`MessageDisplay`",
    "auto-mode-explicit-ask-user-question": "AskUserQuestion",
    "managed-required-version-settings": "`requiredMinimumVersion`",
    "plugin-list-command": "`/plugin list`",
    "stop-subagentstop-additional-context": "`hookSpecificOutput.additionalContext`",
    "skill-dollar-escape-syntax": "`\\$` escape syntax",
    "stdio-mcp-session-id-on-resume": "`CLAUDE_CODE_SESSION_ID`",
    "claude-code-2-1-165-reliability-rollup": "2.1.165 reliability rollup",
    "fallback-model-and-deny-glob-policy": "`fallbackModel`",
    "claude-code-2-1-167-reliability-rollup": "2.1.167 reliability rollup",
    "claude-code-2-1-168-reliability-rollup": "2.1.168 reliability rollup",
    "nested-subagents-and-background-agent-hardening": "nested sub-agents",
    "claude-code-2-1-173-fable-windows-fixes": "Fable 5 model names",
    "claude-code-2-1-175-enforce-available-models": "`enforceAvailableModels`",
    "claude-code-2-1-176-language-footer-and-policy-fixes": "`footerLinksRegexes`",
    "claude-code-2-1-177-runtime-rollup": "2.1.177 runtime rollup",
    "claude-code-2-1-190-runtime-rollup": "2.1.190 runtime rollup",
}

REQUIRED_2_1_153_SURFACES = (
    "`skipLfs`",
    "`/doctor`",
    "`COLUMNS`",
    "`claude agents`",
)

REQUIRED_2_1_154_SURFACES = (
    "Opus 4.8",
    "Dynamic workflows",
    "Streaming tool execution",
    "pending-approval",
    "`defaultEnabled: false`",
)

REQUIRED_2_1_156_SURFACES = (
    "thinking-block API hotfix",
    "`2.1.156`",
)

REQUIRED_2_1_157_SURFACES = (
    "`.claude/skills` direct loading",
    "`claude plugin init`",
    "`/plugin` autocomplete",
    "`settings.json` `agent`",
    "`EnterWorktree`",
    "`OTEL_LOG_TOOL_DETAILS`",
    "ultracode keyword trigger",
)

REQUIRED_2_1_158_SURFACES = (
    "`CLAUDE_CODE_ENABLE_AUTO_MODE=1`",
    "Bedrock",
    "Vertex",
    "Foundry",
    "Auto mode",
    "Opus 4.8",
)

REQUIRED_2_1_163_SURFACES = (
    "`requiredMinimumVersion`",
    "`requiredMaximumVersion`",
    "`/plugin list`",
    "`hookSpecificOutput.additionalContext`",
    "`\\$` escape syntax",
    "`CLAUDE_CODE_SESSION_ID`",
)

REQUIRED_2_1_165_SURFACES = (
    "2.1.165 reliability rollup",
    "Bug fixes and reliability improvements",
)

REQUIRED_2_1_166_SURFACES = (
    "`fallbackModel`",
    "`--fallback-model`",
    "deny rule",
    "`\"*\"`",
    "`SendMessage`",
    "`MAX_THINKING_TOKENS=0`",
    "`--thinking disabled`",
    "`allowedMcpServers`",
    "`deniedMcpServers`",
    "`${VAR}`",
)

REQUIRED_2_1_167_SURFACES = (
    "2.1.167 reliability rollup",
    "Bug fixes and reliability improvements",
)

REQUIRED_2_1_168_SURFACES = (
    "2.1.168 reliability rollup",
    "Bug fixes and reliability improvements",
)

REQUIRED_2_1_169_SURFACES = (
    "`--safe-mode`",
    "`/cd`",
    "`disableBundledSkills`",
    "`post-session`",
)

REQUIRED_2_1_170_SURFACES = (
    "Claude Fable 5",
    "2.1.170",
)

REQUIRED_2_1_172_SURFACES = (
    "nested sub-agents",
    "background agents",
    "`availableModels`",
)

REQUIRED_2_1_173_SURFACES = (
    "Fable 5 model names",
    "Windows sandbox",
    "2.1.173",
)

REQUIRED_2_1_175_SURFACES = (
    "`enforceAvailableModels`",
    "`availableModels`",
    "2.1.175",
)

REQUIRED_2_1_176_SURFACES = (
    "`footerLinksRegexes`",
    "`language` setting",
    "`ANTHROPIC_DEFAULT_*_MODEL`",
    "`/fast`",
    "hook `if` path matching",
)

REQUIRED_2_1_177_SURFACES = (
    "2.1.177 runtime rollup",
    "npm `@anthropic-ai/claude-code` latest",
)

VALID_DECISIONS = ("Adopt", "Adopted", "Future", "Hybrid", "Intentionally unused")


def version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def main() -> int:
    errors: list[str] = []
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    version = baseline.get("baseline", {}).get("claude_code", {}).get("version")
    required = baseline.get("baseline", {}).get("required_runtime_fixes") or []
    text = ADOPTION.read_text(encoding="utf-8") if ADOPTION.is_file() else ""

    if not text:
        errors.append(f"{ADOPTION.relative_to(ROOT)} is missing")
    for key in required:
        expected = REQUIRED_BASELINE_SURFACES.get(key)
        if expected and expected not in text:
            errors.append(f"{ADOPTION.relative_to(ROOT)} missing decision for {key}")

    parsed_version = version_tuple(str(version))
    if parsed_version >= version_tuple("2.1.153"):
        for marker in REQUIRED_2_1_153_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.153 surface {marker}")
    if parsed_version >= version_tuple("2.1.154"):
        for marker in REQUIRED_2_1_154_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.154 surface {marker}")
        for line in text.splitlines():
            if "Dynamic workflows" in line and "| Future |" in line:
                errors.append(f"{ADOPTION.relative_to(ROOT)} must adopt Dynamic workflows for ry-start")
            if "Dynamic workflows" in line and "Hybrid pending native workflow" not in line:
                errors.append(
                    f"{ADOPTION.relative_to(ROOT)} must mark Dynamic workflows as hybrid pending native workflow"
                )
    if parsed_version >= version_tuple("2.1.156"):
        for marker in REQUIRED_2_1_156_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.156 surface {marker}")
    if parsed_version >= version_tuple("2.1.157"):
        for marker in REQUIRED_2_1_157_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.157 surface {marker}")
    if parsed_version >= version_tuple("2.1.158"):
        for marker in REQUIRED_2_1_158_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.158 surface {marker}")
    if parsed_version >= version_tuple("2.1.163"):
        for marker in REQUIRED_2_1_163_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.163 surface {marker}")
    if parsed_version >= version_tuple("2.1.165"):
        for marker in REQUIRED_2_1_165_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.165 surface {marker}")
    if parsed_version >= version_tuple("2.1.166"):
        for marker in REQUIRED_2_1_166_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.166 surface {marker}")
    if parsed_version >= version_tuple("2.1.167"):
        for marker in REQUIRED_2_1_167_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.167 surface {marker}")
    if parsed_version >= version_tuple("2.1.168"):
        for marker in REQUIRED_2_1_168_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.168 surface {marker}")
    if parsed_version >= version_tuple("2.1.169"):
        for marker in REQUIRED_2_1_169_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.169 surface {marker}")
    if parsed_version >= version_tuple("2.1.170"):
        for marker in REQUIRED_2_1_170_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.170 surface {marker}")
    if parsed_version >= version_tuple("2.1.172"):
        for marker in REQUIRED_2_1_172_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.172 surface {marker}")
    if parsed_version >= version_tuple("2.1.173"):
        for marker in REQUIRED_2_1_173_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.173 surface {marker}")
    if parsed_version >= version_tuple("2.1.175"):
        for marker in REQUIRED_2_1_175_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.175 surface {marker}")
    if parsed_version >= version_tuple("2.1.176"):
        for marker in REQUIRED_2_1_176_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.176 surface {marker}")
    if parsed_version >= version_tuple("2.1.177"):
        for marker in REQUIRED_2_1_177_SURFACES:
            if marker not in text:
                errors.append(f"{ADOPTION.relative_to(ROOT)} missing 2.1.177 surface {marker}")

    for line in text.splitlines():
        if not line.startswith("| `") and not line.startswith("| `/"):
            continue
        if not any(f"| {decision}" in line for decision in VALID_DECISIONS):
            errors.append(f"{ADOPTION.relative_to(ROOT)} row lacks an explicit adoption decision: {line}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Claude surface adoption decisions validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
