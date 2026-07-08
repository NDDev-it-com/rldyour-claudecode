---
description: "Показать экономию токенов rtk за сессию/день (rtk gain). Report rtk token savings for the session or day."
argument-hint: "[--daily|--all --format json]"
allowed-tools:
  - Bash
---

Показать статистику экономии токенов rtk / Report rtk token savings: **$ARGUMENTS**

Run `rtk gain $ARGUMENTS`:

- no args - session/cumulative savings summary
- `--daily` - today's savings
- `--all --format json` - machine-readable totals

If rtk is not installed, say so and point to `brew install rtk`
(github.com/rtk-ai/rtk). Never install it silently.

Reply in Russian when the owner writes in Russian; otherwise reply in English.
