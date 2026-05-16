<!-- Memory Metadata
Last updated: 2026-05-16
Last commit: 61b913d feat(scripts): add validate_reviewer_contracts for heredoc drift detection
Scope: plugins/rldyour-rules/skills/quality-first-engineering/SKILL.md, plugins/rldyour-rules/skills/architecture-boundaries/SKILL.md, plugins/rldyour-rules/skills/dependency-compatibility-policy/SKILL.md, plugins/rldyour-rules/skills/implementation-discipline/SKILL.md, plugins/rldyour-rules/skills/verification-quality-gates/SKILL.md, plugins/rldyour-rules/skills/project-instructions-policy/SKILL.md, plugins/rldyour-rules/skills/ry-rules-review/SKILL.md, plugins/rldyour-rules/references/{rules-policy,quality-gates,architecture-policy,dependency-policy,project-instructions-and-adrs,sources}.md, plugins/rldyour-rules/commands/ry-rules-review.md
Area: RULES
-->

# RULES-01-POLICY

## Purpose

Rules domain catalog for `rldyour-rules`. Seven rule areas + six durable references + one slash command + a `ry-rules-review` auditor define the **enforcement layer** for the quality-first philosophy ([[PHILOSOPHY-01-QUALITY-FIRST]]). This memory is the per-area pointer; per-area details live in the linked skill / reference files.

`rldyour-rules` is **skills-only** (7 skills + 6 references + 1 slash command, 0 agents, 0 hooks). Dependencies: `rldyour-mcps` only.

## Source Of Truth

- `plugins/rldyour-rules/skills/quality-first-engineering/SKILL.md`
- `plugins/rldyour-rules/skills/architecture-boundaries/SKILL.md`
- `plugins/rldyour-rules/skills/dependency-compatibility-policy/SKILL.md`
- `plugins/rldyour-rules/skills/implementation-discipline/SKILL.md`
- `plugins/rldyour-rules/skills/verification-quality-gates/SKILL.md`
- `plugins/rldyour-rules/skills/project-instructions-policy/SKILL.md`
- `plugins/rldyour-rules/skills/ry-rules-review/SKILL.md` (slash-only via `disable-model-invocation: true`)
- `plugins/rldyour-rules/references/rules-policy.md` (full text)
- `plugins/rldyour-rules/references/quality-gates.md` (full text)
- `plugins/rldyour-rules/references/architecture-policy.md` (full text)
- `plugins/rldyour-rules/references/dependency-policy.md` (full text)
- `plugins/rldyour-rules/references/project-instructions-and-adrs.md` (full text)
- `plugins/rldyour-rules/references/sources.md` (citation list)
- `plugins/rldyour-rules/commands/ry-rules-review.md` (slash command)

## Seven Rule Areas

### 1. `quality-first-engineering`

Auto-invokable. Hard bans + semantic-entropy rules + scope policy + Conventional Commits v1.0.0.

**Hard bans**: no hacks, no swallowed errors, no secrets, no fake checks, no unrelated destructive git/filesystem operations.

**Core rules**: code is source of truth (verify against code/diffs/tests/runtime, not docs); quality > speed; Sequential Thinking MCP for non-trivial decisions (≥3 thoughts); consistency with existing patterns; low semantic entropy (one concept = one home/name/contract/implementation); reuse stable code; optimize for future change without speculative over-engineering.

**Scope policy**: fix issues inside touched scope + integration path. Out-of-scope serious tech debt → stop expanding, ask user with 2-3 concrete options.

### 2. `architecture-boundaries`

Auto-invokable. May 2026 defaults: **FSD** (frontend/web/mobile/desktop UI) + **VSA + Hexagonal + Modular Monolith** (backend) + **MADR 4.0.0 ADRs** for irreversible decisions.

**FSD layers**: `app`, `pages`, `widgets`, `features`, `entities`, `shared`. Imports flow to lower layers only. Public APIs (`index.ts`) for slices. `shared` business-agnostic. Deprecated `processes` layer **forbidden**.

**VSA backend**: organize around use cases / commands / queries / routes / handlers. Validation, handler logic, domain orchestration, persistence interaction, response mapping must be traceable for one use case.

**Hexagonal**: domain core isolated from infrastructure (DB, HTTP, queues). Ports define contracts; adapters implement them.

**Modular Monolith**: module boundaries form outer container; vertical slices organize features within; ports/adapters protect the core.

**Pure Layered architecture**: acceptable only for MVPs / small projects where speed matters more than sustainability.

**ADR triggers**: new architecture style, framework/DB/broker/auth/deploy/dependency, intentional FSD/VSA deviation, breaking public API, long-lived tradeoff.

### 3. `dependency-compatibility-policy`

Auto-invokable. May 2026 supply chain standards: **SBOM** (SPDX or CycloneDX, every release), **SLSA Level 2** minimum (GitHub Actions + cosign / slsa-github-generator), **Sigstore / cosign** signing, lockfile discipline (`--frozen-lockfile` / `--immutable` / `npm ci` in CI). OWASP A03 supply-chain top-tier concern.

**Package manager defaults**: pnpm (JS/TS), uv (Python), cargo (Rust), go mod (Go), pub (Dart/Flutter).

**Selection rules**: latest-compatible (not unverified-latest); check docs/release-notes/migration-guides/compatibility-matrices; use `rldyour-explore` ([[EXPLORE-01-RESEARCH]]) for technical research; respect lockfiles; SemVer is signal not proof; major upgrades require migration plan + scope analysis + rollback strategy; new prod deps must have clear purpose + maintenance signal + license + security posture + integration plan; don't add deps to avoid writing small code.

**Rejection criteria**: abandoned (12+ months without explanation); duplicates stable project utility; requires broad architecture changes; magic behavior hard to debug; unclear license / security posture.

### 4. `implementation-discipline`

Auto-invokable. Workflow: Serena-first inspection (`get_symbols_overview` → `find_symbol(body=false)` → `find_symbol(body=true)` → `find_referencing_symbols`); trace all integration points before finalizing (routes, clients, schemas, DTOs, migrations, generated types, config, docs, tests); preserve existing public contracts unless task explicitly requires breaking change; atomic readable changes (separate mechanical refactors from behaviour changes); clear names over comments (comments only for WHY / constraints / non-obvious algorithms / external contract reasons); remove obsolete code/branches/docs/flags/tests when in scope; keep generated files synchronized.

**Reuse**: reuse stable utilities / primitives / domain types / patterns. Extract common code only after real duplication or stable concept (not speculation). No broad abstraction for single speculative future case.

### 5. `verification-quality-gates`

Auto-invokable. **No fake green** principle. Run project-native tests + type checks + linters + format checks + build checks for touched code.

**Per-language May 2026 defaults**:
- Python: **pyright** (default; 2-5× faster than mypy, 98% spec) + **ruff** + pytest.
- TS/JS: ESLint v9 (established) / Biome (greenfield, 24× faster) / Oxlint (CI speed layer); Vitest (new) or Jest (Webpack/CRA only); `tsc --noEmit` or `tsgo`.
- Rust: `cargo check`, `cargo clippy -- -D warnings`, `cargo test`.
- Go: `go vet ./...`, `go test ./...`, `golangci-lint run`.
- Dart/Flutter: `dart analyze` / `flutter analyze`, `dart test` / `flutter test`.

**Per-plugin routing**: LSP diagnostics → `rldyour-lsps` ([[LSPS-01-LANGUAGE-SERVERS]]); browser-visible → `rldyour-browser` ([[BROWSER-01-WORKFLOW]]); auth/secrets/injection → `rldyour-security` ([[SECURITY-01-OWASP]]); Figma/shadcn/FSD/design tokens → `rldyour-design` ([[DESIGN-01-WORKFLOW]]); post-task sync → `rldyour-flow/flow-post-task-sync` ([[FLOW-01-SDLC]]).

**No fake green**: report exact command + output for passes; fix root cause or report blocker for fails; state risk for un-runnable checks; never replace verification with confidence language.

### 6. `project-instructions-policy`

Auto-invokable. `AGENTS.md` (cross-tool, agents.md spec, kept concise) + `.claude/CLAUDE.md` (Claude Code-deep memory, fullrepo-managed) + `REVIEW.md` (when review rules are durable) + ADRs (MADR 4.0.0).

**Forbidden**: thin `@AGENTS.md` import for `.claude/CLAUDE.md` (both first-class, dual-source); root `CLAUDE.md` (`.claude/CLAUDE.md` is the rldyour path); commit `AGENTS.md`/`CLAUDE.md`/`REVIEW.md` to normal product branches (fullrepo-managed); secrets/tokens/chat-history in instruction docs.

**Agent-only / fullrepo lifecycle** ([[FLOW-01-SDLC]] + [[DOCS-01-INSTRUCTIONS]]): restore via `fullrepo_sync.py --bootstrap-init`; ignore via `.git/info/exclude` (fullrepo block); publish via `flow-post-task-sync`.

### 7. `ry-rules-review`

**Slash-only** (`disable-model-invocation: true`) via `/rldyour-rules:ry-rules-review`.

**Workflow**:
1. Determine target (current diff / branch vs main / PR / file scope / user scope).
2. Serena-first code inspection for affected symbols + integration paths.
3. Apply rule skills 1-6 above.
4. Use `rldyour-explore` for tech research when review depends on current technology / dependency versions / architecture best practices.
5. Report findings in Russian, ordered by severity + confidence.
6. **Report-only by default**. Modify files only if user explicitly asks to fix findings.

**Finding format**: Severity (critical/high/medium/low), Confidence (0-100), Location (file:line), Rule (which rldyour rule violated), Evidence (concrete code/config/test/docs), Impact, Fix (actionable), Disposition (must-fix / should-fix / ask-user / defer). Drop confidence <30. Validate confidence 30-49 against extra evidence before reporting.

## Invariants

- `rldyour-rules` plugin: 7 skills + 6 references + 1 slash command, 0 agents, 0 hooks. Dependencies: `rldyour-mcps`.
- All 6 auto-invokable skills emit advisory output (no Stop hook blocking from rules plugin).
- `ry-rules-review` is **report-only by default**. Modify only on explicit user fix request.
- Quality-first hard bans are non-negotiable in **every** touched scope (no per-task exceptions).
- May 2026 tooling defaults are **defaults**, not absolute. Document project-specific deviations via ADR.

## Change Rules

- Adding a new rule area: new skill + (optional) new reference. Update [[PHILOSOPHY-01-QUALITY-FIRST]] cross-references if rule changes core philosophy.
- Updating May 2026 defaults (e.g., new Python type-checker, new TS linter): update `verification-quality-gates` skill + this memory + [[PHILOSOPHY-01-QUALITY-FIRST]] Default Tooling table.
- Adding ADR trigger: update `architecture-boundaries` skill + reference.

## Verification

- `python3 scripts/validate_skill_routing.py`: proves skill description trigger phrases cover routing prompts.
- `python3 scripts/validate_agent_tools.py`: proves agent allowlist invariants ([[TECHDEBT-01-NOW]] R4 mitigation).
- Manual: invoke `/rldyour-rules:ry-rules-review <scope>` and verify findings format + Russian output + Serena-first inspection.

## Cross-References

- Distilled vision + universal applicability: [[PHILOSOPHY-01-QUALITY-FIRST]].
- Canonical patterns inventory: [[PATTERNS-01-CANONICAL]].
- Frontend FSD implementation: [[DESIGN-01-WORKFLOW]].
- Security review specifics: [[SECURITY-01-OWASP]].
- Per-language LSP routing: [[LSPS-01-LANGUAGE-SERVERS]].
- Browser validation gate: [[BROWSER-01-WORKFLOW]].
- Research escalation: [[EXPLORE-01-RESEARCH]].
- Instruction docs (AGENTS.md/CLAUDE.md/REVIEW.md/ADRs): [[DOCS-01-INSTRUCTIONS]].
- SDLC orchestration: [[FLOW-01-SDLC]].
- Closed/open tech debt: [[TECHDEBT-01-NOW]].
