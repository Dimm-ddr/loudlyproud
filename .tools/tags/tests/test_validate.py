#!/usr/bin/env python3

import json
import pytest
from ruamel.yaml import YAML
from tags.validate import validate_tags, load_tags_map, load_color_mapping
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

    # Create colors.yaml with proper capitalization
    colors = {
        "tag_colors": {
            "romance": "#ff0000",
            "Venice": "#00ff00",
            "Italy": "#0000ff",
            "fiction": "#cccccc"
        }
    }
    colors_file = tmp_path / "data" / "tags" / "colors.yaml"
    yaml = YAML()
    with colors_file.open("w") as f:
        yaml.dump(colors, f)

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


def test_load_color_mapping(test_project_dir):
    """Test loading color mapping"""
    colors = load_color_mapping(test_project_dir)
    # Colors should be case-insensitive
    assert "venice" in colors
    assert "italy" in colors
    assert "romance" in colors
