#!/usr/bin/env python3
import sys, os
import FreeCAD as App
import Part, Mesh

try:
	import MeshPart
except Exception:
	MeshPart = None


def log(*args):
	try:
		print(*args, flush=True)
	except Exception:
		pass


def svg_to_stl(svg_path, stl_path, height_mm=3.0, hole_center=(70.0, 70.0), hole_radius=4.0):
	"""Import an SVG, make faces, extrude to height, cut a cylindrical through-hole, export STL."""
	log(f"[SVG2STL] input={svg_path}")
	log(f"[SVG2STL] output={stl_path}")
	log(f"[SVG2STL] height={height_mm} hole_center={hole_center} hole_radius={hole_radius}")
	doc = App.newDocument("SVG2STL")
	try:
		# Import SVG
		import ImportGui
		ImportGui.insert(svg_path, doc.Name)
		doc.recompute()

		# Gather shapes and build faces where possible
		shapes = []
		for obj in doc.Objects:
			if hasattr(obj, "Shape") and obj.Shape and not obj.Shape.isNull():
				sh = obj.Shape
				faces = []
				for w in sh.Wires:
					try:
						faces.append(Part.Face(w))
					except Exception:
						pass
				if faces:
					shapes.extend(faces)
				else:
					shapes.append(sh)

		if not shapes:
			raise RuntimeError("No shapes found after SVG import")

		compound = Part.makeCompound(shapes)

		# Extrude to solid
		solid = compound.extrude(App.Vector(0, 0, float(height_mm)))

		# Through-hole cylinder (slightly longer to ensure clean cut)
		hx, hy = float(hole_center[0]), float(hole_center[1])
		hr = float(hole_radius)
		cyl = Part.makeCylinder(hr, float(height_mm) + 2.0, App.Vector(hx, hy, -1.0), App.Vector(0, 0, 1))

		result = solid.cut(cyl)

		# Export STL (primary path)
		out = doc.addObject("Part::Feature", "Result")
		out.Shape = result
		doc.recompute()
		log("[SVG2STL] exporting via Mesh.export ...")
		Mesh.export([out], stl_path)

		if not os.path.isfile(stl_path) or os.path.getsize(stl_path) == 0:
			# Fallback: use MeshPart to write STL
			if MeshPart is not None:
				log("[SVG2STL] primary export missing; trying MeshPart.meshFromShape fallback ...")
				m = MeshPart.meshFromShape(Shape=result, LinearDeflection=0.1, AngularDeflection=0.523599, Relative=False)
				m.write(stl_path)

		if not os.path.isfile(stl_path) or os.path.getsize(stl_path) == 0:
			raise RuntimeError(f"STL not created at {stl_path}")
		log(f"[SVG2STL] wrote {stl_path}")
	finally:
		App.closeDocument(doc.Name)


def main():
	# CLI args: input.svg output.stl [height_mm] [hole_x] [hole_y] [hole_radius]
	if len(sys.argv) >= 3 and sys.argv[1] != "--":
		svg_path = os.path.abspath(sys.argv[1])
		stl_path = os.path.abspath(sys.argv[2])
		height_mm = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
		hole_x = float(sys.argv[4]) if len(sys.argv) > 4 else 70.0
		hole_y = float(sys.argv[5]) if len(sys.argv) > 5 else 70.0
		hole_r = float(sys.argv[6]) if len(sys.argv) > 6 else 4.0
		svg_to_stl(svg_path, stl_path, height_mm, (hole_x, hole_y), hole_r)
		return

	# Allow a leading "--" so FreeCAD doesn't try to interpret extra args
	if len(sys.argv) >= 4 and sys.argv[1] == "--":
		svg_path = os.path.abspath(sys.argv[2])
		stl_path = os.path.abspath(sys.argv[3])
		height_mm = float(sys.argv[4]) if len(sys.argv) > 4 else 3.0
		hole_x = float(sys.argv[5]) if len(sys.argv) > 5 else 70.0
		hole_y = float(sys.argv[6]) if len(sys.argv) > 6 else 70.0
		hole_r = float(sys.argv[7]) if len(sys.argv) > 7 else 4.0
		svg_to_stl(svg_path, stl_path, height_mm, (hole_x, hole_y), hole_r)
		return

	# ENV fallback: INPUT_SVG, OUTPUT_STL, HEIGHT_MM, HOLE_X, HOLE_Y, HOLE_R
	svg_path = os.getenv("INPUT_SVG")
	stl_path = os.getenv("OUTPUT_STL")
	if not svg_path or not stl_path:
		print("Usage: FreeCADCmd freecad_svg_to_stl.py input.svg output.stl [height_mm] [hole_x] [hole_y] [hole_radius]", file=sys.stderr)
		print("   or: FreeCADCmd -c freecad_svg_to_stl.py -- input.svg output.stl [height_mm] [hole_x] [hole_y] [hole_radius]", file=sys.stderr)
		print("   or: set INPUT_SVG, OUTPUT_STL (and optional HEIGHT_MM, HOLE_X, HOLE_Y, HOLE_R) env vars and run without args.", file=sys.stderr)
		sys.exit(1)

	height_mm = float(os.getenv("HEIGHT_MM", "3"))
	hole_x = float(os.getenv("HOLE_X", "70"))
	hole_y = float(os.getenv("HOLE_Y", "70"))
	hole_r = float(os.getenv("HOLE_R", "4"))

	svg_to_stl(os.path.abspath(svg_path), os.path.abspath(stl_path), height_mm, (hole_x, hole_y), hole_r)


if __name__ == "__main__":
	main()
