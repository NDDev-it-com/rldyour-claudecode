#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SKILLS = {
    "browser-tool-routing",
    "browser-validation",
    "browser-debug",
    "playwright-cli-validation",
    "webwright-task",
    "visual-diff-review",
}
CHROME_COMMAND = "/bin/sh"
CHROME_ARGS = [
    "-c",
    'exec "$HOME/.local/bin/chrome-devtools-mcp" --headless --isolated '
    "--no-usage-statistics --no-performance-crux",
]
EXPECTED_BROWSER_PROVIDERS = {
    "policy": "root config/browser-automation-policy.json",
    "required_common_providers": ["playwright-cli", "chrome-devtools-mcp"],
    "mcp_providers": ["chrome-devtools-mcp"],
    "cli_providers": ["playwright-cli"],
    "compatibility_workflows": ["webwright-task"],
    "forbidden_runtime_providers": ["webwright"],
}
MANDATORY_SKILL_BOUNDARY = """## Mandatory CloakBrowser Boundary

This boundary applies before every browser action:

1. Run exactly:

   ```bash
   $HOME/.local/bin/cloakbrowser-cdp-health
   ```

   If the command is missing or exits nonzero, stop immediately and report `NOT_PROVEN`.
2. Browser execution is permitted only through:
   - the exact `$HOME/.local/bin/playwright-cli` executable; `run-code` and `--filename` are forbidden;
   - the approved Chrome DevTools MCP transport, exactly `/bin/sh -c 'exec "$HOME/.local/bin/chrome-devtools-mcp" --headless --isolated --no-usage-statistics --no-performance-crux'`.
3. Never execute the Webwright Python runtime, stock/raw/in-app Browser, `browser_agent`, `node_repl`, computer-use, Playwright MCP, raw Playwright, `bunx`, `npx`, direct package invocations, alternate CDP endpoints, alternate browser executables, alternate browser configs, or any fallback. No fallback is allowed."""
PLAYWRIGHT_CLI = "$HOME/.local/bin/playwright-cli"
CHROME_WRAPPER = "$HOME/.local/bin/chrome-devtools-mcp"


class Failure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


def bash_blocks(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] | None = None
    for line in text.splitlines():
        if line.strip() == "```bash":
            current = []
            continue
        if line.strip() == "```" and current is not None:
            blocks.append(current)
            current = None
            continue
        if current is not None:
            current.append(line)
    return blocks


def require_exact_provider_mentions(text: str, skill: str) -> None:
    for token, exact in (
        ("playwright-cli", PLAYWRIGHT_CLI),
        ("chrome-devtools-mcp", CHROME_WRAPPER),
    ):
        pattern = re.compile(rf"(?<![\w-]){re.escape(token)}(?![\w-])")
        prefix = exact[: -len(token)]
        for match in pattern.finditer(text):
            actual_prefix = text[max(0, match.start() - len(prefix)) : match.start()]
            require(actual_prefix == prefix, f"{skill}: {token} must use exact {exact}")


def validate_skill_contract(skill: str, text: str) -> None:
    require(
        text.count(MANDATORY_SKILL_BOUNDARY) == 1,
        f"{skill}: mandatory CloakBrowser boundary must appear exactly once",
    )
    remainder = text.replace(MANDATORY_SKILL_BOUNDARY, "", 1)
    require(
        "run-code" not in remainder,
        f"{skill}: run-code is forbidden outside the boundary declaration",
    )
    require(
        "--filename" not in remainder,
        f"{skill}: --filename is forbidden outside the boundary declaration",
    )
    require_exact_provider_mentions(remainder, skill)

    for block in bash_blocks(remainder):
        previous_command = ""
        for raw_line in block:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "$HOME/.local/bin/playwright-cli" in line:
                require(
                    previous_command == "$HOME/.local/bin/cloakbrowser-cdp-health",
                    f"{skill}: every Playwright CLI action must be immediately health-gated",
                )
            previous_command = line

    if skill == "webwright-task":
        require(
            "This skill name is retained only for routing compatibility." in text,
            "webwright-task must be a compatibility workflow",
        )
        require(
            "Never install, import, or execute `webwright` Python code." in text,
            "webwright-task must forbid the Webwright Python runtime",
        )


def validate() -> None:
    mcp = json.loads((ROOT / "plugins/rldyour-mcps/.mcp.json").read_text(encoding="utf-8"))[
        "mcpServers"
    ]
    require("playwright" not in mcp, "playwright must not be an active MCP server")
    require("webwright" not in mcp, "webwright must not be an active MCP server")
    chrome = mcp.get("chrome-devtools") or {}
    require(bool(chrome), "chrome-devtools MCP server is required")
    require(
        chrome.get("command") == CHROME_COMMAND,
        "chrome-devtools must use the managed wrapper shell transport",
    )
    require(
        chrome.get("args") == CHROME_ARGS,
        "chrome-devtools must use the exact managed CloakBrowser wrapper invocation",
    )

    skills_root = ROOT / "plugins/rldyour-browser/skills"
    for skill in sorted(REQUIRED_SKILLS):
        path = skills_root / skill / "SKILL.md"
        require(path.is_file(), f"missing browser skill: {skill}")
        validate_skill_contract(skill, path.read_text(encoding="utf-8"))

    env = (ROOT / "config/mcp-runtime-versions.env").read_text(encoding="utf-8")
    require("PLAYWRIGHT_CLI_VERSION=0.1.17" in env, "Playwright CLI version pin missing")
    require("WEBWRIGHT_" not in env, "Webwright runtime pins must be absent")

    contract = json.loads((ROOT / "config/rldyour-contract.json").read_text(encoding="utf-8"))
    require(
        contract.get("browser_providers") == EXPECTED_BROWSER_PROVIDERS,
        "browser_providers must contain only managed providers plus the webwright-task compatibility workflow",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Claude browser provider policy.")
    parser.add_argument("--strict", action="store_true")
    parser.parse_args()
    try:
        validate()
    except Failure as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1
    print("ok: Claude CloakBrowser skill boundary and provider policy validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
