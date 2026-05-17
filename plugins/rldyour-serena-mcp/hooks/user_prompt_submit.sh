#!/usr/bin/env bash
# user_prompt_submit.sh - UserPromptSubmit hook.
#
# Injects a one-paragraph Serena-first reminder into the model's context when
# the prompt looks like it concerns project code, symbols, or implementation.
#
# Routing logic (P3 audit refinement, surgical not blunt):
#   strong trigger          -> inject
#   weak trigger + action verb -> inject
#   weak trigger alone      -> do NOT inject (avoids noise on prompts like
#                                            "add this to the project" or "open file X")
#   neither                 -> do NOT inject
#
# Strong triggers are unambiguous code/architecture markers; weak triggers
# (project / directory / file) only inject when paired with an action verb that
# implies actual code work. Single Python parser/emitter (no pipe chain) keeps
# the hook deterministic and easy to test.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

INPUT=$(cat 2>/dev/null || true)

RLDYOUR_PROMPT_RAW="$INPUT" python3 <<'PY'
import json
import os
import re
import sys

# --- Parse stdin payload --------------------------------------------------
raw = os.environ.get("RLDYOUR_PROMPT_RAW", "")
try:
    payload = json.loads(raw) if raw else {}
except (json.JSONDecodeError, ValueError):
    payload = {}

prompt = payload.get("prompt", "")
if not isinstance(prompt, str):
    prompt = ""

if len(prompt) < 5:
    sys.exit(0)

# --- Trigger sets ---------------------------------------------------------
# Strong triggers are unambiguous code/symbol/architecture words (EN + RU).
STRONG = re.compile(
    r"\b("
    r"code|repo|repository|class|function|method|symbol|refactor|bug|trace|"
    r"architecture|implementation|debugging|stacktrace|exception|"
    r"код|класс(?:ы|ов)?|функци[ияй]|метод[ыов]?|символ[ыов]?|"
    r"рефактор|ошибк[ауеи]?|архитектур[ауеы]?|реализаци[ияей]"
    r")\b",
    re.IGNORECASE | re.UNICODE,
)

# Weak triggers are too broad to inject on their own (project/directory/file
# appear in many non-code prompts) - they require a paired action verb.
WEAK = re.compile(
    r"\b("
    r"project|directory|dir|file|module|package|"
    r"проект[ауе]?|директори[ияей]|папк[аеу]|файл[ыов]?|модул[ьяей]|пакет[ыов]?"
    r")\b",
    re.IGNORECASE | re.UNICODE,
)

# Action verbs paired with weak triggers indicate actual code work.
# Trailing \b prevents over-match on derived nouns/adjectives (e.g. "editor"
# previously matched "edit" - quality reviewer F-6 closure). The `\w*` after
# select stems intentionally allows verb conjugations: "implemented",
# "refactoring", "rename(s)".
ACTION = re.compile(
    r"\b("
    r"inspect|analyz\w*|review|fix(?:es|ed|ing)?|edit(?:s|ed|ing)?|modify|"
    r"implement\w*|find|search\w*|trac(?:e|ed|ing)|debug\w*|"
    r"refactor\w*|navigat\w*|locat\w*|renam\w*|extract\w*|optimi[sz]\w*|test\w*|"
    r"изуч[аи]|посмотр[ие]|проверь|проанализир|исправ[ьи]|измен[ия]|"
    r"реализ[уя]|найди|поищи|просмотр[ие]|инспект|рефактор|переименуй"
    r")\b",
    re.IGNORECASE | re.UNICODE,
)

inject = False
if STRONG.search(prompt):
    inject = True
elif WEAK.search(prompt) and ACTION.search(prompt):
    inject = True

if not inject:
    sys.exit(0)

# --- Emit additionalContext ----------------------------------------------
CONTEXT = (
    "Serena-first code workflow: for repository/project/directory/file code "
    "inspection, use Serena MCP before raw text reads when available: "
    "check_onboarding_performed -> list_memories -> read_memory(relevant) -> "
    "get_symbols_overview -> find_symbol(include_body=false) -> "
    "find_symbol(include_body=true only for needed symbols) -> "
    "find_referencing_symbols -> search_for_pattern. Use raw rg/read only as "
    "fallback, broad text sweep, or tiny known-location edit."
)

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": CONTEXT,
    }
}))
PY
