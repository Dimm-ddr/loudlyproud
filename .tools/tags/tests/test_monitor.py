#!/usr/bin/env python3

import pytest
from pathlib import Path
from tags.monitor import update_tags_report
from tags.validate import validate_tags
from tags.file_ops import write_mapping_file, write_colors_file
from tags.common import CONTENT_DIR, DATA_DIR, MAPPING_FILENAME, COLORS_FILENAME


@pytest.fixture
def test_book_file(tmp_path):
    """Create a test book file with tags."""
    book_file = tmp_path / "test-book.md"
    book_file.write_text(
        """---
params:
  tags:
    - "known tag"
    - "unknown tag"
---
Book content
"""
    )
    return book_file


def test_validate_tags_with_unmapped(test_project: Path):
    """Test validation report with unmapped tags."""
    # Create test book files structure
    books_dir = test_project / "content" / "en" / "books"
    books_dir.mkdir(parents=True)

    # Create test data directory
    data_dir = test_project / "data" / "tags"
    data_dir.mkdir(parents=True)

    # Create a few test book files with known tags
    book1_content = """---
params:
  tags:
    - "mapped tag"
    - "unknown tag"
    - "another unknown"
---
"""
    (books_dir / "book1.md").write_text(book1_content)

    # Create test mapping file with only one of the tags
    mapping = {"mapped tag": "Mapped Tag"}
    mapping_file = data_dir / MAPPING_FILENAME
    mapping_file.parent.mkdir(parents=True, exist_ok=True)
    write_mapping_file(mapping_file, mapping)

    # Create test colors file
    colors = {"Genres": {"Mapped Tag": "forest"}}
    colors_file = data_dir / COLORS_FILENAME
    write_colors_file(colors_file, colors)

    # Validate tags in the test content directory
    content_dir = test_project / "content"
    report = validate_tags(
        test_project,
        content_path=content_dir,
        mapping_file=mapping_file,
        colors_file=colors_file,
    )

    # Now we should only see our test tags
    assert set(report["unmapped_tags"]) == {"unknown tag", "another unknown"}
    assert "mapped tag" not in report["unmapped_tags"]


def test_update_tags_report():
    """Test updating tags report."""
    new_tags = {"file1.md": ["tag1", "tag2"], "file2.md": ["tag2", "tag3"]}
    report = {"unprocessed_tags": {}, "processed_tags": {}}

    updated = update_tags_report(new_tags, report)

    assert "tag1" in updated["unprocessed_tags"]
    assert "tag2" in updated["unprocessed_tags"]
    assert "tag3" in updated["unprocessed_tags"]

    tag2_info = updated["unprocessed_tags"]["tag2"]
    assert len(tag2_info["files"]) == 2
    assert tag2_info["occurrences"] == 2
