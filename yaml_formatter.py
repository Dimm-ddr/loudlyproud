#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import re
import yaml
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ProcessingStats:
    processed: int = 0
    errors: int = 0
    skipped: int = 0


def split_frontmatter(content: str) -> Optional[Tuple[dict, str]]:
    """Split content into frontmatter and body."""
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
        content = match.group(2)
        return frontmatter, content
    except yaml.YAMLError as e:
        print(f"YAML parsing error: {e}")
        return None


def validate_frontmatter(frontmatter: dict, locale: str) -> List[str]:
    """Validate frontmatter structure and required fields."""
    errors = []

    # Required fields at root level
    required_root = ["title", "params"]
    for field in required_root:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")

    # Required fields in params
    if "params" in frontmatter and isinstance(frontmatter["params"], dict):
        required_params = ["title", "authors"]
        for field in required_params:
            if field not in frontmatter["params"]:
                errors.append(f"Missing required field in params: {field}")

        # Validate authors is a list
        if "authors" in frontmatter["params"] and not isinstance(
            frontmatter["params"]["authors"], list
        ):
            errors.append("'authors' must be a list")

        # Validate translation status for Russian books
        if locale == "ru" and "russian_translation_status" in frontmatter["params"]:
            valid_statuses = [
                "unknown",
                "might_exist",
                "unlikely_to_exist",
                "does_not_exist",
                "exists",
            ]
            if (
                frontmatter["params"]["russian_translation_status"]
                not in valid_statuses
            ):
                errors.append(
                    f"Invalid translation status. Must be one of: {', '.join(valid_statuses)}"
                )

    return errors


def format_frontmatter(directory: Path) -> Dict[str, ProcessingStats]:
    """Process all markdown files in the given directory structure."""
    stats = defaultdict(ProcessingStats)

    # Get locale directories
    locale_dirs = [d for d in directory.iterdir() if d.is_dir()]

    if not locale_dirs:
        print(f"Warning: No locale directories found in {directory}")
        return stats

    for locale_dir in locale_dirs:
        locale = locale_dir.name
        print(f"\nProcessing locale: {locale}")

        for file_path in locale_dir.rglob("*.md"):
            relative_path = file_path.relative_to(directory)
            try:
                # Read the file
                content = file_path.read_text(encoding="utf-8")

                # Split and parse
                result = split_frontmatter(content)
                if not result:
                    print(f"  Skipping {relative_path}: No valid frontmatter found")
                    stats[locale].skipped += 1
                    continue

                frontmatter, body = result

                # Validate frontmatter
                validation_errors = validate_frontmatter(frontmatter, locale)
                if validation_errors:
                    print(f"  Validation errors in {relative_path}:")
                    for error in validation_errors:
                        print(f"    - {error}")
                    stats[locale].errors += 1
                    continue

                # Format the frontmatter with consistent indentation
                formatted_frontmatter = yaml.dump(
                    frontmatter,
                    allow_unicode=True,
                    default_flow_style=False,
                    indent=2,
                    width=1000,  # Prevent line wrapping
                    sort_keys=False,  # Preserve key order
                )

                # Reconstruct the file
                new_content = f"---\n{formatted_frontmatter}---\n{body}"

                # Write back to file
                file_path.write_text(new_content, encoding="utf-8")
                print(f"  Processed: {relative_path}")
                stats[locale].processed += 1

            except Exception as e:
                print(f"  Error processing {relative_path}: {str(e)}")
                stats[locale].errors += 1

    return stats


def main():
    # Get the books directory from the current working directory
    current_dir = Path.cwd()
    books_dir = current_dir / "content" / "books"

    if not books_dir.exists():
        print(f"Error: Books directory not found at {books_dir}")
        print("Make sure you're running the script from the project root directory")
        sys.exit(1)

    print(f"Processing books in: {books_dir}")
    stats = format_frontmatter(books_dir)

    # Print summary
    print("\nProcessing Summary:")
    print("-" * 40)
    for locale, stat in stats.items():
        print(f"\nLocale: {locale}")
        print(f"  Processed: {stat.processed}")
        print(f"  Errors: {stat.errors}")
        print(f"  Skipped: {stat.skipped}")


if __name__ == "__main__":
    main()
