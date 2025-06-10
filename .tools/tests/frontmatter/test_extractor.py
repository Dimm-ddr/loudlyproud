"""
Tests for the frontmatter extractor module.
"""
from pathlib import Path

import pytest

from frontmatter.extractor import extract_frontmatter, FrontmatterExtractionError


def test_extract_valid_frontmatter(temp_dir: Path) -> None:
    """Test extracting valid frontmatter from markdown file."""
    content = """---
title: "Sample Book"
draft: false
params:
  authors: ["John Doe"]
  book_title: "The Sample Book"
  tags: ["fiction", "test"]
---

# Sample Book Content
Some content here.
"""
    test_file = temp_dir / "test.md"
    test_file.write_text(content)
    
    result = extract_frontmatter(test_file)
    
    assert result.frontmatter["title"] == "Sample Book"
    assert result.frontmatter["draft"] is False
    assert result.frontmatter["params"]["authors"] == ["John Doe"]
    assert "# Sample Book Content" in result.body


def test_extract_invalid_frontmatter(temp_dir: Path) -> None:
    """Test extracting invalid frontmatter raises appropriate error."""
    content = """---
title: "Test Book"
draft: "not_a_boolean"  # Invalid type
type: "wrong_type"      # Should be "books"
---

Content
"""
    test_file = temp_dir / "test.md"
    test_file.write_text(content)
    
    with pytest.raises(FrontmatterExtractionError):
        extract_frontmatter(test_file)


def test_extract_missing_frontmatter(temp_dir: Path) -> None:
    """Test file without frontmatter raises appropriate error."""
    content = "# Just markdown content without frontmatter"
    test_file = temp_dir / "test.md"
    test_file.write_text(content)
    
    with pytest.raises(FrontmatterExtractionError):
        extract_frontmatter(test_file)


def test_extract_hugo_incompatible_yaml(temp_dir: Path) -> None:
    """Test Hugo-incompatible YAML features raise appropriate error."""
    content = """---
title: &title "Test Book"
slug: *title
---

Content
"""
    test_file = temp_dir / "test.md"
    test_file.write_text(content)
    
    with pytest.raises(FrontmatterExtractionError):
        extract_frontmatter(test_file) 