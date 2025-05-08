#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import json
from dataclasses import dataclass, field
from collections import Counter

from frontmatter import parse_frontmatter, validate_value
from book_schema import SCHEMA

@dataclass
class ContentIssue:
    """Represents a content validation issue."""
    file_path: str
    issue_type: str
    message: str
    field: str | None = None
    auto_fixable: bool = False

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "issue_type": self.issue_type,
            "message": self.message,
            "field": self.field,
            "auto_fixable": self.auto_fixable,
        }

@dataclass
class ValidationStats:
    total_files: int = 0
    files_with_issues: int = 0
    issue_types: Counter = field(default_factory=Counter)
    field_issues: Counter = field(default_factory=Counter)

def print_stats(stats: ValidationStats) -> None:
    """Print validation statistics."""
    print("\nValidation Statistics:")
    print("-" * 40)
    print(f"Total files checked: {stats.total_files}")
    print(f"Files with issues: {stats.files_with_issues}")

    if stats.issue_types:
        print("\nIssue types:")
        for issue_type, count in stats.issue_types.most_common():
            print(f"  {issue_type}: {count}")

    if stats.field_issues:
        print("\nField issues:")
        for field, count in stats.field_issues.most_common():
            print(f"  {field}: {count}")

class ContentChecker:
    def __init__(self) -> None:
        self.schema = SCHEMA
        self.project_root = Path(__file__).parent.parent

    def validate_required_fields(self, data: dict, relative_path: str) -> list[ContentIssue]:
        """Validate required fields in data."""
        issues = []
        for required_field in self.schema["required_fields"]:
            if required_field not in data:
                issues.append(
                    ContentIssue(
                        relative_path,
                        "missing_field",
                        f"Missing required field: {required_field}",
                        field=required_field,
                    )
                )
        return issues

    def validate_params(self, data: dict, relative_path: str) -> list[ContentIssue]:
        """Validate params section of the data."""
        issues = []
        if not isinstance(data.get("params"), dict):
            return issues

        params = data["params"]
        params_schema = self.schema["params"]

        # Required params fields
        for required_field in params_schema["required_fields"]:
            if required_field not in params:
                issues.append(
                    ContentIssue(
                        relative_path,
                        "missing_field",
                        f"Missing required params field: {required_field}",
                        field=f"params.{required_field}",
                    )
                )

        # Field validation
        for required_field, value in params.items():
            if field_def := params_schema["field_types"].get(required_field):
                if field_type := field_def.get("type"):
                    if error := validate_value(value, field_type, field_def):
                        issues.append(
                            ContentIssue(
                                relative_path,
                                "validation_error",
                                f"Field 'params.{required_field}': {error}",
                                field=f"params.{required_field}",
                                auto_fixable=field_def.get("format") == "isbn",
                            )
                        )

        # Special checks
        if isinstance(params.get("languages"), str):
            issues.append(
                ContentIssue(
                    relative_path,
                    "format_error",
                    "'languages' should be a list, not a string",
                    field="languages",
                    auto_fixable=True,
                )
            )
        elif isinstance(params.get("languages"), list):
            for lang in params["languages"]:
                if isinstance(lang, str) and "," in lang:
                    issues.append(
                        ContentIssue(
                            relative_path,
                            "format_error",
                            f"Language entry contains comma: '{lang}'",
                            field="languages",
                            auto_fixable=True,
                        )
                    )

        if isinstance(params.get("russian_audioversion"), str):
            issues.append(
                ContentIssue(
                    relative_path,
                    "format_error",
                    "'russian_audioversion' should be a boolean, not a string",
                    field="params.russian_audioversion",
                    auto_fixable=True,
                )
            )

        return issues

    def check_file(self, file_path: Path) -> list[ContentIssue]:
        """Check a single file for issues."""
        issues = []
        relative_path = str(file_path.relative_to(self.project_root))
        content = file_path.read_text(encoding="utf-8")

        # Check for HTML line breaks
        if "<br" in content:
            issues.append(
                ContentIssue(
                    relative_path,
                    "html_line_break",
                    "Found HTML line break tags. These should be converted to markdown line breaks.",
                    auto_fixable=True,
                )
            )

        # Parse frontmatter using our new utilities
        data, parse_errors, is_fixable = parse_frontmatter(content)
        
        # If parsing failed, add issues and return
        if parse_errors:
            for error in parse_errors:
                issues.append(
                    ContentIssue(
                        relative_path,
                        "yaml_error",
                        error,
                        auto_fixable=is_fixable,
                    )
                )
            return issues
        
        # If we couldn't parse the frontmatter, return early
        if data is None:
            return issues

        # Validate required fields
        issues.extend(self.validate_required_fields(data, relative_path))
        # Validate params
        issues.extend(self.validate_params(data, relative_path))

        # Check for malformed YAML with extra newlines
        parts = content.split("---", 2)
        if len(parts) < 3:
            issues.append(
                ContentIssue(
                    file_path=relative_path,
                    field="frontmatter",
                    message="Invalid frontmatter format",
                    auto_fixable=False,
                    issue_type="format",
                )
            )
            return issues

        # Check for extra newlines in YAML
        yaml_content = parts[1]
        lines = yaml_content.split("\n")
        in_multiline = False
        multiline_indent = 0
        current_field = None

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())
            
            # Check if we're starting a multiline string
            if ":" in line and not line.strip().startswith("#"):
                field_indent = len(line) - len(line.lstrip())
                if field_indent == 2:  # This is a top-level field
                    field_name = line.split(":", 1)[0].strip()
                    value_part = line.split(":", 1)[1].strip()
                    
                    # Check if this is a multiline string start
                    if value_part == "|" or value_part == "|-":
                        in_multiline = True
                        multiline_indent = indent + 2
                        current_field = field_name
                        continue
            
            # If we're in a multiline string, check for its end
            if in_multiline:
                if indent < multiline_indent and stripped:  # Less indentation and non-empty
                    in_multiline = False
                    current_field = None
                else:
                    continue  # Skip newline checks while in multiline string
            
            # Check for extra newlines only outside of multiline strings
            if not in_multiline and stripped == "" and i > 1 and i < len(lines):
                prev_line = lines[i-2].strip()
                next_line = lines[i+1].strip()
                if prev_line and next_line:
                    # Only flag if neither line is part of a multiline string
                    prev_indent = len(lines[i-2]) - len(lines[i-2].lstrip())
                    next_indent = len(lines[i+1]) - len(lines[i+1].lstrip())
                    if prev_indent == 2 and next_indent == 2:  # Both are top-level fields
                        context = f"around line {i}:\n  {prev_line}\n  {line}\n  {next_line}"
                        issues.append(
                            ContentIssue(
                                file_path=relative_path,
                                field="frontmatter",
                                message=f"Found extra newline in YAML frontmatter {context}",
                                auto_fixable=True,
                                issue_type="format",
                            )
                        )

        # Check for HTML line breaks in text fields
        text_fields = ["book_description", "short_book_description"]
        if isinstance(data.get("params"), dict):
            for field in text_fields:
                if field in data["params"]:
                    value = data["params"][field]
                    if isinstance(value, str) and "<br" in value:
                        # Find the line number where this field is defined
                        field_lines = yaml_content.split("\n")
                        for i, line in enumerate(field_lines, start=1):
                            if line.strip().startswith(f"{field}:"):
                                context = f"in {field} at line {i}:\n  {line}"
                                issues.append(
                                    ContentIssue(
                                        file_path=relative_path,
                                        field=field,
                                        message=f"Found HTML line breaks that should be converted to YAML multiline {context}",
                                        auto_fixable=True,
                                        issue_type="format",
                                    )
                                )
                                break

        return issues

def main() -> None:
    project_root = Path(__file__).parent.parent
    content_dir = project_root / "content"
    issues_file = project_root / ".data" / "content_issues.json"

    checker = ContentChecker()
    all_issues: list[ContentIssue] = []
    stats = ValidationStats()

    for locale_dir in content_dir.iterdir():
        if not locale_dir.is_dir():
            continue

        books_dir = locale_dir / "books"
        if not books_dir.exists():
            continue

        print(f"\nChecking {locale_dir.name} books:")
        for file_path in books_dir.glob("*.md"):
            stats.total_files += 1
            relative_path = file_path.relative_to(project_root)
            if issues := checker.check_file(file_path):
                stats.files_with_issues += 1
                print(f"\n{relative_path}:")
                for issue in issues:
                    print(f"  ❌ {issue.message}")
                    stats.issue_types[issue.issue_type] += 1
                    if issue.field:
                        stats.field_issues[issue.field] += 1
                all_issues.extend(issues)

    # Save issues to file
    if all_issues:
        issues_file.parent.mkdir(exist_ok=True)
        issues_data = {
            "timestamp": datetime.now().isoformat(),
            "issues": [issue.to_dict() for issue in all_issues],
        }
        with issues_file.open("w", encoding="utf-8") as f:
            json.dump(issues_data, f, indent=2, ensure_ascii=False)
        print(f"\nIssues have been logged to {issues_file}")
        print_stats(stats)
    else:
        print("\nNo issues found!")
        if issues_file.exists():
            issues_file.unlink()

if __name__ == "__main__":
    main()
