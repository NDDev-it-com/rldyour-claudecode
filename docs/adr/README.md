# Architecture Decision Records

Decisions are recorded in MADR 4.0.0 format. The format and policy live in
`plugins/rldyour-rules/references/project-instructions-and-adrs.md`.

| ID | Status | Title |
|---|---|---|
| 0001 | Accepted | [Fullrepo branch policy for agent-only files](./0001-fullrepo-branch-policy.md) |
| 0002 | Accepted | [Two-file AGENTS.md and .claude/CLAUDE.md split](./0002-dual-doc-agents-claude-split.md) |
| 0003 | Accepted | [Bilingual skill descriptions and listing budget](./0003-bilingual-skill-descriptions.md) |
| 0004 | Accepted | [File-first reviewer transport with RLDYOUR_REPORT_EOF heredoc](./0004-file-first-reviewer-transport.md) |
| 0005 | Accepted | [Local stdio GitHub MCP server](./0005-local-stdio-github-mcp.md) |
| 0006 | Accepted | [MCP and hook ownership boundaries](./0006-mcp-hook-ownership-boundaries.md) |
| 0007 | Accepted | [MCP runtime pinning strategy](./0007-mcp-runtime-pinning-strategy.md) |
| 0008 | Accepted | [CI security baseline without paid add-ons](./0008-ci-baseline-without-paid-addons.md) |
| 0009 | Accepted | [Release version and tag convention](./0009-release-version-and-tag-convention.md) |
| 0010 | Superseded | [macOS runner egress trust gap and current cross-platform smoke](./0010-macos-egress-trust-gap.md) |
| 0011 | Accepted | [Agent instruction knowledge equivalence](./0011-agent-instruction-knowledge-equivalence.md) |
| 0012 | Superseded | [Owner full-auto standard](./0012-owner-full-auto-standard.md) |
| 0013 | Accepted | [Five-adapter owner autonomous standard](./0013-five-adapter-owner-autonomous-standard.md) |

## When to write an ADR

Write one whenever a decision is:

- **Irreversible** without significant rework (changing ownership boundaries,
  introducing a new plugin, removing a hook owner).
- **Cross-cutting** across multiple plugins or workflows.
- **Driven by external constraints** (Anthropic precedent, OWASP requirements,
  GitHub plan limits) that future contributors might want to revisit.
- **Counter-intuitive** without context (why we do NOT use `pluginRoot`, why
  we keep BOTH AGENTS.md and .claude/CLAUDE.md, etc.).

## Format

Use the MADR 4.0.0 template in [0000-template.md](./0000-template.md).
Required sections: Status, Context and Problem Statement, Decision Drivers,
Considered Options, Decision Outcome, Consequences. Add Confirmation
(verification commands) when the decision can be machine-verified.

Numbering is monotonic; do not reuse IDs even when superseding.
