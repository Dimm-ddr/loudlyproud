#!/usr/bin/env python3

import pytest
import json
from tags.monitor import extract_tags_from_file, find_unmapped_tags, update_tags_report


@pytest.fixture
def test_data(tmp_path):
    """Create test data structure with books and tag configurations"""
    # Create book content
    book_content = """---
params:
  tags:
    - "fiction"
    - "romance"
    - "unmapped tag"
---
Book content
"""
    books_dir = tmp_path / "content" / "ru" / "books"
    books_dir.mkdir(parents=True)
    (books_dir / "test-book.md").write_text(book_content)

    # Create mapping.json
    mapping = {"fiction": "fiction", "romance": "romance", "unused tag": "unused tag"}
    mapping_file = tmp_path / "data" / "tags" / "mapping.json"
    mapping_file.parent.mkdir(parents=True)
    mapping_file.write_text(json.dumps(mapping))

    return tmp_path


def test_extract_tags(test_data):
    """Test extracting tags from books"""
    book_file = test_data / "content" / "ru" / "books" / "test-book.md"
    tags = extract_tags_from_file(book_file)
    assert "fiction" in tags
    assert "romance" in tags
    assert "unmapped tag" in tags


def test_find_unmapped_tags(test_data):
    """Test finding tags that are used in books but not in mapping"""
    tags = ["fiction", "romance", "unmapped tag"]
    mapping = {"fiction": "fiction", "romance": "romance"}
    valid_colors = {"fiction", "romance"}
    unmapped = find_unmapped_tags(tags, mapping, valid_colors)
    assert "unmapped tag" in unmapped
    assert "fiction" not in unmapped
    assert "romance" not in unmapped


def test_update_tags_report(test_data):
    """Test report generation"""
    new_tags = {
        "book1.md": ["new tag1", "new tag2"],
        "book2.md": ["new tag1", "new tag3"],
    }
    report = {"unprocessed_tags": {}, "processed_tags": {}}

    updated_report = update_tags_report(new_tags, report)

    assert "new tag1" in str(updated_report["unprocessed_tags"])
    assert len(updated_report["unprocessed_tags"]["new tag1"]["files"]) == 2
    assert updated_report["unprocessed_tags"]["new tag1"]["occurrences"] == 2
