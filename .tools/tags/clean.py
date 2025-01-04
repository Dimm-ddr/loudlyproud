#!/usr/bin/env python3

from pathlib import Path
from collections import defaultdict

from .file_ops import (
    load_patterns,
    load_tags_map,
    load_colors_file,
    extract_tags_from_file,
    split_frontmatter,
    write_frontmatter,
    load_special_display_names,
)
from .valid_tags import get_valid_tags
from .transform import get_internal_name, get_display_name
from .common import (
    MAPPING_FILE,
    PATTERNS_FILE,
    TO_REMOVE_FILE,
    SPECIAL_DISPLAY_NAMES_FILE,
)


def get_removable_mapping_keys(
    mapping_file: Path, patterns_file: Path
) -> dict[str, list[str]]:
    """
    Find mapping keys that could be removed, grouped by pattern category.
    Returns a dict where keys are pattern categories and values are lists of removable tags.
    """
    # Load files
    mapping = load_tags_map(mapping_file)
    patterns = load_patterns(patterns_file)
    valid_tags = get_valid_tags(mapping_file)

    # Initialize categories
    removable = defaultdict(list)

    for key in mapping:
        key_lower = key.lower()
        # Skip if key maps to a valid tag
        if key_lower in valid_tags:
            continue

        # Check prefixes
        matched = False
        for prefix in patterns.get("remove", {}).get("prefixes", []):
            if key_lower.startswith(prefix.lower()):
                removable["prefixes"].append(key)
                matched = True
                break

        if not matched:
            # Check exact matches
            for exact in patterns.get("remove", {}).get("exact", []):
                if key_lower == exact.lower():
                    removable["exact matches"].append(key)
                    break

    # Sort lists within each category
    return {k: sorted(v) for k, v in removable.items()}


def get_removable_color_tags(
    colors_file: Path, mapping_file: Path
) -> dict[str, list[str]]:
    """
    Find color tags that are not in valid tags list, grouped by color category.
    Returns a dict where keys are color categories and values are lists of removable tags.
    """
    # Load files
    colors = load_colors_file(colors_file)
    valid_tags = get_valid_tags(mapping_file)
    special_display_names = load_special_display_names(SPECIAL_DISPLAY_NAMES_FILE)
    display_to_internal = {v: k for k, v in special_display_names.items()}

    # Find removable tags by category
    removable = defaultdict(list)

    for category, tags in colors.items():
        for tag in tags:
            # Get internal name for the tag
            if tag in display_to_internal:
                internal = display_to_internal[tag]
            else:
                internal = get_internal_name(tag)

            # Check if internal form exists in valid tags
            if internal not in valid_tags:
                removable[category].append(tag)

    # Sort lists within each category
    return {k: sorted(v) for k, v in removable.items()}


def clean_frontmatter(
    content_dir: Path,
    normalizer,
    mapping_file: Path = MAPPING_FILE,
    patterns_file: Path = PATTERNS_FILE,
    to_remove_file: Path = TO_REMOVE_FILE,
) -> None:
    """Clean up tags in book files."""
    total_files = 0
    changed_files = 0

    for locale_dir in content_dir.iterdir():
        if not locale_dir.is_dir():
            continue

        books_dir = locale_dir / "books"
        if not books_dir.exists():
            continue

        for book_file in books_dir.glob("*.md"):
            total_files += 1
            changed, original_tags = process_book_file(book_file, normalizer)
            if changed:
                changed_files += 1
                print(f"Updated tags in: {book_file.relative_to(content_dir)}")

    if changed_files == 0:
        print("\nNo changes were needed in any files.")
    else:
        print(f"\nUpdated {changed_files} out of {total_files} files.")


def process_book_file(
    file_path: Path,
    normalizer,
    mapping_file: Path = MAPPING_FILE,
    patterns_file: Path = PATTERNS_FILE,
    to_remove_file: Path = TO_REMOVE_FILE,
) -> tuple[bool, list[str]]:
    """Process a single book file, extracting and normalizing tags."""
    try:
        tags = extract_tags_from_file(file_path)
        if not tags:
            return False, []

        normalized_tags = normalizer.normalize_tags(tags)
        if not normalized_tags:  # Handle case where all tags were removed
            return False, []

        # Filter out any None values that might have slipped through
        normalized_tags = [t for t in normalized_tags if t is not None]
        if not normalized_tags:  # Check again after filtering
            return False, []

        # Convert normalized tags to their display form
        display_tags = [get_display_name(tag, mapping_file) for tag in normalized_tags]

        original_set = {t.lower() for t in tags if t is not None}
        normalized_set = {t.lower() for t in normalized_tags if t is not None}

        if original_set != normalized_set:
            content = file_path.read_text(encoding="utf-8")
            if not (result := split_frontmatter(content)):
                print(f"Failed to parse frontmatter in {file_path}")
                return False, []

            frontmatter, body = result
            frontmatter["params"]["tags"] = display_tags
            if write_frontmatter(file_path, frontmatter, body):
                return True, tags
            return False, tags
        return False, tags
    except Exception as e:
        import traceback

        print(f"\nError processing {file_path}:")
        print(f"Original error: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        return False, []


def print_removable_tags(tag_dict: dict[str, list[str]], title: str) -> None:
    """Print removable tags in a formatted way."""
    print(f"\n{title}:")
    if not tag_dict:
        print("  No removable tags found")
        return

    for category, tags in tag_dict.items():
        print(f"\n{category}:")
        for tag in tags:
            print(f"  - {tag}")
