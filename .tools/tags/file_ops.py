#!/usr/bin/env python3

from pathlib import Path
from typing import TypedDict
from ruamel.yaml import YAML
import json
import tomllib
from collections import Counter
import tomli_w


class TagReport(TypedDict):
    original_forms: list[str]
    first_seen: str
    files: list[str]
    occurrences: int


class TagsReport(TypedDict):
    unprocessed_tags: dict[str, TagReport]
    processed_tags: dict[str, TagReport]


def split_frontmatter(content: str) -> tuple[dict, str] | None:
    """Split content into frontmatter and body."""
    try:
        # Normalize line endings
        content = content.replace("\r\n", "\n")

        # Try to split on frontmatter delimiters
        parts = content.split("---\n", 2)
        if len(parts) < 3:
            # Try alternative delimiter format
            parts = content.split("---", 2)

        match parts:
            case ["", frontmatter, *rest] if rest:
                try:
                    yaml = YAML()
                    yaml.preserve_quotes = True
                    data = yaml.load(frontmatter)
                    if not isinstance(data, dict):
                        print(f"Warning: Frontmatter is not a dictionary")
                        return None
                    return data, rest[0]
                except Exception as e:
                    print(f"Warning: Failed to parse YAML frontmatter: {str(e)}")
                    return None
            case _:
                print(f"Warning: Could not find valid frontmatter delimiters")
                return None
    except Exception as e:
        print(f"Warning: Error processing frontmatter: {str(e)}")
        return None


def extract_tags_from_file(file_path: Path) -> list[str]:
    """Extract tags from a book's frontmatter."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if not content.strip():
            print(f"Warning: File is empty: {file_path}")
            return []

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
            # Filter out None values and ensure all elements are strings
            return [
                str(tag)
                for tag in tags
                if tag is not None and not isinstance(tag, (dict, list))
            ]
        print(f"Warning: No valid frontmatter found in {file_path}")
        return []
    except Exception as e:
        print(f"Warning: Could not process {file_path}: {str(e)}")
        return []


def write_frontmatter(file_path: Path, frontmatter: dict, body: str) -> bool:
    """Write frontmatter and body back to file."""
    try:
        # Validate frontmatter structure
        if "type" not in frontmatter:
            print(f"Error: Missing 'type' in frontmatter for {file_path}")
            return False
        if "params" not in frontmatter:
            print(f"Error: Missing 'params' in frontmatter for {file_path}")
            return False
        if "tags" not in frontmatter["params"]:
            print(f"Error: Missing 'tags' in params for {file_path}")
            return False

        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 4096
        yaml.indent(mapping=2, sequence=4, offset=2)

        with open(file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("---\n")  # Opening delimiter
            yaml.dump(frontmatter, f)
            f.write("---\n")  # Closing delimiter with newline
            if body:
                f.write(body)  # Body already includes leading newline from split
            else:
                f.write("\n")  # Ensure there's always a final newline
        return True
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
        return False


def collect_all_tags(content_dir: Path) -> Counter[str]:
    """
    Collect all unique tags from all book files with their frequencies.
    """
    tag_counter = Counter()

    for locale_dir in content_dir.iterdir():
        if not locale_dir.is_dir():
            continue

        books_dir = locale_dir / "books"
        if not books_dir.exists():
            continue

        for book_file in books_dir.glob("*.md"):
            tags = extract_tags_from_file(book_file)
            tag_counter.update(tags)

    return tag_counter


def load_tags_map(file_path: Path) -> dict:
    """Load tags mapping configuration."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading tags map: {e}")
        return {}


def load_color_mapping(file_path: Path) -> set[str]:
    """Load valid tags from color mapping."""
    try:
        with open(file_path, "rb") as f:  # TOML requires binary mode
            data = tomllib.load(f)
            # Collect all tags from all categories
            tags = set()
            for category in data.values():
                tags.update(category.keys())
            return tags
    except Exception as e:
        print(f"Error loading TOML color mapping: {e}")
        return set()


def load_colors_file(file_path: Path) -> dict:
    """Load full color mapping structure."""
    try:
        with open(file_path, "rb") as f:  # TOML requires binary mode
            return tomllib.load(f)
    except Exception as e:
        print(f"Error loading TOML color mapping: {e}")
        return {}


def load_patterns(file_path: Path) -> dict:
    """Load tag patterns configuration."""
    try:
        with open(file_path, "rb") as f:  # TOML requires binary mode
            return tomllib.load(f)
    except Exception as e:
        print(f"Error loading patterns: {e}")
        return {}


def load_tags_report(project_root: Path) -> TagsReport:
    """Load existing tags report from file."""
    report_file = project_root.joinpath(".data/tags", "new_tags_report.json")
    try:
        if report_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading existing report: {e}")
    return {"unprocessed_tags": {}, "processed_tags": {}}


def write_tags_report(project_root: Path, report: dict, new_tags: dict) -> None:
    """Write tags report to files."""
    data_dir = project_root.joinpath(".data/tags")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Save updated report
    report_file = data_dir.joinpath("new_tags_report.json")
    with open(report_file, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Save immediate results for PR comment
    with open("new_tags.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(new_tags, f, indent=2, ensure_ascii=False)


def write_mapping_file(mapping_file: Path, mapping: dict) -> None:
    """Write mapping to JSON file."""
    with open(mapping_file, "w", encoding="utf-8", newline="\n") as f:
        json.dump(mapping, f, indent=4, ensure_ascii=False)


def write_colors_file(colors_file: Path, colors: dict) -> None:
    """Write colors to TOML file."""
    with open(colors_file, "w", encoding="utf-8", newline="\n") as f:
        for section in colors:
            f.write(f'["{section}"]\n')
            for tag, color in colors[section].items():
                f.write(f'"{tag}" = "{color}"\n')
            f.write("\n")


def load_removable_tags(file_path: Path) -> set[str]:
    """Load removable tags from TOML file."""
    if not file_path.exists():
        return set()

    try:
        with open(file_path, "rb") as f:  # TOML requires binary mode
            data = tomllib.load(f)
            return set(data.get("to_remove", []))
    except Exception as e:
        print(f"Error loading removable tags: {e}")
        return set()


def write_patterns_file(file_path: Path, patterns: dict) -> None:
    """Write patterns to TOML file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as f:
        tomli_w.dump(patterns, f)


def write_removable_tags(file_path: Path, tags: list[str]) -> None:
    """Write removable tags to TOML file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"to_remove": tags}
    with open(file_path, "wb") as f:
        tomli_w.dump(data, f)


def load_special_display_names(file_path: Path) -> dict[str, str]:
    """Load special display names mapping."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading special display names: {e}")
        return {}
