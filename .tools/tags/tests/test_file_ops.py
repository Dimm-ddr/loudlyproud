#!/usr/bin/env python3

from pathlib import Path
from ..file_ops import (
    load_patterns,
    write_frontmatter,
)


def test_load_patterns_error_cases(tmp_path: Path):
    # Non-existent file
    nonexistent = tmp_path / "nonexistent.yaml"
    assert load_patterns(nonexistent) == {}

    # Invalid YAML
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("invalid: [yaml: content")
    assert load_patterns(invalid) == {}


def test_write_frontmatter_error_cases(tmp_path: Path):
    file_path = tmp_path / "test.md"

    # Invalid frontmatter structure (missing required fields)
    frontmatter = {
        "invalid": None,
        # Missing required fields like type, params, etc.
    }
    assert not write_frontmatter(file_path, frontmatter, "content")

    # Invalid frontmatter structure (missing tags in params)
    frontmatter = {
        "type": "books",
        "params": {
            "authors": [],
            # Missing tags
        },
    }
    assert not write_frontmatter(file_path, frontmatter, "content")

    # Permission error simulation (if possible on your system)
    # This might be system-dependent and could be skipped
    if hasattr(file_path, "chmod"):
        file_path.touch()
        file_path.chmod(0o444)  # Read-only
        assert not write_frontmatter(file_path, {"valid": "content"}, "body")
