#!/usr/bin/env python3
import argparse
import os
import sys
from typing import List, Tuple

import shapely.geometry as geom
import shapely.ops as ops
import trimesh
from io import BytesIO
from PIL import Image
import numpy as np


def log(*args):
	try:
		print(*args, flush=True)
	except Exception:
		pass


def load_svg_polygons(svg_path: str, black_only: bool = False) -> List[geom.Polygon]:
	"""Load an SVG as 2D polygons in SVG units.

	Returns a list of shapely Polygon objects (with holes captured in the polygon interiors when possible).
	
	If black_only=True, attempts to filter only black paths from SVG XML.
	"""
	if black_only:
		# Try to extract only black paths from SVG XML
		try:
			import xml.etree.ElementTree as ET
			import re
			tree = ET.parse(svg_path)
			root = tree.getroot()
			
			black_paths = []
			# Track transforms (could be nested)
			current_transform = None
			
			def parse_transform(transform_str):
				"""Parse SVG transform attribute and return (tx, ty) for translate."""
				if not transform_str:
					return 0, 0
				# Simple translate extraction
				match = re.search(r'translate\(([^,]+),([^)]+)\)', transform_str)
				if match:
					return float(match.group(1)), float(match.group(2))
				return 0, 0
			
			def is_black_fill(elem):
				"""Check if element has black fill color."""
				fill_color = None
				if 'fill' in elem.attrib:
					fill_color = elem.attrib['fill']
				elif 'style' in elem.attrib:
					style = elem.attrib['style']
					# Match fill:#000000, fill:#000, fill:black, etc.
					fill_match = re.search(r'fill:([^;]+)', style)
					if fill_match:
						fill_color = fill_match.group(1).strip()
				
				return fill_color in ('#000000', '#000', 'black', 'rgb(0,0,0)', 'rgb(0, 0, 0)')
			
			def process_element(elem, parent_transform=(0, 0)):
				"""Recursively process SVG elements, tracking transforms."""
				# Get current transform
				transform_str = elem.get('transform', '')
				tx, ty = parse_transform(transform_str)
				current_tx = parent_transform[0] + tx
				current_ty = parent_transform[1] + ty
				
				# Process path elements
				if elem.tag.endswith('path') and 'd' in elem.attrib:
					if is_black_fill(elem):
						try:
							# Apply transform to path data (simplified - just translate)
							path_d = elem.attrib['d']
							# Use trimesh to parse path
							from io import StringIO, BytesIO
							path_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 140"><g transform="translate({current_tx},{current_ty})"><path d="{path_d}"/></g></svg>'
							path_obj = trimesh.load_path(BytesIO(path_svg.encode('utf-8')), file_type='svg')
							path_polys = getattr(path_obj, "polygons_full", None) or path_obj.polygons_2D
							if path_polys:
								black_paths.extend(path_polys)
						except Exception as e:
							log(f"Failed to parse path: {e}")
				
				# Recursively process children
				for child in elem:
					process_element(child, (current_tx, current_ty))
			
			process_element(root)
			
			if black_paths:
				return black_paths
		except Exception as e:
			log(f"XML parsing for black-only paths failed: {e}, using full vector parsing")
	
	# Use trimesh to parse vector paths from SVG
	# load_path handles SVG into Path2D
	path = trimesh.load_path(svg_path)
	# Path2D exposes polygons_full when shapely is installed
	# polygons_full groups exterior with interior rings
	polys = getattr(path, "polygons_full", None)
	if polys is None:
		# Fallback: attempt to polygonize entities
		polys = path.polygons_2D
	if not polys:
		return []
	return polys


def rasterize_svg_to_mask(svg_path: str, target_mm: float = 140.0, px_per_mm: float = 5.0) -> Tuple[np.ndarray, float]:
	"""Rasterize SVG to a binary mask (True for black art), return mask and mm-per-pixel scale.

	- target_mm: assumed logical size of the artwork; default 140 mm diameter plate area
	- px_per_mm: pixels per mm; higher gives smoother contours
	"""
	width_px = int(target_mm * px_per_mm)
	height_px = int(target_mm * px_per_mm)
	with open(svg_path, 'rb') as f:
		svg_bytes = f.read()
	import cairosvg
	png_bytes = cairosvg.svg2png(bytestring=svg_bytes, output_width=width_px, output_height=height_px)
	img = Image.open(BytesIO(png_bytes)).convert('L')
	arr = np.array(img)
	# Threshold: consider near-black as art
	mask = arr < 128
	mm_per_px = target_mm / float(width_px)
	return mask, mm_per_px


def polygons_from_mask(mask: np.ndarray, mm_per_px: float, origin_mm: Tuple[float, float]) -> List[geom.Polygon]:
	"""Extract valid shapely polygons from a binary mask.

	Strategy:
	- Label connected components
	- For each component, find contours on a padded sub-image
	- Convert to mm coords and repair with buffer(0)
	- Filter tiny areas
	"""
	from skimage import measure
	labeled = measure.label(mask.astype(np.uint8), connectivity=1)
	regions = measure.regionprops(labeled)
	x0, y0 = origin_mm
	polys: List[geom.Polygon] = []
	for reg in regions:
		minr, minc, maxr, maxc = reg.bbox
		sub = reg.image.astype(float)
		# pad to ensure closed boundaries
		sub_pad = np.pad(sub, 1, mode='constant', constant_values=0)
		contours = measure.find_contours(sub_pad, 0.5)
		for c in contours:
			# remove the +1 padding offset
			c = c - 1.0
			coords = []
			for r, c0 in c:
				x = x0 + float(minc + c0) * mm_per_px
				y = y0 + float(minr + r) * mm_per_px
				coords.append((x, y))
			if len(coords) < 3:
				continue
			poly = geom.Polygon(coords)
			if not poly.is_valid:
				poly = poly.buffer(0)
			if isinstance(poly, geom.Polygon):
				if poly.area > 0:
					polys.append(poly)
			elif isinstance(poly, geom.MultiPolygon):
				for p in poly.geoms:
					if p.area > 0:
						polys.append(p)
	# Merge overlaps
	if polys:
		merged = ops.unary_union(polys)
		if isinstance(merged, geom.Polygon):
			return [merged]
		elif isinstance(merged, geom.MultiPolygon):
			return list(merged.geoms)
	return []


def build_solid_2d(
	svg_path: str,
	hole_center: Tuple[float, float],
	hole_radius: float,
	clip_circle: Tuple[float, float, float] | None = (70.0, 70.0, 70.0),
) -> geom.base.BaseGeometry:
	"""Create a 2D shapely solid from the SVG, optionally clipped to a circle, then subtract a center hole.

	Assumes SVG viewBox is in mm or uniformly scalable units; many files here use viewBox 0 0 140 140
	with width/height in mm, so 1 unit == 1 mm.
	"""
	polys = load_svg_polygons(svg_path)
	if polys:
		union = ops.unary_union(polys)
	else:
		# Raster fallback
		mask, mm_per_px = rasterize_svg_to_mask(svg_path)
		polys = polygons_from_mask(mask, mm_per_px, origin_mm=(0.0, 0.0))
		if not polys:
			raise RuntimeError("Rasterization produced no polygons")
		union = ops.unary_union(polys)
	if union.is_empty:
		raise RuntimeError("Empty geometry after parsing SVG")

	# If a circle is requested but likely mismatched in scale/location, derive from geometry bounds
	def derive_circle_from_bounds(g: geom.base.BaseGeometry) -> Tuple[float, float, float]:
		minx, miny, maxx, maxy = g.bounds
		cx = (minx + maxx) / 2.0
		cy = (miny + maxy) / 2.0
		w = (maxx - minx)
		h = (maxy - miny)
		r = max(w, h) / 2.0
		return cx, cy, r

	# Optionally clip to an outer circle (to ensure a circular plate instead of square)
	if clip_circle is not None:
		ccx, ccy, cr = clip_circle
		# Heuristic: if default circle seems far from geometry, recompute from bounds
		bx, by, br = derive_circle_from_bounds(union)
		if (abs(ccx - bx) > br * 0.6) or (abs(ccy - by) > br * 0.6):
			ccx, ccy, cr = bx, by, br
		circle = geom.Point(float(ccx), float(ccy)).buffer(float(cr), resolution=128)
		clipped = union.intersection(circle)
		if clipped.is_empty:
			# Ensure output remains circular even if art is empty or outside
			union = circle
		else:
			union = clipped

	# Subtract center hole explicitly (some SVG masks may not be honored by parsers)
	cx, cy = hole_center
	# resolution controls circle smoothness; 64 segments is usually fine for 3D printing
	hole = geom.Point(cx, cy).buffer(hole_radius, resolution=64)
	solid_2d = union.difference(hole)
	if solid_2d.is_empty and clip_circle is not None:
		# Fallback: at least return the circular plate minus hole
		ccx, ccy, cr = clip_circle if clip_circle is not None else derive_circle_from_bounds(union)
		circle = geom.Point(float(ccx), float(ccy)).buffer(float(cr), resolution=128)
		solid_2d = circle.difference(hole)
	return solid_2d


def build_bicolor_solids(
	svg_path: str,
	hole_center: Tuple[float, float],
	hole_radius: float,
	clip_circle: Tuple[float, float, float],
) -> Tuple[geom.base.BaseGeometry, geom.base.BaseGeometry]:
	"""Return two 2D solids: (black_geometry, white_geometry).

	- black: union of SVG paths (black art), clipped to circle, minus center hole
	- white: circle minus black, minus center hole
	"""
	# Try rasterization first (properly separates by color), fallback to vector parsing
	try:
		mask, mm_per_px = rasterize_svg_to_mask(svg_path)
		# mask is True for black pixels
		black_polys = polygons_from_mask(mask, mm_per_px, origin_mm=(0.0, 0.0))
		if black_polys:
			union = ops.unary_union(black_polys)
		else:
			raise RuntimeError("Rasterization produced no black polygons")
	except Exception as e:
		log(f"Rasterization failed ({e}), trying vector parsing...")
		# Fallback: try vector parsing with black-only filter
		polys = load_svg_polygons(svg_path, black_only=True)
		if not polys:
			# Last resort: try full vector parsing
			polys = load_svg_polygons(svg_path, black_only=False)
		if not polys:
			raise RuntimeError("Neither rasterization nor vector parsing produced polygons")
		union = ops.unary_union(polys)
	# Clip to circle with safety fallbacks
	def derive_circle_from_bounds(g: geom.base.BaseGeometry) -> Tuple[float, float, float]:
		minx, miny, maxx, maxy = g.bounds
		cx = (minx + maxx) / 2.0
		cy = (miny + maxy) / 2.0
		w = (maxx - minx)
		h = (maxy - miny)
		r = max(w, h) / 2.0
		return cx, cy, r

	ccx, ccy, cr = clip_circle
	# Heuristic: re-center to geometry if needed
	bx, by, br = derive_circle_from_bounds(union)
	if (abs(ccx - bx) > br * 0.6) or (abs(ccy - by) > br * 0.6):
		ccx, ccy, cr = bx, by, br
	circle = geom.Point(float(ccx), float(ccy)).buffer(float(cr), resolution=128)
	union_clipped = union.intersection(circle)
	if union_clipped.is_empty:
		union_clipped = union
	
	cx, cy = hole_center
	hole = geom.Point(cx, cy).buffer(hole_radius, resolution=64)
	
	# For vector parsing: union might include white background circle
	# If union covers most of the circle, it likely includes the white background
	# In that case, we'll use the entire union as the "art" and white will be minimal
	# The key is to ensure we have valid geometry for both
	black = union_clipped.difference(hole)
	white_temp = circle.difference(union_clipped)
	
	# If white is empty or very small, it means union covers the circle
	# In that case, white should be the circle minus the black art
	# But since we can't separate them, make white = circle - black (will be mostly empty, but valid)
	if white_temp.is_empty or white_temp.area < circle.area * 0.1:
		# Union includes white background, so white is just circle minus union
		white = circle.difference(union_clipped).difference(hole)
	else:
		# Normal case: union is black art, white is circle minus black
		white = white_temp.difference(hole)
	
	return black, white


def extrude_to_mesh(shape_2d: geom.base.BaseGeometry, height_mm: float) -> trimesh.Trimesh:
	"""Extrude a 2D shapely geometry to a 3D mesh of given height in mm."""
	parts: List[trimesh.Trimesh] = []

	def to_polygons(g: geom.base.BaseGeometry) -> List[geom.Polygon]:
		# Make geometry valid and extract polygonal parts
		try:
			from shapely import make_valid as _make_valid
		except Exception:
			_make_valid = None
		if _make_valid is not None:
			g = _make_valid(g)
		else:
			g = g.buffer(0)

		polys: List[geom.Polygon] = []
		if isinstance(g, geom.Polygon):
			polys = [g]
		elif isinstance(g, geom.MultiPolygon):
			polys = list(g.geoms)
		elif isinstance(g, geom.GeometryCollection):
			for sub in g.geoms:
				polys.extend(to_polygons(sub))
		else:
			# Non-areal geometry; ignore
			polys = []
		return [p for p in polys if not p.is_empty and p.is_valid and p.area > 0]

	geoms = to_polygons(shape_2d)
	if not geoms:
		# Nudge geometry to create area if lines were produced
		nudged = shape_2d.buffer(0.05)
		geoms = to_polygons(nudged)

	for poly in geoms:
		if poly.is_empty or not poly.is_valid:
			continue
		mesh = trimesh.creation.extrude_polygon(poly, height=height_mm)
		parts.append(mesh)

	if not parts:
		raise RuntimeError("No mesh parts produced from 2D geometry")
	return trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]


def convert_one(
	svg_path: str,
	stl_path: str,
	height_mm: float,
	hole_center: Tuple[float, float],
	hole_radius: float,
	clip_circle: Tuple[float, float, float] | None,
) -> None:
	log(f"[SVG2STL] {os.path.basename(svg_path)} -> {os.path.basename(stl_path)} (height={height_mm}mm)")
	shape_2d = build_solid_2d(svg_path, hole_center, hole_radius, clip_circle)
	mesh = extrude_to_mesh(shape_2d, height_mm)
	# Ensure watertightness when possible
	if not mesh.is_watertight:
		mesh.fill_holes()
	mesh.export(stl_path)
	if not os.path.isfile(stl_path) or os.path.getsize(stl_path) == 0:
		raise RuntimeError(f"Failed to write STL: {stl_path}")


def convert_to_3mf(
	svg_path: str,
	output_path: str,
	height_mm: float,
	hole_center: Tuple[float, float],
	hole_radius: float,
	clip_circle: Tuple[float, float, float],
) -> None:
	"""Export a bicolor SVG as a single 3MF file with black and white materials."""
	log(f"[SVG23MF] {os.path.basename(svg_path)} -> {os.path.basename(output_path)} (height={height_mm}mm)")
	black2d, white2d = build_bicolor_solids(svg_path, hole_center, hole_radius, clip_circle)
	
	# Validate geometries before extrusion
	if black2d.is_empty:
		log(f"Warning: Black geometry is empty for {os.path.basename(svg_path)}")
	if white2d.is_empty:
		log(f"Warning: White geometry is empty for {os.path.basename(svg_path)}")
	
	meshes_to_add = []
	
	# Try to extrude black geometry
	try:
		black3d = extrude_to_mesh(black2d, height_mm)
		if not black3d.is_watertight:
			black3d.fill_holes()
		black3d.visual.face_colors = [0, 0, 0, 255]
		meshes_to_add.append(("black", black3d))
	except Exception as e:
		log(f"Warning: Could not extrude black geometry: {e}")
	
	# Try to extrude white geometry
	try:
		white3d = extrude_to_mesh(white2d, height_mm)
		if not white3d.is_watertight:
			white3d.fill_holes()
		white3d.visual.face_colors = [255, 255, 255, 255]
		meshes_to_add.append(("white", white3d))
	except Exception as e:
		log(f"Warning: Could not extrude white geometry: {e}")
	
	if not meshes_to_add:
		raise RuntimeError("Both black and white geometries failed to produce meshes")
	
	# Create a scene with available meshes
	scene = trimesh.Scene()
	for name, mesh in meshes_to_add:
		scene.add_geometry(mesh, node_name=name)
	
	# Export as 3MF
	scene.export(output_path, file_type="3mf")
	if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
		raise RuntimeError(f"Failed to write 3MF: {output_path}")


def find_svgs(input_dir: str, pattern: str) -> List[str]:
	from glob import glob
	return sorted(glob(os.path.join(input_dir, pattern)))


def main():
	parser = argparse.ArgumentParser(description="Convert SVGs to 3MF (multi-color) or STL files using pure Python")
	parser.add_argument("--input-dir", default=os.getcwd(), help="Directory containing SVG files")
	parser.add_argument("--output-dir", default=None, help="Directory for output files (default: same as input")
	parser.add_argument("--pattern", default="tagStandard41h12-*.svg", help="Glob pattern for SVGs to convert")
	parser.add_argument("--height-mm", type=float, default=None, help="Extrusion height in mm (default: 4.0 for STL, 3.0 for 3MF)")
	parser.add_argument("--hole-x", type=float, default=70.0, help="Center hole X in mm")
	parser.add_argument("--hole-y", type=float, default=70.0, help="Center hole Y in mm")
	parser.add_argument("--hole-radius", type=float, default=4.0, help="Center hole radius in mm")
	parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
	parser.add_argument("--split-bicolor", action="store_true", help="Export two separate STL files per SVG (*_black.stl and *_white.stl) instead of 3MF")
	parser.add_argument("--export-stl", action="store_true", help="Export single STL file (black+white combined) instead of 3MF")
	parser.add_argument("--export-3mf", "--3mf", dest="export_3mf", action="store_true", help="Export as 3MF files with black/white materials (default, best for multi-color printing)")
	parser.add_argument("--no-clip-circle", action="store_true", help="Do not clip to outer circle")
	parser.add_argument("--circle-x", type=float, default=70.0, help="Outer circle center X in mm")
	parser.add_argument("--circle-y", type=float, default=70.0, help="Outer circle center Y in mm")
	parser.add_argument("--circle-radius", type=float, default=70.0, help="Outer circle radius in mm")
	args = parser.parse_args()

	# Default to 3MF export if no other mode is specified
	if not args.split_bicolor and not args.export_stl:
		args.export_3mf = True

	# Default height: 3mm for 3MF, 4mm for STL
	if args.height_mm is None:
		args.height_mm = 3.0 if args.export_3mf else 4.0

	in_dir = os.path.abspath(args.input_dir)
	# Default output directory: 3mf/ for 3MF exports, stl/ for split STL, same as input for single STL
	# Use project root (current working directory) for output directories, not input directory
	project_root = os.getcwd()
	if args.output_dir:
		out_dir = os.path.abspath(args.output_dir)
	elif args.export_3mf:
		out_dir = os.path.join(project_root, "3mf")
	elif args.split_bicolor:
		out_dir = os.path.join(project_root, "stl")
	else:
		out_dir = in_dir
	os.makedirs(out_dir, exist_ok=True)

	svgs = find_svgs(in_dir, args.pattern)
	if not svgs:
		log("No SVGs found matching pattern", args.pattern, "in", in_dir)
		return 0

	failures = 0
	for svg in svgs:
		name = os.path.splitext(os.path.basename(svg))[0]
		clip = None if args.no_clip_circle else (args.circle_x, args.circle_y, args.circle_radius)
		if args.export_3mf:
			# Export as 3MF with materials
			output_name = os.path.join(out_dir, f"{name}.3mf")
			if os.path.exists(output_name) and not args.overwrite:
				log(f"Skip existing {os.path.basename(output_name)} (use --overwrite)")
				continue
			try:
				if clip is None:
					raise RuntimeError("--export-3mf requires a clipping circle to define the white background")
				convert_to_3mf(svg, output_name, args.height_mm, (args.hole_x, args.hole_y), args.hole_radius, clip)
			except Exception as e:
				failures += 1
				log(f"ERROR converting {os.path.basename(svg)} (3MF): {e}")
		elif args.split_bicolor:
			black_name = os.path.join(out_dir, f"{name}_black.stl")
			white_name = os.path.join(out_dir, f"{name}_white.stl")
			if not args.overwrite and os.path.exists(black_name) and os.path.exists(white_name):
				log(f"Skip existing {os.path.basename(black_name)}, {os.path.basename(white_name)} (use --overwrite)")
				continue
			try:
				if clip is None:
					raise RuntimeError("--split-bicolor requires a clipping circle to define the white background")
				black2d, white2d = build_bicolor_solids(svg, (args.hole_x, args.hole_y), args.hole_radius, clip)
				black3d = extrude_to_mesh(black2d, args.height_mm)
				if not black3d.is_watertight:
					black3d.fill_holes()
				black3d.export(black_name)
				white3d = extrude_to_mesh(white2d, args.height_mm)
				if not white3d.is_watertight:
					white3d.fill_holes()
				white3d.export(white_name)
			except Exception as e:
				failures += 1
				log(f"ERROR converting {os.path.basename(svg)} (bicolor): {e}")
		else:
			stl = os.path.join(out_dir, f"{name}.stl")
			if os.path.exists(stl) and not args.overwrite:
				log(f"Skip existing {os.path.basename(stl)} (use --overwrite to regenerate)")
				continue
			try:
				convert_one(svg, stl, args.height_mm, (args.hole_x, args.hole_y), args.hole_radius, clip)
			except Exception as e:
				failures += 1
				log(f"ERROR converting {os.path.basename(svg)}: {e}")

	format_name = "3MF" if args.export_3mf else ("STL (split)" if args.split_bicolor else "STL")
	log(f"Done. Converted {len(svgs) - failures}/{len(svgs)} SVGs to {format_name} in {out_dir}")
	return 1 if failures else 0


if __name__ == "__main__":
	sys.exit(main())
