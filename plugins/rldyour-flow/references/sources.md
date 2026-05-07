# Source-Backed Design Notes

Primary sources used for this workflow:

- Claude Code memory and CLAUDE.md: https://code.claude.com/docs/en/memory
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Claude Code extension model: https://code.claude.com/docs/en/features-overview
- Claude Code hooks: https://code.claude.com/docs/en/hooks
- Claude Code plugins reference: https://code.claude.com/docs/en/plugins-reference
- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Claude Code skills: https://code.claude.com/docs/en/skills
- Claude Code slash commands: https://code.claude.com/docs/en/slash-commands
- OpenAI Codex AGENTS.md (cross-CLI compatibility): https://developers.openai.com/codex/guides/agents-md
- Git ignore rules: https://git-scm.com/docs/gitignore
- Git push force-with-lease: https://git-scm.com/docs/git-push
- GitHub protected branches: https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub Flow: https://docs.github.com/en/get-started/using-github/github-flow
- GitHub pull request reviews: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews
- Conventional Commits: https://www.conventionalcommits.org/en/v1.0.0/
- Google code review, what to look for: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- Google code review, small CLs: https://google.github.io/eng-practices/review/developer/small-cls.html
- Google SRE release engineering: https://sre.google/sre-book/release-engineering/
- C4 model: https://c4model.com/
- arc42: https://arc42.org/overview
- Architecture decision records: https://adr.github.io/
- OWASP secure coding and review concepts: https://owasp.org/

Engineering conclusions:

- Skills should stay focused and use references/scripts for progressive disclosure.
- Hooks should be deterministic and non-destructive; they should ask Claude Code to continue rather than silently mutating code.
- Multiple Stop hooks run independently, so post-task sync must coordinate with Serena using state checks and loop markers (`stop_hook_active` field on stdin).
- Subagents are useful for parallel reviews, but prompts must be self-contained and bounded.
- `AGENTS.md` is Codex-native and `.claude/CLAUDE.md` is Claude Code-native in rldyour projects. Keep both optimized for their own CLI instead of reducing one to a thin import of the other.
- `.git/info/exclude` is local exclude state, so it is appropriate for per-repository agent-only files that should exist locally but not in normal branch history.
- Use `--force-with-lease` for generated `fullrepo` snapshots so unexpected remote updates are not overwritten silently.
- Reviewer subagents (`agents/*.md`) are preferred over flag-disabled skills for orchestrated-only review tracks because Claude Code's plugin `disable-model-invocation` flag has known limitations as of May 2026.
- PostToolUse `additionalContext` injection has known issues; PreToolUse with matcher-based filtering is more reliable for command intercept patterns.
