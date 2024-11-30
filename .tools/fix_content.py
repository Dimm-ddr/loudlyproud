#!/usr/bin/env python3

import sys
import json
from pathlib import Path
from ruamel.yaml import YAML

from fixers.text_fixes import apply_text_fixes
from fixers.yaml_fixes import apply_yaml_fixes
from fixers.format_fixes import reorder_frontmatter


def fix_file(project_root: Path, file_path: str, reorder: bool = False) -> None:
    """Fix issues in a single file."""
    full_path = project_root / file_path
    if not full_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    try:
        # First, handle text-based fixes
        content = full_path.read_text(encoding="utf-8")
        content, text_fixes = apply_text_fixes(content)
        modified = bool(text_fixes)
        all_fixes = text_fixes

        if modified:
            # Write back the text fixes
            with full_path.open("w", encoding="utf-8") as f:
                f.write(content)

        # Then handle YAML-based fixes
        parts = content.split("---", 2)
        if len(parts) < 3:
            print(f"❌ Invalid frontmatter format in {file_path}")
            return

        # Configure YAML
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 4096
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.default_flow_style = False

        try:
            data = yaml.load(parts[1])
        except yaml.YAMLError as e:
            print(f"❌ YAML error in {file_path}: {e}")
            return

        # Apply YAML-based fixes
        yaml_modified, yaml_fixes, data = apply_yaml_fixes(data)
        if yaml_modified:
            modified = True
            all_fixes.extend(yaml_fixes)

        if reorder:
            data = reorder_frontmatter(data)
            modified = True
            all_fixes.append("Reordered frontmatter fields")

        if modified:
            print(f"\n✅ Fixing {file_path}:")
            for fix in all_fixes:
                print(f"  - {fix}")

            # Write back with proper formatting
            with full_path.open("w", encoding="utf-8") as f:
                f.write("---\n")
                yaml.dump(data, f)
                f.write("---")
                if parts[2]:
                    f.write(parts[2])

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {str(e)}")


def main() -> None:
    project_root = Path(__file__).parent.parent
    issues_file = project_root / ".data" / "content_issues.json"

    # Process arguments
    reorder = "--reorder" in sys.argv

    if not issues_file.exists():
        print("No issues file found. Run check_content.py first.")
        sys.exit(1)

    try:
        issues_data = json.loads(issues_file.read_text(encoding="utf-8"))
        fixable_issues = [
            issue for issue in issues_data["issues"] if issue["auto_fixable"]
        ]

        if not fixable_issues:
            print("No auto-fixable issues found.")
            return

        print(f"Found {len(fixable_issues)} auto-fixable issues:")
        # Add debug info about issues
        for issue in fixable_issues:
            print(f"  - {issue['file_path']}: {issue['message']} ({issue['field']})")

        # Group issues by file
        files_to_fix = set(issue["file_path"] for issue in fixable_issues)
        print(f"\nProcessing {len(files_to_fix)} files:")
        for file_path in files_to_fix:
            print(f"\nChecking {file_path}")
            fix_file(project_root, file_path, reorder)

        # Remove issues file after fixing
        issues_file.unlink()
        print("\nDone! Run check_content.py again to verify fixes.")

    except Exception as e:
        print(f"Error processing issues file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
