#!/usr/bin/env python3

import json
import pytest
from tags.validate import (
    validate_tags,
    load_tags_map,
    load_color_mapping,
    extract_tags_from_file,
)
from .test_helpers import detailed_assert, with_context


@pytest.fixture
def test_project_dir(tmp_path):
    """Create test project directory with required files"""
    # Create mapping.json
    mapping = {
        "romance": "romance",
        "venice": "Venice",
        "italy": "Italy",
        "fiction": "fiction"
    }
    mapping_file = tmp_path / "data" / "tags" / "mapping.json"
    mapping_file.parent.mkdir(parents=True)
    mapping_file.write_text(json.dumps(mapping))

    # Create colors.toml with proper categories
    colors_file = tmp_path / "data" / "tags" / "colors.toml"
    colors_file.write_text('''
    ["Genres"]
    "romance" = "forest"

    ["Cultural and Geographic"]
    "Venice" = "deep-blue"
    "Italy" = "deep-blue"

    ["Literary Classifications"]
    "fiction" = "aubergine"
    ''')

    # Create test book with unmapped tag
    book_content = """---
params:
  tags:
    - "fiction"
    - "romance"
    - "unknown tag"
---
Book content
"""
    book_dir = tmp_path / "content" / "en" / "books"
    book_dir.mkdir(parents=True)
    book_file = book_dir / "test-book.md"
    book_file.write_text(book_content)

    return tmp_path


@with_context
def test_validate_tags(test_project_dir):
    """Test tag validation"""
    report = validate_tags(test_project_dir)
    color_mapping = load_color_mapping(test_project_dir)
    tags_map = load_tags_map(test_project_dir)

    detailed_assert(
        "unmapped tags detection",
        "unknown tag",
        True,
        "unknown tag" in report["unmapped_tags"],
        report=report
    )

    missing_colors = [
        tag for tag in tags_map.values()
        if tag.lower() not in {c.lower() for c in color_mapping}
    ]

    detailed_assert(
        "color mapping completeness",
        tags_map.values(),
        [],
        missing_colors,
        available_colors=sorted(color_mapping),
        tags_needing_colors=sorted(tags_map.values())
    )


def test_load_tags_map(test_project_dir):
    """Test loading tags mapping"""
    tags_map = load_tags_map(test_project_dir)
    assert "romance" in tags_map
    assert "venice" in tags_map
    assert "italy" in tags_map


@pytest.fixture
def mock_colors_toml(tmp_path):
    """Create a mock colors.toml file."""
    colors_file = tmp_path / "data" / "tags" / "colors.toml"
    colors_file.parent.mkdir(parents=True)
    colors_file.write_text('''
["Genres"]
"fantasy" = "forest"
"science fiction" = "forest"

["Cultural and Geographic"]
"American fiction" = "deep-blue"
"British literature" = "deep-blue"
''')
    return colors_file


def test_load_color_mapping(mock_colors_toml):
    """Test loading color mapping from TOML file."""
    colors = load_color_mapping(mock_colors_toml.parent.parent.parent)
    assert colors == {
        "fantasy",
        "science fiction",
        "American fiction",
        "British literature"
    }


def test_validate_tags_with_colors(tmp_path, mock_colors_toml):
    """Test tag validation with color mapping."""
    # Create mock mapping file
    mapping_file = tmp_path / "data" / "tags" / "mapping.json"
    mapping_file.parent.mkdir(parents=True, exist_ok=True)
    mapping_file.write_text('''{
        "fantasy": "fantasy",
        "science fiction": "science fiction",
        "american fiction": "American fiction",
        "british literature": "British literature",
        "unmapped tag": "unmapped tag"
    }''')

    # Create mock content file
    content_dir = tmp_path / "content"
    content_dir.mkdir(parents=True)
    (content_dir / "books").mkdir()
    (content_dir / "books" / "test.md").write_text('''---
params:
  tags: ["fantasy", "unmapped tag"]
---
''')

    report = validate_tags(tmp_path)
    assert "unmapped tag" in report["uncolored_tags"]
    assert "fantasy" not in report["uncolored_tags"]


@pytest.mark.parametrize(
    "content,expected",
    [
        (
            """---
params: "not a dictionary"
---
""",
            [],
        ),
        (
            """---
params:
  tags: "not a list"
---
""",
            [],
        ),
        (
            """---
no_params: true
---
""",
            [],
        ),
        (
            "Not a YAML content",
            [],
        ),
        (
            """---
params:
  tags:
    - "valid tag"
  other: value
---
""",
            ["valid tag"],
        ),
    ],
)
def test_extract_tags_invalid_frontmatter(tmp_path, content, expected):
    """Test extracting tags with various invalid frontmatter structures."""
    book_file = tmp_path / "test.md"
    book_file.write_text(content)
    assert extract_tags_from_file(book_file) == expected


def test_extract_tags_missing_file(tmp_path):
    """Test extracting tags from non-existent file."""
    non_existent = tmp_path / "does_not_exist.md"
    assert extract_tags_from_file(non_existent) == []


def test_extract_tags_invalid_encoding(tmp_path):
    """Test extracting tags from file with invalid encoding."""
    book_file = tmp_path / "test.md"
    # Write bytes that are not valid UTF-8
    book_file.write_bytes(b"\xFF\xFE Invalid UTF-8 content")
    assert extract_tags_from_file(book_file) == []
