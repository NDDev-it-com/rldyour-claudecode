# Claude Code Surface Adoption

Verified: 2026-05-28

Source of truth:
- Runtime baseline: `references/claude-baseline.json`
- Runtime package pin: `package.json`
- Official changelog: `https://code.claude.com/docs/en/changelog`

## Decisions

| Surface | Introduced | Decision | Implementation | Validator |
| --- | --- | --- | --- | --- |
| `disallowed-tools` skill/slash-command frontmatter | 2.1.152 | Adopt selectively | Use only for read-only/review/reporting routes where removing mutation tools reduces accidental capability. Keep positive `allowed-tools` routing as the default because it is easier to validate against plugin MCP namespaces. | `scripts/validate_skill_allowed_tools.py` |
| `/reload-skills` | 2.1.152 | Adopt operationally | Document as the operator command after plugin, skill, or marketplace updates. Do not call it from static validators. | `scripts/validate_claude_surface_adoption.py` |
| `SessionStart.reloadSkills` hook output | 2.1.152 | Future | Adopt only when a startup hook can cheaply prove that skill directories changed. Blind reload on every session start is unnecessary churn. | `scripts/validate_claude_surface_adoption.py` |
| `MessageDisplay` hook event | 2.1.152 | Intentionally unused | No current redaction or display-observability requirement justifies adding a high-volume hook. | `scripts/validate_claude_surface_adoption.py` |
| `/code-review --fix` and `/simplify` integration | 2.1.152 | Future | Keep rldyour reviewer tracks as the canonical review workflow until parity with file-first reviewer reports is designed and validated. | `scripts/validate_claude_surface_adoption.py` |
| `skipLfs` for `github`/`git` plugin marketplace sources | 2.1.153 | Future | This adapter does not currently use Git LFS-heavy plugin marketplace sources. Add only when marketplace source installs prove LFS download cost or failures. | `scripts/validate_claude_surface_adoption.py` |
| npm auto-update diagnostics and `/doctor` update reporting | 2.1.153 | Adopt operationally | Keep the package pin in `package.json`; use `/doctor` and `claude --version` in installed-runtime checks when local update failures are suspected. | `scripts/validate_release_state.py` |
| status line `COLUMNS`/`LINES` env | 2.1.153 | Future | No custom status-line integration currently depends on terminal dimensions. | `scripts/validate_claude_surface_adoption.py` |
| `claude agents` native command and bundled skill autocomplete | 2.1.153 | Adopt implicitly | Existing agent names remain explicit. No config migration is required. | `scripts/validate_agent_tools.py` |

## AskUserQuestion And Owner Full-Auto

The owner-standard Claude launcher remains `claude --dangerously-skip-permissions`.
That bypasses permission prompts by design. Claude Code Auto mode is a separate
native mode where a classifier model can reduce permission prompts, but it has
plan/account/model requirements and does not create a repository-controlled way
to answer semantic `AskUserQuestion` prompts on the owner's behalf.

For rldyour workflows, semantic ambiguity is handled by the main model or the
reviewer/research agents before mutation. Permission prompts are handled by the
owner-standard bypass launcher. Do not add a custom auto-answer hook that
fabricates owner decisions.

## Validation

`scripts/validate_claude_surface_adoption.py` requires this file to contain an
explicit decision for every runtime surface listed in
`references/claude-baseline.json` and every Claude Code `2.1.153` surface that
affects this adapter's plugin, skill, hook, or marketplace behavior.
