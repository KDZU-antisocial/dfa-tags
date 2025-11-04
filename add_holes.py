#!/usr/bin/env python3
import os
import glob

# Get all SVG files
svg_files = glob.glob("tagStandard41h12-*.svg")
svg_files.sort()

# Circle to add: 8mm diameter = 4mm radius, centered at (45, 45)
hole_circle = '<circle cx="45" cy="45" r="4" style="fill:#ffffff; stroke:none;"/>\n'

for svg_file in svg_files:
    # Read the file
    with open(svg_file, 'r') as f:
        content = f.read()
    
    # Check if hole already exists (to avoid duplicates)
    if 'cx="45" cy="45" r="4"' in content:
        print(f"Skipping {svg_file} - hole already exists")
        continue
    
    # Insert the circle before the closing </svg> tag
    if content.rstrip().endswith('</svg>'):
        content = content.rstrip()[:-6] + hole_circle + '</svg>\n'
    else:
        # Fallback: just append before closing tag
        content = content.replace('</svg>', hole_circle + '</svg>')
    
    # Write back
    with open(svg_file, 'w') as f:
        f.write(content)
    
    print(f"Added hole to {svg_file}")

print(f"\nProcessed {len(svg_files)} files")

