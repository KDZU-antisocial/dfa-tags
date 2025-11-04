#!/usr/bin/env python3
import os, subprocess

FREECAD = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
WORKDIR = "/Users/006504390/Dropbox/KDZU/dubplate forensics agent/AprilTag-Standard41h12-90mm-total-size"
SCRIPT = os.path.join(WORKDIR, "freecad_svg_to_stl.py")

HEIGHT_MM = "3"; HOLE_X = "70"; HOLE_Y = "70"; HOLE_R = "4"

def run_one(n: int):
    svg = os.path.join(WORKDIR, f"tagStandard41h12-{n}.svg")
    stl = os.path.join(WORKDIR, f"tagStandard41h12-{n}.stl")
    if not os.path.isfile(svg):
        print(f"Skip missing {svg}")
        return
    env = os.environ.copy()
    env.update({
        "INPUT_SVG": svg, "OUTPUT_STL": stl,
        "HEIGHT_MM": HEIGHT_MM, "HOLE_X": HOLE_X, "HOLE_Y": HOLE_Y, "HOLE_R": HOLE_R
    })
    print(f"Converting {os.path.basename(svg)} -> {os.path.basename(stl)}")
    subprocess.run([FREECAD, SCRIPT], cwd=WORKDIR, env=env, check=True)

def main():
    run_one(0)               # test one
    for i in range(13, 100): # batch 13..99
        run_one(i)

if __name__ == "__main__":
    main()