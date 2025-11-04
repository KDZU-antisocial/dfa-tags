#!/usr/bin/env python3
"""Verify that triangle and other dependencies are installed correctly."""
import sys
import platform

print("=" * 60)
print("Setup Verification")
print("=" * 60)

print(f"\nPython version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Architecture: {platform.machine()}")

print("\n" + "-" * 60)
print("Checking dependencies...")
print("-" * 60)

dependencies = [
    "numpy",
    "shapely",
    "trimesh",
    "triangle",
    "cairosvg",
    "pillow",
    "scikit-image",
]

all_ok = True
for dep in dependencies:
    try:
        mod = __import__(dep)
        version = getattr(mod, "__version__", "unknown")
        print(f"✓ {dep:20} {version:15} installed")
    except ImportError as e:
        print(f"✗ {dep:20} NOT INSTALLED")
        all_ok = False
        print(f"  Error: {e}")

print("\n" + "=" * 60)
if all_ok:
    print("✓ All dependencies are installed!")
    if platform.machine() == "arm64":
        print("✓ Using ARM64 Python (correct for triangle package)")
    else:
        print("⚠ Using non-ARM64 Python - triangle may not work")
else:
    print("✗ Some dependencies are missing")
    print("\nRun: export PATH=/opt/homebrew/bin:$PATH && uv sync")
print("=" * 60)

sys.exit(0 if all_ok else 1)

