#!/usr/bin/env python3
"""Analyze changed files and derive Serena memory refresh focus."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from collections.abc import Iterable
from typing import Any

MEMORY_TAXONOMY = {
    "version": 1,
    "filename_pattern": "AREA-01-SLUG.md",
    "index_memory": "CORE-01-INDEX.md",
    "split_rule": "one durable topic per memory; split when a file starts carrying multiple responsibilities",
    "areas": [
        {"area": "CORE", "purpose": "project index, marketplace architecture, plugin boundaries"},
        {"area": "CLAUDECODE", "purpose": "Claude Code plugin, skill, agent, hook and CLI canon"},
        {"area": "MCP", "purpose": "MCP transport, runtime pins, capability smoke contracts"},
        {"area": "SERENA", "purpose": "Serena memory sync, freshness state, analyzer contracts"},
        {"area": "HOOKS", "purpose": "Claude Code lifecycle hooks and advisory gate coordination"},
        {"area": "FLOW", "purpose": "ry-* SDLC workflow, tracked context, worktree, post-task sync"},
        {"area": "DOCS", "purpose": "AGENTS.md, CLAUDE.md, durable instruction policy"},
        {"area": "RELEASE", "purpose": "versioning, changelog, validation and release gates"},
        {"area": "TECHDEBT", "purpose": "open debt, closed error patterns, anti-regression rules"},
    ],
}

MEMORY_CANDIDATE_MEMORY_FILES = {
    "CORE-01-INDEX.md",
    "CORE-02-MARKETPLACE.md",
    "TECHDEBT-01-NOW.md",
}

KNOWN_MEMORIES = (
    ".serena/memories/",
    ".serena/plans/",
    ".serena/research/",
    ".serena/newproj/",
    ".serena/deploy/",
)

SERENA_RUNTIME_FILES = (
    ".serena/project.yml",
    ".serena/.sync_marker",
    ".serena/.serena_sync_state.json",
    ".serena/.auto_sync_head",
    ".serena/.active_workflow_intent.json",
    ".serena/.dirty_stop_ack",
    ".serena/.flow_sync_marker",
    ".serena/.flow_post_task_state.json",
    ".serena/.stop_lifecycle_timeout_marker",
)

AGENT_INSTRUCTION_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".claude/CLAUDE.md",
    "REVIEW.md",
    "GEMINI.md",
    "QWEN.md",
)

AGENT_INSTRUCTION_PREFIXES = (
    ".agents/commands/",
    ".agents/hooks/",
    ".agents/skills/",
    ".claude/",
    ".cursor/rules/",
    ".gemini/",
    ".roo/",
    ".windsurf/",
    ".openhands/",
    ".github/instructions/",
    ".github/prompts/",
)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], check=False, capture_output=True, text=True)


def _git_changed_files(from_ref: str, to_ref: str) -> list[str]:
    if not from_ref or not to_ref:
        return []
    proc = _git("diff", "--name-only", f"{from_ref}..{to_ref}")
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _match_prefix(path: str, prefixes: tuple[str, ...]) -> str | None:
    for prefix in prefixes:
        if path.startswith(prefix):
            return prefix.rstrip("/")
    return None


def _classify(path: str) -> str:
    if path.startswith(".serena/"):
        knowledge_area = _match_prefix(path, KNOWN_MEMORIES)
        if knowledge_area:
            return knowledge_area
        if path in SERENA_RUNTIME_FILES:
            return "serena-runtime"
        return "serena-runtime"

    if (
        path in AGENT_INSTRUCTION_FILES
        or path == ".github/copilot-instructions.md"
        or path.startswith(".aider")
        or _match_prefix(path, AGENT_INSTRUCTION_PREFIXES)
    ):
        return "agent-instructions"

    if path == ".claude-plugin/marketplace.json":
        return "marketplace-manifest"

    if path.startswith(".claude-plugin/"):
        return "marketplace-support"

    if path in {"VERSION", "CHANGELOG.md"}:
        return "release-versioning"

    if path.startswith("config/"):
        if path == "config/mcp-runtime-versions.env":
            return "mcp-runtime-config"
        return "repo-config"

    if path.startswith("plugins/"):
        parts = path.split("/", 3)
        if len(parts) >= 3:
            plugin = parts[1]
            if parts[2] == ".claude-plugin":
                if path.endswith("plugin.json"):
                    return f"{plugin}:manifest"
                return f"{plugin}:manifest"
            if path.endswith("/hooks.json") or path.startswith(f"plugins/{plugin}/hooks/"):
                return f"{plugin}:hooks"
            if path.startswith(f"plugins/{plugin}/skills/"):
                return f"{plugin}:skills"
            if path.startswith(f"plugins/{plugin}/commands/"):
                return f"{plugin}:commands"
            if path.startswith(f"plugins/{plugin}/agents/"):
                return f"{plugin}:agents"
            if path.startswith(f"plugins/{plugin}/scripts/"):
                return f"{plugin}:scripts"
            if path.startswith(f"plugins/{plugin}/references/"):
                return f"{plugin}:references"
            if path == f"plugins/{plugin}/.mcp.json":
                return f"{plugin}:mcp-transport"
            if path.startswith(f"plugins/{plugin}/.claude-plugin/"):
                return f"{plugin}:plugin-meta"
            if path.startswith(f"plugins/{plugin}/README.md"):
                return f"{plugin}:docs"
            return f"{plugin}:plugin-code"
        return "plugins-misc"

    if path.startswith("scripts/"):
        return "repo-scripts"

    if path.startswith(".github/workflows/") or path.startswith(".github/actions/"):
        return "ci-workflows"

    if path.startswith("docs/") or path == "README.md":
        if path.startswith("docs/release") or path in {"docs/dependency-updates.md", "README.md"}:
            return "release-docs"
        return "docs"

    return "other"


def _priority_for_area(area: str) -> str:
    if area in {
        "agent-instructions",
        "marketplace-manifest",
        "marketplace-support",
        "mcp-runtime-config",
        "release-versioning",
        "serena-runtime",
        ".serena-runtime",
    }:
        return "high"
    if area.endswith((":manifest", ":hooks", ":skills", ":commands", ":agents", ":scripts", ":mcp-transport")):
        return "high"
    if area.startswith("rldyour-serena-mcp:") or area.startswith("rldyour-flow:"):
        return "high"
    if area in {"ci-workflows", "repo-scripts"}:
        return "medium"
    return "low"


def _memory_targets_by_areas(areas: set[str]) -> list[tuple[str, str]]:
    targets: set[tuple[str, str]] = set()
    for area in areas:
        plugin = area.split(":", 1)[0] if ":" in area else None
        plugin_contract_change = area.endswith((":manifest", ":hooks", ":skills", ":commands", ":agents"))
        plugin_docs_change = area.endswith((":docs", ":references"))

        if area in {
            "marketplace-manifest",
            "marketplace-support",
            "release-versioning",
            "rldyour-mcps:manifest",
            "rldyour-mcps:mcp-transport",
            "rldyour-serena-mcp:manifest",
            "rldyour-flow:manifest",
        }:
            targets.add(("CORE-02-MARKETPLACE.md", "plugin manifests and marketplace contracts changed"))
            targets.add(("RELEASE-01-VALIDATION.md", "release or version contract changed"))
            targets.add(("CLAUDECODE-01-PLUGIN-CANON.md", "Claude Code plugin metadata contract changed"))
            if plugin in {"rldyour-serena-mcp", "rldyour-flow"}:
                targets.add(("SERENA-01-MEMORY-SYNC.md", "workflow and memory contracts changed"))

        if plugin_contract_change:
            targets.add(("CLAUDECODE-01-PLUGIN-CANON.md", "Claude Code plugin component contract changed"))

        if area.endswith(":hooks") or area.endswith(":skills") or area.endswith(":commands") or area.endswith(":agents") or area.endswith(":scripts") or plugin_docs_change:
            if plugin == "rldyour-serena-mcp":
                targets.add(("SERENA-01-MEMORY-SYNC.md", "Serena hooks/workflow automation changed"))
                targets.add(("HOOKS-01-LIFECYCLE.md", "Serena hook coordination changed"))
                targets.add(("CORE-02-MARKETPLACE.md", "Serena plugin contract changed"))
            elif plugin == "rldyour-flow":
                targets.add(("FLOW-01-SDLC.md", "flow workflow automation changed"))
                if area.endswith(":hooks"):
                    targets.add(("HOOKS-01-LIFECYCLE.md", "flow hook coordination changed"))
            else:
                targets.add(("CORE-02-MARKETPLACE.md", "plugin architecture and boundaries changed"))

        if area in {"mcp-runtime-config", "rldyour-mcps:mcp-transport"}:
            targets.add(("MCP-01-TRANSPORT.md", "MCP runtime or transport contract changed"))
            targets.add(("TECHDEBT-01-NOW.md", "MCP drift and validation guardrails changed"))

        if area.startswith("rldyour-flow:") and area.endswith((":hooks", ":scripts")):
            targets.add(("FLOW-01-SDLC.md", "workflow orchestration changed"))
            targets.add(("TECHDEBT-01-NOW.md", "operational sequencing and guardrails changed"))

        if area in {"agent-instructions", "marketplace-support"}:
            targets.add(("DOCS-01-INSTRUCTIONS.md", "agent instruction context changed"))
            targets.add(("CLAUDECODE-01-PLUGIN-CANON.md", "Claude Code instruction context changed"))
            targets.add(("TECHDEBT-01-NOW.md", "agent context and process constraints changed"))

        if area in {"repo-scripts", "ci-workflows", "docs", "release-docs", "release-versioning", "repo-config"}:
            targets.add(("RELEASE-01-VALIDATION.md", "operational or release validation contract changed"))
            targets.add(("TECHDEBT-01-NOW.md", "operational/process implications captured"))

    durable_non_runtime_areas = {
        area for area in areas if not area.startswith(".serena/") and area != "serena-runtime"
    }
    if durable_non_runtime_areas and not targets:
        for memory in MEMORY_CANDIDATE_MEMORY_FILES:
            if memory == "SERENA-01-MEMORY-SYNC.md":
                continue
            targets.add((memory, "baseline project memory update"))

    return sorted(targets, key=lambda item: (item[0], item[1]))


def analyze(paths: list[str]) -> dict[str, Any]:
    normalized = _unique(path for path in paths if path)
    scope: dict[str, list[str]] = defaultdict(list)
    for path in normalized:
        area = _classify(path)
        scope[area].append(path)

    for files in scope.values():
        files.sort()

    areas_sorted = sorted(
        (
            {
                "area": area,
                "count": len(files),
                "files": files,
                "priority": _priority_for_area(area),
            }
            for area, files in scope.items()
        ),
        # Pyright cannot narrow item["count"] to int from the dict's mixed
        # value type (str | int | list[str]); the construction site above
        # always sets count to an int.
        key=lambda item: (-item["count"], item["area"]),  # type: ignore[operator]
    )

    changed_areas = set(scope.keys())
    high_impact_areas = sorted(area for area in changed_areas if _priority_for_area(area) == "high")
    memory_targets = _memory_targets_by_areas(changed_areas)
    candidate_memory_focus = sorted({path for path, _ in memory_targets})

    knowledge_only = (
        all(area in {"serena-runtime", "agent-instructions"} or area.startswith(".serena/") for area in changed_areas)
        if changed_areas
        else False
    )
    strong_verification = bool(
        changed_areas
        and any(
            area == "agent-instructions"
            or area.startswith("rldyour-serena-mcp:")
            or area.startswith("rldyour-flow:")
            or area == "marketplace-manifest"
            for area in changed_areas
        )
    )
    sync_focus = "high" if high_impact_areas else ("medium" if memory_targets or (areas_sorted and not knowledge_only) else "low")

    return {
        "schema_version": 2,
        "memory_taxonomy": MEMORY_TAXONOMY,
        "file_count": len(normalized),
        "changed_files": normalized,
        "areas": areas_sorted,
        "areas_summary": {
            "high_impact": high_impact_areas,
            "all": sorted(changed_areas),
            "high_impact_count": len(high_impact_areas),
            "knowledge_only": knowledge_only,
        },
        "memory_targets": [
            {"path": path, "reason": reason}
            for path, reason in memory_targets
        ],
        "candidate_memory_focus": candidate_memory_focus,
        "risk_profile": {
            "sync_focus": sync_focus,
            "is_knowledge_only_change": knowledge_only,
            "requires_strong_verification": strong_verification,
        },
        "impact_signature": {
            "areas_count": len(changed_areas),
            "high_impact_count": len(high_impact_areas),
            "known_memory_targets": bool(memory_targets),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze Serena sync impact for changed files")
    parser.add_argument("--from-ref", default="", help="Git ref (short/long commit) for diff start")
    parser.add_argument("--to-ref", default="", help="Git ref (short/long commit) for diff end")
    parser.add_argument("--path", action="append", dest="paths", default=None, help="Explicit path to analyze")
    parser.add_argument("--stdin", action="store_true", help="Read one path per line from stdin")
    return parser.parse_args()


def gather_paths(args: argparse.Namespace) -> list[str]:
    if args.paths:
        return _unique(args.paths)
    if args.from_ref and args.to_ref:
        return _git_changed_files(args.from_ref, args.to_ref)
    if args.stdin:
        raw = sys.stdin.read()
        return [line.strip() for line in raw.splitlines() if line.strip()]
    return []


def main() -> int:
    args = parse_args()
    paths = gather_paths(args)
    json.dump(analyze(paths), sys.stdout, sort_keys=True, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
