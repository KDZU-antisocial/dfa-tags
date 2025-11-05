#!/bin/bash
# Batch convert tagStandard41h12-0.svg through tagStandard41h12-99.svg

export PATH="/opt/homebrew/bin:$PATH"
cd "$(dirname "$0")"

echo "Starting batch conversion for files 0-99..."
echo ""

for i in {0..99}; do
  echo "=========================================="
  echo "Processing tagStandard41h12-$i.svg"
  echo "=========================================="
  uv run python convert_svgs_to_3mf.py --input-dir svg --pattern "tagStandard41h12-$i.svg" --overwrite
  echo ""
done

echo "=========================================="
echo "Batch conversion complete!"
echo "=========================================="

