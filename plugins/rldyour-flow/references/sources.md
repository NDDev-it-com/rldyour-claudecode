# Source-Backed Design Notes

Primary sources used for this workflow:

- OpenAI Codex AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex Skills: https://developers.openai.com/codex/skills
- OpenAI Codex Hooks: https://developers.openai.com/codex/hooks
- OpenAI Codex best practices: https://developers.openai.com/codex/learn/best-practices
- OpenAI Codex Subagents: https://developers.openai.com/codex/subagents
- Claude Code memory and CLAUDE.md: https://code.claude.com/docs/en/memory
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Claude Code extension model: https://code.claude.com/docs/en/features-overview
- Claude Code hooks: https://code.claude.com/docs/en/hooks
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
- Hooks should be deterministic and non-destructive; they should ask Codex to continue rather than silently mutating code.
- Multiple Stop hooks run independently, so post-task sync must coordinate with Serena using state checks and loop markers.
- Subagents are useful for parallel reviews, but prompts must be self-contained and bounded.
- `AGENTS.md` is Codex-native and `.claude/CLAUDE.md` is Claude Code-native in rldyour projects. Keep both optimized for their own CLI instead of reducing one to a thin import of the other.
- Agent context (`.serena/`, `AGENTS.md`, `.claude/`) is tracked normally on `main` as ordinary source; only runtime-local cache/state/markers stay gitignored.
- Use `--force-with-lease` instead of a blind `--force` for any rare force update so unexpected remote changes are not overwritten silently. Never force-push `main`.
