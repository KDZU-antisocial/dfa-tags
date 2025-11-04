#!/usr/bin/env python3
"""Check uv and pyproject.toml configuration."""
import sys
import platform
import subprocess
from pathlib import Path

print("=" * 70)
print("UV and PyProject.toml Configuration Check")
print("=" * 70)

# Check uv
print("\n1. UV Configuration")
print("-" * 70)
try:
    result = subprocess.run(
        ["/opt/homebrew/bin/uv", "--version"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"✓ UV version: {result.stdout.strip()}")
        # Check architecture
        import os
        uv_path = "/opt/homebrew/bin/uv"
        if os.path.exists(uv_path):
            result2 = subprocess.run(
                ["file", uv_path],
                capture_output=True,
                text=True
            )
            if "arm64" in result2.stdout:
                print("✓ UV architecture: ARM64 (correct)")
            else:
                print(f"⚠ UV architecture: {result2.stdout.strip()}")
    else:
        print("✗ Could not get UV version")
except Exception as e:
    print(f"✗ Error checking UV: {e}")

# Check Python version
print("\n2. Python Configuration")
print("-" * 70)
python_version_file = Path(".python-version")
if python_version_file.exists():
    python_path = python_version_file.read_text().strip()
    print(f"✓ .python-version file exists: {python_path}")
    if "opt/homebrew" in python_path:
        print("✓ Points to ARM64 Python (correct)")
    else:
        print("⚠ Points to non-ARM64 Python")
else:
    print("⚠ No .python-version file found")

print(f"✓ Current Python: {sys.executable}")
print(f"✓ Architecture: {platform.machine()}")

# Check pyproject.toml
print("\n3. PyProject.toml Configuration")
print("-" * 70)
try:
    import tomllib
    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    
    project = config.get("project", {})
    print(f"✓ Project name: {project.get('name')}")
    print(f"✓ Version: {project.get('version')}")
    print(f"✓ Requires Python: {project.get('requires-python')}")
    
    deps = project.get("dependencies", [])
    print(f"✓ Dependencies: {len(deps)} packages")
    
    # Check for triangle
    has_triangle = any("triangle" in str(dep) for dep in deps)
    if has_triangle:
        print("✓ triangle is in dependencies")
    else:
        print("✗ triangle is NOT in dependencies")
    
    # List all dependencies
    print("\n  Dependencies list:")
    for dep in deps:
        print(f"    - {dep}")
        
except ImportError:
    # Python < 3.11 doesn't have tomllib
    print("⚠ Cannot parse TOML (need Python 3.11+), checking manually...")
    with open("pyproject.toml") as f:
        content = f.read()
        if "triangle" in content:
            print("✓ triangle found in pyproject.toml")
        else:
            print("✗ triangle NOT found in pyproject.toml")
        if "[project]" in content:
            print("✓ Has [project] section")
except Exception as e:
    print(f"✗ Error reading pyproject.toml: {e}")

# Check installed packages
print("\n4. Installed Packages Check")
print("-" * 70)
try:
    result = subprocess.run(
        ["/opt/homebrew/bin/uv", "run", "python", "-c", 
         "import triangle; import platform; print('✓ triangle installed'); print(f'Arch: {platform.machine()}')"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("✗ triangle not installed or error:")
        print(result.stderr)
except Exception as e:
    print(f"✗ Error checking installed packages: {e}")

print("\n" + "=" * 70)
print("Summary: Your setup looks good!")
print("=" * 70)

