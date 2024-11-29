#!/usr/bin/env python3

from pathlib import Path
import yaml
from datetime import datetime
from urllib.parse import urlparse
from typing import Any, NotRequired, TypedDict
from dataclasses import dataclass, field
from book_schema import SCHEMA
import json
from collections import Counter


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
    properties: NotRequired[dict[str, 'FieldDefinition']]
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
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except:
        return False


def validate_value(value: Any, field_type: str, field_def: FieldDefinition) -> str | None:
    """Validate a single value against its type definition."""
    match field_type:
        case "string":
            if not isinstance(value, str):
                return "Must be a string"
            # Check format if specified
            match field_def.get("format"):
                case "url" if not is_valid_url(value):
                    return "Must be a valid URL"
                case "date" if not is_valid_date(value):
                    return "Must be a valid date in YYYY-MM-DD format"

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
                                    item[prop_name],
                                    prop_def["type"],
                                    prop_def
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
            parts = content.split("---", 2)
            if len(parts) < 3:
                issues.append(ContentIssue(
                    relative_path,
                    "format_error",
                    "Invalid markdown frontmatter format"
                ))
                return issues

            # Parse only the frontmatter part
            try:
                data = yaml.safe_load(parts[1])
            except yaml.YAMLError as e:
                issues.append(ContentIssue(relative_path, "yaml_error", str(e)))
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
                            issues.append(
                                ContentIssue(
                                    relative_path,
                                    "validation_error",
                                    f"Field '{field}': {error}",
                                    field=field,
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
                                auto_fixable=True
                            )
                        )

        except Exception as e:
            issues.append(
                ContentIssue(relative_path, "error", f"Error processing file: {str(e)}")
            )

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
            "issues": [issue.to_dict() for issue in all_issues]
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
