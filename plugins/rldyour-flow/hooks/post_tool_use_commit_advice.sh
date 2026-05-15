#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
unset CDPATH

if [ "${RLDYOUR_SKIP_FLOW_COMMIT_ADVICE:-0}" = "1" ]; then
  exit 0
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

INPUT=$(cat 2>/dev/null || true)
COMMAND=$(printf "%s" "$INPUT" | python3 -c '
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

WARNINGS=$(python3 - "$HEAD_SHA" "$SUBJECT" "$FILES" <<'PY'
import re
import sys

head_sha, subject, raw_files = sys.argv[1:4]

# Sanitize commit subject before echoing back into LLM context. The hook's
# warnings text travels via `additionalContext` to the model, so an
# attacker-controlled subject (e.g., auto-merged PR from a fork, or a
# branch-rename attack on a shared repo) could theoretically inject prompts.
# Defence-in-depth — not a complete mitigation, but reduces the vector:
#   1. Truncate to 200 chars. Conventional Commits subjects are ≤72 by policy,
#      so this only fires for abnormal subjects.
#   2. Collapse control chars and newlines to spaces — subjects are single-line.
#   3. Strip known prompt-injection markers (system tags, instruction overrides,
#      turn-boundary tokens). Replace with `[REDACTED]` so the audit trail shows
#      the subject was modified rather than silently dropping content.
MAX_SUBJECT_LEN = 200
# Prompt-injection markers — defence-in-depth, not exhaustive. Covers known LLM
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
    r"|теперь ты\b",
    re.IGNORECASE | re.UNICODE,
)
sanitized_subject = re.sub(r"[\x00-\x1f\x7f]+", " ", subject)
sanitized_subject = INJECTION_MARKERS.sub("[REDACTED]", sanitized_subject)
if len(sanitized_subject) > MAX_SUBJECT_LEN:
    sanitized_subject = sanitized_subject[:MAX_SUBJECT_LEN] + "...[truncated]"
subject = sanitized_subject

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
            f"commit includes sensitive-looking path `{path}`; verify no secrets or credentials were committed"
        )
        break

runtime_patterns = [
    re.compile(r"^\.serena/\.(flow_sync_marker|flow_post_task_state\.json|sync_marker|serena_sync_state\.json|auto_sync_head|active_workflow_intent\.json|dirty_stop_ack)$"),
    re.compile(r"^browser/.*\.(png|jpg|jpeg|webp|gif)$", re.IGNORECASE),
]
for path in files:
    if any(pattern.search(path) for pattern in runtime_patterns):
        warnings.append(
            f"commit includes runtime/browser evidence path `{path}`; remove it unless the user explicitly requested it"
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
            f"commit includes agent-only path `{path}`; verify this repository intentionally tracks AI files in the current branch or move them to fullrepo"
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

python3 - "$WARNINGS" <<'PY'
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
