import os
import yaml
import json
from pathlib import Path
from dataclasses import dataclass
from tags_map import tags_normalization_map


@dataclass
class TagStats:
    total_files: int = 0
    files_with_changes: int = 0
    unknown_tags: set[str] = None
    normalized_tags: dict[str, int] = None

    def __post_init__(self) -> None:
        if self.unknown_tags is None:
            self.unknown_tags = set()
        if self.normalized_tags is None:
            self.normalized_tags = {}


def split_frontmatter(content: str) -> tuple[dict, str] | None:
    """Split content into frontmatter and body."""
    if content.startswith("---\n"):
        parts: list[str] = content.split("---\n", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                return frontmatter, "---\n".join([""] + parts[2:])
            except yaml.YAMLError:
                return None
    return None


def normalize_tag(tag: str) -> list[str] | None:
    """Normalize a single tag using the mapping."""
    normalized: str | list[str] | None = tags_normalization_map.get(tag.lower())
    if normalized is None:
        return [tag]  # Keep original if not in mapping
    if isinstance(normalized, str):
        return [normalized]
    return normalized  # Already a list


def normalize_tags(tags: list[str]) -> list[str]:
    """Normalize a list of tags, removing duplicates and None values."""
    if not tags:
        return []

    normalized: list = []
    for tag in tags:
        result: list[str] | None = normalize_tag(tag)
        if result:
            normalized.extend(result)

    return sorted(list(set(normalized)))


def process_book_file(file_path: Path, stats: TagStats) -> bool:
    """Process a single book file, updating tags if necessary."""
    content: str = file_path.read_text(encoding="utf-8")
    result: tuple[dict, str] | None = split_frontmatter(content)

    if not result:
        return False

    frontmatter, body = result
    if "params" not in frontmatter or "tags" not in frontmatter["params"]:
        return False

    original_tags = frontmatter["params"]["tags"]
    if not original_tags:
        return False

    # Normalize tags
    normalized_tags: list[str] = normalize_tags(original_tags)

    # Update stats
    for tag in normalized_tags:
        stats.normalized_tags[tag] = stats.normalized_tags.get(tag, 0) + 1
        if tag.lower() not in tags_normalization_map:
            stats.unknown_tags.add(tag)

    # Check if tags changed
    if set(original_tags) != set(normalized_tags):
        frontmatter["params"]["tags"] = normalized_tags
        new_content: str = f"---\n{yaml.dump(frontmatter, allow_unicode=True)}---{body}"
        file_path.write_text(new_content, encoding="utf-8")
        return True

    return False


def generate_tag_colors(stats: TagStats, output_file: Path):
    """Generate CSS for tags that don't have styles."""
    existing_colors = set()
    try:
        if output_file.exists():
            content: str = output_file.read_text(encoding="utf-8")
            # Extract existing tag names using simple regex
            import re

            existing_colors = set(re.findall(r"\.tag-([\w-]+)\s*{", content))
    except Exception as e:
        print(f"Error reading existing tag colors: {e}")
        existing_colors = set()

    # Generate CSS for new tags
    new_css: list = []
    for tag in sorted(stats.normalized_tags.keys()):
        tag_class: str = tag.lower().replace(" ", "-").replace("(", "").replace(")", "")
        if tag_class not in existing_colors:
            new_css.append(
                f"""
.tag-{tag_class} {{
    background-color: #e5e5e5;  /* Default gray background */
    color: #374151;            /* Default text color */
}}"""
            )

    if new_css:
        # Append new styles to the file
        with output_file.open("a", encoding="utf-8") as f:
            f.write("\n/* New tags added */\n")
            f.write("\n".join(new_css))


def process_books(content_dir: Path) -> TagStats:
    """Process all book files in the content directory."""
    stats = TagStats()

    for locale_dir in content_dir.iterdir():
        if not locale_dir.is_dir():
            continue

        for book_file in locale_dir.rglob("*.md"):
            stats.total_files += 1
            if process_book_file(book_file, stats):
                stats.files_with_changes += 1

    return stats


def main() -> None:
    # Paths
    project_root: Path = Path.cwd()
    content_dir: Path = project_root / "content" / "books"
    tag_colors_file: Path = project_root / "assets" / "css" / "tag-colors.css"
    stats_file: Path = project_root / "tag-stats.json"

    # Process books
    print("Processing book files...")
    stats: TagStats = process_books(content_dir)

    # Generate report
    print(f"\nProcessed {stats.total_files} files")
    print(f"Updated tags in {stats.files_with_changes} files")
    print(f"\nFound {len(stats.unknown_tags)} unknown tags:")
    for tag in sorted(stats.unknown_tags):
        print(f"  - {tag}")

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
    with stats_file.open("w", encoding="utf-8") as f:
        json.dump(stats_dict, f, indent=2, ensure_ascii=False)

    # Generate CSS for new tags
    generate_tag_colors(stats, tag_colors_file)
    print(f"\nTag statistics saved to {stats_file}")
    print(f"New tag styles added to {tag_colors_file}")


if __name__ == "__main__":
    main()
