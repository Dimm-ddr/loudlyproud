from pathlib import Path

from .file_ops import load_tags_map, load_special_display_names
from .transform import get_internal_name
from .common import SPECIAL_DISPLAY_NAMES_FILE


def build_valid_tags(mapping: dict) -> set[str]:
    """Build set of valid tags from mapping values only."""
    valid_tags = set()
    special_display_names = load_special_display_names(SPECIAL_DISPLAY_NAMES_FILE)
    display_to_internal = {v: k for k, v in special_display_names.items()}

    # Add all mapping values as valid tags
    for value in mapping.values():
        if value is not None:
            if isinstance(value, str):
                if value in display_to_internal:
                    valid_tags.add(display_to_internal[value])
                else:
                    valid_tags.add(get_internal_name(value))
            elif isinstance(value, list):
                for tag in value:
                    if tag in display_to_internal:
                        valid_tags.add(display_to_internal[tag])
                    else:
                        valid_tags.add(get_internal_name(tag))
    return valid_tags


def get_valid_tags(mapping_file: Path) -> set[str]:
    """Load mapping file and extract valid tags."""
    mapping = load_tags_map(mapping_file)
    return build_valid_tags(mapping)
