#!/usr/bin/env python3

from pathlib import Path
from ruamel.yaml import YAML
from dataclasses import dataclass
from typing import TypedDict
import json

# Path constants
TAGS_CONFIG_DIR = Path("data/tags")
GENERATED_DATA_DIR = Path(".data/tags")
CONTENT_DIR = Path("content")

# File names
MAPPING_FILE = "mapping.json"
COLORS_FILE = "colors.yaml"
VALIDATION_FILE = "validation-report.txt"

class ValidationReport(TypedDict):
    unmapped_tags: list[str]  # Tags not in mapping keys or values
    unknown_tags: list[str]   # Tags not in mapping keys
    uncolored_tags: list[str] # Tags not in colors (excluding mapped values)

def load_tags_map(project_root: Path) -> dict:
    """Load tags mapping configuration."""
    tags_file = project_root.joinpath(TAGS_CONFIG_DIR, MAPPING_FILE)
    try:
        return json.loads(tags_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading tags map: {e}")
        return {}

def load_color_mapping(project_root: Path) -> set[str]:
    """Load valid tags from color mapping."""
    color_file = project_root.joinpath(TAGS_CONFIG_DIR, COLORS_FILE)
    try:
        yaml = YAML()
        data = yaml.load(color_file)
        return {k.lower() for k in data.get('tag_colors', {})}
    except Exception as e:
        print(f"Error loading color mapping: {e}")
        return set()

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

def extract_tags_from_file(file_path: Path) -> list[str]:
    """Extract tags from a book's frontmatter."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if result := split_frontmatter(content):
            frontmatter, _ = result
            return frontmatter.get("params", {}).get("tags", []) or []
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return []

def collect_all_tags(content_dir: Path) -> set[str]:
    """Collect all unique tags from all book files."""
    all_tags = set()

    for locale_dir in content_dir.iterdir():
        if not locale_dir.is_dir():
            continue

        books_dir = locale_dir / "books"
        if not books_dir.exists():
            continue

        for book_file in books_dir.glob("*.md"):
            tags = extract_tags_from_file(book_file)
            all_tags.update(tag.lower() for tag in tags)

    return all_tags

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
    """Validate tags against mapping and colors."""
    content_dir = project_root.joinpath(CONTENT_DIR)

    # Load configurations
    tags_map = load_tags_map(project_root)
    color_tags = load_color_mapping(project_root)

    # Collect all tags from files
    all_tags = collect_all_tags(content_dir)
    mapped_values = get_mapped_values(tags_map)
    mapping_keys = {k.lower() for k in tags_map}

    # Generate reports
    unmapped_tags = sorted(tag for tag in all_tags
                          if tag not in mapping_keys and tag not in mapped_values)

    unknown_tags = sorted(tag for tag in all_tags
                         if tag not in mapping_keys)

    uncolored_tags = sorted(tag for tag in all_tags
                           if tag not in mapping_keys
                           and tag.replace(' ', '-') not in color_tags)

    return {
        "unmapped_tags": unmapped_tags,
        "unknown_tags": unknown_tags,
        "uncolored_tags": uncolored_tags
    }

def main() -> None:
    project_root = Path.cwd()

    # Validate tags
    report = validate_tags(project_root)

    # Print summary
    print(f"\nValidation Summary:")
    print(f"Tags not in mapping (keys or values): {len(report['unmapped_tags'])}")
    print(f"Tags not in mapping keys: {len(report['unknown_tags'])}")
    print(f"Tags without colors: {len(report['uncolored_tags'])}")

    # Save detailed report
    data_dir = project_root.joinpath(GENERATED_DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)

    report_file = data_dir.joinpath(VALIDATION_FILE)

    # Create formatted output
    output = [
        "Tags not in mapping keys or values:",
        "=" * 30,
        *[f"- {tag}" for tag in report['unmapped_tags']],
        "",
        "Tags not in mapping keys:",
        "=" * 20,
        *[f"- {tag}" for tag in report['unknown_tags']],
        "",
        "Tags without colors:",
        "=" * 17,
        *[f"- {tag}" for tag in report['uncolored_tags']]
    ]

    # Write to file
    report_file.write_text(
        "\n".join(output),
        encoding="utf-8"
    )

    print(f"\nDetailed report saved to {report_file}")

if __name__ == "__main__":
    main()