#!/usr/bin/env python3
import os

hole_circle = '<circle cx="45" cy="45" r="4" style="fill:#ffffff; stroke:none;"/>\n'

for i in range(17, 100):
    filename = f"tagStandard41h12-{i}.svg"
    if not os.path.exists(filename):
        continue
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Check if already has the hole
    if any('cx="45" cy="45" r="4"' in line for line in lines):
        print(f"Skipping {filename} - already has hole")
        continue
    
    # Find the last line (should be </svg>)
    for j in range(len(lines) - 1, -1, -1):
        if '</svg>' in lines[j]:
            # Insert circle before </svg>
            lines.insert(j, hole_circle)
            break
    
    with open(filename, 'w') as f:
        f.writelines(lines)
    
    print(f"Processed {filename}")

print("Done!")

