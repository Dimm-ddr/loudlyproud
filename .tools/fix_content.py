#!/usr/bin/env python3

import sys
import json
from pathlib import Path
from ruamel.yaml import YAML
from typing import List, Tuple, Dict


def reorder_frontmatter(data: Dict) -> Dict:
    """Reorder frontmatter fields in a consistent way."""
    # Define the order of root level fields
    root_order = ["draft", "slug", "title", "type", "params"]

    # Define the order of params fields
    params_order = [
        "authors",
        "book_title",
        "book_description",
        "short_book_description",
        "cover",
        "isbn",
        "languages",
        "goodreads_link",
        "page_count",
        "publication_year",
        "publishers",
        "russian_audioversion",
        "russian_translation_status",
        "tags",
    ]

    # Create new ordered dict for root level
    ordered = {}
    # Add fields in specified order
    for field in root_order:
        if field in data:
            ordered[field] = data[field]
    # Add any remaining fields
    for field in data:
        if field not in ordered:
            ordered[field] = data[field]

    # Order params if present
    if "params" in ordered and isinstance(ordered["params"], dict):
        params = ordered["params"]
        ordered_params = {}
        # Add fields in specified order
        for field in params_order:
            if field in params:
                ordered_params[field] = params[field]
        # Add any remaining fields
        for field in params:
            if field not in ordered_params:
                ordered_params[field] = params[field]
        ordered["params"] = ordered_params

    return ordered


def fix_languages_field(data: dict) -> Tuple[bool, List[str]]:
    """Fix languages field in the data."""
    fixes = []
    modified = False

    if "params" in data and "languages" in data["params"]:
        params = data["params"]
        if isinstance(params["languages"], str):
            langs = [l.strip() for l in params["languages"].split(",")]
            params["languages"] = langs
            fixes.append("Converted 'languages' from string to list")
            modified = True
        elif isinstance(params["languages"], list):
            new_langs = []
            for lang in params["languages"]:
                if "," in lang:
                    new_langs.extend(l.strip() for l in lang.split(","))
                    modified = True
                else:
                    new_langs.append(lang)
            if modified:
                params["languages"] = new_langs
                fixes.append("Split comma-separated language entries")

    return modified, fixes


def fix_audioversion_field(data: dict) -> tuple[bool, list[str]]:
    """Fix russian_audioversion field in the data."""
    fixes = []
    modified = False

    if "params" in data and "russian_audioversion" in data["params"]:
        params = data["params"]
        if isinstance(params["russian_audioversion"], str):
            value = params["russian_audioversion"].lower()
            params["russian_audioversion"] = value == "yes"
            fixes.append("Converted 'russian_audioversion' from string to boolean")
            modified = True

    return modified, fixes


def fix_file(project_root: Path, file_path: str, reorder: bool = False) -> None:
    """Fix issues in a single file."""
    full_path = project_root / file_path
    if not full_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    try:
        # Use ruamel.yaml to preserve formatting
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 4096  # Prevent line wrapping
        yaml.indent(mapping=2, sequence=4, offset=2)

        with full_path.open("r", encoding="utf-8") as f:
            data = yaml.load(f)

        modified = False
        fixes = []

        # Fix languages
        langs_modified, lang_fixes = fix_languages_field(data)
        if langs_modified:
            modified = True
            fixes.extend(lang_fixes)

        # Fix audioversion
        audio_modified, audio_fixes = fix_audioversion_field(data)
        if audio_modified:
            modified = True
            fixes.extend(audio_fixes)

        # Reorder frontmatter if requested
        if reorder:
            data = reorder_frontmatter(data)
            modified = True
            fixes.append("Reordered frontmatter fields")

        if modified:
            print(f"\n✅ Fixing {file_path}:")
            for fix in fixes:
                print(f"  - {fix}")

            with full_path.open("w", encoding="utf-8") as f:
                yaml.dump(data, f)

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {str(e)}")


def main():
    project_root = Path(__file__).parent.parent
    issues_file = project_root / ".data" / "content_issues.json"

    # Process arguments
    reorder = "--reorder" in sys.argv

    if not issues_file.exists():
        print("No issues file found. Run check_content.py first.")
        sys.exit(1)

    issues_data = json.loads(issues_file.read_text())
    fixable_issues = [issue for issue in issues_data["issues"] if issue["auto_fixable"]]

    if not fixable_issues:
        print("No auto-fixable issues found.")
        return

    print(f"Found {len(fixable_issues)} auto-fixable issues.")

    # Group issues by file
    files_to_fix = set(issue["file_path"] for issue in fixable_issues)

    for file_path in files_to_fix:
        fix_file(project_root, file_path, reorder)

    # Remove issues file after fixing
    issues_file.unlink()
    print("\nDone! Run check_content.py again to verify fixes.")


if __name__ == "__main__":
    main()
