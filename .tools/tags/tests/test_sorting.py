#!/usr/bin/env python3

import pytest
import json
import tomllib
from pathlib import Path
from tags.sorting import sort_mapping, sort_colors


@pytest.fixture
def test_mapping_file(tmp_path):
    """Create a test mapping file with unsorted content"""
    mapping = {"zebra": "Zebra", "apple": "Apple", "banana": "Banana"}
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(json.dumps(mapping))
    return mapping_file


def test_sort_mapping(tmp_path):
    """Test sorting mapping file."""
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text('{"c": 1, "a": 2, "b": 3}')

    sort_mapping(mapping_file)

    with open(mapping_file) as f:
        sorted_mapping = json.load(f)
        assert list(sorted_mapping.keys()) == ["a", "b", "c"]


def test_sort_colors(tmp_path):
    """Test sorting colors file."""
    colors_file = tmp_path / "colors.toml"
    colors_file.write_text('''
["Genres"]
"horror" = "forest"
"fantasy" = "forest"

["Cultural and Geographic"]
"Venice" = "deep-blue"
"Africa" = "deep-blue"
''')

    sort_colors(colors_file)

    with open(colors_file, "rb") as f:
        sorted_colors = tomllib.load(f)
        assert list(sorted_colors["Genres"].keys()) == ["fantasy", "horror"]
        assert list(sorted_colors["Cultural and Geographic"].keys()) == ["Africa", "Venice"]


def test_sort_mapping_preserves_content(test_mapping_file):
    """Test that sorting preserves all content and just reorders it"""
    # Read original content
    with open(test_mapping_file) as f:
        original = json.load(f)

    # Sort the mapping file
    sort_mapping(test_mapping_file)

    # Read sorted content
    with open(test_mapping_file) as f:
        sorted_content = json.load(f)

    # Check that no data was lost or modified
    assert set(original.keys()) == set(sorted_content.keys())
    assert all(original[k] == sorted_content[k] for k in original)
