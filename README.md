# DFA Tags - SVG to 3D Printer Format Converter

Convert black and white SVG files (like AprilTags) to 3D printable formats (3MF, STL) with multi-color/multi-material support.

## Features

- **3MF Export (Default)**: Single file with black/white materials for multi-color 3D printing
- **Split STL Export**: Separate black and white STL files for manual assembly
- **Single STL Export**: Combined black and white geometry
- **Circular Base**: Automatically clips to circular tags (customizable)
- **Center Hole**: Adds a through-hole for mounting
- **Raster Fallback**: Handles complex SVGs by rasterizing if vector parsing fails

## Installation

This project uses `uv` for dependency management. Install dependencies with:

```bash
uv sync
```

### Optional: Install Cairo for Better SVG Handling

For best results with complex SVGs (especially those with masks and transforms), install the Cairo library system-wide. On macOS with Homebrew:

```bash
brew install cairo
```

**Why?** Cairo enables proper SVG rasterization that correctly separates black and white regions. Without it, the script falls back to vector parsing which may not separate colors as accurately.

**Note:** The script will work without Cairo, but you may see warnings about empty white geometry. The script will still create valid 3MF files with at least the black material.

## Quick Start

Convert all SVGs to 3MF files (default):

```bash
uv run python convert_svgs_to_3mf.py --overwrite
```

This will:
- Read all `tagStandard41h12-*.svg` files from the current directory
- Export 3MF files to the `3mf/` directory
- Use 3mm height (default for 3MF)
- Create circular tags with 70mm radius
- Include a 4mm radius center hole

## Usage

### Basic Command

```bash
uv run python convert_svgs_to_3mf.py [OPTIONS]
```

### Export Modes

#### 3MF Export (Default - Recommended)
Single file with black and white materials. Best for multi-color printers.

```bash
uv run python convert_svgs_to_3mf.py --overwrite
# or explicitly:
uv run python convert_svgs_to_3mf.py --export-3mf --overwrite
```

**Output**: `3mf/tagStandard41h12-0.3mf`, `3mf/tagStandard41h12-1.3mf`, etc.

#### Split STL Export
Two separate STL files per SVG (one for black, one for white parts).

```bash
uv run python convert_svgs_to_3mf.py --split-bicolor --overwrite
```

**Output**: `stl/tagStandard41h12-0_black.stl`, `stl/tagStandard41h12-0_white.stl`, etc.

#### Single STL Export
Combined black and white geometry in one STL file.

```bash
uv run python convert_svgs_to_3mf.py --export-stl --overwrite
```

**Output**: `tagStandard41h12-0.stl`, `tagStandard41h12-1.stl`, etc. (in input directory)

## Command Line Options

### Input/Output Options

- `--input-dir DIR`: Directory containing SVG files (default: current directory)
- `--output-dir DIR`: Directory for output files (default: auto-selected based on mode)
  - 3MF mode → `3mf/` subdirectory
  - Split STL mode → `stl/` subdirectory
  - Single STL mode → same as input directory
- `--pattern PATTERN`: Glob pattern for SVG files (default: `tagStandard41h12-*.svg`)
- `--overwrite`: Overwrite existing output files (default: skip existing files)

### Export Mode Options

- `--export-3mf` or `--3mf`: Export as 3MF files with black/white materials (default)
- `--split-bicolor`: Export two separate STL files per SVG (*_black.stl and *_white.stl)
- `--export-stl`: Export single combined STL file

### Geometry Options

- `--height-mm HEIGHT`: Extrusion height in mm
  - Default: 3.0mm for 3MF, 4.0mm for STL
  - Example: `--height-mm 5.0`

- `--hole-x X`: Center hole X position in mm (default: 70.0)
- `--hole-y Y`: Center hole Y position in mm (default: 70.0)
- `--hole-radius R`: Center hole radius in mm (default: 4.0)

### Circular Clipping Options

- `--no-clip-circle`: Disable circular clipping (keeps original SVG shape)
- `--circle-x X`: Outer circle center X in mm (default: 70.0)
- `--circle-y Y`: Outer circle center Y in mm (default: 70.0)
- `--circle-radius R`: Outer circle radius in mm (default: 70.0)

## Examples

### Convert specific SVGs to 3MF

```bash
uv run python convert_svgs_to_3mf.py \
  --pattern "tagStandard41h12-0*.svg" \
  --overwrite
```

### Custom height and hole size

```bash
uv run python convert_svgs_to_3mf.py \
  --height-mm 5.0 \
  --hole-radius 5.0 \
  --overwrite
```

### Custom circle size

```bash
uv run python convert_svgs_to_3mf.py \
  --circle-radius 80.0 \
  --circle-x 70.0 \
  --circle-y 70.0 \
  --overwrite
```

### Export to specific directory

```bash
uv run python convert_svgs_to_3mf.py \
  --output-dir /path/to/output \
  --overwrite
```

### Keep original SVG shape (no circular clipping)

```bash
uv run python convert_svgs_to_3mf.py \
  --no-clip-circle \
  --overwrite
```

### Split STL files for manual assembly

```bash
uv run python convert_svgs_to_3mf.py \
  --split-bicolor \
  --height-mm 4.0 \
  --overwrite
```

## Output Format Details

### 3MF Format (Default)
- **Single file per SVG** with both black and white regions
- **Material assignments**: Black regions (RGB: 0,0,0), White regions (RGB: 255,255,255)
- **Slicer support**: PrusaSlicer, Cura, Bambu Studio, etc.
- **Multi-color printing**: Assign different filaments to each material in your slicer
- **Height**: Default 3mm (optimized for multi-color printing)

### Split STL Format
- **Two files per SVG**: `*_black.stl` and `*_white.stl`
- **Manual assembly**: Print each file separately and assemble
- **Use case**: Printers without multi-color support, or when you want to use different materials/colors
- **Output directory**: `stl/` subdirectory

### Single STL Format
- **One file per SVG**: Combined geometry
- **No color information**: Single material print
- **Use case**: Single-color prints where you don't need material separation

## Technical Details

### SVG Processing
1. **Vector parsing**: Attempts to parse SVG paths directly using trimesh
2. **Raster fallback**: If vector parsing fails, rasterizes the SVG to a bitmap and extracts contours
3. **Geometry union**: Combines all paths into a single 2D shape
4. **Circular clipping**: Clips to circular boundary (unless `--no-clip-circle`)
5. **Hole subtraction**: Removes center hole for mounting

### 3D Mesh Generation
- Extrudes 2D geometry to specified height
- Uses shapely for 2D geometry operations
- Uses trimesh for 3D mesh generation and export
- Automatically repairs non-watertight meshes

### Coordinate System
- Assumes SVG units are in millimeters (common for AprilTag SVGs)
- Default viewBox: 0 0 140 140 (140mm × 140mm)
- Circle clipping: 70mm radius centered at (70, 70)
- Center hole: 4mm radius at (70, 70)

## Project Structure

```
dfa-tags/
├── convert_svgs_to_3mf.py  # Main conversion script
├── svg/                     # Input SVG files
├── 3mf/                     # Output 3MF files (with .gitkeep)
├── stl/                     # Output STL files (with .gitkeep)
├── pyproject.toml           # Python dependencies
└── README.md               # This file
```

## Dependencies

- `trimesh` - 3D mesh processing and export
- `shapely` - 2D geometry operations
- `cairosvg` - SVG rasterization fallback
- `pillow` - Image processing
- `scikit-image` - Image analysis and contour extraction
- `numpy` - Numerical operations
- `svgpathtools`, `lxml`, `networkx`, `rtree` - SVG parsing support
- `mapbox_earcut`, `triangle` - Polygon triangulation

## Troubleshooting

### "No mesh parts produced from 2D geometry"
- The script will automatically try rasterization fallback
- Check that your SVG has visible black/white content
- Ensure the SVG viewBox matches expected dimensions

### Circular clipping removes all content
- The script auto-adjusts circle position if geometry is far from center
- Use `--no-clip-circle` to disable clipping
- Adjust `--circle-x`, `--circle-y`, `--circle-radius` if needed

### Missing dependencies
Run `uv sync` to install all required packages.

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

