# ry-start Workflow Contract

Last verified: 2026-05-30

Source of truth:
- Root lifecycle standard: `../../docs/standards/ry-start-lifecycle-standard.md`
- Root lifecycle contract: `../../config/ry-start-lifecycle-contract.json`
- Claude command shim: `plugins/rldyour-flow/commands/ry-start.md`
- Fallback skill: `plugins/rldyour-flow/skills/ry-start/SKILL.md`

Claude Code `2.1.154` introduced dynamic workflows and `/workflows`; this
adapter pins `2.1.167` to track the current npm `latest` while retaining the
Opus 4.8 thinking-block API hotfix introduced in `2.1.156`. The
stable owner entrypoint remains `/rldyour-flow:ry-start`.

Native workflow policy:
- Current state: hybrid pending native saved workflow. No `.claude/workflows/`
  artifact is committed until Claude Code generates and saves it through the
  installed `/workflows` runtime.
- Prefer the project workflow command `ry-start-workflow` when a saved
  `.claude/workflows/` projection exists and installed-runtime smoke proves it
  is discoverable.
- Keep `/rldyour-flow:ry-start` as the plugin command shim to avoid untested
  slash-command collisions between plugin commands and saved workflow commands.
- Do not hand-author a saved workflow script from an undocumented file format.
  Official docs describe saving through `/workflows` with the `s` action.
- The fallback Markdown skill remains authoritative for phase semantics,
  reviewer fan-out, memory sync, version decisions, and release/deploy gates.

Validation:

```bash
python3 ../../scripts/validate_ry_start_lifecycle.py
python3 scripts/validate_claude_surface_adoption.py
claude --version
```
