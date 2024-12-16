#!/usr/bin/env python3

import os
import json
from datetime import datetime
from pathlib import Path
from typing import TypedDict
from .validate import validate_tags, extract_tags_from_file
from .sorting import sort_strings, sort_dict_by_keys

# Path constants
TAGS_CONFIG_DIR = Path("data/tags")
GENERATED_DATA_DIR = Path(".data/tags")
CONTENT_DIR = Path("content")

# File names
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


def load_tags_report(project_root: Path) -> TagsReport:
    """Load existing tags report from file."""
    report_file = project_root.joinpath(GENERATED_DATA_DIR, REPORT_FILE)
    try:
        if report_file.exists():
            with open(report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading existing report: {e}")
    return {"unprocessed_tags": {}, "processed_tags": {}}


def update_tags_report(new_tags: dict[str, list], report: TagsReport) -> TagsReport:
    """Update the tags report with newly found tags."""
    current_time = datetime.now().isoformat()

    for file_path, tags in sorted(new_tags.items()):
        for tag in sort_strings(tags):
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
                    # Keep original_forms sorted
                    tag_info["original_forms"].append(tag)
                    tag_info["original_forms"] = sort_strings(tag_info["original_forms"])
                if file_path not in tag_info["files"]:
                    # Keep files sorted
                    tag_info["files"].append(file_path)
                    tag_info["files"] = sort_strings(tag_info["files"])
                tag_info["occurrences"] += 1

    # Sort the unprocessed_tags dictionary by keys
    report["unprocessed_tags"] = sort_dict_by_keys(report["unprocessed_tags"])
    report["processed_tags"] = sort_dict_by_keys(report["processed_tags"])

    return report


def main() -> None:
    """Main function for monitoring tag changes."""
    project_root = Path.cwd()

    # Get changed files
    base_ref = os.environ.get("GITHUB_BASE_REF", "main")
    diff_command = f"git diff --name-only origin/{base_ref}...HEAD"

    changed_files = os.popen(diff_command).read().splitlines()
    book_files = sort_strings(
        [f for f in changed_files if f.startswith(str(CONTENT_DIR)) and f.endswith(".md")]
    )

    # Validate changed files
    validation_report = validate_tags(project_root)
    new_tags: dict[str, list[str]] = {}

    # Process each file
    for file_path in book_files:
        tags = extract_tags_from_file(Path(file_path))
        # Check for unmapped or uncolored tags
        invalid_tags = sort_strings(
            [tag for tag in tags
             if tag in validation_report["unmapped_tags"] or
                tag in validation_report["uncolored_tags"]]
        )
        if invalid_tags:
            new_tags[file_path] = invalid_tags

    # Update report if new tags found
    if new_tags:
        report = load_tags_report(project_root)
        report = update_tags_report(new_tags, report)

        # Ensure data directory exists
        data_dir = project_root.joinpath(GENERATED_DATA_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)

        # Save updated report
        report_file = data_dir.joinpath(REPORT_FILE)
        with open(report_file, "w", encoding="utf-8", newline='\n') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Save immediate results for PR comment
        with open(PR_REPORT_FILE, "w", encoding="utf-8", newline='\n') as f:
            # Sort new_tags before saving
            sorted_new_tags = {k: sort_strings(v) for k, v in sorted(new_tags.items())}
            json.dump(sorted_new_tags, f, indent=2, ensure_ascii=False)

    # Set output for GitHub Actions
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        print(f"has_new_tags={'true' if new_tags else 'false'}", file=f)


if __name__ == "__main__":
    main()
