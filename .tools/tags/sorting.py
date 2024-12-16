#!/usr/bin/env python3

from pathlib import Path
from typing import TypeVar, Sequence
from .file_ops import (
    load_tags_map,
    load_colors_file,
    write_mapping_file,
    write_colors_file,
)

T = TypeVar("T", str, Path)


def sort_strings(items: Sequence[T]) -> list[T]:
    """Sort strings or paths using byte value comparison."""
    return sorted(items)


def sort_dict_by_keys(d: dict) -> dict:
    """Sort dictionary by keys using byte value comparison."""
    return dict(sorted(d.items()))


def sort_dict_values_by_keys(d: dict) -> dict:
    """Sort dictionary values that are dictionaries by their keys."""
    sorted_dict = {}
    for section in sort_strings(d.keys()):
        if isinstance(d[section], dict):
            sorted_dict[section] = sort_dict_by_keys(d[section])
        else:
            sorted_dict[section] = d[section]
    return sorted_dict


def sort_stats_dict(stats: dict) -> dict:
    """Sort stats dictionary with special handling for lists and counters."""
    return {
        "total_files": stats["total_files"],
        "files_with_changes": stats["files_with_changes"],
        "unknown_tags": sort_strings(stats["unknown_tags"]),
        "normalized_tags": sort_dict_by_keys(stats["normalized_tags"]),
    }


def sort_mapping_file(mapping_file: Path) -> None:
    """Sort mapping file alphabetically by keys."""
    # Read mapping using file_ops
    mapping = load_tags_map(mapping_file)

    # Sort mapping
    sorted_mapping = sort_dict_by_keys(mapping)

    # Write sorted mapping using file_ops
    write_mapping_file(mapping_file, sorted_mapping)


def sort_colors_file(colors_file: Path) -> None:
    """Sort colors file by sections and tags."""
    # Read colors using file_ops
    colors = load_colors_file(colors_file)

    # Sort colors by sections and tags
    sorted_colors = sort_dict_values_by_keys(colors)

    # Write sorted colors using file_ops
    write_colors_file(colors_file, sorted_colors)


def main() -> None:
    """Main function for sorting tag files."""
    project_root = Path.cwd()
    mapping_file = project_root / "data" / "tags" / "mapping.json"
    colors_file = project_root / "data" / "tags" / "colors.toml"

    sort_mapping_file(mapping_file)
    print(f"Sorted mapping file: {mapping_file}")

    sort_colors_file(colors_file)
    print(f"Sorted colors file: {colors_file}")


if __name__ == "__main__":
    main()
