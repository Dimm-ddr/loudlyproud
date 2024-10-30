#!/usr/bin/env python3

import sys
import json
import yaml
from pathlib import Path
from dataclasses import dataclass


@dataclass
class TagStats:
    total_files: int = 0
    files_with_changes: int = 0
    unknown_tags: set = None
    normalized_tags: dict = None

    def __post_init__(self):
        if self.unknown_tags is None:
            self.unknown_tags = set()
        if self.normalized_tags is None:
            self.normalized_tags = {}


def load_tags_map() -> dict:
    """Load tags mapping from JSON file."""
    project_root = Path.cwd()
    tags_file = project_root / ".data" / "tags_map.json"
    try:
        return json.loads(tags_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading tags map: {e}")
        sys.exit(1)


def split_frontmatter(content: str) -> tuple[dict, str] | None:
    """Split content into frontmatter and body."""
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                return frontmatter, "---\n".join([""] + parts[2:])
            except yaml.YAMLError:
                return None
    return None


def normalize_tag(tag: str, tags_map: dict) -> list:
    """
    Normalize a single tag using the mapping.
    Returns a list of tags or empty list if tag should be removed.
    The mapping handles both normalization and capitalization.
    """
    # Use the lowercase version as key, but default to original tag
    # if not found in the mapping
    mapped_value = tags_map.get(tag.lower(), tag)

    # Handle different mapping cases
    if mapped_value is None:
        return []  # Tag should be removed
    elif isinstance(mapped_value, list):
        return mapped_value  # Multiple tags
    elif isinstance(mapped_value, str):
        return [mapped_value]  # Single tag
    else:
        return [tag]  # This shouldn't happen with proper JSON


def normalize_tags(tags: list, tags_map: dict) -> list:
    """Normalize a list of tags, handling all mapping cases."""
    if not tags:
        return []

    normalized = []
    for tag in tags:
        normalized.extend(normalize_tag(tag, tags_map))

    return sorted(list(set(normalized)))  # Remove duplicates and sort


def process_book_file(file_path: Path, tags_map: dict, stats: TagStats) -> bool:
    """Process a single book file, updating tags if necessary."""
    content = file_path.read_text(encoding="utf-8")
    result = split_frontmatter(content)

    if not result:
        return False

    frontmatter, body = result
    if "params" not in frontmatter or "tags" not in frontmatter["params"]:
        return False

    original_tags = frontmatter["params"]["tags"]
    if not original_tags:
        return False

    # Normalize tags
    normalized_tags = normalize_tags(original_tags, tags_map)

    # Update stats
    for tag in normalized_tags:
        stats.normalized_tags[tag] = stats.normalized_tags.get(tag, 0) + 1
        if tag.lower() not in tags_map:
            stats.unknown_tags.add(tag)

    # Check if tags changed
    if set(original_tags) != set(normalized_tags):
        frontmatter["params"]["tags"] = normalized_tags
        new_content = f"---\n{yaml.dump(frontmatter, allow_unicode=True)}---{body}"
        file_path.write_text(new_content, encoding="utf-8")
        return True

    return False


def process_books(content_dir: Path, tags_map: dict) -> TagStats:
    """Process all book files in the content directory."""
    stats = TagStats()

    for locale_dir in content_dir.iterdir():
        if not locale_dir.is_dir():
            continue

        for book_file in locale_dir.rglob("*.md"):
            stats.total_files += 1
            if process_book_file(book_file, tags_map, stats):
                stats.files_with_changes += 1
                print(f"Updated tags in: {book_file.relative_to(content_dir)}")

    return stats


def main():
    # Paths
    project_root = Path.cwd()
    content_dir = project_root / "content" / "books"
    stats_file = project_root / ".data" / "tag-cleanup-stats.json"

    # Load tags map
    tags_map = load_tags_map()

    # Process books
    print("\nProcessing book files...")
    stats = process_books(content_dir, tags_map)

    # Generate report
    print(f"\nProcessed {stats.total_files} files")
    print(f"Updated tags in {stats.files_with_changes} files")

    if stats.unknown_tags:
        print(f"\nFound {len(stats.unknown_tags)} unknown tags:")
        for tag in sorted(stats.unknown_tags):
            print(f"  - {tag}")

    if stats.normalized_tags:
        print("\nTag usage statistics:")
        for tag, count in sorted(
            stats.normalized_tags.items(), key=lambda x: (-x[1], x[0])
        ):
            print(f"  {tag}: {count}")

    # Save statistics to file
    stats_dict = {
        "total_files": stats.total_files,
        "files_with_changes": stats.files_with_changes,
        "unknown_tags": sorted(list(stats.unknown_tags)),
        "normalized_tags": dict(sorted(stats.normalized_tags.items())),
    }

    # Ensure .data directory exists
    stats_file.parent.mkdir(exist_ok=True)

    with stats_file.open("w", encoding="utf-8") as f:
        json.dump(stats_dict, f, indent=2, ensure_ascii=False)

    print(f"\nTag statistics saved to {stats_file}")


if __name__ == "__main__":
    main()
