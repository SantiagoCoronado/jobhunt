#!/usr/bin/env bash
# Copy every user-owned path (docs/spec-open-source.md decision 3) to a directory OUTSIDE
# the repo, then prove the copy: per-path file counts taken on disk with `find` (never
# `git ls-files`: data/, applications/ and interviews/ were never tracked and are the paths
# with no copy anywhere else) plus a SHA-256 list of every copied file.
#
# Usage:  scripts/backup_user_data.sh [DEST_ROOT]      default ~/jobhunt-user-data
# Exit 1 when any per-path count differs between source and copy.
set -euo pipefail
cd "$(dirname "$0")/.."

DEST_ROOT="${1:-$HOME/jobhunt-user-data}"
STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="$DEST_ROOT/$STAMP"

PATHS=(
  config/profile.yaml
  config/sources.local.yaml
  config/identity.local.yaml
  config/notify.yaml
  resume/master_resume.yaml
  resume/answers.yaml
  resume/originals
  research/companies
  research/upskill
  applications
  interviews
  data
  .env
)
# Never-tracked paths: the copy is the only copy, so a zero here deserves a loud line.
UNTRACKED_EVER=(applications interviews data)

count() { # files under a path (a file counts as 1), 0 when absent
  if [ -f "$1" ]; then echo 1; elif [ -d "$1" ]; then find "$1" -type f | wc -l | tr -d ' '; else echo 0; fi
}

mkdir -p "$DEST"
fail=0
printf "%-28s %8s %8s\n" "path" "source" "copy"
for p in "${PATHS[@]}"; do
  src_n=$(count "$p")
  if [ "$src_n" != "0" ]; then
    mkdir -p "$DEST/$(dirname "$p")"
    if [ -d "$p" ]; then cp -R "$p" "$DEST/$(dirname "$p")/"; else cp "$p" "$DEST/$p"; fi
  fi
  dst_n=$(count "$DEST/$p")
  flag=""
  [ "$src_n" != "$dst_n" ] && { flag="  MISMATCH"; fail=1; }
  for u in "${UNTRACKED_EVER[@]}"; do
    [ "$p" = "$u" ] && [ "$src_n" = "0" ] && flag="  (empty: this path has no copy anywhere else)"
  done
  printf "%-28s %8s %8s%s\n" "$p" "$src_n" "$dst_n" "$flag"
done

( cd "$DEST" && find . -type f -print0 | sort -z | xargs -0 shasum -a 256 ) > "$DEST.sha256"
echo
echo "copied to $DEST"
echo "checksums: $DEST.sha256 ($(wc -l < "$DEST.sha256" | tr -d ' ') files)"
if [ "$fail" != "0" ]; then echo "FAILED: a per-path count differs; do not untrack anything." >&2; exit 1; fi
echo "verified: every per-path count matches."
