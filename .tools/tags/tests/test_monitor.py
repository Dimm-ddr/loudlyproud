#!/usr/bin/env python3

import pytest
from tags.monitor import update_tags_report
from tags.validate import validate_tags


@pytest.fixture
def test_book_file(tmp_path):
    """Create a test book file with tags."""
    book_file = tmp_path / "test-book.md"
    book_file.write_text("""---
params:
  tags:
    - "known tag"
    - "unknown tag"
---
Book content
""")
    return book_file


def test_validate_tags_with_unmapped(tmp_path):
    """Test validation finds unmapped tags."""
    # Create test project structure
    (tmp_path / "content" / "en" / "books").mkdir(parents=True)
    book_file = tmp_path / "content" / "en" / "books" / "test.md"
    book_file.write_text("""---
params:
  tags: ["known tag", "unknown tag"]
---
""")

    # Create mapping file
    mapping_file = tmp_path / "data" / "tags" / "mapping.json"
    mapping_file.parent.mkdir(parents=True)
    mapping_file.write_text('{"known tag": "Known Tag"}')

    # Create colors file
    colors_file = tmp_path / "data" / "tags" / "colors.toml"
    colors_file.write_text('''
["Test Category"]
"Known Tag" = "test-color"
''')

    report = validate_tags(tmp_path)
    assert "unknown tag" in report["unmapped_tags"]
    assert "known tag" not in report["unmapped_tags"]


def test_update_tags_report():
    """Test updating tags report."""
    new_tags = {
        "file1.md": ["tag1", "tag2"],
        "file2.md": ["tag2", "tag3"]
    }
    report = {
        "unprocessed_tags": {},
        "processed_tags": {}
    }

    updated = update_tags_report(new_tags, report)

    assert "tag1" in updated["unprocessed_tags"]
    assert "tag2" in updated["unprocessed_tags"]
    assert "tag3" in updated["unprocessed_tags"]

    tag2_info = updated["unprocessed_tags"]["tag2"]
    assert len(tag2_info["files"]) == 2
    assert tag2_info["occurrences"] == 2
