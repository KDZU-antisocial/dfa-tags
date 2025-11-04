#!/usr/bin/env python3
import os
import glob
import re

# Get all SVG files
svg_files = sorted(glob.glob("tagStandard41h12-*.svg"))

# Circle to add: 8mm diameter = 4mm radius, centered at (45, 45)
hole_circle = '<circle cx="45" cy="45" r="4" style="fill:#ffffff; stroke:none;"/>'

count = 0
for svg_file in svg_files:
    # Read the file
    with open(svg_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if hole already exists (to avoid duplicates)
    if 'cx="45" cy="45" r="4"' in content:
        continue
    
    # Insert the circle before the closing </svg> tag
    # Handle both cases: </svg> with or without newline before it
    content = re.sub(r'</svg>\s*$', hole_circle + '\n</svg>', content, flags=re.MULTILINE)
    
    # Write back
    with open(svg_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    count += 1

print(f"Added holes to {count} files")

