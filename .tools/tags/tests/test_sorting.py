#!/usr/bin/env python3

import pytest
import json
from tags.sorting import sort_mapping


@pytest.fixture
def test_mapping_file(tmp_path):
    """Create a test mapping file with unsorted content"""
    mapping = {"zebra": "Zebra", "apple": "Apple", "banana": "Banana"}
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text(json.dumps(mapping))
    return mapping_file


def test_sort_mapping(test_mapping_file):
    """Test that mapping file gets sorted alphabetically"""
    # Sort the mapping file
    sort_mapping(test_mapping_file)

    # Read the sorted file
    with open(test_mapping_file) as f:
        content = f.read()

    # Check that keys appear in alphabetical order in the file
    key_positions = {
        key: content.index(f'"{key}"') for key in ["apple", "banana", "zebra"]
    }

    assert key_positions["apple"] < key_positions["banana"] < key_positions["zebra"]


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
