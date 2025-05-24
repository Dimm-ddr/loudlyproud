from typing import Any, NamedTuple
import pytest
from pathlib import Path
from tags.common import DATA_DIR, CONTENT_DIR
from tags.file_ops import write_frontmatter


class TestAssertContext(NamedTuple):
    """Context for test execution with detailed reporting."""

    test_name: str
    input_value: Any
    expected: Any
    actual: Any
    extra_info: dict[str, Any]


@pytest.fixture
def assert_context():
    """Fixture providing test assertion context."""

    def _make_context(
        test_name: str, input_value: Any, expected: Any, actual: Any, **extra_info: Any
    ) -> TestAssertContext:
        return TestAssertContext(
            test_name=test_name,
            input_value=input_value,
            expected=expected,
            actual=actual,
            extra_info=extra_info,
        )

    return _make_context


@pytest.fixture
def test_project(tmp_path: Path, monkeypatch):
    """Create a test project structure with isolated test files."""
    # Create data directory
    test_data_dir = tmp_path / DATA_DIR.name
    test_data_dir.mkdir(parents=True)

    # Create content directory
    test_content_dir = tmp_path / CONTENT_DIR.name
    test_content_dir.mkdir(parents=True)

    # Patch DATA_DIR to point to our test directory
    monkeypatch.setattr("tags.common.DATA_DIR", test_data_dir)

    return tmp_path


@pytest.fixture
def test_data_dir(test_project):
    """Alias for test_project for backward compatibility."""
    return test_project


@pytest.fixture
def test_book_file(test_data_dir: Path, test_book_frontmatter: dict) -> Path:
    """Create a test book file with tags.

    Args:
        test_data_dir: The test data directory
        test_book_frontmatter: The frontmatter content for the book file

    Returns:
        Path to the created book file
    """
    content_dir = test_data_dir.parent.parent / "content"
    book_dir = content_dir / "en" / "books"
    book_dir.mkdir(parents=True, exist_ok=True)
    book_file = book_dir / "test-book.md"
    write_frontmatter(book_file, test_book_frontmatter, "Book content\n")
    return book_file


# Add if any new fixtures are needed for clean.py tests
