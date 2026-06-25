<!-- Thanks for opening a PR. Please complete the sections below. -->

## What changed

<!-- One-sentence summary of the change. -->

## Why

<!-- Concrete reason. Reference Issue # or wave context. -->

## Scope

- Plugin(s) affected: <!-- e.g. rldyour-flow, rldyour-serena-mcp -->
- Component types: <!-- skills / agents / commands / hooks / scripts / docs / tests / config -->
- Breaking change: <!-- yes / no. If yes, link to ADR. -->

## Evidence

<!-- Paste relevant output. Required: -->

```bash
# Full validate harness must pass:
bash scripts/validate_marketplace.sh
# Expected: ✔ marketplace validation passed
```

```bash
# Unit tests must pass:
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/ -m "not integration"
# Expected: N passed, M deselected
```

<!-- If shell scripts changed, also include: -->

```bash
gh workflow run cross-platform.yml --ref <branch>
# Wait for green, paste run URL.
```

## Checklist

- [ ] Commit messages follow Conventional Commits v1.0.0
  (`type(scope): subject`)
- [ ] One logical change per commit (atomic)
- [ ] `scripts/validate_marketplace.sh` is GREEN locally
- [ ] Unit tests added / updated for new behavior
- [ ] ADR added if this is an architectural change
- [ ] CHANGELOG `[Unreleased]` entry added (or new `[<X.Y.Z>]` section if
      this PR is a release boundary)
- [ ] Plugin / marketplace versions bumped per
      `RELEASE-01-VALIDATION` rule (every wave touching plugin files
      bumps marketplace VERSION AND the affected plugin versions)
- [ ] No secrets, tokens, PII added to any file
- [ ] No `latest` pins introduced
- [ ] Agent-only files (AGENTS.md, .claude/, .serena/, etc.) stay on
      runtime-local state and are NOT committed to `main`

## Related

<!-- Link Issue #, ADR, prior PR, or `.serena/reviews/<run_id>/` -->
