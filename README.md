# DFA Tags - SVG to 3MF Converter

Convert black and white SVG files (like AprilTags) to 3MF format with multi-color/multi-material support.

## Features

- **3MF Export**: Single file with black/white materials for multi-color 3D printing
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

## SVG Format Preparation

If you have SVG files in the old 90x90 viewBox format, you'll need to convert them to the 140x140 format with mask/hole structure before converting to 3MF.

### Using `update_svgs.py`

The `update_svgs.py` script converts old-format SVGs to the format expected by `convert_svgs_to_3mf.py`:

```bash
python update_svgs.py
```

**What it does:**
- Converts viewBox from `"0 0 90 90"` to `"0 0 140 140"`
- Adds mask structure with center hole at (70, 70)
- Wraps content in `translate(25,25)` transform
- Removes old-style holes at (45, 45)
- Processes files: `tagStandard41h12-13.svg` through `tagStandard41h12-99.svg`
- Skips files that already have the new format (idempotent)

**When to use it:**
- If you have SVG files with 90x90 viewBox that need to be converted
- If you need to add the mask/hole structure to existing SVGs
- Before running `convert_svgs_to_3mf.py` on old-format files

**Note:** The script checks if files already have the new format and skips them, so it's safe to run multiple times.

## Quick Start

Convert all SVGs to 3MF files (default):

```bash
uv run python convert_svgs_to_3mf.py --overwrite
```

This will:
- Read all `tagStandard41h12-*.svg` files from the current directory
- Export 3MF files to the `3mf/` directory
- Use 3mm height
- Create circular tags with 70mm radius
- Include a 4mm radius center hole

## Usage

### Basic Command

```bash
uv run python convert_svgs_to_3mf.py [OPTIONS]
```

### Export Mode

#### 3MF Export (Default)
Single file with black and white materials. Best for multi-color printers.

```bash
uv run python convert_svgs_to_3mf.py --overwrite
# or explicitly:
uv run python convert_svgs_to_3mf.py --export-3mf --overwrite
```

**Output**: `3mf/tagStandard41h12-0.3mf`, `3mf/tagStandard41h12-1.3mf`, etc.

## Command Line Options

### Input/Output Options

#### `--input-dir DIR`
Specifies the directory containing SVG files to convert. If not provided, the script uses the current working directory.

- **Default**: Current directory (`.`)
- **Example**: `--input-dir svg` to read from the `svg/` subdirectory
- **Example**: `--input-dir /path/to/my/svgs` to read from an absolute path

The script will search for SVG files matching the pattern (see `--pattern` below) in this directory.

#### `--pattern PATTERN`
Specifies a glob pattern to match SVG files in the input directory. Uses standard shell glob patterns with `*` and `?` wildcards.

- **Default**: `tagStandard41h12-*.svg`
- **Example**: `--pattern "tagStandard41h12-*.svg"` matches all files starting with `tagStandard41h12-` and ending with `.svg`
- **Example**: `--pattern "tagStandard41h12-0*.svg"` matches only files starting with `tagStandard41h12-0`
- **Example**: `--pattern "*.svg"` matches all SVG files in the input directory
- **Example**: `--pattern "tagStandard41h12-[0-9].svg"` matches single-digit tag numbers

**Note**: Use quotes around the pattern if it contains special shell characters like `*` or `?`.

#### `--overwrite`
Controls whether to overwrite existing output files. By default, the script skips files that already exist.

- **Default behavior**: Skip existing files (no overwrite)
- **With `--overwrite`**: Overwrite existing files

This is useful when you've updated the conversion script or want to regenerate all files, even if they already exist.

**Tip**: Always use `--overwrite` when testing or when you want to ensure all files are regenerated with the latest code.

### Export Mode Options

- `--export-3mf` or `--3mf`: Export as 3MF files with black/white materials (default)

### Geometry Options

- `--height-mm HEIGHT`: Extrusion height in mm (default: 3.0mm)
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

### Basic usage with default settings

Convert all `tagStandard41h12-*.svg` files from the current directory:

```bash
uv run python convert_svgs_to_3mf.py --overwrite
```

### Convert SVGs from a specific directory

Read SVG files from the `svg/` subdirectory:

```bash
uv run python convert_svgs_to_3mf.py \
  --input-dir svg \
  --overwrite
```

### Convert specific SVGs using pattern matching

Convert only files matching a specific pattern (e.g., tagStandard41h12-0, tagStandard41h12-01, etc.):

```bash
uv run python convert_svgs_to_3mf.py \
  --pattern "tagStandard41h12-0*.svg" \
  --overwrite
```

Convert all SVG files in the input directory:

```bash
uv run python convert_svgs_to_3mf.py \
  --input-dir svg \
  --pattern "*.svg" \
  --overwrite
```

### Combine input directory and pattern

Read from a custom directory and match a specific pattern:

```bash
uv run python convert_svgs_to_3mf.py \
  --input-dir /path/to/svg/files \
  --pattern "tagStandard41h12-[0-9].svg" \
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

### Complete workflow: Convert old-format SVGs to 3MF

If you have SVG files in the old 90x90 format, first convert them, then generate 3MF files:

```bash
# Step 1: Convert SVG format (if needed)
python update_svgs.py

# Step 2: Convert to 3MF
uv run python convert_svgs_to_3mf.py \
  --input-dir svg \
  --overwrite
```

## Output Format Details

### 3MF Format
- **Single file per SVG** with both black and white regions
- **Material assignments**: Black regions (RGB: 0,0,0), White regions (RGB: 255,255,255)
- **Slicer support**: PrusaSlicer, Cura, Bambu Studio, etc.
- **Multi-color printing**: Assign different filaments to each material in your slicer
- **Height**: Default 3mm (optimized for multi-color printing)

## Logging

The conversion script outputs detailed logging information to help debug issues and understand the conversion process. Log messages include:

- **Path detection**: Which black and white paths were found in the SVG
- **Geometry processing**: How paths are combined, subtracted, and processed
- **Area calculations**: The area of each geometry component
- **Mesh generation**: Number of polygons extruded and mesh statistics
- **Errors and warnings**: Any issues encountered during conversion

Log output is written to standard output (stdout) and can be redirected to a file:

```bash
uv run python convert_svgs_to_3mf.py --overwrite > conversion_log.txt 2>&1
```

**Note**: Log files (like `conversion_log*.txt`) are automatically ignored by git (see `.gitignore`).

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
├── convert_svgs_to_3mf.py  # Main conversion script (SVG → 3MF)
├── update_svgs.py          # SVG format converter (90x90 → 140x140 with mask)
├── setup.sh                # Environment setup script
├── svg/                    # Input SVG files
├── 3mf/                    # Output 3MF files
├── pyproject.toml          # Python dependencies
└── README.md               # This file
```

### Utility Scripts

- **`setup.sh`**: Sets up ARM64 Python environment and installs dependencies
- **`update_svgs.py`**: Converts old 90x90 format SVGs to 140x140 format with mask/hole structure
- **`run_with_log.sh`**: Runs conversion with logging output
- **`verify_setup.py`**: Verifies that all dependencies are installed correctly
- **`check_setup.py`**: Checks uv and pyproject.toml configuration
- **`test_conversion.py`**: Tests conversion with detailed logging

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

