#!/usr/bin/env python3

import json
import tomllib
from pathlib import Path
from typing import TypeVar, Sequence

T = TypeVar('T', str, Path)

def sort_strings(items: Sequence[T]) -> list[T]:
    """Sort strings or paths using byte value comparison."""
    return sorted(items)

def sort_dict_by_keys(d: dict) -> dict:
    """Sort dictionary by keys using byte value comparison."""
    return dict(sorted(d.items()))

def sort_mapping(mapping_file: Path) -> None:
    """Sort mapping file alphabetically by keys using byte value comparison."""
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    sorted_mapping = sort_dict_by_keys(mapping)

    with open(mapping_file, "w", encoding="utf-8", newline='\n') as f:
        json.dump(sorted_mapping, f, indent=4, ensure_ascii=False)


def sort_colors(colors_file: Path) -> None:
    """Sort colors file by sections and tags using byte value comparison."""
    with open(colors_file, "rb") as f:
        colors = tomllib.load(f)

    sorted_colors = {}
    for section in sort_strings(colors.keys()):
        sorted_colors[section] = sort_dict_by_keys(colors[section])

    with open(colors_file, "w", encoding="utf-8", newline='\n') as f:
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
