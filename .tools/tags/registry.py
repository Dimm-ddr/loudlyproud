"""Tag registry generation module."""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import TypedDict, Optional

from .common import (
    MAPPING_FILE,
    COLORS_FILE,
    DATA_DIR,
)
from .file_ops import (
    load_tags_map,
    load_colors_file,
    load_patterns,
)


class TagRegistryEntry(TypedDict):
    """Type for registry entry."""

    internal: str
    display: str
    color: str
    category: str
    aliases: Optional[list[str]]


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


def normalize_tag(tag: str, normalization_rules: dict) -> str:
    """
    Normalize a tag using the provided normalization rules.

    Args:
        tag: The tag to normalize
        normalization_rules: Dictionary containing normalization patterns

    Returns:
        The normalized tag
    """
    # Convert to lowercase for consistent comparison
    tag_lower = tag.lower().strip()

    # Check direct normalizations
    if "normalizations" in normalization_rules:
        if tag_lower in normalization_rules["normalizations"]:
            return normalization_rules["normalizations"][tag_lower]

    # Check URL normalizations
    if "url_normalizations" in normalization_rules:
        if tag in normalization_rules["url_normalizations"]:
            return normalization_rules["url_normalizations"][tag]

    # Default normalization: lowercase and replace spaces/special chars with hyphens
    normalized = tag_lower.replace(" ", "-")
    # Remove any non-alphanumeric characters (except hyphens)
    normalized = "".join(c for c in normalized if c.isalnum() or c == "-")
    # Remove multiple consecutive hyphens and trailing/leading hyphens
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    return normalized.strip("-")


def get_display_name(tag: str, normalization_rules: dict) -> str:
    """
    Get the display name for a tag.

    Args:
        tag: The tag to get the display name for
        normalization_rules: Dictionary containing display name mappings

    Returns:
        The display name for the tag
    """
    # Normalize the tag first
    normalized = normalize_tag(tag, normalization_rules)

    # Check if there's a display override
    if "display" in normalization_rules:
        if normalized in normalization_rules["display"]:
            return normalization_rules["display"][normalized]

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


def compare_tag_sets(
    mapping_tags: set[str], colors_tags: set[str], normalization_rules: dict
) -> tuple[set[str], set[str]]:
    """
    Compare two sets of tags after normalization.

    Args:
        mapping_tags: Set of tags from mapping.json
        colors_tags: Set of tags from colors.toml
        normalization_rules: Dictionary containing normalization patterns

    Returns:
        Tuple of (tags missing in colors, tags missing in mapping)
    """
    # Normalize all tags for comparison
    normalized_mapping = {
        normalize_tag(tag, normalization_rules) for tag in mapping_tags
    }
    normalized_colors = {normalize_tag(tag, normalization_rules) for tag in colors_tags}

    # Find differences
    missing_in_colors = {
        tag
        for tag in mapping_tags
        if normalize_tag(tag, normalization_rules) not in normalized_colors
    }
    missing_in_mapping = {
        tag
        for tag in colors_tags
        if normalize_tag(tag, normalization_rules) not in normalized_mapping
    }

    return missing_in_colors, missing_in_mapping


def generate_registry() -> TagRegistry:
    """
    Generate a unified tag registry from mapping.json and colors.toml.

    Returns:
        Dictionary containing the tag registry
    """
    # Load source files
    mapping_file = DATA_DIR / "mapping.json"
    colors_file = DATA_DIR / "colors.toml"
    patterns_file = DATA_DIR / "tag_normalization.yaml"

    mapping_data = load_tags_map(MAPPING_FILE)
    colors_data = load_colors_file(COLORS_FILE)
    normalization_rules = load_patterns(patterns_file)

    # Get all tags
    mapping_tags = set(mapping_data.keys())
    colors_tags = get_tags_from_colors(colors_data)

    # Compare tag sets
    missing_in_colors, missing_in_mapping = compare_tag_sets(
        mapping_tags, colors_tags, normalization_rules
    )

    if missing_in_colors or missing_in_mapping:
        error_msg = []
        if missing_in_colors:
            error_msg.append(
                f"Tags missing in colors.toml: {', '.join(missing_in_colors)}"
            )
        if missing_in_mapping:
            error_msg.append(
                f"Tags missing in mapping.json: {', '.join(missing_in_mapping)}"
            )
        raise ValueError("\n".join(error_msg))

    # Generate registry
    registry: TagRegistry = {
        "metadata": {
            "version": "1.0.0",
            "last_generated": datetime.utcnow().isoformat() + "Z",
            "source_files": {
                "mapping": calculate_file_hash(MAPPING_FILE),
                "colors": calculate_file_hash(COLORS_FILE),
                "normalization": calculate_file_hash(patterns_file),
            },
        },
        "tags": {},
    }

    # Process each tag
    for tag in mapping_tags:
        normalized = normalize_tag(tag, normalization_rules)
        display = get_display_name(tag, normalization_rules)
        color = get_tag_color(display, colors_data)

        # Find category
        category = next(
            (cat for cat, tags in colors_data.items() if tag in tags), "Uncategorized"
        )

        # Add to registry
        registry["tags"][tag] = {
            "internal": normalized,
            "display": display,
            "color": color,
            "category": category,
        }

        # Add aliases if any
        aliases = []
        for src_tag, norm_tag in normalization_rules["normalizations"].items():
            if norm_tag == normalized and src_tag != tag.lower():
                aliases.append(src_tag)
        if aliases:
            registry["tags"][tag]["aliases"] = sorted(aliases)

    return registry


def write_registry(registry: TagRegistry, registry_path: Path) -> None:
    """Write registry to JSON file."""
    with open(registry_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def main() -> None:
    """Entry point for registry generation."""
    registry = generate_registry()
    registry_path = DATA_DIR / "tags.registry.json"
    write_registry(registry, registry_path)
    print(f"Tags registry generated successfully at {registry_path}")
    print(f"Total tags: {len(registry['tags'])}")


if __name__ == "__main__":
    main()
