# ADR-0012: Owner Full-Auto Standard

- **Status**: superseded by ADR-0013 (Five-Adapter Owner Autonomous Standard)
- **Date**: 2026-05-21
- **Decision-Makers**: rldyourmnd
- **Consulted**: cross-adapter control-plane audit
- **Informed**: future contributors

## Context and Problem Statement

The rldyour AI CLI toolchain spans Claude Code, Codex, and OpenCode adapters.
The owner has made an explicit product policy decision: YOLO mode, full-auto
mode, and dangerously-skip-permissions mode must be available as the standard
operating posture across the toolchain.

Claude Code does not use the same config fields as Codex
(`approval_policy`, `sandbox_mode`, `default_permissions`) or OpenCode
(`permission.edit`, `permission.bash`). The Claude adapter therefore records
the cross-tool policy in the canonical contract and must avoid reintroducing a
safe-default posture that conflicts with the owner's standard.

## Decision Drivers

- The owner is the maintainer and intended operator of this configuration
  marketplace.
- Cross-adapter policy must be machine-readable so future audits do not treat
  full-auto mode as accidental drift.
- Claude's implementation must stay native to Claude Code plugins, hooks,
  skills, agents, and marketplace manifests instead of copying Codex/OpenCode
  config syntax.
- Deterministic hooks and validation remain quality controls, not a replacement
  for the owner-selected runtime posture.

## Considered Options

- Keep safe defaults as the canonical policy and require local overrides.
- Make full-auto the standard policy only for Codex and OpenCode.
- Record owner full-auto as the canonical cross-tool standard and map each
  adapter to its native runtime surface.

## Decision Outcome

Chosen option: **Record owner full-auto as the canonical cross-tool standard**,
because it matches the owner's explicit policy and keeps each adapter native.

The Claude contract now includes `runtime_policy.id =
"owner-full-auto-standard"` with aliases `yolo`, `full-auto`, and
`dangerously-skip-permissions`. Codex maps the policy to `rldyour-yolo` through
the legacy sandbox dialect: `approval_policy = "never"` and
`sandbox_mode = "danger-full-access"` without an active `default_permissions`
permission-profile field. OpenCode maps it to primary `edit: "allow"` and
`bash: "allow"` permissions.

### Consequences

- Good: future validators and audits can see that full-auto is intentional.
- Good: the Claude adapter stays aligned with Codex and OpenCode without
  adopting non-Claude config fields.
- Bad: running the full-auto standard on shared or untrusted machines has
  higher operational risk and is outside the intended owner-controlled use.

## Confirmation

- `config/rldyour-contract.json`
- `docs/adr/0012-owner-full-auto-standard.md`
- `python3 scripts/validate_contract.py`

## More Information

- Codex ADR-0006 records the concrete Codex profile.
- OpenCode ADR-010 records the concrete OpenCode permission posture.
