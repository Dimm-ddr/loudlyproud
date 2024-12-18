#!/usr/bin/env python3

import pytest
from tags.validate import validate_tags
from tags.file_ops import (
    extract_tags_from_file,
    write_mapping_file,
    write_colors_file,
)
from tags.common import (
    MAPPING_FILENAME,
    COLORS_FILENAME,
    DATA_DIR,
    CONTENT_DIR,
)


@pytest.fixture
def test_data_dir(tmp_path):
    """Create test data directory with sample files"""
    # Create test book file
    book_content = """---
params:
  tags:
    - "romance"
    - "unknown-tag"
    - "uncolored-tag"
---
Book content
"""
    # Create content directory structure
    book_dir = tmp_path / "content" / "en" / "books"
    book_dir.mkdir(parents=True)
    book_file = book_dir / "test-book.md"
    book_file.write_text(book_content)

    # Create data directory structure
    data_dir = tmp_path / "data" / "tags"
    data_dir.mkdir(parents=True)

    # Create test mapping file
    mapping = {"romance": "Romance", "uncolored-tag": "Uncolored Tag"}
    mapping_file = data_dir / MAPPING_FILENAME
    write_mapping_file(mapping_file, mapping)

    # Create test colors file
    colors = {"Genres": {"Romance": "forest"}}
    colors_file = data_dir / COLORS_FILENAME
    write_colors_file(colors_file, colors)

    return tmp_path


def test_extract_tags_from_file(test_data_dir):
    """Test extracting tags from a book file"""
    book_file = test_data_dir / "content" / "en" / "books" / "test-book.md"
    tags = extract_tags_from_file(book_file)
    assert "romance" in tags
    assert "unknown-tag" in tags
    assert "uncolored-tag" in tags


def test_validate_tags(test_data_dir):
    """Test tag validation"""
    # Get paths to test files
    mapping_file = test_data_dir / "data" / "tags" / MAPPING_FILENAME
    colors_file = test_data_dir / "data" / "tags" / COLORS_FILENAME
    content_dir = test_data_dir / "content"

    validation = validate_tags(
        test_data_dir,
        content_path=content_dir,
        mapping_file=mapping_file,
        colors_file=colors_file,
    )

    print(f"Got validation: {validation}, from folder: {test_data_dir}")
    assert (
        "unknown-tag" in validation["unmapped_tags"]
    ), f"Got unmapped tags: {validation['unmapped_tags']}"
    assert "Uncolored Tag" in validation["uncolored_tags"]
    assert "romance" not in validation["unmapped_tags"]
    assert "Romance" not in validation["uncolored_tags"]
