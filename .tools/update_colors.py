#!/usr/bin/env python3

import json
import tomllib
from pathlib import Path

def get_canonical_tags(mapping_file: Path) -> set[str]:
    """Get all canonical tag names from mapping."""
    with open(mapping_file) as f:
        mapping = json.load(f)

    canonical = set()
    for value in mapping.values():
        if value is None:
            continue
        if isinstance(value, str):
            canonical.add(value)
        elif isinstance(value, list):
            canonical.update(value)

    return canonical

def update_colors_toml(colors_file: Path, mapping_file: Path) -> None:
    """Update colors.toml with canonical tag names."""
    # Load current colors
    with open(colors_file, "rb") as f:
        colors = tomllib.load(f)

    # Load canonical names
    canonical_tags = get_canonical_tags(mapping_file)

    # Track which canonical tags are covered
    covered_tags = set()

    # Update each section with sorted tags
    new_colors = {}
    for section in sorted(colors.keys()):  # Sort sections
        new_tags = {}
        for tag, color in colors[section].items():
            # Find canonical version
            canonical = next(
                (c for c in canonical_tags if c.lower().replace(" ", "-") == tag),
                None
            )
            if canonical:
                new_tags[canonical] = color
                covered_tags.add(canonical)
        # Sort tags case-insensitively
        new_colors[section] = dict(
            sorted(new_tags.items(), key=lambda x: x[0].lower())
        )

    # Check for missing tags
    missing_tags = canonical_tags - covered_tags
    if missing_tags:
        print("\nWarning: The following canonical tags are missing colors:")
        for tag in sorted(missing_tags):
            print(f"  - {tag!r}")

    # Save updated file
    with open(colors_file, "w", encoding="utf-8") as f:
        # Format TOML manually since tomllib is read-only
        for section in sorted(new_colors.keys()):  # Sort sections again to be safe
            f.write(f'["{section}"]\n')
            # Tags are already sorted in new_colors
            for tag, color in new_colors[section].items():
                f.write(f'"{tag}" = "{color}"\n')
            f.write("\n")
    print("\nUpdated colors.toml with canonical tag names")

if __name__ == "__main__":
    project_root = Path.cwd()
    mapping_file = project_root / "data" / "tags" / "mapping.json"
    colors_file = project_root / "data" / "tags" / "colors.toml"
    update_colors_toml(colors_file, mapping_file)