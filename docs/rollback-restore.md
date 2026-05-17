# Rollback And Restore

Safe rollback paths when a `rldyour-claudecode` change breaks consumer projects or the marketplace itself.

## Rollback scopes

There are three independent surfaces that can need rollback:

1. **Marketplace `main`** - the source-of-truth git history.
2. **`fullrepo` branch** - agent-only file snapshot.
3. **User local Claude Code state** - installed plugin cache under `~/.claude/plugins/`.

Each has a different rollback technique. Pick the narrowest one that fixes the problem.

## Rollback `main` to a previous tag

```bash
# Identify the last green tag.
git fetch --all --tags
git tag --list 'rldyour-flow--*' --sort=-v:refname | head -5

# Inspect the diff before reverting.
git log --oneline <tag>..main
git diff <tag>..main -- plugins/rldyour-flow

# Option A: revert specific commits (preserves history).
git revert <bad-commit>..<head-commit>
git push origin main

# Option B: hard reset to tag (DESTRUCTIVE - only if no consumer cloned the bad state).
# This requires `--force-with-lease` to a remote and is rarely used.
# Prefer Option A for shared branches.
```

Re-run the pre-release checks (`scripts/validate_marketplace.sh`) after rollback before re-tagging.

## Rollback `fullrepo`

`fullrepo` is rebuilt from `HEAD` of the normal branch + local agent-only files. To rollback, restore `main` first, then republish:

```bash
# After main is back to a known-good state:
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --publish

# Or restore agent-only context from a previous fullrepo SHA without changing main:
git fetch origin fullrepo
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --restore
```

`--publish` uses safe `--force-with-lease` so concurrent pushes from another machine are detected and refused.

## Rollback consumer local state

A consumer with the bad version installed can:

```bash
# Pin to the previous version.
claude plugin uninstall rldyour-flow@rldyour-claudecode
claude plugin install rldyour-flow@rldyour-claudecode  # picks up the new (rolled-back) main

# Or remove the marketplace entirely and re-add.
claude plugin marketplace remove rldyour-claudecode
claude plugin marketplace add /path/to/rldyour-claudecode

# Verify.
claude plugin list | grep rldyour
```

Restart Claude Code so plugin agents and hooks reload.

## Bootstrap from scratch on a new machine

When pulling the repo for the first time, agent-only context lives on `fullrepo`, not `main`. Restore it locally:

```bash
git clone https://github.com/nddev-it-com/rldyour-claudecode.git
cd rldyour-claudecode
python3 plugins/rldyour-flow/scripts/fullrepo_sync.py --bootstrap-init
```

`--bootstrap-init` installs the `.git/info/exclude` block for agent-only files, restores `AGENTS.md`, `.claude/CLAUDE.md`, `.serena/memories/**`, etc. from `origin/fullrepo`, and migrates any tracked agent-only files out of `main`'s index.

## Recover from runtime markers stuck

If the Stop hook chain seems stuck in a loop, runtime markers may be pointing at a stale fingerprint:

```bash
rm -f .serena/.sync_marker
rm -f .serena/.flow_sync_marker
rm -f .serena/.serena_sync_state.json
rm -f .serena/.flow_post_task_state.json
# Optionally:
RLDYOUR_SKIP_STOP_GATES=1 claude  # one-shot bypass for debugging
```

Then trigger a normal sync to repopulate markers correctly.

## Recover from a corrupted memory

Memories are agent-only. To restore the last known-good version:

```bash
git fetch origin fullrepo
git show origin/fullrepo:.serena/memories/<name>.md > .serena/memories/<name>.md
bash plugins/rldyour-serena-mcp/scripts/commit_serena_knowledge.sh
```

If the corruption was created in this session and not yet published, check `.serena/diagnostics/` for the latest bundle from `collect_diagnostics.sh` - it carries snapshot copies of state JSONs and runtime markers.
