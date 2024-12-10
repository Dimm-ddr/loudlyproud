#!/usr/bin/env python3

from pathlib import Path
import sys
from dataclasses import dataclass, field
from typing import TypedDict, NotRequired
from collections import Counter
from ruamel.yaml import YAML
import json
from .normalize import TagNormalizer
from .validate import validate_tags

# Path constants
TAGS_CONFIG_DIR = Path("data/tags")
GENERATED_DATA_DIR = Path(".data/tags")
CONTENT_DIR = Path("content")

# File names
MAPPING_FILE = "mapping.json"
COLORS_FILE = "colors.yaml"
STATS_FILE = "cleanup-stats.json"


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

    def to_dict(self) -> StatsDict:
        """Convert stats to dictionary for JSON output."""
        return {
            "total_files": self.total_files,
            "files_with_changes": self.files_with_changes,
            "unknown_tags": sorted(self.unknown_tags),
            "normalized_tags": dict(sorted(self.normalized_tags.items())),
        }


def load_tags_map(project_root: Path) -> dict[str, TagMapping]:
    """Load tags mapping from JSON file."""
    tags_file = project_root.joinpath(TAGS_CONFIG_DIR, MAPPING_FILE)
    try:
        return json.loads(tags_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading tags map: {e}")
        sys.exit(1)


def load_color_mapping(project_root: Path) -> set[str]:
    """Load valid tags from color mapping file."""
    color_file = project_root.joinpath(TAGS_CONFIG_DIR, COLORS_FILE)
    try:
        yaml = YAML()
        data = yaml.load(color_file)
        return set(data.get("tag_colors", {}).keys())
    except Exception as e:
        print(f"Error loading color mapping: {e}")
        sys.exit(1)


def split_frontmatter(content: str) -> tuple[dict, str] | None:
    """Split content into frontmatter and body."""
    match content.split("---\n", 2):
        case ["", frontmatter, *rest] if rest:
            try:
                yaml = YAML()
                yaml.preserve_quotes = True
                return yaml.load(frontmatter), rest[0]
            except yaml.YAMLError:
                return None
        case _:
            return None


def normalize_tags(tags: list[str], normalizer: TagNormalizer) -> list[str]:
    """Normalize a list of tags using the normalizer."""
    return normalizer.normalize_tags(tags)


def process_book_file(
    file_path: Path,
    tags_map: dict[str, TagMapping],
    normalizer: TagNormalizer,
    stats: TagStats,
) -> bool:
    """Process a single book file, updating tags if necessary."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if not (result := split_frontmatter(content)):
            return False

        frontmatter, body = result
        if not (tags := frontmatter.get("params", {}).get("tags")):
            return False

        normalized_tags = normalize_tags(tags, normalizer)

        # Update stats
        for tag in normalized_tags:
            stats.normalized_tags[tag] += 1
            if tag.lower() not in tags_map:
                stats.unknown_tags.add(tag)

        # Update file if tags changed
        if set(tags) != set(normalized_tags):
            frontmatter["params"]["tags"] = normalized_tags

            yaml = YAML()
            yaml.preserve_quotes = True
            yaml.width = 4096
            yaml.indent(mapping=2, sequence=4, offset=2)

            with file_path.open("w", encoding="utf-8") as f:
                f.write("---\n")
                yaml.dump(frontmatter, f)
                f.write("---")
                if body:
                    f.write(body)

            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def process_books(
    content_dir: Path, tags_map: dict[str, TagMapping], normalizer: TagNormalizer
) -> TagStats:
    """Process all book files in the content directory."""
    stats = TagStats()

    for locale_dir in content_dir.iterdir():
        if not locale_dir.is_dir():
            continue

        books_dir = locale_dir / "books"
        if not books_dir.exists():
            continue

        for book_file in books_dir.glob("*.md"):
            stats.total_files += 1
            if process_book_file(book_file, tags_map, normalizer, stats):
                stats.files_with_changes += 1
                print(f"Updated tags in: {book_file.relative_to(content_dir)}")

    return stats


def main() -> None:
    """Main function for tag cleanup."""
    project_root = Path.cwd()
    content_dir = project_root.joinpath(CONTENT_DIR)
    stats_file = project_root.joinpath(GENERATED_DATA_DIR, STATS_FILE)

    tags_map = load_tags_map(project_root)
    valid_colors = load_color_mapping(project_root)
    normalizer = TagNormalizer()

    # Validate before cleanup
    validation = validate_tags(project_root)
    if validation["uncolored_tags"]:
        print("\nWarning: Some tags are missing color definitions:")
        for tag in validation["uncolored_tags"]:
            print(f"  - {tag}")
        if input("\nContinue with cleanup? [y/N] ").lower() != "y":
            sys.exit(1)

    print("\nProcessing book files...")
    stats = process_books(content_dir, tags_map, normalizer)

    # Print and save report
    print(f"\nProcessed {stats.total_files} files")
    print(f"Updated tags in {stats.files_with_changes} files")

    if stats.unknown_tags:
        print(f"\nFound {len(stats.unknown_tags)} unknown tags:")
        for tag in sorted(stats.unknown_tags):
            print(f"  - {tag}")

    if stats.normalized_tags:
        print("\nTag usage statistics:")
        for tag, count in stats.normalized_tags.most_common():
            print(f"  {tag}: {count}")

    # Save statistics
    stats_file.parent.mkdir(parents=True, exist_ok=True)
    with stats_file.open("w", encoding="utf-8") as f:
        json.dump(stats.to_dict(), f, indent=2, ensure_ascii=False)

    print(f"\nTag statistics saved to {stats_file}")


if __name__ == "__main__":
    main()
