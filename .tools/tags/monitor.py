#!/usr/bin/env python3

import os
from pathlib import Path
from datetime import datetime
from .common import CONTENT_DIR
from .sorting import sort_strings, sort_dict_by_keys
from .file_ops import (
    extract_tags_from_file,
    load_tags_report,
    write_tags_report,
)
from .git_ops import get_changed_book_files
from .validate import validate_tags


def update_tags_report(new_tags: dict[str, list], report: dict) -> dict:
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
                    tag_info["original_forms"] = sort_strings(
                        tag_info["original_forms"]
                    )
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

    # Get changed book files
    book_files = get_changed_book_files(project_root.joinpath(CONTENT_DIR))

    # Validate changed files
    validation_report = validate_tags(project_root)
    new_tags: dict[str, list[str]] = {}

    # Process each file
    for file_path in book_files:
        tags = extract_tags_from_file(Path(file_path))
        # Check for unmapped or uncolored tags
        invalid_tags = sort_strings(
            [
                tag
                for tag in tags
                if tag in validation_report["unmapped_tags"]
                or tag in validation_report["uncolored_tags"]
            ]
        )
        if invalid_tags:
            new_tags[file_path] = invalid_tags

    # Update report if new tags found
    if new_tags:
        report = load_tags_report(project_root)
        report = update_tags_report(new_tags, report)
        write_tags_report(project_root, report, new_tags)

    # Set output for GitHub Actions
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        print(f"has_new_tags={'true' if new_tags else 'false'}", file=f)


if __name__ == "__main__":
    main()
