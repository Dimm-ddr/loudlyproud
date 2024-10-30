# .github/scripts/check_new_tags.py
import os
import yaml
import json
from pathlib import Path
from datetime import datetime


def load_tags_map() -> dict:
    """
    Load tags mapping configuration from JSON file.

    Returns:
        dict: Mapping of lowercase tag variations to their normalized forms.
        Empty dict if file cannot be loaded.

    The mapping supports three types of values:
    - str: Direct replacement for the tag
    - list[str]: Tag should be replaced with multiple tags
    - None: Tag should be removed
    """
    tags_file: Path = Path(__file__).parent.parent.parent / ".data" / "tags_map.json"
    try:
        return json.loads(tags_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading tags map: {e}")
        return {}


def process_single_tag(tag: str, tags_map: dict) -> list[str]:
    """
    Process a single tag according to the mapping rules.

    Args:
        tag: Original tag to process
        tags_map: Dictionary of tag mappings

    Returns:
        list[str]: List of processed tags. Can be:
        - Empty list if tag should be removed
        - List with one tag if straight replacement or unknown tag
        - List with multiple tags if tag should be split
    """
    mapped_value = tags_map.get(tag.lower(), tag)

    if mapped_value is None:
        return []  # Tag should be removed
    elif isinstance(mapped_value, list):
        return mapped_value  # Tag splits into multiple tags
    elif isinstance(mapped_value, str):
        return [mapped_value]  # Direct replacement or original if not in map
    else:
        # This shouldn't happen with valid JSON but handle it gracefully
        print(f"Warning: Unexpected mapping value for tag '{tag}': {mapped_value}")
        return [tag]


def process_tag_list(tags: list[str], tags_map: dict) -> list[str]:
    """
    Process a list of tags according to the mapping rules.

    Args:
        tags: List of original tags
        tags_map: Dictionary of tag mappings

    Returns:
        list[str]: Deduplicated and sorted list of processed tags
    """
    if not tags:
        return []

    processed = []
    for tag in tags:
        processed.extend(process_single_tag(tag, tags_map))

    return sorted(list(set(processed)))  # Remove duplicates and sort


def find_unmapped_tags(tags: list[str], tags_map: dict) -> list[str]:
    """
    Find tags that don't have entries in the mapping.

    Args:
        tags: List of tags to check
        tags_map: Dictionary of tag mappings

    Returns:
        list[str]: List of tags not present in the mapping (case-insensitive check)
    """
    return [tag for tag in tags if tag.lower() not in tags_map]


def extract_tags_from_file(file_path: Path) -> list[str]:
    """
    Extract tags from a book's frontmatter.

    Args:
        file_path: Path to the markdown file

    Returns:
        list[str]: List of tags found in the file.
        Empty list if no tags found or in case of errors.
    """
    try:
        content: str = file_path.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            return []

        frontmatter = yaml.safe_load(content.split("---\n", 2)[1])
        return frontmatter.get("params", {}).get("tags", []) or []
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def update_tags_report(new_tags: dict[str, list], report: dict) -> dict:
    """
    Update the tags report with newly found tags.

    Args:
        new_tags: Dictionary mapping file paths to their new tags
        report: Existing report dictionary to update

    Returns:
        dict: Updated report with new tag information
    """
    current_time: str = datetime.now().isoformat()

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


def load_tags_report() -> dict:
    """
    Load existing tags report from file.

    Returns:
        dict: Existing report or empty template if no report exists
    """
    report_file: Path = Path(__file__).parent.parent.parent / ".data" / "new_tags_report.json"
    try:
        if report_file.exists():
            return json.loads(report_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading existing report: {e}")
    return {"unprocessed_tags": {}, "processed_tags": {}}


def main() -> None:
    # Get changed files
    base_ref: str = os.environ.get("GITHUB_BASE_REF", "main")
    diff_command: str = f"git diff --name-only origin/{base_ref}...HEAD"

    changed_files: list[str] = os.popen(diff_command).read().splitlines()
    book_files: list[str] = [
        f for f in changed_files if f.startswith("content/books/") and f.endswith(".md")
    ]

    # Load configurations
    tags_map: dict = load_tags_map()
    new_tags: dict[str, list] = {}

    # Process each file
    for file_path in book_files:
        tags: list[str] = extract_tags_from_file(Path(file_path))
        unmapped_tags: list[str] = find_unmapped_tags(tags, tags_map)

        if unmapped_tags:
            new_tags[file_path] = unmapped_tags

    # Update report if new tags found
    if new_tags:
        report: dict = load_tags_report()
        report = update_tags_report(new_tags, report)

        # Ensure .data directory exists
        data_dir: Path = Path(__file__).parent.parent.parent / ".data"
        data_dir.mkdir(exist_ok=True)

        # Save updated report
        report_file: Path = data_dir / "new_tags_report.json"
        report_file.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # Set output for GitHub Actions
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        print(f"has_new_tags={'true' if new_tags else 'false'}", file=f)

    # Save immediate results for PR comment
    if new_tags:
        with open("new_tags.json", "w", encoding="utf-8") as f:
            json.dump(new_tags, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
