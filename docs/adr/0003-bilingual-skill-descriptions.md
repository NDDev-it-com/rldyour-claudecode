# ADR-0003: Bilingual skill descriptions and listing budget

- **Status**: accepted
- **Date**: 2026-05-17
- **Decision-Makers**: rldyourmnd

## Context and Problem Statement

Skill discovery in Claude Code happens through `description` fields shown
in the skill listing. The maintainer's primary language is Russian; the
LLM trigger phrases canonically used across English-speaking ecosystems
are also needed for accurate auto-invocation. A Russian-only description
loses English routing fidelity; an English-only description forces the
maintainer to use a non-native language for daily work.

The skill-listing budget (`skillListingBudgetFraction`, default `0.01` =
1% of context window with 8000-char fallback) truncates descriptions when
the total exceeds budget. With 32 skills and Russian-leading bilingual
descriptions averaging ~400 chars per entry (vs ~250 for pure English),
the default budget truncates tail-end descriptions and Claude can no
longer auto-trigger them.

Evidence: README.md:9-15, .claude/CLAUDE.md skill-listing-budget section,
`code.claude.com/docs/en/settings` `maxSkillDescriptionChars` and
`skillListingBudgetFraction` (both v2.1.105+).

## Decision Drivers

- Russian user-facing conversation per global rules.
- English LLM routing fidelity (cross-language trigger phrases).
- 32+ skills currently; growth to 50+ projected without breaking discovery.

## Considered Options

- A: Russian-only descriptions. Loses English routing.
- B: English-only descriptions. Violates user-facing language policy.
- C: Bilingual (Russian-leading + `EN triggers: ...` appended). Costs
  ~1.5-2x tokens but preserves both reach and native UX.

## Decision Outcome

Chosen option: **C**. All 32 skill descriptions follow the pattern:

```
"<RU-leading text>. Используй для: <RU trigger phrases>. EN triggers:
<EN trigger phrases>."
```

Combined with `skillListingBudgetFraction: 0.04` (4%) and
`maxSkillDescriptionChars: 1536` user settings, this gives ~12.8K chars of
total skill-listing budget at 32 skills - room for both growth and
bilingual cost. The `0.04` value is bumped above the Anthropic+claudekit
baseline `0.03` specifically because of the bilingual cost.

### Consequences

- Good: native-language UX maintained.
- Good: English trigger phrases unchanged from convention - LLM routing
  works as expected.
- Good: `scripts/validate_skill_routing.py` + `config/skill-routing-policy.json`
  (15 prompt cases covering RU and EN inputs) regression-tests routing
  accuracy.
- Bad: per-entry budget consumed faster than English-only plugins.
  Mitigation: `disable-model-invocation: true` on 4 slash-only skills
  (`ry-deploy`, `ry-newp`, `ry-rules-review`, `ry-sec-review`) frees budget
  for auto-invoked skills.
- Bad: maintainer must keep RU and EN trigger lists synchronized when
  conventions shift.

## Confirmation

- `python3 scripts/validate_skill_routing.py` ensures all 15 routing
  cases in `config/skill-routing-policy.json` find the expected skills
  via the expected description terms.
- `python3 scripts/validate_text_hygiene.py` enforces ASCII-only
  punctuation (no em-dashes/en-dashes/BIDI controls in skill bodies).

## More Information

- Settings ref: `code.claude.com/docs/en/settings` (v2.1.105+ for both
  knobs; `skillOverrides` is v2.1.129+ and does NOT apply to plugin skills).
- Related: ADR-0008 (CI runs the routing validator).
