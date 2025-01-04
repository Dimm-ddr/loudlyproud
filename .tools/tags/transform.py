"""Tag name transformation utilities."""

from .file_ops import load_tags_map, load_special_display_names
from .common import MAPPING_FILE, SPECIAL_DISPLAY_NAMES_FILE


def get_internal_name(tag: str) -> str:
    """
    Convert a display tag to its internal name format.

    Args:
        tag: The display tag to convert

    Returns:
        The internal name format of the tag
    """
    # Convert to lowercase
    internal = tag.lower()

    # Remove parenthetical suffixes like (YA), (NA), (BL)
    if "(" in internal:
        internal = internal.split("(")[0].strip()

    # Replace special characters
    internal = internal.replace("'", "")  # Remove apostrophes
    internal = internal.replace(".", "")  # Remove dots
    internal = internal.replace(" ", "-")  # Replace spaces with hyphens

    # Clean up multiple hyphens
    while "--" in internal:
        internal = internal.replace("--", "-")

    # Remove leading/trailing hyphens
    internal = internal.strip("-")

    return internal


def get_display_name(tag: str, mapping_file: str = MAPPING_FILE) -> str:
    """
    Convert an internal tag name to its display form using mapping and special display names.

    Args:
        tag: The internal tag name to convert
        mapping_file: Path to the mapping file

    Returns:
        The display form of the tag
    """
    # Load mapping and special display names
    mapping = load_tags_map(mapping_file)
    special_display_names = load_special_display_names(SPECIAL_DISPLAY_NAMES_FILE)

    # First check special display names
    for internal, display in special_display_names.items():
        if tag == internal:
            return display

    # Then check mapping values
    # Create a mapping of internal names to their display forms
    display_forms = {}
    for value in mapping.values():
        if value is not None:
            if isinstance(value, str):
                display_forms[get_internal_name(value)] = value
            elif isinstance(value, list):
                for v in value:
                    display_forms[get_internal_name(v)] = v

    # Return the display form if found
    if tag in display_forms:
        return display_forms[tag]

    # If no display name found, return the original tag
    return tag
