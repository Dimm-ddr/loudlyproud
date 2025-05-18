#!/usr/bin/env python3

import pytest
from pathlib import Path
from tags.monitor import update_tags_report
from tags.validate import validate_tags
from tags.file_ops import (
    write_mapping_file,
    write_colors_file,
    write_patterns_file,
    write_removable_tags,
    write_frontmatter,
    TagsReport,
)


@pytest.fixture
def test_mapping() -> dict:
    """Return test mapping data."""
    return {
        "mapped-tag": "Mapped Tag",
    }


@pytest.fixture
def test_colors() -> dict:
    """Return test colors data."""
    return {
        "romance": {
            "color": "#FF0000",
            "category": "test",
        }
    }


@pytest.fixture
def test_patterns() -> dict:
    """Return test patterns data."""
    return {
        "remove": {"prefixes": []},
        "split": {"separators": []},
        "compounds": {"values": []},
    }


@pytest.fixture
def test_files(
    test_data_dir: Path,
    test_mapping: dict,
    test_colors: dict,
    test_patterns: dict,
) -> tuple[Path, Path, Path, Path]:
    """Create and write all test files."""
    mapping_file = test_data_dir / "mapping.json"
    colors_file = test_data_dir / "colors.toml"
    patterns_file = test_data_dir / "patterns.toml"
    to_remove_file = test_data_dir / "to_remove.toml"

    write_mapping_file(mapping_file, test_mapping)
    write_colors_file(colors_file, test_colors)
    write_patterns_file(patterns_file, test_patterns)
    write_removable_tags(to_remove_file, [])

    return mapping_file, colors_file, patterns_file, to_remove_file


@pytest.fixture
def test_book_frontmatter() -> dict:
    """Return test book frontmatter with tags."""
    return {
        "type": "books",
        "params": {
            "tags": [
                "mapped-tag",
                "unmapped-tag",
            ],
        },
    }


def test_update_tags_report() -> None:
    """Test updating tags report."""
    # Test data
    new_tags = {
        "file1.md": ["tag1", "tag2"],
        "file2.md": ["tag2", "tag3"],
    }
    report: TagsReport = {
        "unprocessed_tags": {},
        "processed_tags": {},
    }

    # Update report
    updated = update_tags_report(new_tags, report)

    # Verify results
    assert "tag1" in updated["unprocessed_tags"]
    assert "tag2" in updated["unprocessed_tags"]
    assert "tag3" in updated["unprocessed_tags"]

    # Check tag2 which appears in multiple files
    tag2_info = updated["unprocessed_tags"]["tag2"]
    assert len(tag2_info["files"]) == 2
    assert tag2_info["occurrences"] == 2


def test_validate_tags_with_unmapped(
    test_book_file: Path,
    test_files: tuple[Path, Path, Path, Path],
    test_book_frontmatter: dict,
) -> None:
    """Test validating tags with unmapped tags."""
    mapping_file, colors_file, patterns_file, to_remove_file = test_files
    content_dir = (
        test_book_file.parent.parent
    )  # Go up one more level to create books dir
    books_dir = content_dir / "books"
    books_dir.mkdir(parents=True, exist_ok=True)
    book_file = books_dir / "test_book.md"

    # Write test book file
    write_frontmatter(book_file, test_book_frontmatter, "Test book content.\n")

    # Run validation
    report = validate_tags(
        content_dir,
        content_path=content_dir,
        mapping_file=mapping_file,
        colors_file=colors_file,
        patterns_file=patterns_file,
        to_remove_file=to_remove_file,
    )

    # Verify results
    assert "unmapped-tag" in report["unmapped_tags"], (
        f"Expected 'unmapped-tag' to be in unmapped_tags. "
        f"Current unmapped_tags: {report['unmapped_tags']}, "
        f"Mapping file contents: {mapping_file.read_text()}"
    )

    assert "mapped-tag" not in report["unmapped_tags"], (
        f"'mapped-tag' should not be in unmapped_tags but was found. "
        f"Current unmapped_tags: {report['unmapped_tags']}, "
        f"Mapping file contents: {mapping_file.read_text()}"
    )
