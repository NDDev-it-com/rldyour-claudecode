#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path

FULLREPO_BRANCH = "fullrepo"
DEFAULT_REMOTE = "origin"
EXCLUDE_BEGIN = "# >>> rldyour fullrepo agent-only files >>>"
EXCLUDE_END = "# <<< rldyour fullrepo agent-only files <<<"

AGENT_ONLY_PATTERNS = (
    "AGENTS.md",
    "CLAUDE.md",
    "REVIEW.md",
    "GEMINI.md",
    "QWEN.md",
    ".cursorrules",
    ".windsurfrules",
    ".aider*",
    ".claude/**",
    ".codex/**",
    ".cursor/rules/**",
    ".gemini/**",
    ".roo/**",
    ".windsurf/**",
    ".openhands/**",
    ".github/copilot-instructions.md",
    ".github/instructions/**",
    ".github/prompts/**",
    ".agents/skills/**",
    ".agents/commands/**",
    ".agents/hooks/**",
    ".serena/project.yml",
    ".serena/memories/**",
    ".serena/plans/**",
    ".serena/research/**",
    ".serena/newproj/**",
    ".serena/deploy/**",
)

RUNTIME_EXCLUDE_PATTERNS = (
    ".serena/cache/**",
    ".serena/diagnostics/**",
    ".serena/reviews/**",
    ".serena/.gitignore",
    ".serena/project.local.yml",
    ".serena/.sync_marker",
    ".serena/.serena_sync_state.json",
    ".serena/.auto_sync_head",
    ".serena/.active_workflow_intent.json",
    ".serena/.dirty_stop_ack",
    ".serena/.flow_sync_marker",
    ".serena/.flow_post_task_state.json",
    ".serena/.bootstrap_overrides.log",
)

SECRET_RE = re.compile(
    r"ctx7sk-[A-Za-z0-9-]+|"
    r"ghp_[A-Za-z0-9_]+|"
    r"github_pat_[A-Za-z0-9_]+|"
    r"sk-[A-Za-z0-9_-]{16,}|"
    r"xox[baprs]-[A-Za-z0-9-]+|"
    r"BEGIN (?:RSA|OPENSSH|PRIVATE) KEY|"
    r"Bearer\s+[A-Za-z0-9._-]{20,}"
)


class FullrepoError(RuntimeError):
    pass


def _git(*args: str, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(["git", *args], check=False, capture_output=True, text=True, env=env)
    if check and proc.returncode != 0:
        details = (proc.stderr or proc.stdout).strip()
        raise FullrepoError(f"git {' '.join(args)} failed: {details}")
    return proc


def _stdout(*args: str, check: bool = True, env: dict[str, str] | None = None) -> str:
    return _git(*args, check=check, env=env).stdout.strip()


def git_identity_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "Danil Silantyev")
    env.setdefault("GIT_AUTHOR_EMAIL", "rldyourmnd@users.noreply.github.com")
    env.setdefault("GIT_COMMITTER_NAME", "Danil Silantyev")
    env.setdefault("GIT_COMMITTER_EMAIL", "rldyourmnd@users.noreply.github.com")
    return env


def repo_root() -> Path:
    proc = _git("rev-parse", "--show-toplevel", check=False)
    if proc.returncode != 0:
        raise FullrepoError("Not inside a git repository")
    return Path(proc.stdout.strip())


def git_dir() -> Path:
    return Path(_stdout("rev-parse", "--git-dir")).resolve()


def normalize_path(path: str | Path) -> str:
    return str(path).replace(os.sep, "/").strip("/")


def pattern_matches(path: str, patterns: Iterable[str]) -> bool:
    normalized = normalize_path(path)
    for pattern in patterns:
        pattern = normalize_path(pattern)
        if pattern.endswith("/**"):
            prefix = pattern[:-3].rstrip("/")
            if normalized == prefix or normalized.startswith(prefix + "/"):
                return True
        if fnmatch.fnmatchcase(normalized, pattern):
            return True
    return False


def is_agent_path(path: str) -> bool:
    return pattern_matches(path, AGENT_ONLY_PATTERNS) and not pattern_matches(path, RUNTIME_EXCLUDE_PATTERNS)


def git_exclude_path() -> Path:
    return git_dir() / "info" / "exclude"


def exclude_block() -> str:
    lines = [EXCLUDE_BEGIN]
    for pattern in AGENT_ONLY_PATTERNS:
        lines.append("/" + pattern)
    for pattern in RUNTIME_EXCLUDE_PATTERNS:
        lines.append("!/" + pattern)
    lines.append(EXCLUDE_END)
    return "\n".join(lines) + "\n"


def exclude_installed() -> bool:
    path = git_exclude_path()
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    return EXCLUDE_BEGIN in text and EXCLUDE_END in text


def install_exclude(dry_run: bool = False) -> None:
    path = git_exclude_path()
    current = path.read_text(encoding="utf-8") if path.is_file() else ""
    block = exclude_block()
    pattern = re.compile(
        re.escape(EXCLUDE_BEGIN) + r".*?" + re.escape(EXCLUDE_END) + r"\n?",
        re.S,
    )
    if pattern.search(current):
        new_text = pattern.sub(block, current)
    else:
        separator = "" if not current or current.endswith("\n") else "\n"
        new_text = current + separator + block

    if new_text == current:
        print("fullrepo exclude block already installed")
        return

    if dry_run:
        print(f"dry-run: would update {path}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new_text, encoding="utf-8")
    print(f"installed fullrepo exclude block in {path}")


def split_porcelain_path(line: str) -> str:
    path = line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return normalize_path(path)


def dirty_non_agent_paths() -> list[str]:
    raw = _git("status", "--porcelain", "--untracked-files=all").stdout.rstrip("\n")
    paths: list[str] = []
    for line in raw.splitlines():
        if not line:
            continue
        path = split_porcelain_path(line)
        if path and not is_agent_path(path) and not pattern_matches(path, RUNTIME_EXCLUDE_PATTERNS):
            paths.append(path)
    return sorted(set(paths))


def tracked_agent_paths(ref: str = "HEAD") -> list[str]:
    raw = _stdout("ls-tree", "-r", "--name-only", ref, check=False)
    return sorted(path for path in raw.splitlines() if is_agent_path(path))


def tracked_agent_paths_in_index() -> list[str]:
    raw = _stdout("ls-files", check=False)
    return sorted(path for path in raw.splitlines() if is_agent_path(path))


def remote_branch_sha(remote: str, branch: str) -> str:
    raw = _stdout("ls-remote", "--heads", remote, branch, check=False)
    if not raw:
        return ""
    return raw.split()[0]


def remote_configured(remote: str) -> bool:
    return _git("remote", "get-url", remote, check=False).returncode == 0


def local_ref_sha(ref: str) -> str:
    return _stdout("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", check=False)


def ref_tree_sha(ref: str) -> str:
    return _stdout("rev-parse", "--verify", "--quiet", f"{ref}^{{tree}}", check=False)


def fetch_fullrepo(remote: str, branch: str) -> bool:
    spec = f"+refs/heads/{branch}:refs/remotes/{remote}/{branch}"
    proc = _git("fetch", "--quiet", remote, spec, check=False)
    return proc.returncode == 0


def iter_worktree_agent_files(root: Path) -> list[str]:
    paths: set[str] = set()
    for pattern in AGENT_ONLY_PATTERNS:
        for candidate in root.glob(pattern):
            if ".git" in candidate.parts:
                continue
            if candidate.is_dir():
                for file_path in candidate.rglob("*"):
                    if file_path.is_file():
                        rel = normalize_path(file_path.relative_to(root))
                        if is_agent_path(rel):
                            paths.add(rel)
            elif candidate.is_file():
                rel = normalize_path(candidate.relative_to(root))
                if is_agent_path(rel):
                    paths.add(rel)
    return sorted(paths)


def scan_for_secrets(root: Path, paths: Iterable[str]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        file_path = root / path
        if not file_path.is_file():
            continue
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if SECRET_RE.search(text):
            hits.append(path)
    return hits


def build_fullrepo_tree(root: Path) -> tuple[str, list[str]]:
    agent_paths = iter_worktree_agent_files(root)
    secret_hits = scan_for_secrets(root, agent_paths)
    if secret_hits:
        raise FullrepoError("refusing to publish secret-looking agent-only files: " + ", ".join(secret_hits))

    with tempfile.NamedTemporaryFile(prefix="rldyour-fullrepo-index.") as tmp_index:
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = tmp_index.name
        _git("read-tree", "HEAD", env=env)

        head_agent_paths = tracked_agent_paths("HEAD")
        if head_agent_paths:
            _git("rm", "--cached", "-q", "--ignore-unmatch", "--", *head_agent_paths, env=env)

        if agent_paths:
            _git("add", "-f", "--", *agent_paths, env=env)

        tree = _stdout("write-tree", env=env)
        return tree, agent_paths


def publish(remote: str, branch: str, dry_run: bool = False) -> None:
    root = repo_root()
    non_agent_dirty = dirty_non_agent_paths()
    if non_agent_dirty:
        raise FullrepoError(
            "refusing to publish fullrepo while non-agent files are dirty: "
            + ", ".join(non_agent_dirty)
        )

    install_exclude(dry_run=dry_run)
    tree, agent_paths = build_fullrepo_tree(root)
    head = _stdout("rev-parse", "HEAD")
    head_short = head[:7]

    expected_remote = remote_branch_sha(remote, branch)
    remote_ref = f"refs/remotes/{remote}/{branch}"
    remote_tree = ""
    if expected_remote:
        fetch_fullrepo(remote, branch)
        remote_tree = _stdout("rev-parse", f"{remote_ref}^{{tree}}", check=False)

    if remote_tree and remote_tree == tree:
        print(f"fullrepo already matches HEAD {head_short} plus {len(agent_paths)} agent-only files")
        return

    parent_args: list[str] = []
    parent_args = ["-p", expected_remote] if expected_remote else ["-p", head]

    message = (
        f"chore(fullrepo): sync {head_short}\n\n"
        f"Base-branch-head: {head}\n"
        f"Agent-only-files: {len(agent_paths)}\n"
    )
    commit = _stdout("commit-tree", tree, *parent_args, "-m", message, env=git_identity_env())

    if dry_run:
        print(f"dry-run: would update refs/heads/{branch} to {commit[:12]}")
        print(f"dry-run: would push {branch} with --force-with-lease")
        return

    _git("update-ref", f"refs/heads/{branch}", commit)
    lease_value = expected_remote if expected_remote else ""
    lease = f"--force-with-lease=refs/heads/{branch}:{lease_value}"
    _git("push", lease, remote, f"{commit}:refs/heads/{branch}")
    print(f"published {branch} at {commit[:12]} from HEAD {head_short} with {len(agent_paths)} agent-only files")


def restore(remote: str, branch: str, dry_run: bool = False) -> None:
    install_exclude(dry_run=dry_run)
    if not fetch_fullrepo(remote, branch):
        print(f"fullrepo branch {remote}/{branch} does not exist; restore skipped")
        return

    ref = f"refs/remotes/{remote}/{branch}"
    remote_paths = tracked_agent_paths(ref)
    if not remote_paths:
        print(f"fullrepo branch {remote}/{branch} has no agent-only files")
        return

    if dry_run:
        print(f"dry-run: would restore {len(remote_paths)} agent-only files from {remote}/{branch}")
        return

    for index in range(0, len(remote_paths), 64):
        chunk = remote_paths[index : index + 64]
        _git("restore", "--source", ref, "--worktree", "--", *chunk)

    print(f"restored {len(remote_paths)} agent-only files from {remote}/{branch}")


def migrate_main(dry_run: bool = False) -> None:
    install_exclude(dry_run=dry_run)
    paths = tracked_agent_paths_in_index()
    if not paths:
        print("no tracked agent-only files in current branch index")
        return
    if dry_run:
        print("dry-run: would remove agent-only files from current branch index:")
        for path in paths:
            print(path)
        return
    _git("rm", "--cached", "-r", "--ignore-unmatch", "--", *paths)
    print(f"removed {len(paths)} agent-only files from current branch index; files remain in the working tree")


def bootstrap_init(remote: str, branch: str, dry_run: bool = False) -> None:
    root = repo_root()
    local_agent_paths = iter_worktree_agent_files(root)
    remote_exists = fetch_fullrepo(remote, branch)
    actions: list[str] = []

    install_exclude(dry_run=dry_run)

    if remote_exists:
        actions.append("restore")
        restore(remote, branch, dry_run=dry_run)
    elif local_agent_paths:
        actions.append("publish")
        publish(remote, branch, dry_run=dry_run)
    else:
        print(f"fullrepo branch {remote}/{branch} does not exist and no local agent-only files were found")

    if tracked_agent_paths_in_index():
        actions.append("migrate-main")
        migrate_main(dry_run=dry_run)

    payload = status(remote, branch)
    payload["bootstrap_actions"] = actions
    print_status(payload, as_json=False)


def status(remote: str, branch: str) -> dict[str, object]:
    root = repo_root()
    has_remote = remote_configured(remote)
    remote_sha = remote_branch_sha(remote, branch)
    local_sha = local_ref_sha(f"refs/heads/{branch}")
    remote_ref = f"refs/remotes/{remote}/{branch}"
    remote_tree = ""
    if remote_sha and fetch_fullrepo(remote, branch):
        remote_tree = ref_tree_sha(remote_ref)
    local_tree = ref_tree_sha(f"refs/heads/{branch}") if local_sha else ""
    expected_tree, agent_paths = build_fullrepo_tree(root)
    comparison_tree = remote_tree or local_tree
    return {
        "is_git_repo": True,
        "root": str(root),
        "branch": _stdout("branch", "--show-current", check=False) or "detached",
        "head": _stdout("rev-parse", "--short=12", "HEAD", check=False),
        "remote": remote,
        "remote_configured": has_remote,
        "fullrepo_branch": branch,
        "network_checked": True,
        "remote_fullrepo_exists": bool(remote_sha),
        "remote_fullrepo_sha": remote_sha[:12] if remote_sha else "",
        "remote_fullrepo_tree": remote_tree,
        "local_fullrepo_sha": local_sha[:12] if local_sha else "",
        "local_fullrepo_tree": local_tree,
        "expected_fullrepo_tree": expected_tree,
        "fullrepo_matches_worktree": bool(comparison_tree and comparison_tree == expected_tree),
        "local_fullrepo_matches_worktree": bool(local_tree and local_tree == expected_tree),
        "exclude_installed": exclude_installed(),
        "tracked_agent_paths": tracked_agent_paths_in_index(),
        "worktree_agent_paths": agent_paths,
        "dirty_non_agent_paths": dirty_non_agent_paths(),
    }


def print_status(payload: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, sort_keys=True))
        return
    print(json.dumps(payload, indent=2, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synchronize rldyour agent-only files through a fullrepo branch.")
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    parser.add_argument("--branch", default=FULLREPO_BRANCH)
    parser.add_argument("--dry-run", action="store_true")
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--status", action="store_true")
    actions.add_argument("--status-json", action="store_true")
    actions.add_argument("--install-exclude", action="store_true")
    actions.add_argument("--restore", action="store_true")
    actions.add_argument("--publish", action="store_true")
    actions.add_argument("--migrate-main", action="store_true")
    actions.add_argument("--bootstrap-init", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        repo_root()
        if args.status or args.status_json:
            print_status(status(args.remote, args.branch), as_json=args.status_json)
        elif args.install_exclude:
            install_exclude(dry_run=args.dry_run)
        elif args.restore:
            restore(args.remote, args.branch, dry_run=args.dry_run)
        elif args.publish:
            publish(args.remote, args.branch, dry_run=args.dry_run)
        elif args.migrate_main:
            migrate_main(dry_run=args.dry_run)
        elif args.bootstrap_init:
            bootstrap_init(args.remote, args.branch, dry_run=args.dry_run)
    except FullrepoError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
