#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
unset CDPATH

INPUT=$(cat 2>/dev/null || true)
PROMPT=$(printf "%s" "$INPUT" | python3 -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}

prompt = payload.get("prompt", "")
print(prompt if isinstance(prompt, str) else "")
' 2>/dev/null || true)

if [ ${#PROMPT} -lt 5 ]; then
  exit 0
fi

if ! printf "%s" "$PROMPT" | grep -qiE 'код|code|repo|repository|project|проект|директор|directory|file|файл|class|function|method|symbol|refactor|рефактор|bug|ошиб|trace|архитектур|implementation|реализац|индекс|index'; then
  exit 0
fi

CONTEXT="Serena-first code workflow: for repository/project/directory/file code inspection, use Serena MCP before raw text reads when available: check_onboarding_performed -> list_memories -> read_memory(relevant) -> get_symbols_overview -> find_symbol(include_body=false) -> find_symbol(include_body=true only for needed symbols) -> find_referencing_symbols -> search_for_pattern. Use raw rg/read only as fallback, broad text sweep, or tiny known-location edit."

python3 - "$CONTEXT" <<'PY'
import json
import sys

print(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": sys.argv[1],
            }
        }
    )
)
PY
