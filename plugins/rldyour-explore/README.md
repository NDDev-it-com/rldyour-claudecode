# rldyour-explore

Deep multi-source research workflows.

## What's inside

- `2` skills: `tech-research` (library/framework research via Context7 + DeepWiki + Grep MCP), `web-research` (internet via WebSearch + WebFetch).
- `1` subagent: `ry-explore` (`model: opus[1m]`, `effort: max`, `maxTurns: 90`, `color: cyan`, explicit `tools:` allowlist with only read-only Serena tools + Read/Grep/Glob/Bash/WebFetch/WebSearch + Context7/DeepWiki/Grep MCPs - no write tools available) - runs in forked context with deep MCP-first research workflow (Context7 → DeepWiki → Grep → Web validation → cross-validation → synthesis).
- `1` slash command: `/rldyour-explore:ry-explore` with `context: fork` and `agent: ry-explore` so each invocation gets a fresh isolated context window.

## Routing

- "изучи библиотеку / исследуй фреймворк / найди официальную доку" → `tech-research` (MCP-first lookup).
- "текущие тренды / индустриальные новости / security advisories / актуальные релизы" → `web-research` (authoritative web sources only).
- "исследуй детально / глубокое исследование / разберись глубоко" → `/ry-explore <topic>` (90 turns, cross-validates ≥2 sources per critical claim, dated/versioned facts, confidence labels).

## Min Claude Code version

`v2.1.111+` for this repository's `CLAUDE_CODE_MIN_VERSION` compatibility floor. Availability of `[1m]` variants remains account/plan-dependent: `opus[1m]`/`sonnet[1m]` are shown only when your account is provisioned for extended context.

## Dependencies

`rldyour-mcps` (Context7, DeepWiki, Grep MCP servers live there).
