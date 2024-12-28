"""Common constants and utilities."""

from pathlib import Path
from collections import Counter, defaultdict


class TagStats:
    """Statistics for tag normalization."""

    def __init__(self) -> None:
        """Initialize tag statistics."""
        self.total_files = 0
        self.files_with_changes = 0
        self.unknown_tags = set()
        self.normalized_tags = Counter()


# Directory paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
CONTENT_DIR = Path(__file__).parent.parent.parent / "content"
TAGS_DIR = DATA_DIR / "tags"
GENERATED_DATA_DIR = Path(__file__).parent.parent.parent / ".data"

# File paths
MAPPING_FILE = TAGS_DIR / "mapping.json"
COLORS_FILE = TAGS_DIR / "colors.toml"
PATTERNS_FILE = TAGS_DIR / "patterns.toml"
TO_REMOVE_FILE = TAGS_DIR / "to_remove.toml"
SPECIAL_DISPLAY_NAMES_FILE = TAGS_DIR / "special_display_names.json"
VALIDATION_FILE = "tags.validation.txt"
