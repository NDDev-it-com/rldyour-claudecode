---
name: owasp-top-10-implementation
description: "Незаблокирующая проверка по OWASP Top 10 2025 при реализации. Используй для: безопасность, проверь авторизацию, права доступа, секреты, инъекции, XSS, SSRF, цепочка поставок, криптография, заголовки безопасности, CORS. EN triggers: security check, OWASP audit, auth/authz, secrets handling, injection check, XSS prevention, SSRF check, supply chain, crypto, security headers, CORS, secure coding."
---

# OWASP Top 10 Implementation Guidance

## Purpose

Keep implementation work security-aware without turning every task into a blocking audit. Use OWASP Top 10 2025 as the awareness baseline, ASVS 5.0.0 as the deeper verification reference, and OWASP secure coding checklist principles for practical coding decisions.

User-facing conversation stays in Russian unless requested otherwise. Repository documentation, code comments, and commit messages stay in English.

## When To Use

Use this skill without waiting for explicit invocation when implementation touches:

- Authentication, authorization, sessions, permissions, tenant boundaries, user/admin boundaries, or protected resources.
- API input/output handling, validation, serialization, deserialization, file upload/download, shell/database/template sinks, or external integrations.
- Secrets, credentials, tokens, crypto, sensitive data, logging, error handling, security headers, CORS, CSP, rate limits, or configuration.
- Dependencies, lockfiles, install scripts, CI/CD, container images, generated code, or supply-chain-sensitive changes.
- Any task where the user asks for secure coding, OWASP alignment, security comments, or hardening while implementing.

For explicit security review, audit, vulnerability check, or `/ry-sec-review`, use the `ry-sec-review` skill instead or in addition.

## Behavior

This skill is advisory and non-blocking. During implementation, surface concise security comments and apply high-confidence fixes when they are clearly in scope. If a risk is real but outside the requested scope, report it as a security comment with file paths and suggested follow-up.

Do not derail the implementation with low-confidence speculation. Do not require a full security review unless the user asks for `/ry-sec-review` or the change touches a high-risk area.

## OWASP Top 10 2025 Map

Check the implementation against:

1. `A01:2025 Broken Access Control`: object ownership, tenant boundaries, role checks, authorization at the server boundary, indirect object access, admin paths.
2. `A02:2025 Security Misconfiguration`: unsafe defaults, debug flags, permissive CORS, missing security headers, public storage, over-broad cloud/IAM rules, exposed admin surfaces.
3. `A03:2025 Software Supply Chain Failures`: dependency trust, lockfiles, install scripts, unpinned actions/images, vulnerable packages, untrusted generated code.
4. `A04:2025 Cryptographic Failures`: weak algorithms, incorrect key handling, plaintext secrets, insecure randomness, missing TLS assumptions, sensitive data exposure.
5. `A05:2025 Injection`: SQL/NoSQL/LDAP/template/command injection, unsafe eval, shell interpolation, unsafe deserialization, missing parameterization.
6. `A06:2025 Insecure Design`: missing abuse-case handling, unsafe business logic, race conditions, replay/double-spend, missing rate limits, trust-boundary mistakes.
7. `A07:2025 Authentication Failures`: session fixation, weak password reset, token lifetime, MFA bypass, confused identity flow, insecure credential storage.
8. `A08:2025 Software or Data Integrity Failures`: unsafe update paths, unsigned/unverified artifacts, mass assignment, trusted client-controlled state, insecure CI/CD assumptions.
9. `A09:2025 Security Logging & Alerting Failures`: missing audit events, sensitive logs, weak failure visibility, no alertable signal for authz/authn/security events.
10. `A10:2025 Mishandling of Exceptional Conditions`: unsafe error paths, leaked stack traces/secrets, fail-open behavior, inconsistent rollback/cleanup, exception-driven bypasses.

## Implementation Checklist

When touching a security-relevant surface, check:

- Inputs are validated on a trusted side, canonicalized when needed, and constrained by allowlist, type, length, range, and schema.
- Outputs are encoded or escaped for the exact sink: HTML, attribute, URL, JavaScript, SQL, shell, LDAP, XML, logs, or third-party API.
- Authorization is enforced at the server or trusted boundary and is independent from UI visibility.
- Authentication/session changes use framework primitives, secure cookies, token expiry, rotation where needed, and no localStorage token default for sensitive sessions.
- Secrets never enter repo files, logs, browser-visible payloads, prompts, telemetry, or generated artifacts.
- Database and command interactions use parameterized APIs. Avoid shell execution; if unavoidable, do not concatenate untrusted input.
- File uploads/downloads validate type, size, path, permissions, storage location, and content handling.
- Errors fail closed, avoid sensitive detail, and preserve safe cleanup.
- Security-significant events produce useful logs without logging secrets.
- Dependency/config changes preserve lockfiles, least privilege, pinned versions where appropriate, and safe defaults.
- Tests or checks cover abuse cases when the changed behavior is security-sensitive.

## Output

For ordinary implementation, keep security comments short and actionable:

- `Security comments`: only relevant high-signal notes.
- `Applied fixes`: security improvements already implemented.
- `Residual risks`: real risks outside current scope or requiring user decision.
- `Suggested verification`: exact tests, lint, project security scripts, CI security artifacts, manual checks, or review steps.

If there are no meaningful security notes, say that briefly and do not invent risks.

## Anti-patterns

- Inventing risks where there are none ("just to be safe")
- Blocking implementation on low-confidence speculation
- Reporting OWASP categories without code-level evidence
- Skipping authorization checks because "the UI hides it"
- Recommending generic hardening (`use HTTPS`, `validate input`) without project-specific scope
