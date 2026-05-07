---
name: tech-research
description: "Технический ресёрч библиотек и кода через Context7/DeepWiki/Grep. Use when user asks to research a library, look up official docs, find production code patterns, compare implementations, or understand open-source architecture."
---

# Tech research

Auto-invoked when the user needs authoritative technical information before deciding on or implementing something. Routes the question to the right MCP transport rather than generic web search.

## When to use

- Library or framework API lookup ("how does X library handle Y in version Z?")
- Open-source repo architecture, design notes, module layout
- Real-world code patterns and idioms across GitHub at scale
- Comparing implementation approaches between several libraries
- Verifying potentially-stale documentation against current code

Skip when: question is news / current events (use `web-research`), or it's purely about local code (use Serena tools).

## Workflow

1. **Pick the right transport** for the question:
   - Official docs / API reference → **Context7** (`mcp__context7__resolve-library-id` then `mcp__context7__get-library-docs`)
   - Open-source repo architecture, design rationale → **DeepWiki**
   - Real-world code patterns / production usage at scale → **Grep**
2. Query the chosen MCP first. Pull exact quotes, file paths, version numbers, section anchors.
3. If the claim is critical or contested, cross-validate against at least one other source (often: docs claim vs code reality).
4. Synthesize with citations: source name + version + section / file path.

## Output style

- Tag each finding with confidence: **Confirmed** / **Strongly supported** / **Inferred**
- Cite exact source — `<library>@<version>`, repo path, doc section
- Distinguish documentation claims from real-world code observations
- Flag version-specific behavior with explicit version numbers
- Reply in Russian when the user wrote in Russian

## Anti-patterns

- Single-source claims for critical decisions
- Mixing inferences with confirmed facts without explicit labels
- Ignoring contradictions between docs and code — surface them, don't hide
- Using `web-research` when an MCP server has the authoritative answer
- Generic "best practice" lists without dated, named sources
