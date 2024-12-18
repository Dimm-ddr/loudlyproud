from pathlib import Path
from dataclasses import dataclass, field
from typing import TypedDict, NotRequired
from collections import Counter

# Base paths
PROJECT_ROOT = Path.cwd()
CONTENT_DIR = PROJECT_ROOT / "content"
DATA_DIR = PROJECT_ROOT / "data/tags"
GENERATED_DATA_DIR = PROJECT_ROOT / ".data/tags"

# File names
MAPPING_FILENAME = "mapping.json"
COLORS_FILENAME = "colors.toml"
PATTERNS_FILENAME = "patterns.yaml"
TO_REMOVE_FILENAME = "to_remove.toml"
STATS_FILENAME = "cleanup-stats.json"
VALIDATION_FILENAME = "validation-report.txt"

# Config files
MAPPING_FILE = DATA_DIR / MAPPING_FILENAME
COLORS_FILE = DATA_DIR / COLORS_FILENAME
PATTERNS_FILE = DATA_DIR / PATTERNS_FILENAME
TO_REMOVE_FILE = DATA_DIR / TO_REMOVE_FILENAME
STATS_FILE = GENERATED_DATA_DIR / STATS_FILENAME
VALIDATION_FILE = GENERATED_DATA_DIR / VALIDATION_FILENAME


class TagMapping(TypedDict):
    """Type for tag mapping entries."""

    normalized: str | list[str] | None


class StatsDict(TypedDict):
    """Type for statistics output."""

    total_files: int
    files_with_changes: int
    unknown_tags: list[str]
    normalized_tags: dict[str, int]
    tag_mapping_issues: NotRequired[list[str]]


@dataclass
class TagStats:
    """Statistics for tag processing."""

    total_files: int = 0
    files_with_changes: int = 0
    unknown_tags: set[str] = field(default_factory=set)
    normalized_tags: Counter = field(default_factory=Counter)
