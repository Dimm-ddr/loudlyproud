#!/usr/bin/env python3

import pytest
from pathlib import Path
from tags.validate import validate_tags, ValidationReport
from tags.file_ops import (
    write_mapping_file,
    write_colors_file,
    write_patterns_file,
    write_removable_tags,
    write_frontmatter,
)


@pytest.fixture
def test_book_frontmatter() -> dict:
    """Return test book frontmatter with tags."""
    return {
        "type": "books",
        "params": {
            "tags": [
                "romance",
                "unknown-tag",
                "uncolored-tag",
                "mapped-tag",
            ],
        },
    }


@pytest.fixture
def test_mapping() -> dict:
    """Return test mapping data."""
    return {
        "romance": "Romance",
        "uncolored-tag": "Uncolored Tag",
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
        "remove": {"prefixes": ["nyt:"], "exact": ["fiction", "general"]},
        "compounds": {
            "values": [
                {
                    "pattern": r"^young adult fiction (.+)$",
                    "map_to": ["young adult (YA)", "{}"],
                }
            ]
        },
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

    # Verify results with detailed error messages
    assert "unknown-tag" in report["unmapped_tags"], (
        f"Expected 'unknown-tag' to be in unmapped_tags.\n"
        f"Book frontmatter tags: {test_book_frontmatter['params']['tags']}\n"
        f"Current unmapped_tags: {report['unmapped_tags']}\n"
        f"Mapping file contents: {mapping_file.read_text()}\n"
        f"Book file contents: {book_file.read_text()}"
    )

    assert "Uncolored Tag" in report["uncolored_tags"], (
        f"Expected 'uncolored-tag' to be in uncolored_tags.\n"
        f"Book frontmatter tags: {test_book_frontmatter['params']['tags']}\n"
        f"Current uncolored_tags: {report['uncolored_tags']}\n"
        f"Colors file contents: {colors_file.read_text()}"
    )

    assert "Mapped Tag" not in report["unmapped_tags"], (
        f"'mapped-tag' should not be in unmapped_tags but was found.\n"
        f"Book frontmatter tags: {test_book_frontmatter['params']['tags']}\n"
        f"Current unmapped_tags: {report['unmapped_tags']}\n"
        f"Mapping file contents: {mapping_file.read_text()}"
    )

    assert "Romance" not in report["unmapped_tags"], (
        f"'romance' should not be in unmapped_tags but was found.\n"
        f"Book frontmatter tags: {test_book_frontmatter['params']['tags']}\n"
        f"Current unmapped_tags: {report['unmapped_tags']}\n"
        f"Mapping file contents: {mapping_file.read_text()}"
    )
