<!-- Memory Metadata
Last updated: 2026-05-28
Last commit: cf5b25eb348ff012a2bcbbd2e4e61308207d674e test: avoid brittle Claude sync claim count
Scope: deploy and rollout verification contracts
Area: DEPLOY
-->

# Deploy Runtime

## Scope
deploy and rollout verification contracts

## Current source of truth
- `path:README.md`
- `path:plugins/rldyour-flow/skills/ry-deploy`


## Source Of Truth
- `path:README.md`
- `path:plugins/rldyour-flow/skills/ry-deploy`

## Last verified
- date: 2026-05-28
- commit: `cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- checked by: Codex ry-start Claude CI stabilization

## Facts
- Deploy memories record preflight, rollout, postflight, rollback, and sync requirements.

## Evidence
- `commit:cf5b25eb348ff012a2bcbbd2e4e61308207d674e`
- `path:README.md`
- `path:plugins/rldyour-flow/skills/ry-deploy`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.

## Cross-References
- `RELEASE-01-VALIDATION.md`
- `TESTS-01-VALIDATION-GATES.md`
- `SECURITY-01-OWASP.md`
