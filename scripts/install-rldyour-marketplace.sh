#!/usr/bin/env bash
# install-rldyour-marketplace.sh - universal installer for the rldyour-claudecode Claude Code marketplace.
#
# Works on any Claude Code install:
#   - Fresh CC (no rldyour-* present): installs rldyour-claudecode + 9 plugins.
#   - CC with the legacy `rldyour-claudecode` marketplace (NDDev-Platform): cleanly removes
#     that marketplace, its plugins, cache, and stale settings.json keys; then installs the new
#     marketplace and plugins.
#   - CC with any other rldyour-* setup: left untouched. Only the explicit legacy names in
#     LEGACY_MARKETPLACES are cleaned; everything else is the user's responsibility.
#
# Marketplace source: nddev-it-com/rldyour-claudecode. No local clone required.
#
# Usage:
#   bash scripts/install-rldyour-marketplace.sh --dry-run                 # preview
#   bash scripts/install-rldyour-marketplace.sh --i-exited-claude         # live run
#   bash scripts/install-rldyour-marketplace.sh --i-exited-claude --continue-from 5
#
# Or remote (no clone needed):
#   curl -fsSL https://raw.githubusercontent.com/nddev-it-com/rldyour-claudecode/main/scripts/install-rldyour-marketplace.sh \
#     | bash -s -- --dry-run
#
# Flags:
#   --dry-run            preview every plugin/jq/rm call without executing
#   --i-exited-claude    mandatory for live execution (refuses inside any Claude Code session)
#   --continue-from <N>  resume from stage N after a partial failure
#
# Stages:
#   0  self-replacement guard
#   1  pre-flight backup of ~/.claude/{settings.json,plugins/installed_plugins.json,plugins/known_marketplaces.json}
#   2  detect + remove any LEGACY marketplace: disable+uninstall its plugins, then marketplace remove
#   3  jq-scrub settings.json: extraKnownMarketplaces + enabledPlugins entries pointing at legacy marketplaces
#   4  filesystem cleanup: ~/.claude/plugins/cache/<legacy>/ subtrees and known leftover symlinks
#   5  add nddev-it-com/rldyour-claudecode as a new marketplace
#   6  install 9 plugins from @rldyour-claudecode in dependency order
#   7  verify final state and write migration-report.md into the backup directory

set -euo pipefail
IFS=$'\n\t'
unset CDPATH

readonly NEW_MARKETPLACE="rldyour-claudecode"
readonly NEW_MARKETPLACE_SOURCE="nddev-it-com/rldyour-claudecode"

# Known legacy marketplace names that this installer cleans up. Add others here only when their
# removal is safe and intended. Anything else is left untouched.
readonly LEGACY_MARKETPLACES=(
  "rldyour-claudecode"
)

# Known leftover symlinks under ~/.claude/plugins/cache/ that point at legacy caches.
readonly LEGACY_CACHE_SYMLINKS=(
  "rldyourcc"
)

# Plugins to install from the new marketplace, in dependency order.
readonly NEW_PLUGINS=(
  rldyour-mcps
  rldyour-serena-mcp
  rldyour-browser
  rldyour-explore
  rldyour-lsps
  rldyour-rules
  rldyour-security
  rldyour-design
  rldyour-flow
)

readonly CLAUDE_HOME="$HOME/.claude"
readonly SETTINGS_PATH="$CLAUDE_HOME/settings.json"
readonly INSTALLED_PLUGINS_PATH="$CLAUDE_HOME/plugins/installed_plugins.json"
readonly KNOWN_MARKETPLACES_PATH="$CLAUDE_HOME/plugins/known_marketplaces.json"
readonly PLUGINS_CACHE_DIR="$CLAUDE_HOME/plugins/cache"

# Runtime flags.
DRY_RUN=0
I_EXITED_CLAUDE=0
CONTINUE_FROM=0

# Populated in stage 1.
BACKUP_DIR=""
REPORT_PATH=""

# ----- output helpers -------------------------------------------------------

if [[ -t 1 ]]; then
  readonly C_RED=$'\033[31m'
  readonly C_GREEN=$'\033[32m'
  readonly C_YELLOW=$'\033[33m'
  readonly C_BLUE=$'\033[34m'
  readonly C_BOLD=$'\033[1m'
  readonly C_DIM=$'\033[2m'
  readonly C_RESET=$'\033[0m'
else
  readonly C_RED=''
  readonly C_GREEN=''
  readonly C_YELLOW=''
  readonly C_BLUE=''
  readonly C_BOLD=''
  readonly C_DIM=''
  readonly C_RESET=''
fi

info()  { printf '%s[INFO]%s %s\n' "$C_BLUE"    "$C_RESET" "$*" >&2; }
ok()    { printf '%s[OK]%s   %s\n' "$C_GREEN"   "$C_RESET" "$*" >&2; }
warn()  { printf '%s[WARN]%s %s\n' "$C_YELLOW"  "$C_RESET" "$*" >&2; }
err()   { printf '%s[FAIL]%s %s\n' "$C_RED"     "$C_RESET" "$*" >&2; }
step()  { printf '\n%s%s== %s ==%s\n' "$C_BOLD" "$C_BLUE"  "$*" "$C_RESET" >&2; }

die() {
  err "$*"
  if [[ -n "$BACKUP_DIR" && -d "$BACKUP_DIR" ]]; then
    err "Rollback hint: restore configs from $BACKUP_DIR"
  fi
  exit 2
}

usage() {
  sed -n '2,36p' "$0"
}

require_command() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1 || die "Missing required command: $cmd"
}

# Execute a command (array form) or print it under dry-run.
run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '%s[DRY]%s %s\n' "$C_DIM" "$C_RESET" "$(printf '%q ' "$@")" >&2
    return 0
  fi
  "$@"
}

# Like run() but tolerates non-zero exit and emits a warning instead of dying.
run_soft() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '%s[DRY-SOFT]%s %s\n' "$C_DIM" "$C_RESET" "$(printf '%q ' "$@")" >&2
    return 0
  fi
  if ! "$@"; then
    warn "command tolerated non-zero exit: $*"
    return 0
  fi
}

stage_should_run() {
  local n="$1"
  [[ "$n" -ge "$CONTINUE_FROM" ]]
}

# List plugins installed under a given marketplace by reading installed_plugins.json.
installed_plugins_for_marketplace() {
  local marketplace="$1"
  if [[ ! -f "$INSTALLED_PLUGINS_PATH" ]]; then
    return 0
  fi
  jq -r --arg m "$marketplace" '
    (.plugins // {}) | to_entries[] | .key
    | select(endswith("@\($m)"))
    | sub("@\($m)$"; "")
  ' "$INSTALLED_PLUGINS_PATH"
}

# Probe whether a marketplace name is currently registered with the CC CLI.
marketplace_registered() {
  local marketplace="$1"
  claude plugin marketplace list 2>/dev/null \
    | grep -qE "^\s*[^[:alnum:]]?\s*$(printf '%s' "$marketplace" | sed 's/[][\.*^$/]/\\&/g')\b"
}

# ----- arg parsing ----------------------------------------------------------

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1; shift ;;
    --i-exited-claude)
      I_EXITED_CLAUDE=1; shift ;;
    --continue-from)
      [[ -n "${2:-}" ]] || die "--continue-from requires a stage number"
      [[ "$2" =~ ^[0-9]+$ ]] || die "--continue-from expects an integer, got: $2"
      CONTINUE_FROM="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      err "Unknown flag: $1"
      usage
      exit 2 ;;
  esac
done

# ----- stage 0: self-replacement guard --------------------------------------

stage_0_guard() {
  step "Stage 0: self-replacement guard"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "dry-run: skipping live-session probes (always allowed)"
    return 0
  fi

  if [[ "$I_EXITED_CLAUDE" -ne 1 ]]; then
    die "Refusing live run without --i-exited-claude. Exit Claude Code, then rerun."
  fi

  local pids
  pids="$(pgrep -af '(^|/)claude(-code)?( |$)' || true)"
  if [[ -n "$pids" ]]; then
    err "Live claude process(es) detected:"
    printf '%s\n' "$pids" >&2
    die "Exit all Claude Code sessions before running the live installer."
  fi

  if [[ -n "${CLAUDE_CODE_SESSION_ID:-}" ]]; then
    die "CLAUDE_CODE_SESSION_ID is set - you are inside a CC session."
  fi

  local recent_sessions
  recent_sessions="$(find "$CLAUDE_HOME/sessions" -maxdepth 2 -name '*.jsonl' -mmin -1 2>/dev/null || true)"
  if [[ -n "$recent_sessions" ]]; then
    err "Session file modified in the last minute:"
    printf '%s\n' "$recent_sessions" >&2
    die "Wait at least 60 seconds after exiting Claude Code, then retry."
  fi

  ok "no live CC session detected"
}

# ----- stage 1: backup ------------------------------------------------------

stage_1_backup() {
  step "Stage 1: pre-flight backup"

  local ts
  ts="$(date -u +%Y%m%d-%H%M%S)"
  BACKUP_DIR="$CLAUDE_HOME/backups/rldyour-install-$ts"
  REPORT_PATH="$BACKUP_DIR/migration-report.md"

  run mkdir -p "$BACKUP_DIR"

  local f
  for f in "$SETTINGS_PATH" "$INSTALLED_PLUGINS_PATH" "$KNOWN_MARKETPLACES_PATH"; do
    if [[ -f "$f" ]]; then
      run cp -p "$f" "$BACKUP_DIR/$(basename "$f")"
    else
      info "not present, skipping: $f"
    fi
  done

  ok "backup at $BACKUP_DIR"
}

# ----- stage 2: detect and remove legacy marketplaces -----------------------

stage_2_remove_legacy() {
  step "Stage 2: detect + remove legacy marketplaces"

  local legacy
  for legacy in "${LEGACY_MARKETPLACES[@]}"; do
    if ! marketplace_registered "$legacy"; then
      info "legacy marketplace not present: $legacy"
      continue
    fi

    info "found legacy marketplace: $legacy"

    local plugins
    plugins="$(installed_plugins_for_marketplace "$legacy" || true)"
    if [[ -z "$plugins" ]]; then
      info "  no plugins installed under @$legacy"
    else
      local plugin
      while IFS= read -r plugin; do
        [[ -z "$plugin" ]] && continue
        info "  disable $plugin@$legacy"
        run_soft claude plugin disable "$plugin@$legacy"
      done <<<"$plugins"

      while IFS= read -r plugin; do
        [[ -z "$plugin" ]] && continue
        info "  uninstall $plugin@$legacy --prune -y"
        run_soft claude plugin uninstall "$plugin@$legacy" --prune -y
      done <<<"$plugins"
    fi

    info "  marketplace remove $legacy"
    run_soft claude plugin marketplace remove "$legacy"
  done

  ok "legacy removal pass complete"
}

# ----- stage 3: scrub stale settings.json keys ------------------------------

stage_3_scrub_settings() {
  step "Stage 3: scrub stale settings.json keys"

  if [[ ! -f "$SETTINGS_PATH" ]]; then
    info "$SETTINGS_PATH missing, nothing to scrub"
    return 0
  fi

  # Build a jq program that removes every legacy marketplace from
  # extraKnownMarketplaces and every enabledPlugins entry ending with
  # @<legacy>.
  local jq_filters=()
  local legacy
  for legacy in "${LEGACY_MARKETPLACES[@]}"; do
    jq_filters+=( "del(.extraKnownMarketplaces[\"$legacy\"])" )
    jq_filters+=( "(.enabledPlugins // {}) as \$ep | .enabledPlugins = (\$ep | with_entries(select(.key | endswith(\"@$legacy\") | not)))" )
  done

  local jq_program
  jq_program=$(IFS=$' | '; printf '%s' ".${jq_filters[*]}")
  # The leading ". | " is illegal but the IFS join produced ". <filter> | <filter>..."
  # We just need the joined filters separated by " | ".
  jq_program="$(printf '%s\n' "${jq_filters[@]}" | paste -sd '|' -)"
  jq_program="${jq_program//|/ | }"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "dry-run: would jq-rewrite $SETTINGS_PATH with filter:"
    printf '%s%s%s\n' "$C_DIM" "$jq_program" "$C_RESET" >&2
    jq "$jq_program" "$SETTINGS_PATH" >/dev/null \
      || die "jq pre-check failed; settings.json is not valid JSON"
    return 0
  fi

  local tmp
  tmp="$(mktemp "${SETTINGS_PATH}.XXXXXX")"
  if ! jq "$jq_program" "$SETTINGS_PATH" >"$tmp"; then
    rm -f "$tmp"
    die "jq rewrite of $SETTINGS_PATH failed; original untouched"
  fi
  mv "$tmp" "$SETTINGS_PATH"
  ok "scrubbed legacy extraKnownMarketplaces + enabledPlugins entries"
}

# ----- stage 4: filesystem cleanup ------------------------------------------

stage_4_filesystem_cleanup() {
  step "Stage 4: filesystem cleanup"

  local target
  for target in "${LEGACY_MARKETPLACES[@]}"; do
    local cache_dir="$PLUGINS_CACHE_DIR/$target"
    if [[ -d "$cache_dir" ]]; then
      run rm -rf -- "$cache_dir"
      ok "rm -rf $cache_dir"
    else
      info "absent: $cache_dir"
    fi
  done

  for target in "${LEGACY_CACHE_SYMLINKS[@]}"; do
    local link="$PLUGINS_CACHE_DIR/$target"
    if [[ -L "$link" ]]; then
      run rm -f -- "$link"
      ok "rm symlink $link"
    else
      info "absent: $link"
    fi
  done
}

# ----- stage 5: add new marketplace -----------------------------------------

stage_5_add_marketplace() {
  step "Stage 5: add marketplace $NEW_MARKETPLACE from $NEW_MARKETPLACE_SOURCE"

  if marketplace_registered "$NEW_MARKETPLACE"; then
    info "marketplace $NEW_MARKETPLACE already registered, skipping add"
    return 0
  fi

  run claude plugin marketplace add "$NEW_MARKETPLACE_SOURCE"

  if [[ "$DRY_RUN" -eq 0 ]]; then
    marketplace_registered "$NEW_MARKETPLACE" \
      || die "marketplace $NEW_MARKETPLACE not registered after add"
    ok "marketplace $NEW_MARKETPLACE registered"
  fi
}

# ----- stage 6: install new plugins -----------------------------------------

stage_6_install() {
  step "Stage 6: install plugins from @$NEW_MARKETPLACE (dep order)"

  local plugin
  for plugin in "${NEW_PLUGINS[@]}"; do
    info "install $plugin@$NEW_MARKETPLACE"
    run claude plugin install "$plugin@$NEW_MARKETPLACE"
  done

  if [[ "$DRY_RUN" -eq 1 ]]; then
    return 0
  fi

  local installed_count
  installed_count="$(claude plugin list 2>/dev/null \
    | grep -cE "@$NEW_MARKETPLACE\b" || true)"

  if [[ "$installed_count" -ne "${#NEW_PLUGINS[@]}" ]]; then
    err "Expected ${#NEW_PLUGINS[@]} plugins under @$NEW_MARKETPLACE, found $installed_count"
    die "Install reconciliation failed; rerun with --continue-from 6 after fixing"
  fi
  ok "all ${#NEW_PLUGINS[@]} plugins installed under @$NEW_MARKETPLACE"
}

# ----- stage 7: verify ------------------------------------------------------

stage_7_verify() {
  step "Stage 7: verify final state"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "dry-run: skipping live assertions"
    return 0
  fi

  local errors=0

  local legacy
  for legacy in "${LEGACY_MARKETPLACES[@]}"; do
    if [[ "$legacy" == "$NEW_MARKETPLACE" ]]; then
      continue
    fi
    if marketplace_registered "$legacy"; then
      err "legacy marketplace still present: $legacy"
      errors=$((errors + 1))
    else
      ok "legacy marketplace absent: $legacy"
    fi
  done

  if marketplace_registered "$NEW_MARKETPLACE"; then
    ok "marketplace $NEW_MARKETPLACE present"
  else
    err "marketplace $NEW_MARKETPLACE missing"
    errors=$((errors + 1))
  fi

  local plugin_list new_count
  plugin_list="$(claude plugin list 2>/dev/null || true)"
  new_count="$(printf '%s\n' "$plugin_list" | grep -cE "@$NEW_MARKETPLACE\b" || true)"
  if [[ "$new_count" -eq "${#NEW_PLUGINS[@]}" ]]; then
    ok "$new_count plugins under @$NEW_MARKETPLACE"
  else
    err "plugin count under @$NEW_MARKETPLACE = $new_count, expected ${#NEW_PLUGINS[@]}"
    errors=$((errors + 1))
  fi

  for legacy in "${LEGACY_MARKETPLACES[@]}"; do
    if [[ "$legacy" == "$NEW_MARKETPLACE" ]]; then
      continue
    fi
    local cache_dir="$PLUGINS_CACHE_DIR/$legacy"
    if [[ -d "$cache_dir" ]]; then
      err "legacy cache still present: $cache_dir"
      errors=$((errors + 1))
    else
      ok "legacy cache absent: $legacy"
    fi
  done

  for legacy in "${LEGACY_MARKETPLACES[@]}"; do
    if [[ "$legacy" == "$NEW_MARKETPLACE" ]]; then
      continue
    fi
    local extra_present
    extra_present="$(jq -r --arg m "$legacy" '.extraKnownMarketplaces[$m] // empty' "$SETTINGS_PATH" 2>/dev/null || true)"
    if [[ -n "$extra_present" ]]; then
      err "settings.json extraKnownMarketplaces still has $legacy"
      errors=$((errors + 1))
    else
      ok "settings.json extraKnownMarketplaces clean of $legacy"
    fi

    local leftover
    leftover="$(jq -r --arg m "$legacy" '.enabledPlugins // {} | keys[] | select(endswith("@" + $m))' "$SETTINGS_PATH" 2>/dev/null || true)"
    if [[ -n "$leftover" ]]; then
      err "settings.json enabledPlugins has leftover @$legacy keys:"
      printf '  %s\n' "$leftover" >&2
      errors=$((errors + 1))
    else
      ok "settings.json enabledPlugins clean of @$legacy"
    fi
  done

  if [[ "$errors" -gt 0 ]]; then
    die "verification produced $errors error(s); see $REPORT_PATH"
  fi

  if [[ -n "$REPORT_PATH" ]]; then
    {
      printf '# rldyour-claudecode install report\n\n'
      printf '- Timestamp: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      printf '- Marketplace: %s (%s)\n' "$NEW_MARKETPLACE" "$NEW_MARKETPLACE_SOURCE"
      printf '- Plugins installed: %d\n' "$new_count"
      printf '- Legacy cleaned: %s\n' "${LEGACY_MARKETPLACES[*]}"
      printf '- Backup: %s\n\n' "$BACKUP_DIR"
      printf '## Verification\n\nAll assertions passed.\n\n'
      printf '## Recovery\n\n'
      printf 'To restore the previous state:\n\n'
      printf '```bash\n'
      printf 'cp %s/settings.json %s\n' "$BACKUP_DIR" "$SETTINGS_PATH"
      printf 'cp %s/installed_plugins.json %s\n' "$BACKUP_DIR" "$INSTALLED_PLUGINS_PATH"
      printf 'cp %s/known_marketplaces.json %s\n' "$BACKUP_DIR" "$KNOWN_MARKETPLACES_PATH"
      printf '```\n'
    } >>"$REPORT_PATH"
  fi

  ok "all checks passed - see $REPORT_PATH"
}

# ----- main -----------------------------------------------------------------

main() {
  require_command claude
  require_command jq

  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "DRY-RUN mode: no changes will be made"
  fi
  if [[ "$CONTINUE_FROM" -gt 0 ]]; then
    info "resuming from stage $CONTINUE_FROM"
  fi

  stage_should_run 0 && stage_0_guard
  stage_should_run 1 && stage_1_backup
  stage_should_run 2 && stage_2_remove_legacy
  stage_should_run 3 && stage_3_scrub_settings
  stage_should_run 4 && stage_4_filesystem_cleanup
  stage_should_run 5 && stage_5_add_marketplace
  stage_should_run 6 && stage_6_install
  stage_should_run 7 && stage_7_verify

  printf '\n%s%sInstall finished.%s\n' "$C_GREEN" "$C_BOLD" "$C_RESET" >&2
  if [[ "$DRY_RUN" -eq 1 ]]; then
    info "next: rerun without --dry-run and with --i-exited-claude"
  else
    info "next: re-launch claude and check /plugin + /mcp + /doctor"
  fi
}

main "$@"
