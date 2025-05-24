"""
Pytest configuration and fixtures for frontmatter validation tests.
"""
import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest

from frontmatter.types import FileContent, ValidationError, ValidationResult, ErrorSeverity


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def valid_frontmatter() -> dict[str, Any]:
    """Valid frontmatter data for testing."""
    return {
        "title": "Test Book",
        "draft": False,
        "slug": "test-book",
        "type": "books",
        "params": {
            "authors": ["Test Author"],
            "book_title": "Test Book Title"
        }
    }


@pytest.fixture
def invalid_frontmatter() -> dict[str, Any]:
    """Invalid frontmatter data for testing."""
    return {
        "title": "Test Book",
        "draft": "not_a_boolean",  # Should be boolean
        "slug": "test-book",
        "type": "wrong_type",      # Should be "books"
        "unknown_field": "value",  # Unknown field
        "params": {
            "authors": "not_a_list",  # Should be list
            "book_title": "Test Book Title",
            "unknown_param": "value"  # Unknown param
        }
    }


@pytest.fixture
def sample_markdown_content() -> str:
    """Sample markdown content with frontmatter."""
    return """---
title: "Sample Book"
draft: false
slug: "sample-book"
type: "books"
params:
  authors:
    - "John Doe"
  book_title: "Sample Book Title"
---

# Sample Book

This is a sample book content.
"""


@pytest.fixture
def invalid_yaml_content() -> str:
    """Invalid YAML content for testing extraction errors."""
    return """---
title: "Test"
invalid: yaml: structure
---

Content here.
"""


@pytest.fixture
def unsupported_yaml_features() -> list[str]:
    """YAML content with unsupported features."""
    return [
        # YAML anchors
        """---
title: &title "Test"
slug: *title
---""",
        
        # YAML tags
        """---
title: !str "Test"
---""",
        
        # YAML aliases
        """---
base: &base
  key: value
derived:
  <<: *base
---"""
    ]


@pytest.fixture
def where_to_get_data() -> list[dict[str, Any]]:
    """Valid where_to_get data."""
    return [
        {
            "store": "Amazon",
            "link": "https://amazon.com/book",
            "date": "2023-01-01T00:00:00+00:00"
        },
        {
            "store": "Goodreads",
            "link": "https://goodreads.com/book"
        }
    ]


@pytest.fixture
def file_content_factory():
    """Factory for creating FileContent objects."""
    def _create_file_content(
        path: Path | None = None,
        frontmatter: dict[str, Any] | None = None,
        body: str = "",
        raw_frontmatter: str = ""
    ) -> FileContent:
        if path is None:
            path = Path("test.md")
        if frontmatter is None:
            frontmatter = {"title": "Test"}
        return FileContent(
            path=path,
            frontmatter=frontmatter,
            body=body,
            raw_frontmatter=raw_frontmatter
        )
    return _create_file_content


@pytest.fixture
def validation_error_factory():
    """Factory for creating ValidationError objects."""
    def _create_error(
        message: str = "Test error",
        path: list[str] | None = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        fixable: bool = False,
        suggested_fix: Any = None
    ) -> ValidationError:
        if path is None:
            path = ["test"]
        return ValidationError(
            message=message,
            path=path,
            severity=severity,
            fixable=fixable,
            suggested_fix=suggested_fix
        )
    return _create_error


@pytest.fixture
def validation_result_factory():
    """Factory for creating ValidationResult objects."""
    def _create_result(
        path: Path | None = None,
        errors: list[ValidationError] | None = None,
        warnings: list[ValidationError] | None = None
    ) -> ValidationResult:
        if path is None:
            path = Path("test.md")
        if errors is None:
            errors = []
        if warnings is None:
            warnings = []
        return ValidationResult(path=path, errors=errors, warnings=warnings)
    return _create_result 