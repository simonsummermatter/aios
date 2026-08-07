#!/bin/sh
# Open the ob1-review picker in its own Ghostty window (macOS: the CLI cannot
# start the emulator directly, so go through `open -na`). Returns immediately;
# the caller waits for $2 to appear.
#
#   run_picker.sh <items.json> <out.json>

set -eu
items=$1
out=$2
dir=$(cd "$(dirname "$0")" && pwd)

rm -f "$out"
exec open -na Ghostty.app --args \
  --window-width=104 --window-height=36 --title="ob1 review" \
  -e /usr/bin/env python3 "$dir/picker.py" --items "$items" --out "$out"
