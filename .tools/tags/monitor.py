#!/usr/bin/env python3

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import os
import json
from datetime import datetime
from typing import TypedDict
from ruamel.yaml import YAML
from normalize import normalize_tag, get_tag_display_name
from validate import validate_tags

# Path constants
TAGS_CONFIG_DIR = Path("data/tags")
GENERATED_DATA_DIR = Path(".data/tags")
CONTENT_DIR = Path("content")

# File names
MAPPING_FILE = "mapping.json"
COLORS_FILE = "colors.yaml"
REPORT_FILE = "new_tags_report.json"
PR_REPORT_FILE = "new_tags.json"


class TagReport(TypedDict):
    original_forms: list[str]
    first_seen: str
    files: list[str]
    occurrences: int


class TagsReport(TypedDict):
    unprocessed_tags: dict[str, TagReport]
    processed_tags: dict[str, TagReport]


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
        return set(data.get("tag_colors", {}).keys())
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


def find_unmapped_tags(
    tags: list[str], tags_map: dict, valid_colors: set[str]
) -> list[str]:
    """Find tags that don't have proper mappings."""
    unmapped = []
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower not in tags_map:
            unmapped.append(tag)
            continue

        # Check if normalized tags have color mappings
        mapping = tags_map[tag_lower]
        if mapping:
            normalized_tags = mapping if isinstance(mapping, list) else [mapping]
            for normalized in normalized_tags:
                if normalize_tag(normalized) not in valid_colors:
                    unmapped.append(tag)
                    break

    return unmapped


def update_tags_report(new_tags: dict[str, list], report: TagsReport) -> TagsReport:
    """Update the tags report with newly found tags."""
    current_time = datetime.now().isoformat()

    for file_path, tags in new_tags.items():
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower not in report["unprocessed_tags"]:
                report["unprocessed_tags"][tag_lower] = {
                    "original_forms": [tag],
                    "first_seen": current_time,
                    "files": [file_path],
                    "occurrences": 1,
                }
            else:
                tag_info = report["unprocessed_tags"][tag_lower]
                if tag not in tag_info["original_forms"]:
                    tag_info["original_forms"].append(tag)
                if file_path not in tag_info["files"]:
                    tag_info["files"].append(file_path)
                tag_info["occurrences"] += 1

    return report


def load_tags_report(project_root: Path) -> TagsReport:
    """Load existing tags report from file."""
    report_file = project_root.joinpath(GENERATED_DATA_DIR, REPORT_FILE)
    try:
        if report_file.exists():
            return json.loads(report_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading existing report: {e}")
    return {"unprocessed_tags": {}, "processed_tags": {}}


def main() -> None:
    project_root = Path.cwd()

    # Get changed files
    base_ref = os.environ.get("GITHUB_BASE_REF", "main")
    diff_command = f"git diff --name-only origin/{base_ref}...HEAD"

    changed_files = os.popen(diff_command).read().splitlines()
    book_files = [
        f for f in changed_files if f.startswith(str(CONTENT_DIR)) and f.endswith(".md")
    ]

    # Load configurations
    tags_map = load_tags_map(project_root)
    valid_colors = load_color_mapping(project_root)
    new_tags: dict[str, list[str]] = {}

    # Process each file
    for file_path in book_files:
        tags = extract_tags_from_file(Path(file_path))
        if unmapped := find_unmapped_tags(tags, tags_map, valid_colors):
            new_tags[file_path] = unmapped

    # Update report if new tags found
    if new_tags:
        report = load_tags_report(project_root)
        report = update_tags_report(new_tags, report)

        # Ensure data directory exists
        data_dir = project_root.joinpath(GENERATED_DATA_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)

        # Save updated report
        report_file = data_dir.joinpath(REPORT_FILE)
        report_file.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Save immediate results for PR comment
        with open(PR_REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(new_tags, f, indent=2, ensure_ascii=False)

    # Set output for GitHub Actions
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        print(f"has_new_tags={'true' if new_tags else 'false'}", file=f)

    # Use validation results in PR comment
    validation = validate_tags(project_root)
    if validation["unmapped_tags"] or validation["uncolored_tags"]:
        body += "\n\nValidation issues found:\n"
        if validation["unmapped_tags"]:
            body += "\nTags missing from mapping:\n"
            for tag in validation["unmapped_tags"]:
                body += f"- `{tag}`\n"
        if validation["uncolored_tags"]:
            body += "\nTags missing color definitions:\n"
            for tag in validation["uncolored_tags"]:
                body += f"- `{tag}`\n"


if __name__ == "__main__":
    main()
