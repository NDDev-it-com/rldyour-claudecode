#!/usr/bin/env python3
"""Validate the rldyour cross-tool business contract.

The contract is intentionally not a Claude Code manifest. It is the
machine-readable parity layer that explains how the same business mechanism is
represented in Claude Code, Codex, and OpenCode.

This validator proves the local Claude Code adapter against the repository and
checks that non-local adapters are explicitly mapped, documented as absent, or
marked as adapter-specific. It does not read sibling repositories.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

REQUIRED_ADAPTERS = ("claude", "codex", "opencode")
CONTRACT_PATH = Path("config/rldyour-contract.json")


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _require_list(payload: Mapping[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        errors.append(f"{key}: expected list")
        return []
    return value


def _ids(items: Iterable[Mapping[str, Any]], section: str, errors: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for index, item in enumerate(items):
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            errors.append(f"{section}[{index}]: missing non-empty id")
            continue
        if item_id in seen:
            errors.append(f"{section}: duplicate id {item_id!r}")
        seen.add(item_id)
        result.append(item_id)
    return result


def _validate_adapter_map(item: Mapping[str, Any], section: str, item_id: str, errors: list[str]) -> None:
    for adapter in REQUIRED_ADAPTERS:
        value = item.get(adapter)
        if not isinstance(value, dict):
            errors.append(f"{section}.{item_id}: missing {adapter} adapter mapping")
            continue
        has_mapping = any(key in value for key in ("path", "plugin", "name", "invocation", "workflow"))
        has_status = isinstance(value.get("status"), str) and bool(value["status"].strip())
        if not has_mapping and not has_status:
            errors.append(
                f"{section}.{item_id}.{adapter}: mapping must include a concrete field or status"
            )


def _require_path(root: Path, section: str, item_id: str, path_value: Any, errors: list[str]) -> Path | None:
    if not isinstance(path_value, str) or not path_value.strip():
        errors.append(f"{section}.{item_id}: missing path")
        return None
    if path_value.startswith("/") or ".." in Path(path_value).parts:
        errors.append(f"{section}.{item_id}: path must be repo-relative and cannot traverse: {path_value}")
        return None
    path = root / path_value
    if not path.exists():
        errors.append(f"{section}.{item_id}: path does not exist: {path_value}")
        return None
    return path


def _marketplace_plugins(root: Path, errors: list[str]) -> dict[str, dict[str, Any]]:
    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    try:
        marketplace = _load_json(marketplace_path)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f".claude-plugin/marketplace.json: cannot read JSON: {exc}")
        return {}

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        errors.append(".claude-plugin/marketplace.json: plugins must be a list")
        return {}

    result: dict[str, dict[str, Any]] = {}
    for entry in plugins:
        if not isinstance(entry, dict):
            errors.append(".claude-plugin/marketplace.json: plugin entry must be object")
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            errors.append(".claude-plugin/marketplace.json: plugin entry missing name")
            continue
        result[name] = entry
    return result


def _plugin_manifest(root: Path, plugin: str, errors: list[str]) -> dict[str, Any] | None:
    path = root / "plugins" / plugin / ".claude-plugin" / "plugin.json"
    if not path.is_file():
        errors.append(f"{plugin}: missing plugin manifest at {_rel(root, path)}")
        return None
    try:
        payload = _load_json(path)
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(root, path)}: invalid JSON: {exc}")
        return None
    if payload.get("name") != plugin:
        errors.append(f"{_rel(root, path)}: name {payload.get('name')!r} does not match {plugin!r}")
    return payload if isinstance(payload, dict) else None


def _validate_domains(root: Path, contract: Mapping[str, Any], errors: list[str]) -> None:
    marketplace = _marketplace_plugins(root, errors)
    domains = _require_list(contract, "domains", errors)
    _ids([entry for entry in domains if isinstance(entry, dict)], "domains", errors)

    contract_plugins: set[str] = set()
    for entry in domains:
        if not isinstance(entry, dict):
            errors.append("domains: every entry must be object")
            continue
        item_id = str(entry.get("id", "<missing>"))
        _validate_adapter_map(entry, "domains", item_id, errors)
        claude = entry.get("claude", {})
        plugin = claude.get("plugin") if isinstance(claude, dict) else None
        if not isinstance(plugin, str):
            errors.append(f"domains.{item_id}.claude: missing plugin")
            continue
        contract_plugins.add(plugin)
        if plugin not in marketplace:
            errors.append(f"domains.{item_id}: Claude plugin {plugin!r} is not in marketplace")
            continue
        _plugin_manifest(root, plugin, errors)

    marketplace_names = set(marketplace)
    missing = sorted(marketplace_names - contract_plugins)
    extra = sorted(contract_plugins - marketplace_names)
    if missing:
        errors.append(f"domains: marketplace plugins missing from contract: {', '.join(missing)}")
    if extra:
        errors.append(f"domains: contract plugins not in marketplace: {', '.join(extra)}")


def _validate_path_mapped_section(
    root: Path,
    contract: Mapping[str, Any],
    section: str,
    errors: list[str],
    *,
    required_suffix: str | None = None,
) -> None:
    entries = _require_list(contract, section, errors)
    _ids([entry for entry in entries if isinstance(entry, dict)], section, errors)
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append(f"{section}: every entry must be object")
            continue
        item_id = str(entry.get("id", "<missing>"))
        _validate_adapter_map(entry, section, item_id, errors)
        claude = entry.get("claude")
        if not isinstance(claude, dict):
            continue
        path_value = claude.get("path")
        if path_value is None:
            # Domain entries validate plugin membership separately. CI entries
            # may point at workflows/scripts instead of a single component.
            continue
        path = _require_path(root, section, item_id, path_value, errors)
        if path is not None and required_suffix and not path.as_posix().endswith(required_suffix):
            errors.append(
                f"{section}.{item_id}: path {path_value!r} must end with {required_suffix!r}"
            )


def _iter_hook_commands(payload: Any) -> Iterable[dict[str, Any]]:
    if isinstance(payload, dict):
        if payload.get("type") == "command":
            yield payload
        for value in payload.values():
            yield from _iter_hook_commands(value)
    elif isinstance(payload, list):
        for value in payload:
            yield from _iter_hook_commands(value)


def _hook_manifest_has_script(manifest: Mapping[str, Any], script_name: str) -> bool:
    expected = "${CLAUDE_PLUGIN_ROOT}/hooks/" + script_name
    for command in _iter_hook_commands(manifest):
        args = command.get("args")
        if isinstance(args, list) and expected in args:
            return True
        command_value = command.get("command")
        if isinstance(command_value, str) and expected in command_value:
            return True
    return False


def _validate_hook_lifecycle(root: Path, contract: Mapping[str, Any], errors: list[str]) -> None:
    entries = _require_list(contract, "hook_lifecycle", errors)
    _ids([entry for entry in entries if isinstance(entry, dict)], "hook_lifecycle", errors)
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("hook_lifecycle: every entry must be object")
            continue
        item_id = str(entry.get("id", "<missing>"))
        _validate_adapter_map(entry, "hook_lifecycle", item_id, errors)
        claude = entry.get("claude")
        if not isinstance(claude, dict):
            continue
        owner = claude.get("plugin")
        event = claude.get("event")
        script_path_value = claude.get("script")
        if not isinstance(owner, str) or not owner:
            errors.append(f"hook_lifecycle.{item_id}.claude: missing plugin")
            continue
        if not isinstance(event, str) or not event:
            errors.append(f"hook_lifecycle.{item_id}.claude: missing event")
            continue
        script_path = _require_path(root, "hook_lifecycle", item_id, script_path_value, errors)
        manifest_path = root / "plugins" / owner / "hooks" / "hooks.json"
        if not manifest_path.is_file():
            errors.append(f"hook_lifecycle.{item_id}: missing hooks manifest {_rel(root, manifest_path)}")
            continue
        try:
            manifest = _load_json(manifest_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{_rel(root, manifest_path)}: invalid JSON: {exc}")
            continue
        hooks = manifest.get("hooks")
        if not isinstance(hooks, dict) or event not in hooks:
            errors.append(f"hook_lifecycle.{item_id}: event {event!r} missing from {_rel(root, manifest_path)}")
        if script_path and not _hook_manifest_has_script(manifest, script_path.name):
            errors.append(
                f"hook_lifecycle.{item_id}: {_rel(root, script_path)} is not referenced by "
                f"{_rel(root, manifest_path)}"
            )


def _validate_ci_baseline(root: Path, contract: Mapping[str, Any], errors: list[str]) -> None:
    entries = _require_list(contract, "ci_baseline", errors)
    _ids([entry for entry in entries if isinstance(entry, dict)], "ci_baseline", errors)
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("ci_baseline: every entry must be object")
            continue
        item_id = str(entry.get("id", "<missing>"))
        _validate_adapter_map(entry, "ci_baseline", item_id, errors)
        claude = entry.get("claude")
        if not isinstance(claude, dict):
            continue
        for field in ("workflow", "script", "command"):
            value = claude.get(field)
            if isinstance(value, str) and value.endswith((".py", ".sh", ".yml", ".yaml", ".json")):
                _require_path(root, "ci_baseline", f"{item_id}.{field}", value, errors)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    contract_path = root / CONTRACT_PATH
    if not contract_path.is_file():
        return [f"{CONTRACT_PATH.as_posix()} is missing"]
    try:
        contract = _load_json(contract_path)
    except json.JSONDecodeError as exc:
        return [f"{CONTRACT_PATH.as_posix()} is not valid JSON: {exc}"]
    if not isinstance(contract, dict):
        return [f"{CONTRACT_PATH.as_posix()} must contain a JSON object"]

    schema_version = contract.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        errors.append("schema_version must be an integer >= 1")

    adapters = contract.get("adapters")
    if adapters != list(REQUIRED_ADAPTERS):
        errors.append(f"adapters must be exactly {list(REQUIRED_ADAPTERS)!r}")

    _validate_domains(root, contract, errors)
    _validate_path_mapped_section(root, contract, "public_flows", errors)
    _validate_path_mapped_section(root, contract, "skills", errors, required_suffix="/SKILL.md")
    _validate_path_mapped_section(root, contract, "agent_roles", errors, required_suffix=".md")
    _validate_hook_lifecycle(root, contract, errors)
    _validate_ci_baseline(root, contract, errors)

    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    print("OK rldyour contract matches local Claude Code implementation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
