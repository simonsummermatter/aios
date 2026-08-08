#!/bin/sh
# Open the ob1-review picker in its own Ghostty window (macOS: the CLI cannot
# start the emulator directly, so go through `open -na`). Returns immediately;
# the caller waits for $2 to appear.
#
#   run_picker.sh <items.json> <out.json>

set -eu
dir=$(cd "$(dirname "$0")" && pwd)

# `open -na` starts the new window in $HOME, not in the caller's cwd, so both
# paths must be absolute before they are handed over — a relative path dies with
# FileNotFoundError inside a window Simon then has to close by hand. realpath(1)
# is not on every macOS, and $2 does not exist yet, so resolve by hand.
abspath() {
  case $1 in
    /*) printf '%s\n' "$1" ;;
    *)  printf '%s/%s\n' "$(cd "$(dirname "$1")" && pwd)" "$(basename "$1")" ;;
  esac
}

items=$(abspath "$1")
out=$(abspath "$2")

[ -f "$items" ] || { echo "run_picker.sh: no such items file: $items" >&2; exit 1; }

rm -f "$out"
exec open -na Ghostty.app --args \
  --window-width=104 --window-height=36 --title="ob1 review" \
  -e /usr/bin/env python3 "$dir/picker.py" --items "$items" --out "$out"
