#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from typing import Any, NotRequired, TypedDict
from dataclasses import dataclass, field
from collections import Counter
from ruamel.yaml import YAML
from book_schema import SCHEMA
import json


@dataclass
class ContentIssue:
    """Represents a content validation issue."""

    file_path: str
    issue_type: str
    message: str
    field: str | None = None
    auto_fixable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "issue_type": self.issue_type,
            "message": self.message,
            "field": self.field,
            "auto_fixable": self.auto_fixable,
        }


class FieldDefinition(TypedDict):
    type: str
    format: NotRequired[str]
    enum: NotRequired[list[str]]
    item_type: NotRequired[str]
    properties: NotRequired[dict[str, "FieldDefinition"]]
    description: NotRequired[str]


def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def is_valid_date(date_str: str) -> bool:
    """Check if string is a valid date in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except:
        return False


def is_valid_isbn(isbn: str) -> bool:
    """Check if string is a valid ISBN-10 or ISBN-13."""
    # Implement ISBN validation logic here
    return True


def validate_value(
    value: Any, field_type: str, field_def: FieldDefinition
) -> str | None:
    """Validate a single value against its type definition."""
    match field_type:
        case "string":
            if not isinstance(value, str):
                if field_def.get("format") == "isbn":
                    # Special case for ISBNs - can be fixed by converting to string
                    return "Must be a string (currently a number)"
                return "Must be a string"
            # Check format if specified
            match field_def.get("format"):
                case "url" if not is_valid_url(value):
                    return "Must be a valid URL"
                case "date" if not is_valid_date(value):
                    return "Must be a valid date in YYYY-MM-DD format"
                case "isbn" if not is_valid_isbn(value):
                    return "Must be a valid ISBN-10 or ISBN-13"

        case "boolean":
            if not isinstance(value, bool):
                return "Must be a boolean"

        case "array":
            if not isinstance(value, list):
                return "Must be a list"

            match field_def.get("item_type"):
                case "object":
                    # Validate each object in array
                    properties = field_def.get("properties", {})
                    for item in value:
                        if not isinstance(item, dict):
                            return "Array item must be an object"
                        for prop_name, prop_def in properties.items():
                            if prop_name in item:
                                if error := validate_value(
                                    item[prop_name], prop_def["type"], prop_def
                                ):
                                    return f"Invalid {prop_name}: {error}"
                case item_type:
                    for item in value:
                        if error := validate_value(item, item_type, {}):
                            return f"List item error: {error}"

        case "object":
            if not isinstance(value, dict):
                return "Must be an object"

    if enum_values := field_def.get("enum"):
        if value not in enum_values:
            return f"Must be one of: {', '.join(str(v) for v in enum_values)}"

    return None


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

    def check_file(self, file_path: Path) -> list[ContentIssue]:
        """Validate a single file and return list of issues."""
        issues: list[ContentIssue] = []
        relative_path = str(file_path)

        try:
            content = file_path.read_text(encoding="utf-8")

            # Extract frontmatter
            match content.split("---\n", 2):
                case ["", frontmatter, *rest] if rest:
                    try:
                        yaml = YAML()
                        yaml.preserve_quotes = True
                        data = yaml.load(frontmatter)
                    except Exception as e:
                        issues.append(ContentIssue(relative_path, "yaml_error", str(e)))
                        return issues
                case _:
                    issues.append(
                        ContentIssue(
                            relative_path,
                            "format_error",
                            "Invalid markdown frontmatter format",
                        )
                    )
                    return issues

            # Basic structure validation
            if not isinstance(data, dict):
                issues.append(
                    ContentIssue(
                        relative_path, "format_error", "Content must be a YAML mapping"
                    )
                )
                return issues

            # Required fields
            for field in self.schema["required_fields"]:
                if field not in data:
                    issues.append(
                        ContentIssue(
                            relative_path,
                            "missing_field",
                            f"Missing required field: {field}",
                            field=field,
                        )
                    )

            # Field validation
            for field, value in data.items():
                if field_def := self.schema["field_types"].get(field):
                    if field_type := field_def.get("type"):
                        if error := validate_value(value, field_type, field_def):
                            auto_fixable = field_def.get(
                                "format"
                            ) == "isbn" and not isinstance(value, str)
                            issues.append(
                                ContentIssue(
                                    relative_path,
                                    "validation_error",
                                    f"Field '{field}': {error}",
                                    field=field,
                                    auto_fixable=auto_fixable,
                                )
                            )

            # Params validation
            if "params" in data and isinstance(data["params"], dict):
                params = data["params"]
                params_schema = self.schema["params"]

                # Required params fields
                for field in params_schema["required_fields"]:
                    if field not in params:
                        issues.append(
                            ContentIssue(
                                relative_path,
                                "missing_field",
                                f"Missing required params field: {field}",
                                field=f"params.{field}",
                            )
                        )

                # Params field validation
                for field, value in params.items():
                    if field_def := params_schema["field_types"].get(field):
                        if field_type := field_def.get("type"):
                            if error := validate_value(value, field_type, field_def):
                                issues.append(
                                    ContentIssue(
                                        relative_path,
                                        "validation_error",
                                        f"Field 'params.{field}': {error}",
                                        field=f"params.{field}",
                                    )
                                )

                # Special checks for languages field
                if "languages" in params:
                    match params["languages"]:
                        case str():
                            issues.append(
                                ContentIssue(
                                    relative_path,
                                    "format_error",
                                    "'languages' should be a list, not a string",
                                    field="languages",
                                    auto_fixable=True,
                                )
                            )
                        case list() as langs:
                            for lang in langs:
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

                if "russian_audioversion" in params:
                    if isinstance(params["russian_audioversion"], str):
                        issues.append(
                            ContentIssue(
                                relative_path,
                                "format_error",
                                "'russian_audioversion' should be a boolean, not a string",
                                field="params.russian_audioversion",
                                auto_fixable=True,
                            )
                        )

            # Check multi-line strings
            multiline_issues = self.check_multiline_strings(data)
            for issue in multiline_issues:
                issue.file_path = relative_path
                issues.append(issue)

            # Check content issues
            content_issues = self.check_content_issues(data)
            for issue in content_issues:
                issue.file_path = relative_path
                issues.append(issue)

        except Exception as e:
            issues.append(
                ContentIssue(relative_path, "error", f"Error processing file: {str(e)}")
            )

        return issues

    def check_multiline_strings(self, data: dict, field_path: str = "") -> list[ContentIssue]:
        """Check for improperly formatted multi-line strings."""
        issues = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{field_path}.{key}" if field_path else key
                if isinstance(value, str) and '\n' in value:
                    # Multi-line string found, check if it's properly formatted
                    if any(not line.startswith('  ') for line in value.split('\n')[1:]):
                        issues.append(ContentIssue(
                            file_path="",  # Will be set later
                            issue_type="format_error",
                            message=f"Multi-line string in field '{current_path}' needs proper indentation",
                            field=current_path,
                            auto_fixable=False
                        ))
                elif isinstance(value, (dict, list)):
                    issues.extend(self.check_multiline_strings(value, current_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    issues.extend(self.check_multiline_strings(item, field_path))

        return issues

    def check_content_issues(self, data: dict, field_path: str = "") -> list[ContentIssue]:
        """Check for various content issues that might cause YAML problems."""
        issues = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{field_path}.{key}" if field_path else key
                if isinstance(value, str):
                    # Check for potentially problematic characters
                    if '&' in value:
                        issues.append(ContentIssue(
                            file_path="",
                            issue_type="content_warning",
                            message=f"Field '{current_path}' contains ampersand which might cause YAML issues",
                            field=current_path,
                            auto_fixable=True
                        ))

                if isinstance(value, (dict, list)):
                    issues.extend(self.check_content_issues(value, current_path))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    issues.extend(self.check_content_issues(item, field_path))

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
