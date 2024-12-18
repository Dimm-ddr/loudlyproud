#!/usr/bin/env python3

from pathlib import Path
from typing import TypedDict
from .common import GENERATED_DATA_DIR, CONTENT_DIR, VALIDATION_FILE, MAPPING_FILE, COLORS_FILE
from .sorting import sort_strings
from .file_ops import (
    collect_all_tags,
    load_tags_map,
    load_color_mapping,
)


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
) -> dict[str, list[str]]:
    """
    Validate tags in book files against mapping and colors.

    Args:
        project_root: Root path of the project containing data files
        content_path: Path to content directory to check
        mapping_file: Path to mapping file
        colors_file: Path to colors file
    """
    try:
        mapping = load_tags_map(mapping_file)
    except Exception as e:
        print(f"Error loading tags map: {e}")
        mapping = {}

    # Load colors as a set
    colored_tags = set()
    try:
        colors = load_color_mapping(colors_file)
        if isinstance(colors, dict):
            # If it's a dict, collect all tag names
            for category in colors.values():
                if isinstance(category, dict):
                    colored_tags.update(category.keys())
        else:
            # If it's already a set, use it directly
            colored_tags = colors
    except Exception as e:
        print(f"Error loading TOML color mapping: {e}")

    # Get all book files
    book_files = content_path.glob("**/books/*.md")

    # Extract all tags from books
    all_tags = set()
    for book_file in book_files:
        tags = extract_tags_from_file(book_file)
        all_tags.update(tags)

    # Find unmapped and uncolored tags
    unmapped_tags = []
    uncolored_tags = []

    # Check each tag
    for tag in sorted(all_tags):
        mapped_tag = mapping.get(tag)
        if mapped_tag is None:
            unmapped_tags.append(tag)
        elif mapped_tag and mapped_tag not in colored_tags:
            # Only check colors for mapped tags
            uncolored_tags.append(mapped_tag)

    return {
        "unmapped_tags": unmapped_tags,
        "uncolored_tags": uncolored_tags,
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


def extract_tags_from_file(file_path: Path) -> set[str]:
    """Extract tags from a markdown file's frontmatter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple frontmatter parsing - find tags section
        if not content.startswith('---'):
            return set()

        frontmatter_end = content.find('---', 3)
        if frontmatter_end == -1:
            return set()

        frontmatter = content[3:frontmatter_end]

        # Find tags section
        tags_start = frontmatter.find('tags:')
        if tags_start == -1:
            return set()

        # Extract tags (assuming they're in list format with - prefix)
        tags = set()
        for line in frontmatter[tags_start:].split('\n'):
            line = line.strip()
            if line.startswith('- "') and line.endswith('"'):
                tag = line[3:-1]  # Remove - " and "
                tags.add(tag)

        return tags
    except Exception as e:
        print(f"Error reading tags from {file_path}: {e}")
        return set()


if __name__ == "__main__":
    main()
