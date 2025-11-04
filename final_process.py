#!/usr/bin/env python3
import os

hole = '<circle cx="45" cy="45" r="4" style="fill:#ffffff; stroke:none;"/>\n'

for i in range(51, 100):
    filename = f"tagStandard41h12-{i}.svg"
    if not os.path.exists(filename):
        continue
    with open(filename, 'r') as f:
        content = f.read()
    if 'cx="45" cy="45" r="4"' in content:
        continue
    content = content.replace('</svg>', hole + '</svg>', 1)
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Processed {filename}")

print("All done!")

