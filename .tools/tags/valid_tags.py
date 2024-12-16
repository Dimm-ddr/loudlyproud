from pathlib import Path

from .file_ops import load_tags_map


def build_valid_tags(mapping: dict) -> set[str]:
    """Build set of valid tags from mapping values."""
    valid_tags = set()
    for value in mapping.values():
        if value is not None:
            if isinstance(value, str):
                valid_tags.add(value.lower())
            elif isinstance(value, list):
                valid_tags.update(tag.lower() for tag in value)
    return valid_tags


def get_valid_tags(mapping_file: Path) -> set[str]:
    """Load mapping file and extract valid tags."""
    mapping = load_tags_map(mapping_file)
    return build_valid_tags(mapping)
