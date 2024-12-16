#!/usr/bin/env python3

from pathlib import Path
from typing import TypedDict
from .common import GENERATED_DATA_DIR, CONTENT_DIR, VALIDATION_FILE
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


def validate_tags(project_root: Path) -> ValidationReport:
    """
    Validate tags against mapping and colors.
    Returns dictionary with two lists:
    - unmapped_tags: tags not in mapping keys
    - uncolored_tags: tags not in colors (checking mapped values)
    """
    content_dir = project_root.joinpath(CONTENT_DIR)
    mapping_file = project_root.joinpath("data/tags/mapping.json")
    colors_file = project_root.joinpath("data/tags/colors.toml")

    # Load configurations
    tags_map = load_tags_map(mapping_file)
    color_tags = {tag.lower() for tag in load_color_mapping(colors_file)}

    # Collect all tags from files with their frequencies
    tag_counter = collect_all_tags(content_dir)
    tags_lower_map = {tag.lower(): tag for tag in tag_counter}

    mapping_keys = {k.lower() for k in tags_map}

    # Generate reports
    unmapped_tags = sort_strings(
        orig_tag
        for lower_tag, orig_tag in tags_lower_map.items()
        if lower_tag not in mapping_keys
    )

    # Check colors for mapped values and unmapped tags
    # Use canonical names from mapping for mapped values
    mapped_canonical = {
        tags_map[k] for k, v in tags_map.items() if v is not None and isinstance(v, str)
    }
    mapped_canonical.update(
        tag
        for k, v in tags_map.items()
        if v is not None and isinstance(v, list)
        for tag in v
    )

    # Combine with unmapped tags
    tags_to_check = mapped_canonical | set(unmapped_tags)
    uncolored_tags = sort_strings(
        tag for tag in tags_to_check if tag.lower() not in color_tags
    )

    return {"unmapped_tags": unmapped_tags, "uncolored_tags": uncolored_tags}


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
    report = validate_tags(project_root)
    write_report(report, project_root)


if __name__ == "__main__":
    main()
