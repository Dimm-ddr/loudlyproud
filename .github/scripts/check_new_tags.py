# .github/scripts/check_new_tags.py
import os
import yaml
import json
from pathlib import Path
from datetime import datetime


def load_tags_map() -> dict:
    """Load tags mapping from JSON file."""
    tags_file = Path(__file__).parent.parent.parent / ".data" / "tags_map.json"
    try:
        return json.loads(tags_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading tags map: {e}")
        return {}


def load_existing_report() -> dict:
    """Load existing report if it exists."""
    report_file = Path(__file__).parent.parent.parent / ".data" / "new_tags_report.json"
    try:
        if report_file.exists():
            return json.loads(report_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading existing report: {e}")
    return {"unprocessed_tags": {}, "processed_tags": {}}


def normalize_tag(tag: str, tags_map: dict) -> list:
    """
    Normalize a single tag using the mapping.
    Returns a list of tags or empty list if tag should be removed.
    """
    mapped_value = tags_map.get(tag.lower())

    # Handle different mapping cases
    if mapped_value is None:
        return []  # Tag should be removed
    elif isinstance(mapped_value, list):
        return mapped_value  # Multiple tags
    elif isinstance(mapped_value, str):
        return [mapped_value]  # Single tag
    else:
        return [tag]  # Keep original if not in mapping


def normalize_tags(tags: list, tags_map: dict) -> list:
    """Normalize a list of tags, handling all mapping cases."""
    if not tags:
        return []

    normalized = []
    for tag in tags:
        normalized.extend(normalize_tag(tag, tags_map))

    return sorted(list(set(normalized)))  # Remove duplicates and sort


def get_tags_from_file(file_path: Path) -> list:
    """Extract tags from a book markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            return []

        frontmatter = yaml.safe_load(content.split("---\n", 2)[1])
        return frontmatter.get("params", {}).get("tags", []) or []
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def update_report(new_tags: dict, existing_report: dict) -> dict:
    """Update the report with newly found tags."""
    current_time = datetime.now().isoformat()

    # Process each new tag
    for file_path, tags in new_tags.items():
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower not in existing_report["unprocessed_tags"]:
                existing_report["unprocessed_tags"][tag_lower] = {
                    "original_forms": [tag],
                    "first_seen": current_time,
                    "files": [file_path],
                    "occurrences": 1,
                }
            else:
                tag_info = existing_report["unprocessed_tags"][tag_lower]
                if tag not in tag_info["original_forms"]:
                    tag_info["original_forms"].append(tag)
                if file_path not in tag_info["files"]:
                    tag_info["files"].append(file_path)
                tag_info["occurrences"] += 1

    return existing_report


def main():
    # Get changed files
    base_ref = os.environ.get("GITHUB_BASE_REF", "main")
    diff_command = f"git diff --name-only origin/{base_ref}...HEAD"

    changed_files = os.popen(diff_command).read().splitlines()
    book_files = [
        f for f in changed_files if f.startswith("content/books/") and f.endswith(".md")
    ]

    # Load tags map and check for new tags
    tags_map = load_tags_map()
    new_tags: dict[str, list] = {}

    # We now consider a tag "known" if it's in the map, even if it maps to null
    known_tags = set(tags_map.keys())

    # Load existing report
    report = load_existing_report()

    for file_path in book_files:
        tags = get_tags_from_file(Path(file_path))
        unknown_tags = [tag for tag in tags if tag.lower() not in known_tags]

        if unknown_tags:
            new_tags[file_path] = unknown_tags

    # Update and save report
    if new_tags:
        report = update_report(new_tags, report)

        # Ensure .data directory exists
        data_dir = Path(__file__).parent.parent.parent / ".data"
        data_dir.mkdir(exist_ok=True)

        # Save updated report
        report_file = data_dir / "new_tags_report.json"
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
