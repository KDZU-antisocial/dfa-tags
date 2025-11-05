#!/bin/bash
cd /Users/rob/Documents/GitHub/dfa-tags
export PATH="/opt/homebrew/bin:$PATH"

echo "Running conversion with logging..."
uv run python convert_svgs_to_3mf.py --input-dir svg --pattern "tagStandard41h12-0.svg" --overwrite > conversion_log.txt 2>&1

echo "Conversion complete. Log saved to conversion_log.txt"
echo ""
echo "=== Log Contents ==="
cat conversion_log.txt

