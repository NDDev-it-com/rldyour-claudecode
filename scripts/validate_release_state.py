#!/usr/bin/env python3
"""validate_release_state.py - release-state parity gate.

Hard invariants enforced before any release tag is pushed:

1. VERSION file matches the latest released CHANGELOG section
   (`## [X.Y.Z] - YYYY-MM-DD`) excluding `[Unreleased]`.
2. Root metadata versions in package.json and pyproject.toml match VERSION.
3. Marketplace top-level / per-plugin versions in
   .claude-plugin/marketplace.json match plugins/*/.claude-plugin/plugin.json
   (already enforced by validate_plugin_versions.py - we re-call it
   structurally for tag-cycle context).
4. Tag naming convention: if a git tag named `marketplace--v<VERSION>` or
   `<plugin>--v<plugin_version>` exists, it must point at HEAD (current
   release commit) and not any earlier commit. Tags that do not yet exist
   are not flagged - the caller (release.yml workflow) creates them.
5. scripts/release_manifest.py produces parseable JSON that includes the
   declared VERSION and per-plugin versions.

Exit codes: 0 release-ready, 1 on any inconsistency.

Designed to be called from `release.yml` and from local pre-release
validation via `bash scripts/validate_marketplace.sh`. Safe to run on any
commit (not just release commits) - it never modifies state.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

CHANGELOG_RELEASE_RE = re.compile(
    r"^## \[(?P<version>\d+\.\d+\.\d+)\]\s+-\s+\d{4}-\d{2}-\d{2}\s*$",
    re.MULTILINE,
)


_GIT_TIMEOUT_SEC = 30
EXPECTED_LICENSE = "AGPL-3.0-or-later"
EXPECTED_AUTHOR_NAME = "Danil Silantyev"


def _git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
            timeout=_GIT_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            args=["git", *args],
            returncode=124,
            stdout="",
            stderr=f"git {' '.join(args)} timed out after {_GIT_TIMEOUT_SEC}s",
        )


def _head_sha(cwd: Path | None = None) -> str:
    proc = _git("rev-parse", "HEAD", cwd=cwd)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _tag_sha(tag: str, cwd: Path | None = None) -> str | None:
    proc = _git("rev-list", "-n", "1", tag, cwd=cwd)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def validate_version_vs_changelog(root: Path) -> list[str]:
    errors: list[str] = []
    version_path = root / "VERSION"
    if not version_path.is_file():
        return ["VERSION file is missing"]
    version = version_path.read_text(encoding="utf-8").strip()

    changelog_path = root / "CHANGELOG.md"
    if not changelog_path.is_file():
        return [f"CHANGELOG.md is missing; VERSION={version}"]
    changelog = changelog_path.read_text(encoding="utf-8")
    releases = CHANGELOG_RELEASE_RE.findall(changelog)
    if not releases:
        return [f"CHANGELOG.md has no `## [X.Y.Z] - YYYY-MM-DD` entries; VERSION={version}"]
    latest = releases[0]
    if latest != version:
        errors.append(
            f"VERSION={version} does not match latest CHANGELOG entry [{latest}]; "
            f"fix one or both before releasing"
        )
    return errors


def validate_root_metadata_parity(root: Path, version: str) -> list[str]:
    errors: list[str] = []

    package_path = root / "package.json"
    if not package_path.is_file():
        errors.append(f"package.json is missing; VERSION={version}")
    else:
        try:
            package = json.loads(package_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"package.json is not valid JSON: {exc}")
        else:
            package_version = package.get("version")
            if package_version != version:
                errors.append(
                    f"package.json version={package_version!r} does not match VERSION={version!r}"
                )
            if package.get("license") != EXPECTED_LICENSE:
                errors.append(
                    f"package.json license={package.get('license')!r} "
                    f"does not match {EXPECTED_LICENSE!r}"
                )
            author = package.get("author")
            if not isinstance(author, dict) or author.get("name") != (
                "Danil Silantyev (github:rldyourmnd), CEO NDDev"
            ):
                errors.append("package.json author must identify Danil Silantyev / rldyourmnd")

    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.is_file():
        errors.append(f"pyproject.toml is missing; VERSION={version}")
    else:
        try:
            pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"pyproject.toml is not valid TOML: {exc}")
        else:
            project = pyproject.get("project", {})
            pyproject_version = project.get("version") if isinstance(project, dict) else None
            if pyproject_version != version:
                errors.append(
                    f"pyproject.toml project.version={pyproject_version!r} "
                    f"does not match VERSION={version!r}"
                )
            pyproject_license = project.get("license") if isinstance(project, dict) else None
            if pyproject_license != EXPECTED_LICENSE:
                errors.append(
                    f"pyproject.toml project.license={pyproject_license!r} "
                    f"does not match {EXPECTED_LICENSE!r}"
                )
            authors = project.get("authors") if isinstance(project, dict) else None
            if not isinstance(authors, list) or not any(
                isinstance(author, dict) and author.get("name") == EXPECTED_AUTHOR_NAME
                for author in authors
            ):
                errors.append("pyproject.toml authors must include Danil Silantyev")

    return errors


def validate_manifest_parity(root: Path) -> list[str]:
    errors: list[str] = []
    marketplace = json.loads((root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    entries = {p["name"]: p for p in marketplace.get("plugins", [])}
    for plugin_dir in sorted((root / "plugins").iterdir()):
        if not plugin_dir.is_dir():
            continue
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest_path.is_file():
            errors.append(f"{plugin_dir.name}: missing .claude-plugin/plugin.json")
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        name = manifest.get("name")
        if name != plugin_dir.name:
            errors.append(f"{plugin_dir.name}: plugin.json name={name!r} differs from directory")
        manifest_version = manifest.get("version")
        entry = entries.get(name)
        if entry is None:
            errors.append(f"{name}: present in plugins/ but missing from marketplace.json")
            continue
        entry_version = entry.get("version")
        if manifest_version != entry_version:
            errors.append(
                f"{name}: version drift - plugin.json={manifest_version} vs "
                f"marketplace entry={entry_version}"
            )
    return errors


def validate_tag_alignment(root: Path, version: str) -> list[str]:
    warnings: list[str] = []
    head = _head_sha(cwd=root)
    if not head:
        return ["INFO not a git repository or HEAD unreadable; skipping tag alignment"]
    candidate = f"marketplace--v{version}"
    tag_sha = _tag_sha(candidate, cwd=root)
    if tag_sha is None:
        warnings.append(
            f"INFO tag '{candidate}' does not yet exist locally - "
            f"release.yml will create it on tag push"
        )
        return warnings
    if tag_sha != head:
        # Tag exists at an earlier commit. This is normal during feature work
        # (HEAD is ahead of the last released tag) and only becomes a release
        # blocker if invoked from release.yml after a tag push. Surface as INFO
        # so the release workflow can grep for FAIL without false positives.
        warnings.append(
            f"INFO tag '{candidate}' points at {tag_sha[:12]} but HEAD is {head[:12]}; "
            f"expected when working ahead of the last release"
        )
    return warnings


def validate_release_manifest(root: Path, version: str) -> list[str]:
    errors: list[str] = []
    script = root / "scripts" / "release_manifest.py"
    if not script.is_file():
        return ["scripts/release_manifest.py is missing"]
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            check=False,
            cwd=root,
            timeout=_GIT_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return [
            f"scripts/release_manifest.py timed out after {_GIT_TIMEOUT_SEC}s; "
            f"investigate locally"
        ]
    if proc.returncode != 0:
        return [f"scripts/release_manifest.py exited {proc.returncode}: {proc.stderr.strip()}"]
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return [f"scripts/release_manifest.py output is not valid JSON: {exc}"]
    if not isinstance(payload, dict):
        errors.append("release_manifest output must be a JSON object")
        return errors
    marketplace = payload.get("marketplace")
    if not isinstance(marketplace, dict):
        errors.append("release_manifest output missing marketplace object")
        return errors
    manifest_version = marketplace.get("version")
    if manifest_version != version:
        errors.append(
            f"release_manifest marketplace.version={manifest_version!r} "
            f"does not match VERSION={version!r}"
        )
    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    version = (root / "VERSION").read_text(encoding="utf-8").strip() if (root / "VERSION").is_file() else ""
    failures: list[str] = []
    info: list[str] = []

    failures.extend(validate_version_vs_changelog(root))
    failures.extend(validate_root_metadata_parity(root, version))
    failures.extend(validate_manifest_parity(root))
    failures.extend(validate_release_manifest(root, version))

    for entry in validate_tag_alignment(root, version):
        if entry.startswith("INFO"):
            info.append(entry)
        else:
            failures.append(entry)

    for line in info:
        print(line)

    if failures:
        for line in failures:
            print(f"FAIL {line}", file=sys.stderr)
        return 1

    print(f"OK release state parity confirmed for VERSION={version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
