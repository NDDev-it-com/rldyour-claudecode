#!/usr/bin/env bash
# refresh_actions_pins.sh - resolve trailing-tag comments to fresh SHA pins.
#
# Scans .github/workflows/*.yml for lines of the form:
#   uses: owner/repo@<40-hex-sha>  # v1.2.3
# and re-resolves the trailing tag through the GitHub API to the canonical
# 40-char commit SHA. Writes the updated SHA back in place and preserves
# the trailing tag comment so future drift is auditable.
#
# Rationale: SHA-pinning third-party actions (OWASP A03:2025 Software Supply
# Chain Failures, GitHub Actions secure use guidance) requires periodic
# refresh when the upstream cuts a new release that the tag now points at.
# Dependabot covers minor/patch bumps with PRs, but this script lets a
# maintainer refresh an entire workflow file in one pass without manual
# `gh api` calls.
#
# Requires:
#   - gh CLI (authenticated): `brew install gh && gh auth login`
#   - jq
#   - GNU sed (`gsed` on macOS via `brew install gnu-sed`)
#
# Flags:
#   --dry-run   show diffs without writing
#   --workflow <path>   target a single workflow file (default: all)
#
# Exit codes: 0 success (including no drift), 1 missing dependency or API
# failure, 2 invalid arguments.

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

DRY_RUN=0
WORKFLOW=""

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --workflow) WORKFLOW="${2:-}"; shift 2 ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "ERROR unknown arg: $1" >&2; exit 2 ;;
  esac
done

command -v gh >/dev/null 2>&1 || { echo "ERROR gh CLI required: brew install gh" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "ERROR jq required: brew install jq" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "ERROR gh not authenticated: gh auth login" >&2; exit 1; }

# Use GNU sed if available (macOS BSD sed has different -i semantics).
if command -v gsed >/dev/null 2>&1; then
  SED="gsed"
else
  SED="sed"
  if [ "$(uname -s)" = "Darwin" ]; then
    echo "WARN BSD sed on Darwin; install GNU sed via 'brew install gnu-sed' for reliable -i behaviour" >&2
  fi
fi

if [ -n "$WORKFLOW" ]; then
  if [ ! -f "$WORKFLOW" ]; then
    echo "ERROR workflow not found: $WORKFLOW" >&2
    exit 2
  fi
  WORKFLOWS=("$WORKFLOW")
else
  WORKFLOWS=()
  while IFS= read -r -d '' f; do
    WORKFLOWS+=("$f")
  done < <(find .github/workflows -type f -name '*.yml' -print0 2>/dev/null)
fi

if [ ${#WORKFLOWS[@]} -eq 0 ]; then
  echo "WARN no workflow files matched"
  exit 0
fi

# Regex matching `uses: owner/repo@<40-hex>  # vX.Y.Z`
# - capture owner, repo, current SHA, trailing tag
PATTERN='uses:[[:space:]]+([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)@([0-9a-f]{40})[[:space:]]+#[[:space:]]+([A-Za-z0-9._-]+)'

CHANGED=0
TOTAL=0
SKIPPED=0

for wf in "${WORKFLOWS[@]}"; do
  printf '\n\033[1;36m== %s ==\033[0m\n' "$wf"
  TMP="$(mktemp)"
  cp "$wf" "$TMP"

  while IFS= read -r line; do
    if [[ "$line" =~ $PATTERN ]]; then
      owner_repo="${BASH_REMATCH[1]}"
      old_sha="${BASH_REMATCH[2]}"
      tag="${BASH_REMATCH[3]}"
      TOTAL=$((TOTAL + 1))

      # Resolve tag -> sha via GitHub API. Annotated tags require dereference;
      # gh api returns object.sha which for annotated tags is the tag object,
      # not the commit. /git/refs/tags/<tag> returns the tag ref; for
      # lightweight tags object.sha = commit; for annotated tags need extra
      # /git/tags/<sha>.object.sha hop.
      ref_obj="$(gh api "/repos/${owner_repo}/git/refs/tags/${tag}" 2>/dev/null || true)"
      if [ -z "$ref_obj" ]; then
        echo "WARN ${owner_repo}@${tag}: gh api failed (network? deleted tag?), skipping" >&2
        SKIPPED=$((SKIPPED + 1))
        continue
      fi
      obj_type="$(printf '%s' "$ref_obj" | jq -r '.object.type // empty')"
      obj_sha="$(printf '%s' "$ref_obj" | jq -r '.object.sha // empty')"
      if [ -z "$obj_sha" ]; then
        echo "WARN ${owner_repo}@${tag}: unexpected gh api response, skipping" >&2
        SKIPPED=$((SKIPPED + 1))
        continue
      fi

      if [ "$obj_type" = "tag" ]; then
        # Annotated tag: dereference to commit.
        tag_obj="$(gh api "/repos/${owner_repo}/git/tags/${obj_sha}" 2>/dev/null || true)"
        commit_sha="$(printf '%s' "$tag_obj" | jq -r '.object.sha // empty')"
        if [ -z "$commit_sha" ]; then
          echo "WARN ${owner_repo}@${tag}: annotated tag deref failed, skipping" >&2
          SKIPPED=$((SKIPPED + 1))
          continue
        fi
        new_sha="$commit_sha"
      else
        # Lightweight tag: object.sha is already the commit.
        new_sha="$obj_sha"
      fi

      if [ "$new_sha" = "$old_sha" ]; then
        printf '  \033[32mOK\033[0m %s@%s -> still %s\n' "$owner_repo" "$tag" "${new_sha:0:12}"
      else
        printf '  \033[33mDRIFT\033[0m %s@%s: %s -> %s\n' "$owner_repo" "$tag" "${old_sha:0:12}" "${new_sha:0:12}"
        CHANGED=$((CHANGED + 1))
        if [ "$DRY_RUN" -eq 0 ]; then
          # Replace exact old SHA token in the temp file (in-place); preserve
          # surrounding whitespace and trailing tag comment.
          "$SED" -i "s|@${old_sha}|@${new_sha}|g" "$TMP"
        fi
      fi
    fi
  done < "$wf"

  if [ "$DRY_RUN" -eq 0 ] && ! cmp -s "$wf" "$TMP"; then
    mv "$TMP" "$wf"
    printf '  \033[1;32mwrote\033[0m %s\n' "$wf"
  else
    rm -f "$TMP"
  fi
done

printf '\nProcessed %d pinned actions across %d workflow(s): %d drift, %d skipped\n' \
  "$TOTAL" "${#WORKFLOWS[@]}" "$CHANGED" "$SKIPPED"

if [ "$DRY_RUN" -eq 1 ] && [ "$CHANGED" -gt 0 ]; then
  echo "Dry-run: re-run without --dry-run to apply." >&2
fi
