#!/usr/bin/env python3

import json
import tomllib
from pathlib import Path


def sort_mapping(mapping_file: Path) -> None:
    """Sort mapping file alphabetically by keys."""
    with open(mapping_file) as f:
        mapping = json.load(f)

    sorted_mapping = dict(sorted(mapping.items()))

    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(sorted_mapping, f, indent=4, ensure_ascii=False)


def sort_colors(colors_file: Path) -> None:
    """Sort colors file by sections and tags."""
    # Read TOML
    with open(colors_file, "rb") as f:
        colors = tomllib.load(f)

    # Sort sections and their contents
    sorted_colors = {}
    for section in sorted(colors.keys()):
        sorted_colors[section] = dict(
            sorted(colors[section].items(), key=lambda x: x[0].lower())
        )

    # Write back
    with open(colors_file, "w", encoding="utf-8") as f:
        for section in sorted_colors:
            f.write(f'["{section}"]\n')
            for tag, color in sorted_colors[section].items():
                f.write(f'"{tag}" = "{color}"\n')
            f.write("\n")


def main() -> None:
    """Main function for sorting tag files."""
    project_root = Path.cwd()
    mapping_file = project_root / "data" / "tags" / "mapping.json"
    colors_file = project_root / "data" / "tags" / "colors.toml"

    sort_mapping(mapping_file)
    print(f"Sorted mapping file: {mapping_file}")

    sort_colors(colors_file)
    print(f"Sorted colors file: {colors_file}")


if __name__ == "__main__":
    main()
