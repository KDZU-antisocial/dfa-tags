#!/usr/bin/env python3
import glob, re, os

OPEN_TAG_RE = re.compile(r'^<svg[^>]*viewBox="0 0 90 90"[^>]*>\s*', re.S)
CLOSE_TAG = '</svg>'
CENTER_HOLE = '<circle cx="45" cy="45" r="4" style="fill:#ffffff; stroke:none;"/>\n'

header = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="140mm" height="140mm" viewBox="0 0 140 140">\n'
    '<defs>\n'
    '<mask id="holeMask">\n'
    '<rect x="0" y="0" width="140" height="140" fill="#ffffff"/>\n'
    '<circle cx="70" cy="70" r="4" fill="#000000"/>\n'
    '</mask>\n'
    '</defs>\n'
    '<g mask="url(#holeMask)">\n'
    '<circle cx="70" cy="70" r="70" style="fill:#ffffff; stroke:none;"/>\n'
    '<g transform="translate(25,25)">\n'
)

footer = (
    '</g>\n'
    '</g>\n'
    '</svg>\n'
)

converted = 0
for path in sorted(glob.glob("tagStandard41h12-*.svg")):
    num = int(path.split('-')[1].split('.')[0])
    if num < 13 or num > 99:
        continue
    with open(path, 'r', encoding='utf-8') as f:
        svg = f.read()

    if 'mask id="holeMask"' in svg and 'transform="translate(25,25)"' in svg:
        continue

    svg = svg.replace(CENTER_HOLE, '').replace(CENTER_HOLE.strip(), '')

    m = OPEN_TAG_RE.match(svg)
    if m and svg.endswith(CLOSE_TAG):
        inner = svg[m.end():-len(CLOSE_TAG)]
    else:
        first_nl = svg.find('\n')
        if first_nl == -1 or not svg.endswith(CLOSE_TAG):
            continue
        inner = svg[first_nl+1:-len(CLOSE_TAG)]

    new_svg = header + inner + footer
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_svg)
    converted += 1

print(f"Converted {converted} files (13–99)")
