from pathlib import Path
from dataclasses import dataclass, field
from typing import TypedDict, NotRequired
from collections import Counter

# Path constants
TAGS_CONFIG_DIR = Path("data/tags")
GENERATED_DATA_DIR = Path(".data/tags")
CONTENT_DIR = Path("content")

# File names
MAPPING_FILE = "mapping.json"
COLORS_FILE = "colors.yaml"
STATS_FILE = "cleanup-stats.json"
VALIDATION_FILE = "validation-report.txt"


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
