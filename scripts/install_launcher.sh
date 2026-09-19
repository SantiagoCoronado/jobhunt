#!/usr/bin/env bash
# Put the TUI launcher on your PATH under one word.
#   scripts/install_launcher.sh              # installs `jobhunt`
#   scripts/install_launcher.sh hunt         # or any name you would rather type
#   scripts/install_launcher.sh --uninstall [name]
# It is a symlink to bin/jobhunt in ~/.local/bin (JOBHUNT_BIN_DIR overrides the directory).
# It never replaces a command that is not this launcher.
set -euo pipefail

root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="$root/bin/jobhunt"
bin_dir="${JOBHUNT_BIN_DIR:-$HOME/.local/bin}"

uninstall=0
name="jobhunt"
for arg in "$@"; do
  case "$arg" in
    --uninstall) uninstall=1 ;;
    -h|--help) sed -n '2,7p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "unknown option: $arg" >&2; exit 2 ;;
    *) name="$arg" ;;
  esac
done
if [[ ! "$name" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "not a usable command name: $name" >&2
  exit 2
fi

link="$bin_dir/$name"
ours=0
if [ -L "$link" ] && [ "$(readlink "$link")" = "$target" ]; then ours=1; fi

if [ "$uninstall" = 1 ]; then
  if [ "$ours" = 1 ]; then rm "$link"; echo "removed $link"; else echo "$link is not this launcher, left alone" >&2; exit 1; fi
  exit 0
fi

if [ "$ours" = 0 ] && { [ -e "$link" ] || [ -L "$link" ]; }; then
  echo "$link already exists and is not this launcher; pick another name" >&2
  exit 1
fi
if [ "$ours" = 0 ]; then
  other="$(command -v "$name" 2>/dev/null || true)"
  if [ -n "$other" ]; then
    echo "\`$name\` already runs $other; pick another name" >&2
    exit 1
  fi
fi

chmod +x "$target"
mkdir -p "$bin_dir"
ln -sfn "$target" "$link"
echo "installed: $name -> $target"
case ":$PATH:" in
  *":$bin_dir:"*) ;;
  *) echo "note: $bin_dir is not on your PATH; add it to your shell profile" >&2 ;;
esac
