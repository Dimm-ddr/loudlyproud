"""
Tests for the file scanner module.
"""
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from frontmatter.scanner import scan_markdown_files, get_all_markdown_files


class TestScanMarkdownFiles:
    """Test the scan_markdown_files function."""
    
    def test_scan_finds_markdown_files(self, temp_dir: Path) -> None:
        """Test that scanner finds markdown files in configured directories."""
        # Create test directory structure
        content_dir = temp_dir / "content" / "en" / "books"
        content_dir.mkdir(parents=True)
        
        # Create markdown files
        (content_dir / "book1.md").write_text("# Book 1")
        (content_dir / "book2.md").write_text("# Book 2")
        (content_dir / "subdir").mkdir()
        (content_dir / "subdir" / "book3.md").write_text("# Book 3")
        
        # Create non-markdown files
        (content_dir / "not_markdown.txt").write_text("Not markdown")
        (content_dir / "README").write_text("README")
        
        # Mock the content paths to use our temp directory
        with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [str(content_dir)]):
            files = list(scan_markdown_files())
            
        # Should find only the markdown files
        assert len(files) == 3
        file_names = {f.name for f in files}
        assert file_names == {"book1.md", "book2.md", "book3.md"}
        
    def test_scan_multiple_directories(self, temp_dir: Path) -> None:
        """Test scanning multiple content directories."""
        # Create multiple directory structures
        en_dir = temp_dir / "content" / "en" / "books"
        ru_dir = temp_dir / "content" / "ru" / "books"
        en_dir.mkdir(parents=True)
        ru_dir.mkdir(parents=True)
        
        # Create files in each directory
        (en_dir / "english_book.md").write_text("# English Book")
        (ru_dir / "russian_book.md").write_text("# Russian Book")
        
        # Mock the content paths
        with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [str(en_dir), str(ru_dir)]):
            files = list(scan_markdown_files())
            
        assert len(files) == 2
        file_names = {f.name for f in files}
        assert file_names == {"english_book.md", "russian_book.md"}
        
    def test_scan_nested_directories(self, temp_dir: Path) -> None:
        """Test scanning deeply nested directory structures."""
        # Create deeply nested structure
        nested_dir = temp_dir / "content" / "books" / "category" / "subcategory" / "deep"
        nested_dir.mkdir(parents=True)
        
        # Create files at different levels
        (temp_dir / "content" / "books" / "root.md").write_text("# Root")
        (temp_dir / "content" / "books" / "category" / "category.md").write_text("# Category")
        (nested_dir / "deep.md").write_text("# Deep")
        
        with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [str(temp_dir / "content" / "books")]):
            files = list(scan_markdown_files())
            
        assert len(files) == 3
        
    def test_scan_empty_directory(self, temp_dir: Path) -> None:
        """Test scanning empty directories returns empty list."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        
        with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [str(empty_dir)]):
            files = list(scan_markdown_files())
            
        assert len(files) == 0
        
    def test_scan_nonexistent_directory(self) -> None:
        """Test scanning non-existent directories doesn't crash."""
        nonexistent = "/nonexistent/path"
        
        with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [nonexistent]):
            files = list(scan_markdown_files())
            
        assert len(files) == 0
        
    def test_scan_no_markdown_files(self, temp_dir: Path) -> None:
        """Test directory with no markdown files returns empty list."""
        content_dir = temp_dir / "content"
        content_dir.mkdir()
        
        # Create non-markdown files
        (content_dir / "file.txt").write_text("Text file")
        (content_dir / "file.html").write_text("<html></html>")
        (content_dir / "file.json").write_text('{"key": "value"}')
        
        with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [str(content_dir)]):
            files = list(scan_markdown_files())
            
        assert len(files) == 0
        
    def test_scan_special_characters_in_names(self, temp_dir: Path) -> None:
        """Test files with special characters in names."""
        content_dir = temp_dir / "content"
        content_dir.mkdir()
        
        # Create files with special characters
        special_files = [
            "book with spaces.md",
            "book-with-dashes.md",
            "book_with_underscores.md",
            "book.with.dots.md",
            "book@symbol.md",
            "книга_русская.md"  # Cyrillic
        ]
        
        for filename in special_files:
            (content_dir / filename).write_text(f"# {filename}")
            
        with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [str(content_dir)]):
            files = list(scan_markdown_files())
            
        assert len(files) == len(special_files)
        
    @pytest.mark.skipif(os.name == "nt", reason="Symlinks may not work on Windows")
    def test_scan_symlinks(self, temp_dir: Path) -> None:
        """Test handling of symbolic links."""
        content_dir = temp_dir / "content"
        content_dir.mkdir()
        
        # Create a real file
        real_file = content_dir / "real_book.md"
        real_file.write_text("# Real Book")
        
        # Create a symlink
        symlink = content_dir / "symlink_book.md"
        symlink.symlink_to(real_file)
        
        with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [str(content_dir)]):
            files = list(scan_markdown_files())
            
        # Should find both real file and symlink
        assert len(files) == 2
        
    def test_scan_permission_errors(self, temp_dir: Path) -> None:
        """Test handling of files with permission issues."""
        content_dir = temp_dir / "content"
        content_dir.mkdir()
        
        # Create a file
        test_file = content_dir / "book.md"
        test_file.write_text("# Book")
        
        # Remove read permissions (on Unix-like systems)
        if os.name != "nt":  # Skip on Windows
            test_file.chmod(0o000)
            
            try:
                with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [str(content_dir)]):
                    files = list(scan_markdown_files())
                    
                # Should still find the file (scanner doesn't read content)
                assert len(files) == 1
            finally:
                # Restore permissions for cleanup
                test_file.chmod(0o644)


class TestGetAllMarkdownFiles:
    """Test the get_all_markdown_files function."""
    
    def test_returns_list(self, temp_dir: Path) -> None:
        """Test that get_all_markdown_files returns a list."""
        content_dir = temp_dir / "content"
        content_dir.mkdir()
        (content_dir / "book.md").write_text("# Book")
        
        with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [str(content_dir)]):
            files = get_all_markdown_files()
            
        assert isinstance(files, list)
        assert len(files) == 1
        assert files[0].name == "book.md"
        
    def test_large_number_of_files(self, temp_dir: Path) -> None:
        """Test performance with large number of files."""
        content_dir = temp_dir / "content"
        content_dir.mkdir()
        
        # Create many files
        num_files = 100
        for i in range(num_files):
            (content_dir / f"book_{i:03d}.md").write_text(f"# Book {i}")
            
        with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [str(content_dir)]):
            files = get_all_markdown_files()
            
        assert len(files) == num_files
        
    def test_consistent_results(self, temp_dir: Path) -> None:
        """Test that multiple calls return consistent results."""
        content_dir = temp_dir / "content"
        content_dir.mkdir()
        (content_dir / "book1.md").write_text("# Book 1")
        (content_dir / "book2.md").write_text("# Book 2")
        
        with patch("frontmatter.scanner.BOOK_CONTENT_PATHS", [str(content_dir)]):
            files1 = get_all_markdown_files()
            files2 = get_all_markdown_files()
            
        # Results should be identical
        assert len(files1) == len(files2)
        assert {f.name for f in files1} == {f.name for f in files2} 