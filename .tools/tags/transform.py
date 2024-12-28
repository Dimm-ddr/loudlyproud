"""Tag name transformation utilities."""


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
