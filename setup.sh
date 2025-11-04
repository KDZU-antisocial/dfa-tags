#!/bin/bash
set -e

# Use ARM64 uv and Python
export PATH="/opt/homebrew/bin:$PATH"

# Pin to ARM64 Python
echo "Configuring ARM64 Python..."
uv python pin /opt/homebrew/bin/python3

# Sync dependencies with ARM64 Python
echo "Syncing dependencies with ARM64 Python..."
uv sync

# Verify triangle is installed
echo ""
echo "Verifying installation..."
uv run python -c "import triangle; import platform; print('✓ triangle is installed'); print(f'Python architecture: {platform.machine()}')" || echo "⚠ triangle installation may have failed"

echo ""
echo "Setup complete!"
echo "You can now use: uv run python convert_svgs_to_3mf.py"

