#!/usr/bin/env python3
"""Build and validate the five independent ZIPs using Blender's extension CLI."""
import argparse
from pathlib import Path
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", default="blender", help="Path to the Blender 5.2 executable")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    command = [args.blender, "--background", "--factory-startup", "--command", "extension"]
    for manifest in sorted(ROOT.glob("addons/*/blender_manifest.toml")):
        with manifest.open("rb") as handle:
            metadata = tomllib.load(handle)
        path = output / f"{metadata['id']}-{metadata['version']}.zip"
        subprocess.run([*command, "build", "--source-dir", str(manifest.parent),
                        "--output-filepath", str(path)], check=True)
        subprocess.run([*command, "validate", str(path)], check=True)


if __name__ == "__main__":
    main()
