---
name: ry-sec-review
description: "Защитный Mythos-style security review для diff/PR/чувствительного кода. Используй для: /ry-sec-review, проверь безопасность, секьюрити ревью, audit auth/authz/secrets/injection, OWASP findings, hypothesis-driven review."
---

# ry-sec-review

## Purpose

Run a high-quality defensive security review of the current implementation. This is not a general code review and not a blocking policy gate by default. It produces evidence-based findings and comments so the agent can decide what to fix immediately and what to report as follow-up.

User-facing reports are written in Russian unless the user asks otherwise. Code, paths, symbols, vulnerability categories, and references stay exact.

## When To Use

Use this skill without waiting for explicit invocation when the request asks to:

- Review security, vulnerabilities, exploitability, OWASP/ASVS coverage, hardening, or secure implementation quality.
- Audit a diff, pull request, feature, full implementation, module, route, endpoint, API, auth/authz flow, admin path, file handler, webhook, parser, dependency, or configuration.
- Check secrets, credentials, tokens, crypto, injection, access control, SSRF-like external requests, unsafe deserialization, supply chain, logging, or exceptional conditions.
- Produce findings, confidence ranking, remediation, and verification steps.
- React to `/ry-sec-review` slash command invocation.

Do not use this skill for ordinary implementation unless the user asks for security review or the change is high-risk enough to require a focused audit. For lightweight secure-coding comments during implementation, use `owasp-top-10-implementation`.

## Review Style

Use a Mythos-inspired review style without copying unsafe behavior:

- Hypothesis-driven: generate concrete "what could go wrong" hypotheses from entry points, trust boundaries, data flows, and changed files.
- Variant-aware: look for repeated root causes, sibling bugs, and near-miss patterns across the codebase.
- Evidence-first: confirm findings through code paths, configs, tests, and reachable source-to-sink flows.
- Confidence-ranked: separate confirmed vulnerabilities from plausible risks and hardening suggestions.
- Defensive-only: do not produce weaponized exploit code, stealth steps, persistence, credential extraction, or destructive commands.

## Inputs To Establish

Before reviewing, determine:

- Scope: full repo, current diff, PR branch, specific files, feature, or module.
- Assets: protected data, money movement, admin capability, tenant/user boundaries, secrets, credentials, tokens, files, jobs, webhooks, AI outputs.
- Entry points: routes, controllers, CLI commands, background jobs, webhooks, queues, public components, MCP tools, file parsers, config loaders.
- Trust boundaries: browser/server, user/admin, tenant/tenant, internal/external service, local/remote file, generated/manual code.
- Security controls: authn, authz, validation, encoding, rate limiting, logging, error handling, crypto, dependency controls.

If scope is unclear, make a reasonable assumption and state it. Do not stop unless the review cannot be bounded safely.

## Review Workflow

1. Recon: map changed files, entry points, dependencies, configuration, privileged operations, and data flows. Use Serena first when available: `get_symbols_overview`, targeted `find_symbol`, `find_referencing_symbols`, and `search_for_pattern`.
2. Baseline scan: use available automated help when useful — Semgrep MCP (`mcp__semgrep__*`) and local project security scripts — but do not rely on scanners as the only evidence.
3. Hypothesize: generate review hypotheses mapped to OWASP Top 10 2025, ASVS 5.0.0 concepts, and project-specific threat boundaries.
4. Trace: prove or reject each high-risk hypothesis by following source-to-sink paths, authorization checks, validation, output handling, config, and error paths.
5. Variant hunt: search for similar patterns in sibling files, repeated helpers, copied logic, shared middleware, and framework-specific conventions.
6. Assess: rank by severity, exploitability, reachability, business impact, and confidence. Prefer fewer high-confidence findings over broad speculation.
7. Remediate: propose precise fixes, tests, and verification commands. When asked to implement, fix confirmed issues in scope.
8. Report: findings first, then residual risks and verification status.

## OWASP Review Coverage

Review against:

- `A01 Broken Access Control`: missing server-side authorization, IDOR/BOLA, tenant boundary bypass, admin route exposure, confused deputy.
- `A02 Security Misconfiguration`: debug exposure, permissive CORS, missing headers, unsafe cloud/IaC defaults, exposed credentials/config.
- `A03 Software Supply Chain Failures`: vulnerable dependencies, untrusted scripts, unsigned artifacts, unpinned images/actions, typosquatting risk.
- `A04 Cryptographic Failures`: weak crypto, bad randomness, plaintext sensitive data, key misuse, token storage and transport issues.
- `A05 Injection`: SQL/NoSQL/LDAP/template/command injection, unsafe eval, shell interpolation, unsafe deserialization.
- `A06 Insecure Design`: race conditions, business logic abuse, missing abuse controls, replay, quota/rate limit bypass, unsafe workflow assumptions.
- `A07 Authentication Failures`: weak reset/login/session/token flow, MFA bypass, session fixation, missing re-auth for sensitive operations.
- `A08 Software or Data Integrity Failures`: mass assignment, unsafe update/webhook handling, unverified signed data, trusted client-controlled state.
- `A09 Security Logging and Alerting Failures`: missing audit trail, sensitive logs, lack of alertable authz/authn/security events.
- `A10 Mishandling of Exceptional Conditions`: fail-open errors, leaked stack traces/secrets, inconsistent rollback, exception path bypass.

Also check AI/LLM surfaces when present: prompt injection, tool injection, data exfiltration through model output, untrusted tool arguments, unsafe generated code execution, and cost/resource abuse.

## Finding Format

Findings must come first and be ordered by severity.

Use this format:

```markdown
- Severity: Critical | High | Medium | Low | Info
  Category: OWASP/ASVS/security class
  Confidence: 0-100
  Location: `path:line` or `symbol`
  Evidence: concrete code/config behavior proving the issue
  Attack path: high-level defensive explanation without weaponized steps
  Impact: what can go wrong
  Fix: precise remediation
  Verification: exact test, command, or manual check
```

If no findings are found, state that explicitly and list residual risks or untested areas.

## Severity Guidance

- Critical: remote unauthenticated compromise, auth bypass, credential/secret exposure with high impact, arbitrary command execution, cross-tenant data compromise, or destructive data loss.
- High: confirmed authorization bypass, exploitable injection, sensitive data exposure, dangerous misconfiguration, supply-chain risk with reachable execution, or exploitable business logic flaw.
- Medium: reachable weakness requiring constraints, defense bypass with limited impact, missing security control that materially increases risk, or likely variant with strong evidence.
- Low: hardening issue, missing best-practice control, low-impact information disclosure, or incomplete logging without direct exploit path.
- Info: architecture note, verification gap, or secure default recommendation.

## Safety Rules

Do not provide exploit payloads, malware behavior, stealth/persistence instructions, credential extraction steps, or destructive commands. For explicit destructive requests such as deleting protected paths with `rm -rf`, follow Claude Code safety and approval rules.

Use harmless proof only when necessary: describe the condition, test expectation, and safe reproduction shape without weaponizing it.

Do not report secrets verbatim. If a secret-like value is found, redact it and identify only the file path, variable name, and exposure class.

## Output

For a standalone review, answer in Russian (when the user wrote in Russian) with:

- `Findings`: ordered by severity using the finding format.
- `Rejected hypotheses`: important high-risk hypotheses that were checked and rejected, with brief evidence.
- `Residual risks`: untested areas, missing runtime context, or scanner gaps.
- `Verification`: commands/tools run and what they proved.
- `Recommended fixes`: immediate fixes and optional hardening.

For implementation-after-review, keep the final concise: fixed findings, checks run, and remaining risk.

## Anti-patterns

- Findings without `path:line` or symbol-level evidence
- Severity inflation without exploitability proof
- Generic OWASP descriptions copy-pasted without project context
- Weaponized exploit steps or destructive commands
- Reporting raw secret values instead of redacting
- Treating scanner output (Semgrep) as the only evidence
- Stopping at first finding instead of variant-hunting siblings
