#!/usr/bin/env python3
"""Test conversion with detailed logging."""
import sys
import os

# Redirect stdout and stderr to capture all output
log_file = open('/Users/rob/Documents/GitHub/dfa-tags/conversion_log.txt', 'w')
sys.stdout = log_file
sys.stderr = log_file

# Run the conversion
from convert_svgs_to_3mf import convert_to_3mf

svg_path = 'svg/tagStandard41h12-0.svg'
output_path = '3mf/tagStandard41h12-0.3mf'

print("=" * 70)
print("Starting conversion with detailed logging")
print("=" * 70)
print(f"SVG: {svg_path}")
print(f"Output: {output_path}")
print()

try:
    convert_to_3mf(
        svg_path=svg_path,
        output_path=output_path,
        height_mm=3.0,
        hole_center=(70.0, 70.0),
        hole_radius=4.0,
        clip_circle=(70.0, 70.0, 70.0)
    )
    print()
    print("=" * 70)
    print("Conversion completed successfully")
    print("=" * 70)
except Exception as e:
    print()
    print("=" * 70)
    print(f"ERROR: {e}")
    print("=" * 70)
    import traceback
    traceback.print_exc()

log_file.close()

# Restore stdout
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

print("Log written to conversion_log.txt")

