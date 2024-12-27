#!/usr/bin/env python3

from pathlib import Path
from typing import TypedDict
from .common import (
    GENERATED_DATA_DIR,
    CONTENT_DIR,
    VALIDATION_FILE,
    MAPPING_FILE,
    COLORS_FILE,
    TO_REMOVE_FILE,
    PATTERNS_FILENAME,
)
from .sorting import sort_strings
from .file_ops import (
    load_color_mapping,
    extract_tags_from_file,
    load_removable_tags,
)
from .normalize import TagNormalizer


class ValidationReport(TypedDict):
    unmapped_tags: list[str]  # Tags not in mapping keys
    uncolored_tags: list[str]  # Tags not in colors (checking mapped values)


def get_mapped_values(tags_map: dict) -> set[str]:
    """Get all normalized tag values from mapping."""
    values = set()
    for mapping in tags_map.values():
        if mapping is None:
            continue
        if isinstance(mapping, str):
            values.add(mapping.lower())
        elif isinstance(mapping, list):
            values.update(tag.lower() for tag in mapping)
    return values


def validate_tags(
    project_root: Path,
    content_path: Path = CONTENT_DIR,
    mapping_file: Path = MAPPING_FILE,
    colors_file: Path = COLORS_FILE,
    to_remove_file: Path = TO_REMOVE_FILE,
) -> dict[str, list[str]]:
    """
    Validate tags in book files against mapping and colors.

    Args:
        project_root: Root path of the project containing data files
        content_path: Path to content directory to check
        mapping_file: Path to mapping file
        colors_file: Path to colors file
        to_remove_file: Path to to_remove file
    """
    # Initialize normalizer with the provided files
    normalizer = TagNormalizer(
        project_root=project_root,
        mapping_file=mapping_file,
        patterns_file=project_root / "data/tags" / PATTERNS_FILENAME,
        to_remove_file=to_remove_file,
    )

    # Load removable tags (already lowercase from file)
    removable_tags = load_removable_tags(to_remove_file)

    # Load colors as a set of lowercase tags for case-insensitive comparison
    colored_tags = set()
    try:
        colors = load_color_mapping(colors_file)
        if isinstance(colors, dict):
            # If it's a dict, collect all tag names
            for category in colors.values():
                if isinstance(category, dict):
                    colored_tags.update(tag.lower() for tag in category.keys())
        else:
            # If it's already a set, convert to lowercase
            colored_tags = {tag.lower() for tag in colors}
    except Exception as e:
        print(f"Error loading TOML color mapping: {e}")

    # Get all book files
    book_files = content_path.glob("**/books/*.md")

    # Extract and normalize all tags from books
    all_tags = set()
    for book_file in book_files:
        tags = extract_tags_from_file(book_file)
        # Normalize tags and filter out None values
        normalized_tags = normalizer.normalize_tags(tags)
        all_tags.update(normalized_tags)

    # Find unmapped and uncolored tags
    unmapped_tags = []
    uncolored_tags_set = set()

    # Check each tag
    for tag in sorted(all_tags):
        tag_lower = tag.lower()
        # Skip tags that should be removed
        if tag_lower in removable_tags:
            continue
        # Check if the tag is mapped by trying to normalize it
        normalized = normalizer.normalize(tag)
        if normalized is None or (
            isinstance(normalized, str)
            and normalized.lower() not in normalizer.valid_tags
        ):
            unmapped_tags.append(tag_lower)  # Store lowercase version for consistency
        # Check for uncolored tags only if they are in valid_tags
        elif tag_lower not in colored_tags:
            uncolored_tags_set.add(tag)

    return {
        "unmapped_tags": sort_strings(unmapped_tags),
        "uncolored_tags": sorted(uncolored_tags_set),
    }


def write_report(report: ValidationReport, project_root: Path) -> None:
    """Write validation report to file and print summary."""
    # Print summary
    print(f"\nValidation Summary:")
    print(f"Tags not in mapping keys: {len(report['unmapped_tags'])}")
    print(f"Tags without colors (values and unmapped): {len(report['uncolored_tags'])}")

    # Save detailed report
    data_dir = project_root.joinpath(GENERATED_DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    report_file = data_dir.joinpath(VALIDATION_FILE)

    output = [
        "Tags not in mapping keys:",
        "=" * 23,
        *[f"- {tag}" for tag in sort_strings(report["unmapped_tags"])],
        "",
        "Tags without colors (values and unmapped):",
        "=" * 37,
        *[f"- {tag}" for tag in sort_strings(report["uncolored_tags"])],
    ]

    with open(report_file, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(output))
    print(f"\nDetailed report saved to {report_file}")


def main() -> None:
    """Main function for tag validation."""
    project_root = Path.cwd()
    content_path = project_root / "content"
    report = validate_tags(project_root, content_path=content_path)
    write_report(report, project_root)


if __name__ == "__main__":
    main()
