"""Tag registry generation module."""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from .common import (
    MAPPING_FILE,
    COLORS_FILE,
    PATTERNS_FILE,
    TAGS_DIR,
    SPECIAL_DISPLAY_NAMES_FILE,
)
from .file_ops import (
    load_tags_map,
    load_colors_file,
    load_patterns,
    load_special_display_names,
)
from .normalize import TagNormalizer
from .transform import get_internal_name


class TagRegistryEntry(TypedDict):
    """Type for registry entry."""

    internal: str
    display: str
    color: str
    category: str


class TagRegistry(TypedDict):
    """Type for complete registry."""

    metadata: dict[str, any]
    tags: dict[str, TagRegistryEntry]


def calculate_file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_tags_from_colors(colors_data: dict[str, dict[str, str]]) -> set[str]:
    """Extract set of tags from colors.toml."""
    tags = set()
    for category, category_tags in colors_data.items():
        tags.update(category_tags.keys())
    return tags


def get_display_name(tag: str, mapping_data: dict, special_display_names: dict) -> str:
    """
    Get the display name for a tag.

    Args:
        tag: The tag to get the display name for
        mapping_data: Dictionary containing tag mappings
        special_display_names: Dictionary of special display name mappings

    Returns:
        The display name for the tag
    """
    # Check special display names first
    if tag in special_display_names:
        return special_display_names[tag]

    # Check if tag is in mapping
    tag_lower = tag.lower()
    for src_tag, mapped_tag in mapping_data.items():
        if src_tag.lower() == tag_lower:
            if mapped_tag is not None:
                if isinstance(mapped_tag, list):
                    return mapped_tag[0]  # Use first mapped tag as display name
                return mapped_tag
            break

    # Fallback to original tag
    return tag


def get_tag_color(tag: str, colors_data: dict) -> str:
    """
    Get the color for a tag.

    Args:
        tag: The tag to get the color for
        colors_data: Dictionary containing color mappings

    Returns:
        The color for the tag or "fallback" if not found
    """
    tag_lower = tag.lower()
    # Search through all categories
    for category in colors_data.values():
        # Case-insensitive comparison
        for color_tag, color in category.items():
            if tag_lower == color_tag.lower():
                return color

    # Return fallback color if not found
    return "fallback"


def generate_registry() -> TagRegistry:
    """
    Generate a unified tag registry from mapping.json and colors.toml.

    Returns:
        Dictionary containing the tag registry
    """
    # Load source files
    mapping_data = load_tags_map(MAPPING_FILE)
    colors_data = load_colors_file(COLORS_FILE)
    patterns_data = load_patterns(PATTERNS_FILE)
    special_display_names = load_special_display_names(SPECIAL_DISPLAY_NAMES_FILE)

    # Create reverse mapping for special display names
    display_to_internal = {v: k for k, v in special_display_names.items()}

    # Validate mapping against colors
    from .validate import validate_mapping_against_colors

    missing_in_colors, missing_in_mapping = validate_mapping_against_colors(
        MAPPING_FILE, COLORS_FILE
    )
    if missing_in_colors or missing_in_mapping:
        error_msg = []
        if missing_in_colors:
            error_msg.append(
                f"Tags missing in colors.toml: {', '.join(sorted(missing_in_colors))}"
            )
        if missing_in_mapping:
            error_msg.append(
                f"Tags missing in mapping.json: {', '.join(sorted(missing_in_mapping))}"
            )
        raise ValueError("\n".join(error_msg))

    # Get all valid tags from mapping (values, not keys)
    mapping_tags = set()
    for value in mapping_data.values():
        if value is not None:
            if isinstance(value, list):
                mapping_tags.update(value)
            else:
                mapping_tags.add(value)

    # Generate registry
    registry: TagRegistry = {
        "metadata": {
            "version": "1.0.0",
            "last_generated": datetime.utcnow().isoformat() + "Z",
            "source_files": {
                "mapping": calculate_file_hash(MAPPING_FILE),
                "colors": calculate_file_hash(COLORS_FILE),
                "patterns": calculate_file_hash(PATTERNS_FILE),
                "special_display_names": calculate_file_hash(
                    SPECIAL_DISPLAY_NAMES_FILE
                ),
            },
        },
        "tags": {},
    }

    # Process each tag from mapping.json (source of truth for display names)
    for tag in mapping_tags:
        # Get internal name, checking special display names first
        internal = display_to_internal.get(tag, get_internal_name(tag))

        # Get display name (either from special cases or use the mapping tag)
        display = special_display_names.get(internal, tag)

        # Find category and color from colors.toml
        try:
            category = next(
                cat
                for cat, tags in colors_data.items()
                if any(get_internal_name(t) == internal for t in tags)
            )
        except StopIteration:
            raise ValueError(
                f"Tag '{tag}' (internal: '{internal}') is in mapping.json but not found in any category in colors.toml"
            )

        try:
            color = next(
                color
                for tags, color in colors_data[category].items()
                if get_internal_name(tags) == internal
            )
        except StopIteration:
            raise ValueError(
                f"Tag '{tag}' (internal: '{internal}') is in category '{category}' but has no color assigned"
            )

        # Add to registry
        registry["tags"][internal] = {
            "internal": internal,
            "display": display,
            "color": color,
            "category": category,
        }

    return registry


def write_registry(registry: TagRegistry, registry_path: Path) -> None:
    """Write registry to JSON file."""
    with open(registry_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def main() -> None:
    """Entry point for registry generation."""
    registry = generate_registry()
    registry_path = TAGS_DIR / "tags.registry.json"
    write_registry(registry, registry_path)
    print(f"Tags registry generated successfully at {registry_path}")
    print(f"Total tags: {len(registry['tags'])}")


if __name__ == "__main__":
    main()
