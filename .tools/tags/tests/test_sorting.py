#!/usr/bin/env python3

import pytest
from tags.sorting import sort_mapping_file, sort_colors_file
from tags.file_ops import (
    load_tags_map,
    load_colors_file,
    write_mapping_file,
    write_colors_file,
)
from tags.common import MAPPING_FILE, COLORS_FILE


@pytest.fixture
def test_files(tmp_path):
    """Create test files with unsorted content"""
    # Create test mapping file
    mapping = {"zebra": "Zebra", "apple": "Apple", "banana": "Banana"}
    mapping_file = tmp_path / MAPPING_FILE.name
    write_mapping_file(mapping_file, mapping)

    # Create test colors file
    colors = {
        "Section B": {"zebra": "blue", "apple": "red"},
        "Section A": {"dog": "brown", "cat": "black"},
    }
    colors_file = tmp_path / COLORS_FILE.name
    write_colors_file(colors_file, colors)

    return mapping_file, colors_file


def test_sort_mapping_file(test_files):
    """Test sorting mapping file"""
    mapping_file, _ = test_files

    # Sort the file
    sort_mapping_file(mapping_file)

    # Verify the result
    sorted_mapping = load_tags_map(mapping_file)

    # Check if keys are sorted
    keys = list(sorted_mapping.keys())
    assert keys == sorted(keys)


def test_sort_colors_file(test_files):
    """Test sorting colors file"""
    _, colors_file = test_files

    # Sort the file
    sort_colors_file(colors_file)

    # Verify the result
    sorted_colors = load_colors_file(colors_file)

    # Check if sections are sorted
    sections = list(sorted_colors.keys())
    assert sections == sorted(sections)

    # Check if tags within sections are sorted
    for section in sorted_colors:
        tags = list(sorted_colors[section].keys())
        assert tags == sorted(tags)
