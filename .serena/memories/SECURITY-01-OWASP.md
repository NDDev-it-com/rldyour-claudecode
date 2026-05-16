<!-- Memory Metadata
Last updated: 2026-05-17
Last commit: 00d3f82 docs(config): add REVIEW.md template per global CLAUDE.md spec
Scope: plugins/rldyour-security/skills/owasp-top-10-implementation/SKILL.md, plugins/rldyour-security/skills/ry-sec-review/SKILL.md, plugins/rldyour-security/commands/ry-sec-review.md, plugins/rldyour-flow/agents/flow-security-review.md, plugins/rldyour-mcps/.mcp.json (semgrep entry)
Area: SECURITY
-->

# SECURITY-01-OWASP

## Purpose

Security domain workflow for `rldyour-security`. Two operating modes: (1) advisory secure-coding during implementation via `owasp-top-10-implementation` (non-blocking, surface high-signal comments + apply high-confidence in-scope fixes), and (2) explicit defensive audit via `ry-sec-review` (slash-only Mythos-style review producing evidence-based findings). Both follow **defensive-only** rule — no weaponized exploits.

`rldyour-security` is **skills-only** (2 skills + 1 slash command, 0 agents, 0 hooks). Dependencies: `rldyour-mcps`. Companion: `flow-security-review` subagent in `rldyour-flow` plugin (invoked from `/ry-start` or `/ry-review` review phase).

## Source Of Truth

- `plugins/rldyour-security/skills/owasp-top-10-implementation/SKILL.md`: implementation-time advisory.
- `plugins/rldyour-security/skills/ry-sec-review/SKILL.md`: slash-only audit (`disable-model-invocation: true`).
- `plugins/rldyour-security/commands/ry-sec-review.md`: slash command entry.
- `plugins/rldyour-flow/agents/flow-security-review.md`: parallel reviewer subagent (Mythos-style, color red, maxTurns 42 with +6 turns for variant-hunt).
- `plugins/rldyour-mcps/.mcp.json` `semgrep`: `uvx --from semgrep==1.163.0 semgrep mcp` — SAST scanner integration.

## OWASP Top 10 2025 Coverage

This marketplace tracks the **OWASP Top 10 2025** revision (released as the current standard as of May 2026). Categories used in both skills:

1. **A01:2025 Broken Access Control** — object ownership, tenant boundaries, role checks, server-side authorization (not UI-hidden), indirect object access (IDOR/BOLA), admin paths, confused deputy.
2. **A02:2025 Security Misconfiguration** — unsafe defaults, debug flags, permissive CORS, missing security headers, public storage, over-broad cloud/IAM rules, exposed admin surfaces.
3. **A03:2025 Software Supply Chain Failures** — dependency trust, lockfiles, install scripts, unpinned actions/images, vulnerable packages, untrusted generated code. **Top-tier concern in 2025** (jumped to #3). Includes: dependency confusion, upstream infrastructure compromise, code-signing cert theft, CI/CD exploitation, typosquatting.
4. **A04:2025 Cryptographic Failures** — weak algorithms, incorrect key handling, plaintext secrets, insecure randomness, missing TLS, sensitive data exposure.
5. **A05:2025 Injection** — SQL/NoSQL/LDAP/template/command injection, unsafe `eval`, shell interpolation, unsafe deserialization, missing parameterization.
6. **A06:2025 Insecure Design** — missing abuse-case handling, unsafe business logic, race conditions, replay/double-spend, missing rate limits, trust-boundary mistakes.
7. **A07:2025 Authentication Failures** — session fixation, weak password reset, token lifetime, MFA bypass, confused identity flow, insecure credential storage.
8. **A08:2025 Software or Data Integrity Failures** — unsafe update paths, unsigned/unverified artifacts, mass assignment, trusted client-controlled state, insecure CI/CD assumptions.
9. **A09:2025 Security Logging and Alerting Failures** — missing audit events, sensitive logs, weak failure visibility, no alertable signal for authz/authn/security events.
10. **A10:2025 Mishandling of Exceptional Conditions** — unsafe error paths, leaked stack traces/secrets, fail-open behaviour, inconsistent rollback/cleanup, exception-driven bypasses.

**Additional AI/LLM surfaces** (when present): prompt injection, tool injection, data exfiltration through model output, untrusted tool arguments, unsafe generated code execution, cost/resource abuse.

**Reference standard**: OWASP ASVS 5.0.0 for deeper verification; OWASP secure coding checklist for practical coding decisions.

## Mode 1: `owasp-top-10-implementation` (advisory, auto-invoked)

**When**: implementation touches auth, authz, sessions, permissions, tenant boundaries, API input/output, secrets/credentials/tokens, crypto, sensitive data, logging, error handling, security headers, CORS, CSP, rate limits, dependencies, lockfiles, install scripts, CI/CD, container images, generated code.

**Behaviour**: advisory, non-blocking. Surface concise security comments. Apply high-confidence fixes when clearly in scope. Out-of-scope real risks → report as security comment with file paths + suggested follow-up. **Do not derail implementation** with low-confidence speculation. **Do not require full security review** unless `/ry-sec-review` invoked or change is high-risk.

**Implementation checklist** for touched security-relevant surfaces:

- Inputs validated on trusted side, canonicalized when needed, constrained by allowlist / type / length / range / schema.
- Outputs encoded or escaped for exact sink (HTML, attribute, URL, JS, SQL, shell, LDAP, XML, logs, third-party API).
- Authorization enforced at server / trusted boundary (independent from UI visibility).
- Authentication/session changes use framework primitives, secure cookies, token expiry, rotation when needed. No localStorage token default for sensitive sessions.
- Secrets never in repo files / logs / browser-visible payloads / prompts / telemetry / generated artifacts.
- Database and command interactions use parameterized APIs. Avoid shell execution; if unavoidable, never concatenate untrusted input.
- File uploads/downloads validate type, size, path, permissions, storage location, content handling.
- Errors fail closed, avoid sensitive detail, preserve safe cleanup.
- Security-significant events produce useful logs **without** logging secrets.
- Dependency/config changes preserve lockfiles, least privilege, pinned versions, safe defaults.
- Tests / checks cover abuse cases when changed behaviour is security-sensitive.

**Output (Russian)**: `Security comments` (high-signal only), `Applied fixes`, `Residual risks` (out-of-scope real risks), `Suggested verification` (exact tests / lint / Semgrep / manual checks). If no meaningful security notes — say so briefly. **Do not invent risks.**

## Mode 2: `ry-sec-review` (audit, slash-only)

**When**: `/rldyour-security:ry-sec-review` slash command invoked, or user explicitly asks for security review / vulnerabilities / exploitability / OWASP/ASVS coverage / hardening / secure-implementation-quality audit of a diff / PR / feature / endpoint / API / auth flow / admin path / file handler / webhook / parser / dependency / configuration.

**Style**: Mythos-inspired without copying unsafe behaviour.

- **Hypothesis-driven**: generate "what could go wrong" hypotheses from entry points / trust boundaries / data flows / changed files.
- **Variant-aware**: look for repeated root causes, sibling bugs, near-miss patterns across codebase.
- **Evidence-first**: confirm findings through code paths / configs / tests / reachable source-to-sink flows.
- **Confidence-ranked**: separate confirmed vulnerabilities from plausible risks and hardening suggestions.
- **Defensive-only**: never produce weaponized exploit code, stealth steps, persistence, credential extraction, destructive commands.

**Workflow**:
1. **Recon**: map changed files, entry points, dependencies, configuration, privileged operations, data flows. Serena-first (`get_symbols_overview`, `find_symbol`, `find_referencing_symbols`, `search_for_pattern`).
2. **Baseline scan**: Semgrep MCP (`mcp__plugin_rldyour-mcps_semgrep__*`) + local project security scripts — but scanners are not the only evidence.
3. **Hypothesize**: review hypotheses mapped to OWASP Top 10 2025 + ASVS 5.0.0 concepts + project-specific threat boundaries.
4. **Trace**: prove or reject each high-risk hypothesis by following source-to-sink paths, authz checks, validation, output handling, config, error paths.
5. **Variant hunt**: similar patterns in sibling files, repeated helpers, copied logic, shared middleware, framework-specific conventions.
6. **Assess**: rank by severity / exploitability / reachability / business impact / confidence. Prefer fewer high-confidence findings over broad speculation.
7. **Remediate**: precise fixes + tests + verification commands. Implement only when asked.
8. **Report**: findings first, then residual risks + verification status.

**Finding format** (Markdown):
```markdown
- Severity: Critical | High | Medium | Low | Info
  Category: OWASP/ASVS/security class
  Confidence: 0-100
  Location: `path:line` or `symbol`
  Evidence: concrete code/config behaviour proving the issue
  Attack path: high-level defensive explanation without weaponized steps
  Impact: what can go wrong
  Fix: precise remediation
  Verification: exact test, command, or manual check
```

**Severity guidance**:
- **Critical**: remote unauthenticated compromise, auth bypass, credential/secret exposure with high impact, arbitrary command execution, cross-tenant data compromise, destructive data loss.
- **High**: confirmed authorization bypass, exploitable injection, sensitive data exposure, dangerous misconfiguration, supply-chain risk with reachable execution, exploitable business logic flaw.
- **Medium**: reachable weakness requiring constraints, defense bypass with limited impact, missing security control materially increasing risk, likely variant with strong evidence.
- **Low**: hardening issue, missing best-practice control, low-impact information disclosure, incomplete logging without direct exploit path.
- **Info**: architecture note, verification gap, secure default recommendation.

## Safety Rules

**Defensive-only**: never provide exploit payloads, malware behaviour, stealth/persistence instructions, credential extraction steps, destructive commands. Use harmless proof only when necessary (describe condition + test expectation + safe reproduction shape without weaponizing).

**Secret redaction**: do not report secrets verbatim. If secret-like value found, redact and identify only file path + variable name + exposure class.

**Destructive operations**: for explicit destructive requests (e.g., `rm -rf` protected paths), follow Claude Code safety + approval rules.

## Relationship to `flow-security-review` Subagent

`flow-security-review` (in `rldyour-flow` plugin, see [[FLOW-01-SDLC]] + [[CLAUDECODE-01-PLUGIN-CANON]] Subagent Matrix) is the **parallel review** counterpart invoked from `/ry-start` or `/ry-review` review phase. Same hypothesis-driven Mythos-style defensive review; difference is invocation:

- `ry-sec-review` (skill, slash-only) → user-driven standalone audit.
- `flow-security-review` (subagent, color red, maxTurns 42) → orchestrated parallel review track within `ry-start` / `ry-review` workflow. Has explicit `tools:` allowlist (R/G/G/Bash + WebFetch + WebSearch + Serena read-only subset + Semgrep MCP + Context7/DeepWiki/Grep wildcards).

Both use same OWASP coverage, same finding format, same severity guidance, same safety rules. Choose based on intent: standalone audit vs lifecycle-integrated review.

## Invariants

- `rldyour-security` plugin: 2 skills + 1 slash command, 0 agents, 0 hooks. Dependencies: `rldyour-mcps`.
- `owasp-top-10-implementation` is **auto-invokable** + **advisory non-blocking**.
- `ry-sec-review` is **slash-only** (`disable-model-invocation: true`) + **report-only by default** (modify only on explicit user fix request).
- Both modes are **defensive-only** — no weaponized exploits.
- Both use OWASP Top 10 2025 categories (current standard) + ASVS 5.0.0 for deeper verification.
- Confidence <30 findings dropped. Confidence 30-49 validated against extra evidence before reporting.
- Secrets redacted in findings (path + var name + exposure class only, not raw values).
- AI/LLM surfaces explicitly in scope (prompt injection, tool injection, data exfil through model output, unsafe generated code, untrusted tool args).

## Change Rules

- OWASP Top 10 revision update: change `OWASP Top 10 2025` references throughout both skill bodies + this memory.
- Bump Semgrep MCP version: update `plugins/rldyour-mcps/.mcp.json` + `config/mcp-runtime-versions.env` + run `bash scripts/smoke_mcp_capabilities.sh --server semgrep`.
- Add new OWASP category coverage: update both `owasp-top-10-implementation` checklist + `ry-sec-review` OWASP Review Coverage section.

## Verification

- `bash scripts/smoke_mcp_capabilities.sh --server semgrep`: proves Semgrep MCP initializes.
- `python3 scripts/validate_agent_tools.py`: proves `flow-security-review` allowlist includes WebFetch/WebSearch/Semgrep + Serena read-only subset ([[PATTERNS-01-CANONICAL]] Agent Frontmatter).
- Manual: invoke `/rldyour-security:ry-sec-review <scope>` and verify Russian findings + finding format compliance + defensive-only rule.

## Cross-References

- Parallel reviewer subagent: [[CLAUDECODE-01-PLUGIN-CANON]] Subagent Frontmatter Matrix → `flow-security-review`.
- Quality-first hard bans (no secrets, no fake green): [[PHILOSOPHY-01-QUALITY-FIRST]] + [[RULES-01-POLICY]] `quality-first-engineering` skill.
- Supply chain (OWASP A03) policy: [[RULES-01-POLICY]] `dependency-compatibility-policy` skill.
- Sanitization marker `[REDACTED]` pattern: [[PATTERNS-01-CANONICAL]] Input Validation Patterns.
- BRANCH validation pattern: [[PATTERNS-01-CANONICAL]] Input Validation Patterns → worktree_add.
- MCP transport for Semgrep: [[MCP-01-TRANSPORT]].
- Closed debt D18 (commit subject sanitization expanded to 13+ injection-marker families including EN+RU patterns, `re.UNICODE` flag): [[TECHDEBT-01-NOW]]. Note: D17 in TECHDEBT-01 is a different closure (shell strict mode harmonization in Wave 2).
