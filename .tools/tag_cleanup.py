#!/usr/bin/env python3

from pathlib import Path
from dataclasses import dataclass, field
from typing import TypedDict, NotRequired
from collections import Counter
from ruamel.yaml import YAML
import json
import sys


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
    tags_file = project_root / ".data" / "tags_map.json"
    try:
        return json.loads(tags_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading tags map: {e}")
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


def normalize_tag(tag: str, tags_map: dict[str, TagMapping]) -> list[str]:
    """Normalize a single tag using the mapping."""
    match tags_map.get(tag.lower()):
        case None:
            return [tag]  # Keep original if not in mapping
        case [*tags]:  # List of replacement tags
            return tags
        case str() as normalized:  # Single replacement tag
            return [normalized]
        case None if tag.lower() in tags_map:  # Explicit removal
            return []
        case _:  # Unexpected mapping value
            return [tag]


def normalize_tags(tags: list[str], tags_map: dict[str, TagMapping]) -> list[str]:
    """Normalize a list of tags, handling all mapping cases."""
    if not tags:
        return []

    normalized = [new_tag for tag in tags for new_tag in normalize_tag(tag, tags_map)]
    return sorted(set(normalized))


def process_book_file(
    file_path: Path, tags_map: dict[str, TagMapping], stats: TagStats
) -> bool:
    """Process a single book file, updating tags if necessary."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if not (result := split_frontmatter(content)):
            return False

        frontmatter, body = result
        if not (tags := frontmatter.get("params", {}).get("tags")):
            return False

        normalized_tags = normalize_tags(tags, tags_map)

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


def process_books(content_dir: Path, tags_map: dict[str, TagMapping]) -> TagStats:
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
            if process_book_file(book_file, tags_map, stats):
                stats.files_with_changes += 1
                print(f"Updated tags in: {book_file.relative_to(content_dir)}")

    return stats


def main() -> None:
    project_root = Path.cwd()
    content_dir = project_root / "content"
    stats_file = project_root / ".data" / "tag-cleanup-stats.json"

    tags_map = load_tags_map(project_root)
    print("\nProcessing book files...")
    stats = process_books(content_dir, tags_map)

    # Print report
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
    stats_file.parent.mkdir(exist_ok=True)
    with stats_file.open("w", encoding="utf-8") as f:
        json.dump(stats.to_dict(), f, indent=2, ensure_ascii=False)

    print(f"\nTag statistics saved to {stats_file}")


if __name__ == "__main__":
    main()
