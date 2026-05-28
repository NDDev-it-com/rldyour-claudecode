#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
unset CDPATH

# Defensive python3 resolution: subprocess shells (e.g. Claude Code hook runner)
# may have a sanitized PATH that omits ~/.local/bin, and uv-managed Python
# symlinks can be transiently broken during interpreter upgrades. Resolve once
# and exit 0 if no working interpreter exists - hooks must stay non-blocking
# when Python is unavailable. Canonical pattern (tw93/Mole, rsyslog).
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)}"
if [ -z "${PYTHON_BIN}" ] || [ ! -x "${PYTHON_BIN}" ]; then
  exit 0
fi

if [ "${RLDYOUR_SKIP_FLOW_COMMIT_ADVICE:-0}" = "1" ]; then
  exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

INPUT=$(cat 2>/dev/null || true)
COMMAND=$(printf "%s" "$INPUT" | "${PYTHON_BIN}" -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}

if str(payload.get("tool_name", "")).lower() != "bash":
    raise SystemExit(0)

tool_input = payload.get("tool_input", {})
if isinstance(tool_input, dict):
    print(str(tool_input.get("command", tool_input.get("cmd", ""))))
' 2>/dev/null || true)

if ! printf "%s" "$COMMAND" | grep -qE 'git[[:space:]]+commit([[:space:]]|$)'; then
  exit 0
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

HEAD_SHA=$(git rev-parse --short=7 HEAD 2>/dev/null || true)
SUBJECT=$(git log -1 --pretty=%s 2>/dev/null || true)
FILES=$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null || true)

if [ -z "$HEAD_SHA" ] || [ -z "$SUBJECT" ]; then
  exit 0
fi

WARNINGS=$("${PYTHON_BIN}" - "$HEAD_SHA" "$SUBJECT" "$FILES" <<'PY'
import re
import sys

head_sha, subject, raw_files = sys.argv[1:4]

# Sanitize commit subject before echoing back into LLM context. The hook's
# warnings text travels via `additionalContext` to the model, so an
# attacker-controlled subject (e.g., auto-merged PR from a fork, or a
# branch-rename attack on a shared repo) could theoretically inject prompts.
# Defence-in-depth - not a complete mitigation, but reduces the vector:
#   1. Truncate to 200 chars. Conventional Commits subjects are ≤72 by policy,
#      so this only fires for abnormal subjects.
#   2. Collapse control chars and newlines to spaces - subjects are single-line.
#   3. Strip known prompt-injection markers (system tags, instruction overrides,
#      turn-boundary tokens). Replace with `[REDACTED]` so the audit trail shows
#      the subject was modified rather than silently dropping content.
MAX_SUBJECT_LEN = 200
# Prompt-injection markers - defence-in-depth, not exhaustive. Covers known LLM
# system-tag patterns (Anthropic/OpenAI/Llama/Gemini families) and English/Russian
# instruction-override phrases. Add patterns conservatively when new attack
# vectors emerge in commit messages.
INJECTION_MARKERS = re.compile(
    r"\[(?:SYSTEM|ASSISTANT|USER|INST|СИСТЕМА|АССИСТЕНТ|ПОЛЬЗОВАТЕЛЬ)\]"
    r"|</?(?:INST|SYS|role|turn|system(?:-reminder)?)>"
    r"|<<SYS>>"
    r"|<\|?(?:im_start|im_end|begin_of_text|end_of_text|bos|eos)\|?>"
    r"|<\|?/?(?:user|assistant|system)\|?>"
    r"|---system---"
    r"|(?:BEGIN|END) PROMPT"
    r"|ignore (?:all |any )?(?:previous|prior|above|preceding) (?:instructions|prompts|messages)"
    r"|you are now\b"
    r"|from now on(?: you will)?\b"
    r"|игнорируй (?:все )?(?:предыдущие |ранее )?(?:инструкции|команды|указания|сообщения)"
    r"|забудь (?:все )?(?:предыдущие |ранее )?(?:инструкции|команды|сообщения)"
    r"|теперь ты\b"
    # 2026 tool-call / function-call format tags (Anthropic, OpenAI, generic
    # MCP-style). Defence-in-depth against tool-injection where a hostile
    # commit subject mimics a function-call wrapper to coax the parent
    # session into invoking a tool with attacker-chosen arguments.
    r"|</?(?:tool|function)[_-]?(?:call|use|result|invoke|invocations|calls)s?\b[^>]*>"
    r"|</?antml:(?:[a-z_-]+)\b[^>]*>",
    re.IGNORECASE | re.UNICODE,
)

# Unicode BiDi direction-override / isolate control characters - the Trojan
# Source attack family. Render invisible but reorder text so the displayed
# string differs from the byte order. Replace with [REDACTED-BIDI] so the
# audit trail shows the subject contained suspicious invisible characters.
BIDI_CONTROLS = re.compile(
    "["
    "‪‫‬‭‮"  # LRE/RLE/PDF/LRO/RLO
    "⁦⁧⁨⁩"  # LRI/RLI/FSI/PDI
    "]"
)


def sanitize_for_advisory(text: str, max_len: int = MAX_SUBJECT_LEN) -> str:
    """Sanitize user-controlled text before embedding it in advisory output.

    Order:
      1. Collapse C0/C1 control chars + DEL to spaces (subjects/paths are
         single-line; control chars distort terminal output).
      2. Replace BiDi direction-override / isolate characters with a marker
         (Trojan Source attack family, security F-3 sibling of D18).
      3. Strip known prompt-injection / tool-call markers via INJECTION_MARKERS
         and replace with [REDACTED].
      4. Truncate to max_len to bound the advisory payload size.
    """
    cleaned = re.sub(r"[\x00-\x1f\x7f]+", " ", text)
    cleaned = BIDI_CONTROLS.sub("[REDACTED-BIDI]", cleaned)
    cleaned = INJECTION_MARKERS.sub("[REDACTED]", cleaned)
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len] + "...[truncated]"
    return cleaned


subject = sanitize_for_advisory(subject)

files = [line for line in raw_files.splitlines() if line]
warnings: list[str] = []

conventional = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([A-Za-z0-9._-]+\))?(!)?: .+"
)

if not conventional.match(subject):
    warnings.append(
        "commit subject is not a Conventional Commit: "
        f"`{subject}`"
    )

if len(subject) > 72:
    warnings.append(
        f"commit subject is {len(subject)} characters; keep the first line at or below 72 characters when possible"
    )

if len(files) > 20:
    warnings.append(
        f"commit touches {len(files)} files; verify it is still one logical atomic change"
    )

sensitive_patterns = [
    re.compile(r"(^|/)\.env($|[.])", re.IGNORECASE),
    re.compile(r"(^|/)(id_rsa|id_ed25519)($|[.])", re.IGNORECASE),
    re.compile(r"\.(pem|key|p12|pfx)$", re.IGNORECASE),
    re.compile(r"(secret|credential|token|cookie)", re.IGNORECASE),
]
for path in files:
    if any(pattern.search(path) for pattern in sensitive_patterns):
        warnings.append(
            f"commit includes sensitive-looking path `{sanitize_for_advisory(path)}`; verify no secrets or credentials were committed"
        )
        break

runtime_patterns = [
    re.compile(r"^\.serena/\.(flow_sync_marker|flow_post_task_state\.json|stop_lifecycle_timeout_marker|sync_marker|serena_sync_state\.json|auto_sync_head|active_workflow_intent\.json|dirty_stop_ack)$"),
    re.compile(r"^browser/.*\.(png|jpg|jpeg|webp|gif)$", re.IGNORECASE),
]
for path in files:
    if any(pattern.search(path) for pattern in runtime_patterns):
        warnings.append(
            f"commit includes runtime/browser evidence path `{sanitize_for_advisory(path)}`; remove it unless the user explicitly requested it"
        )
        break

agent_only_patterns = [
    re.compile(r"^(AGENTS|CLAUDE|REVIEW|GEMINI|QWEN)\.md$"),
    re.compile(r"^\.(claude|gemini|roo|windsurf|openhands)/"),
    re.compile(r"^\.cursor/rules/"),
    re.compile(r"^\.agents/(skills|commands|hooks)/"),
    re.compile(r"^\.github/(copilot-instructions\.md|instructions/|prompts/)"),
    re.compile(r"^\.serena/(project\.yml|memories/|plans/|research/|newproj/|deploy/)"),
]
for path in files:
    if any(pattern.search(path) for pattern in agent_only_patterns):
        warnings.append(
            f"commit includes agent-only path `{sanitize_for_advisory(path)}`; verify this repository intentionally tracks AI files in the current branch or move them to fullrepo"
        )
        break

if not warnings:
    raise SystemExit(0)

print(
    "[RLDYOUR-FLOW COMMIT ADVICE] Non-blocking review for commit "
    f"{head_sha}:\n"
    + "\n".join(f"- {warning}" for warning in warnings)
    + "\nReview this before pushing or final delivery. This hook is advisory and does not block execution."
)
PY
)

if [ -z "$WARNINGS" ]; then
  exit 0
fi

"${PYTHON_BIN}" - "$WARNINGS" <<'PY'
import json
import sys

print(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": sys.argv[1],
            }
        }
    )
)
PY
