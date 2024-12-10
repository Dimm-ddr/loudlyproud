#!/usr/bin/env python3

from pathlib import Path
from ruamel.yaml import YAML
from tags.normalize import TagNormalizer
import tomllib
from typing import TypedDict
import json

# Path constants
TAGS_CONFIG_DIR = Path("data/tags")
GENERATED_DATA_DIR = Path(".data/tags")
CONTENT_DIR = Path("content")

# File names
MAPPING_FILE = "mapping.json"
COLORS_FILE = "colors.toml"
VALIDATION_FILE = "validation-report.txt"


class ValidationReport(TypedDict):
    unmapped_tags: list[str]  # Tags not in mapping keys
    uncolored_tags: list[str]  # Tags not in colors (checking mapped values)


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
        with open(color_file, "rb") as f:  # TOML requires binary mode
            data = tomllib.load(f)
            # Collect all tags from all categories
            tags = set()
            for category in data.values():
                tags.update(category.keys())
            return tags
    except Exception as e:
        print(f"Error loading TOML color mapping: {e}")
        return set()


def split_frontmatter(content: str) -> tuple[dict, str] | None:
    """Split content into frontmatter and body."""
    yaml = YAML()
    yaml.preserve_quotes = True
    match content.split("---\n", 2):
        case ["", frontmatter, *rest] if rest:
            try:
                return yaml.load(frontmatter), rest[0]
            except Exception:  # Handle any YAML parsing errors
                return None
        case _:
            return None


def extract_tags_from_file(file_path: Path) -> list[str]:
    """Extract tags from a book's frontmatter."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if result := split_frontmatter(content):
            frontmatter, _ = result
            # Handle missing params or tags
            params = frontmatter.get("params", {})
            if not isinstance(params, dict):
                print(f"Warning: 'params' in {file_path} is not a dictionary")
                return []
            tags = params.get("tags", [])
            if not isinstance(tags, list):
                print(f"Warning: 'tags' in {file_path} is not a list")
                return []
            return tags
        return []
    except Exception as e:
        print(f"Warning: Could not process {file_path}: {e}")
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
            all_tags.update(tags)

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
    """
    Validate tags against mapping and colors.
    Returns dictionary with two lists:
    - unmapped_tags: tags not in mapping keys
    - uncolored_tags: tags not in colors (checking mapped values)
    """
    normalizer = TagNormalizer()
    content_dir = project_root.joinpath(CONTENT_DIR)

    # Load configurations
    tags_map = load_tags_map(project_root)
    color_tags = load_color_mapping(
        project_root
    )  # Now contains canonical names from TOML

    # Collect all tags from files
    all_tags = collect_all_tags(content_dir)
    tags_lower_map = {tag.lower(): tag for tag in all_tags}

    mapping_keys = {k.lower() for k in tags_map}
    mapped_values = get_mapped_values(tags_map)

    # Generate reports
    unmapped_tags = sorted(
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
    uncolored_tags = sorted(tag for tag in tags_to_check if tag not in color_tags)

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
        *[f"- {tag}" for tag in report["unmapped_tags"]],
        "",
        "Tags without colors (values and unmapped):",
        "=" * 37,
        *[f"- {tag}" for tag in report["uncolored_tags"]],
    ]

    report_file.write_text("\n".join(output), encoding="utf-8")
    print(f"\nDetailed report saved to {report_file}")


def main() -> None:
    """Main function for tag validation."""
    project_root = Path.cwd()
    report = validate_tags(project_root)
    write_report(report, project_root)


if __name__ == "__main__":
    main()
