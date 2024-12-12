#!/usr/bin/env python3

from pathlib import Path
import sys
from ruamel.yaml import YAML
import json
from .normalize import TagNormalizer
from .validate import validate_tags
from .common import (
    TAGS_CONFIG_DIR,
    GENERATED_DATA_DIR,
    CONTENT_DIR,
    MAPPING_FILE,
    COLORS_FILE,
    STATS_FILE,
    TagStats,
)

# Re-export TagStats for backward compatibility
__all__ = ['TagStats', 'process_book_file', 'normalize_tags']

def split_frontmatter(content: str) -> tuple[dict, str] | None:
    """Split content into frontmatter and body."""
    try:
        # Normalize line endings
        content = content.replace('\r\n', '\n')

        # Try to split on frontmatter delimiters
        parts = content.split("---\n", 2)
        print(f"Split parts: {len(parts)}")  # Debug

        if len(parts) < 3:
            # Try alternative delimiter format
            parts = content.split("---", 2)
            print(f"Trying alternative split: {len(parts)}")  # Debug

        match parts:
            case ["", frontmatter, *rest] if rest:
                try:
                    yaml = YAML()
                    yaml.preserve_quotes = True
                    data = yaml.load(frontmatter)
                    if not isinstance(data, dict):
                        print(f"Frontmatter is not a dictionary: {type(data)}")  # Debug
                        return None
                    return data, rest[0]
                except Exception as e:
                    print(f"YAML parsing error: {str(e)}")  # Debug
                    print(f"Frontmatter content:\n{frontmatter}")  # Debug
                    return None
            case _:
                print(f"Invalid frontmatter format. Parts: {[p[:50] + '...' if len(p) > 50 else p for p in parts]}")  # Debug
                return None
    except Exception as e:
        print(f"Unexpected error in split_frontmatter: {str(e)}")  # Debug
        return None

def process_book_file(
    file_path: Path,
    normalizer: TagNormalizer,
) -> bool:
    """Process a single book file, updating tags if necessary."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if not (result := split_frontmatter(content)):
            print(f"Failed to parse frontmatter in {file_path}")  # Debug
            return False

        frontmatter, body = result
        if not (tags := frontmatter.get("params", {}).get("tags")):
            print(f"No tags found in {file_path}")  # Debug
            return False

        print(f"\nProcessing {file_path}")  # Debug
        print(f"Original tags: {tags}")  # Debug
        normalized_tags = normalizer.normalize_tags(tags)
        print(f"Normalized tags: {normalized_tags}")  # Debug

        # Update file if tags changed
        original_set = {t.lower() for t in tags}
        normalized_set = {t.lower() for t in normalized_tags}

        if original_set != normalized_set:
            print(f"Tags changed, updating file")  # Debug
            print(f"Original set: {original_set}")  # Debug
            print(f"Normalized set: {normalized_set}")  # Debug
            frontmatter["params"]["tags"] = normalized_tags

            yaml = YAML()
            yaml.preserve_quotes = True
            yaml.width = 4096
            yaml.indent(mapping=2, sequence=4, offset=2)

            with file_path.open("w", encoding="utf-8") as f:
                f.write("---\n")  # Opening delimiter
                yaml.dump(frontmatter, f)
                f.write("---\n")  # Closing delimiter with newline
                if body:
                    f.write(body)  # Body already includes leading newline from split
                else:
                    f.write("\n")  # Ensure there's always a final newline

            return True
        else:
            print(f"No changes needed for {file_path}")  # Debug
            print(f"Original set: {original_set}")  # Debug
            print(f"Normalized set: {normalized_set}")  # Debug
            return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def process_books(content_dir: Path, normalizer: TagNormalizer) -> None:
    """Process all book files in the content directory."""
    for locale_dir in content_dir.iterdir():
        if not locale_dir.is_dir():
            continue

        books_dir = locale_dir / "books"
        if not books_dir.exists():
            continue

        for book_file in books_dir.glob("*.md"):
            normalizer.stats.total_files += 1
            if process_book_file(book_file, normalizer):
                normalizer.stats.files_with_changes += 1
                print(f"Updated tags in: {book_file.relative_to(content_dir)}")

def main() -> None:
    """Main function for tag cleanup."""
    project_root = Path.cwd()
    content_dir = project_root.joinpath(CONTENT_DIR)
    stats_file = project_root.joinpath(GENERATED_DATA_DIR, STATS_FILE)

    # Validate before cleanup
    validation = validate_tags(project_root)
    if validation["uncolored_tags"]:
        print("\nWarning: Some tags are missing color definitions:")
        for tag in validation["uncolored_tags"]:
            print(f"  - {tag}")
        if input("\nContinue with cleanup? [y/N] ").lower() != "y":
            sys.exit(1)

    print("\nProcessing book files...")
    normalizer = TagNormalizer(project_root)
    process_books(content_dir, normalizer)

    # Print and save report
    print(f"\nProcessed {normalizer.stats.total_files} files")
    print(f"Updated tags in {normalizer.stats.files_with_changes} files")

    if normalizer.stats.unknown_tags:
        print(f"\nFound {len(normalizer.stats.unknown_tags)} unknown tags:")
        for tag in sorted(normalizer.stats.unknown_tags):
            print(f"  - {tag}")

    if normalizer.stats.normalized_tags:
        print("\nTag usage statistics:")
        for tag, count in normalizer.stats.normalized_tags.most_common():
            print(f"  {tag}: {count}")

    # Save statistics
    stats_file.parent.mkdir(parents=True, exist_ok=True)
    with stats_file.open("w", encoding="utf-8") as f:
        json.dump(normalizer.stats.to_dict(), f, indent=2, ensure_ascii=False)

    print(f"\nTag statistics saved to {stats_file}")

if __name__ == "__main__":
    main()
