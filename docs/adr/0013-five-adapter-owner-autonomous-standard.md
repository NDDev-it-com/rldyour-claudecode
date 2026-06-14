# ADR-0013: Five-Adapter Owner Autonomous Standard

- **Status**: accepted
- **Date**: 2026-06-14
- **Supersedes**: ADR-0012 (Owner Full-Auto Standard)
- **Decision-Makers**: rldyourmnd
- **Consulted**: cross-adapter control-plane audit, upstream CLI source/docs research
- **Informed**: future contributors

## Context and Problem Statement

ADR-0012 recorded the owner full-auto standard for the original three adapters
(Claude Code, Codex, OpenCode). The rldyour toolchain now spans five adapters -
Claude Code, Codex, OpenCode, Gemini CLI, and MiMoCode. The owner's product
policy is unchanged and explicit: every adapter must operate in a fully
autonomous agent posture - no approval prompts, no permission asking, and no
sandbox - as the standard operating mode.

Each adapter expresses autonomy through its own native runtime surface, and two
of the five cannot express full autonomy purely in committed config:

- **Gemini CLI** rejects a committed `yolo` approval mode. Its
  `general.defaultApprovalMode` enum is `default | auto_edit | plan`; a committed
  `yolo` value is silently downgraded to `default` by the config loader. Full
  YOLO is therefore launcher-only (`--approval-mode=yolo`).
- **MiMoCode** is an OpenCode fork that evaluates an OpenCode-style permission
  ruleset with last-rule-wins semantics; full autonomy is expressed by allowing
  every permission key.

## Decision Drivers

- The owner is the maintainer and intended operator of this configuration
  toolchain.
- Cross-adapter policy must be machine-readable so audits do not treat
  full-auto as accidental drift.
- Each adapter must stay native - do not copy one adapter's config dialect into
  another (for example, Codex `approval_policy`/`sandbox_mode` keys are
  meaningless in Gemini `.gemini/settings.json`).
- Where a CLI cannot commit full autonomy, the gap is closed by an owner
  launcher, not by faking an unsupported committed value.

## Decision Outcome

Chosen option: **Record a five-adapter owner autonomous standard and map each
adapter to its native maximal-autonomy surface, closing any committed-config gap
with an owner launcher.**

| Adapter | Committed autonomy | Launcher | Full-auto gap closed by |
|---|---|---|---|
| Claude Code | n/a (no committed approval file) | `claude --dangerously-skip-permissions` (`cl`) | launcher |
| Codex | `approval_policy = "never"`, `sandbox_mode = "danger-full-access"` (legacy sandbox dialect, no active `default_permissions`) | `codex --profile rldyour-yolo --dangerously-bypass-approvals-and-sandbox` (`cx`) | committed + launcher |
| OpenCode | top-level + `build`/`plan` `permission.*: "allow"` | runtime `OPENCODE_CONFIG_CONTENT` allow-all (`oc`) | committed + launcher |
| Gemini CLI | `general.defaultApprovalMode = "auto_edit"`, `security.disableYoloMode = false`, `security.toolSandboxing = false` | `GEMINI_SANDBOX=false gemini --approval-mode=yolo` (`gm`) | launcher (YOLO is CLI-only) |
| MiMoCode | `.mimocode/mimocode.jsonc` permission ruleset `allow` for every key; `build`/`compose` agents `allow` | runtime `MIMOCODE_CONFIG_CONTENT` allow-all (`mm`) | committed + launcher |

The Claude contract keeps `runtime_policy.id = "owner-full-auto-standard"` with
aliases `yolo`, `full-auto`, and `dangerously-skip-permissions`. The root control
plane enforces the cross-adapter posture through
`scripts/validate_owner_full_auto_policy.py`, which now validates all five
adapters and their `cx`/`cl`/`oc`/`gm`/`mm` launchers.

### Defensive carve-outs (not approval prompts)

These remain and are not violations of the autonomous standard, because they are
mode definitions or secret-exfiltration guards, not interactive approval gates:

- MiMoCode keeps the `*.env` read guard at `deny` (secrets protection).
- MiMoCode `plan` keeps `edit: deny` because read-only analysis is the defining
  trait of plan mode.
- Bounded defensive hooks (for example Gemini `before_tool_policy.sh`) may block
  destructive shell/git/file and secret-bearing operations.

### Consequences

- Good: audits and validators see that five-adapter full-auto is intentional.
- Good: each adapter stays native; no cross-dialect leakage.
- Good: the committed-config vs launcher split is explicit and machine-checked.
- Bad: running the autonomous standard on shared or untrusted machines carries
  higher operational risk and is outside the intended owner-controlled use.

## Confirmation

- `config/rldyour-contract.json`
- `docs/adr/0013-five-adapter-owner-autonomous-standard.md`
- root `scripts/validate_owner_full_auto_policy.py`
- root `docs/standards/native-format-boundaries.md`

## More Information

- ADR-0012 is superseded by this ADR and retained as historical context.
- Codex ADR-0006 records the concrete Codex profile; OpenCode ADR-010 records the
  concrete OpenCode permission posture.
