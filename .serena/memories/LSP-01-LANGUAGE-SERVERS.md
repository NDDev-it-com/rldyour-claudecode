<!-- Memory Metadata
Last updated: 2026-05-22
Last commit: 9330d026c96dcf7fd24ea9d6e70aebf063415511 feat(flow): align stop lifecycle and numeric releases
Scope: language-server setup and diagnostic proof
Area: LSP
-->

# Language Server Quality Gates

## Scope
language-server setup and diagnostic proof

## Current source of truth
- `path:plugins/rldyour-lsps`
- `path:README.md`

## Last verified
- date: 2026-05-22
- commit: `9330d026c96dcf7fd24ea9d6e70aebf063415511`
- checked by: Codex ry-start memory-domain normalization

## Facts
- LSP memories record language-server coverage and diagnostic proof requirements.

## Evidence
- `commit:9330d026c96dcf7fd24ea9d6e70aebf063415511`
- `path:plugins/rldyour-lsps`
- `path:README.md`

## Known pitfalls
- Treat this memory as derived context. Current code, configuration, runtime output, and GitHub state override stale memory text.

## Update policy
Update after verified changes to the referenced source-of-truth files.

## Delete / merge policy
- Delete or merge only when the referenced source-of-truth files no longer support this memory and the replacement memory preserves the durable facts.
