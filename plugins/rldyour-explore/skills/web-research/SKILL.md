---
name: web-research
description: "Интернет-исследование с авторитетными источниками через WebSearch + WebFetch. Покрывает: изучи интернет, latest/current. Используй для: текущие тренды, индустриальные новости, секьюрити-уведомления, анонсы вендоров, информация вне статичных доков, актуальные релизы. EN triggers: current trends, industry news, security advisories, vendor announcements, latest releases, news search, web search, current state of X."
allowed-tools:
  - WebSearch
  - WebFetch
---

# Web research

Auto-invoked when the user needs current, authoritative information that does not live in static docs or in code. Returns dated, cited findings - never opinionated synthesis dressed as fact.

## When to use

- Current industry trends, recent releases, breaking changes (≤6 months)
- Security advisories, CVEs, vendor announcements, deprecation notices
- Comparative product / framework evaluation backed by reputable sources
- Standards updates (RFCs, language specs, official changelogs)

Skip when: question can be answered by docs or code (use `tech-research`), or it concerns a local file / repo (use Serena tools).

## Workflow

1. Frame the search query with version / date qualifiers (e.g. "May 2026", "v1.2.x")
2. Prefer authoritative domains: vendor blogs, RFCs, security advisories, official changelogs, standards bodies
3. Fetch top 2-3 candidates via WebFetch; capture publication dates
4. Cross-reference dated info between independent sources
5. Quote directly when the claim is non-trivial; never paraphrase as established fact

## Output style

- Date-stamp every claim ("As of 2026-05-...", "vN.M.K release notes")
- Cite source URL inline next to each claim
- Distinguish vendor statements from third-party analysis
- Mark blog posts as opinion, not fact
- Reply in Russian when the user wrote in Russian

## Anti-patterns

- Generic advice without date or source
- Treating opinionated blogs as facts - cite them explicitly as opinion
- Missing official announcements (always check the project repo / changelog)
- Old information without flagging publication date if older than 6 months
- Using `web-research` when `tech-research` (MCP) has the answer
