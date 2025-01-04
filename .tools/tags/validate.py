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
    PATTERNS_FILE,
    SPECIAL_DISPLAY_NAMES_FILE,
)
from .sorting import sort_strings
from .file_ops import (
    load_tags_map,
    load_colors_file,
    extract_tags_from_file,
    load_removable_tags,
    load_special_display_names,
)
from .normalize import TagNormalizer
from .transform import get_internal_name
from .valid_tags import get_valid_tags


class ValidationReport(TypedDict):
    unmapped_tags: list[str]  # Tags not in mapping keys
    uncolored_tags: list[str]  # Tags not in colors (checking mapped values)


def validate_mapping_against_colors(
    mapping_file: Path = MAPPING_FILE,
    colors_file: Path = COLORS_FILE,
) -> tuple[set[str], set[str]]:
    """
    Validate that all tags in mapping exist in colors and vice versa.

    Args:
        mapping_file: Path to mapping file
        colors_file: Path to colors file

    Returns:
        Tuple of (missing_in_colors, missing_in_mapping) sets
    """
    # Load files
    colors_data = load_colors_file(colors_file)
    special_display_names = load_special_display_names(SPECIAL_DISPLAY_NAMES_FILE)
    display_to_internal = {v: k for k, v in special_display_names.items()}

    # Get valid tags from mapping values
    valid_tags = get_valid_tags(mapping_file)

    # Get all internal names from colors.toml
    colors_internal_names = set()
    for category in colors_data.values():
        for tag in category:
            # Check if tag has a special internal name
            if tag in display_to_internal:
                colors_internal_names.add(display_to_internal[tag])
            else:
                colors_internal_names.add(get_internal_name(tag))

    # Find missing tags
    missing_in_colors = valid_tags - colors_internal_names
    missing_in_mapping = colors_internal_names - valid_tags

    return missing_in_colors, missing_in_mapping


def validate_tags(
    project_root: Path,
    content_path: Path = CONTENT_DIR,
    mapping_file: Path = MAPPING_FILE,
    colors_file: Path = COLORS_FILE,
    patterns_file: Path = PATTERNS_FILE,
    to_remove_file: Path = TO_REMOVE_FILE,
) -> ValidationReport:
    """
    Validate tags in book files against mapping and colors.

    Args:
        project_root: Root path of the project containing data files
        content_path: Path to content directory to check
        mapping_file: Path to mapping file
        colors_file: Path to colors file
        patterns_file: Path to patterns file
        to_remove_file: Path to to_remove file

    Returns:
        ValidationReport containing unmapped and uncolored tags
    """
    # Initialize normalizer with the provided files
    normalizer = TagNormalizer(
        project_root=project_root,
        mapping_file=mapping_file,
        patterns_file=patterns_file,
        to_remove_file=to_remove_file,
    )

    # Load removable tags (already lowercase from file)
    removable_tags = load_removable_tags(to_remove_file)
    special_display_names = load_special_display_names(SPECIAL_DISPLAY_NAMES_FILE)
    display_to_internal = {v: k for k, v in special_display_names.items()}

    # Load colors data and get valid tags
    colors_data = load_colors_file(colors_file)
    valid_tags = get_valid_tags(mapping_file)

    # Get all colored tags
    colored_tags = set()
    for category in colors_data.values():
        for tag in category:
            if tag in display_to_internal:
                colored_tags.add(display_to_internal[tag])
            else:
                colored_tags.add(get_internal_name(tag))

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
        # Check if tag has a special internal name
        if tag in display_to_internal:
            internal = display_to_internal[tag]
        else:
            internal = get_internal_name(tag)

        # Skip tags that should be removed
        if internal in removable_tags:
            continue
        # Check if the tag is mapped
        if internal not in valid_tags:
            unmapped_tags.append(internal)
        # Check for uncolored tags only if they are mapped
        elif internal not in colored_tags:
            uncolored_tags_set.add(tag)

    # Return properly constructed ValidationReport
    return ValidationReport(
        unmapped_tags=sort_strings(unmapped_tags),
        uncolored_tags=sorted(uncolored_tags_set),
    )


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

    # First validate mapping against colors
    missing_in_colors, missing_in_mapping = validate_mapping_against_colors()

    # Create validation report
    report = validate_tags(project_root, content_path=content_path)

    # Add mapping vs colors validation results to the report
    if missing_in_colors:
        report["unmapped_tags"].extend(sorted(missing_in_colors))
    if missing_in_mapping:
        report["uncolored_tags"].extend(sorted(missing_in_mapping))

    # Write the complete report
    write_report(report, project_root)


if __name__ == "__main__":
    main()
