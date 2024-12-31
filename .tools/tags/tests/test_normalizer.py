#!/usr/bin/env python3

import pytest
from pathlib import Path
from ..normalize import TagNormalizer
from ..file_ops import (
    write_mapping_file,
    write_patterns_file,
    write_removable_tags,
)


@pytest.fixture
def test_mapping() -> dict:
    """Return test mapping data."""
    return {
        "fiction": None,
        "general": None,
        "science fiction": "science fiction",
        "nyt:bestseller": None,
        "test tag": "test tag",
        "american-short-stories": ["american", "short-stories"],
        "detective-and-mystery-stories": ["detective", "mystery"],
        "venice-italy": "venice",
        "contemporary-romance": ["contemporary", "romance"],
    }


@pytest.fixture
def test_patterns() -> dict:
    """Return test patterns data."""
    return {
        "remove": {"prefixes": ["nyt:"], "exact": ["fiction", "general"]},
        "split": {
            "separators": [
                {"pattern": "--", "keep_parts": True},
                {"pattern": r"\(([^)]+)\)", "extract_groups": True},
            ]
        },
        "compounds": {
            "values": [
                {
                    "pattern": r"^young adult fiction (.+)$",
                    "map_to": ["young adult (YA)", "{}"],
                },
                {"pattern": r"^fiction lgbtqia\+ (.+)$", "map_to": ["LGBTQIA+", "{}"]},
                {"pattern": r"^(.+) & (.+)$", "map_to": ["{0}", "{1}"]},
            ]
        },
    }


@pytest.fixture
def normalizer(
    tmp_path: Path, test_mapping: dict, test_patterns: dict
) -> TagNormalizer:
    """Create normalizer with test configuration."""
    data_dir = tmp_path / "data" / "tags"
    data_dir.mkdir(parents=True, exist_ok=True)

    mapping_file = data_dir / "mapping.json"
    patterns_file = data_dir / "patterns.toml"
    to_remove_file = data_dir / "to_remove.toml"

    write_mapping_file(mapping_file, test_mapping)
    write_patterns_file(patterns_file, test_patterns)
    write_removable_tags(to_remove_file, [])

    return TagNormalizer(
        project_root=tmp_path,
        mapping_file=mapping_file,
        patterns_file=patterns_file,
        to_remove_file=to_remove_file,
    )


@pytest.mark.parametrize(
    "input_tags,expected",
    [
        (["fiction"], []),  # Should be removed
        (["general"], []),  # Should be removed
        (["nyt:bestseller"], []),  # Should be removed by prefix
        (["science fiction"], ["science fiction"]),  # Should be kept as is
        (["test tag"], ["test tag"]),  # Should be kept as is
        (
            ["young adult fiction romance"],
            ["young adult (YA)", "romance"],
        ),  # Should be transformed
        (["fiction lgbtqia+ gay"], ["LGBTQIA+", "gay"]),  # Should be transformed
        (["science & fiction"], ["science"]),  # Should be split
        (
            ["american-short-stories"],
            ["american", "short-stories"],
        ),  # Should be split via mapping
        (
            ["detective-and-mystery-stories"],
            ["detective", "mystery"],
        ),  # Should be split via mapping
        (["venice-italy"], ["venice"]),  # Should be mapped to single tag
        (
            ["contemporary-romance"],
            ["contemporary", "romance"],
        ),  # Should be split via mapping
    ],
)
def test_normalize_tags(
    normalizer: TagNormalizer, input_tags: list[str], expected: list[str]
) -> None:
    """Test tag normalization with various inputs."""
    normalized = normalizer.normalize_tags(input_tags)
    assert set(normalized) == set(expected), (
        f"Failed with input_tags={input_tags}\n"
        f"Expected: {expected}\n"
        f"Got: {normalized}"
    )
