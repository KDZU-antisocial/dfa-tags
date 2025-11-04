#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Height 3mm, hole center at (70,70) for 140mm SVGs, hole radius 4mm (8mm dia)
for i in $(seq 13 99); do
	in="tagStandard41h12-$i.svg"
	out="tagStandard41h12-$i.stl"
	if [[ -f "$in" ]]; then
		echo "Converting $in -> $out"
		FreeCADCmd "$SCRIPT_DIR/freecad_svg_to_stl.py" "$in" "$out" 3 70 70 4
	else
		echo "Skip missing $in" >&2
	fi
done

echo "All done."
