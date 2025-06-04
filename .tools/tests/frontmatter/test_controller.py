"""
Tests for the controller module.
"""
from pathlib import Path
from unittest.mock import patch

from frontmatter.controller import Controller
from frontmatter.extractor import FrontmatterExtractionError
from frontmatter.types import ValidationError, ValidationResult


class TestController:
    """Test the Controller class."""
    
    def test_controller_init(self, temp_dir: Path) -> None:
        """Test controller initialization."""
        # Test default settings
        controller = Controller()
        assert controller.verbose is False
        assert controller.reporter is not None
        assert controller.project_root == Path.cwd()
        
        # Test verbose mode
        controller = Controller(verbose=True)
        assert controller.verbose is True
        assert controller.reporter is not None
        assert controller.project_root == Path.cwd()
        
        # Test with project root
        controller = Controller(project_root=temp_dir)
        assert controller.project_root == temp_dir

    def test_validate_and_fix_basic_workflow(self, file_content_factory, validation_result_factory, temp_dir: Path) -> None:
        """Test basic validation and fix workflow."""
        controller = Controller(project_root=temp_dir)
        
        # Mock dependencies
        mock_files = [Path("test.md")]
        mock_file_content = file_content_factory()
        mock_result = validation_result_factory()
        
        with patch("frontmatter.controller.get_all_markdown_files", return_value=mock_files), \
             patch("frontmatter.controller.extract_frontmatter", return_value=mock_file_content), \
             patch("frontmatter.controller.validate_frontmatter", return_value=mock_result), \
             patch("frontmatter.controller.autofix_frontmatter", return_value=False), \
             patch("frontmatter.controller.fix_field_order", return_value=False), \
             patch.object(controller.reporter, "print_results") as mock_print:
            
            results = controller.validate_and_fix()
            
        assert len(results) == 1
        assert isinstance(results[0], ValidationResult)
        mock_print.assert_called_once_with([mock_result], verbose=False)

    def test_validate_and_fix_with_fixes(self, file_content_factory, validation_result_factory, temp_dir: Path) -> None:
        """Test workflow when fixes are applied."""
        controller = Controller(project_root=temp_dir)
        
        mock_files = [Path("test.md")]
        mock_file_content = file_content_factory()
        
        # Create result with fixable errors
        mock_result = validation_result_factory()
        mock_result.errors = [ValidationError("Fixable error", ["field"], fixable=True)]
        
        # Mock a valid result after fixing
        fixed_result = validation_result_factory()
        
        with patch("frontmatter.controller.get_all_markdown_files", return_value=mock_files), \
             patch("frontmatter.controller.extract_frontmatter", return_value=mock_file_content), \
             patch("frontmatter.controller.validate_frontmatter", side_effect=[mock_result, fixed_result]), \
             patch("frontmatter.controller.autofix_frontmatter", return_value=True), \
             patch("frontmatter.controller.fix_field_order", return_value=True), \
             patch("builtins.print") as mock_print, \
             patch.object(controller.reporter, "print_results"):
            
            results = controller.validate_and_fix()
            
        mock_print.assert_called_with("Fixed issues in 1 files")
        assert len(results) == 1
        assert results[0] == fixed_result

    def test_validate_and_fix_with_misspelled_field(self, file_content_factory, validation_result_factory, temp_dir: Path) -> None:
        """Test handling of misspelled fields in frontmatter."""
        controller = Controller(project_root=temp_dir)
        
        mock_files = [Path("test.md")]
        mock_file_content = file_content_factory()
        mock_file_content.frontmatter = {"tranlsators": ["John Doe"]}  # Misspelled field
        
        # Create result showing the misspelled field was removed
        mock_result = validation_result_factory()
        mock_result.errors = [ValidationError("Removed misspelled field 'tranlsators'", ["tranlsators"], fixable=True)]
        mock_result.changes = {"removed_fields": ["tranlsators"]}
        
        with patch("frontmatter.controller.get_all_markdown_files", return_value=mock_files), \
             patch("frontmatter.controller.extract_frontmatter", return_value=mock_file_content), \
             patch("frontmatter.controller.validate_frontmatter", return_value=mock_result), \
             patch("frontmatter.controller.autofix_frontmatter", return_value=True), \
             patch("frontmatter.controller.fix_field_order", return_value=False), \
             patch.object(controller.reporter, "print_results") as mock_print:
            
            results = controller.validate_and_fix()
            
        assert len(results) == 1
        assert not results[0].is_valid  # Should still be marked as invalid due to changes
        assert "tranlsators" in results[0].changes["removed_fields"]
        mock_print.assert_called_once()

    def test_validate_and_fix_extraction_error(self, temp_dir: Path) -> None:
        """Test handling of frontmatter extraction errors."""
        controller = Controller(project_root=temp_dir)
        
        mock_files = [Path("error.md")]
        extraction_error = FrontmatterExtractionError("Failed to extract frontmatter")
        
        with patch("frontmatter.controller.get_all_markdown_files", return_value=mock_files), \
             patch("frontmatter.controller.extract_frontmatter", side_effect=extraction_error), \
             patch.object(controller.reporter, "print_results"):
            
            results = controller.validate_and_fix()
            
        assert len(results) == 1
        result = results[0]
        assert result.path == Path("error.md")
        assert len(result.errors) == 1
        assert "Failed to extract frontmatter" in result.errors[0].message
        assert result.errors[0].path == ["frontmatter"]
        assert not result.errors[0].fixable

    def test_validate_and_fix_no_files(self, temp_dir: Path) -> None:
        """Test workflow when no markdown files are found."""
        controller = Controller(project_root=temp_dir)
        
        with patch("frontmatter.controller.get_all_markdown_files", return_value=[]), \
             patch.object(controller.reporter, "print_results") as mock_print:
            
            results = controller.validate_and_fix()
            
        assert len(results) == 0
        mock_print.assert_called_once_with([], verbose=False)

    def test_report(self, validation_result_factory, temp_dir: Path) -> None:
        """Test report generation."""
        controller = Controller(project_root=temp_dir)
        
        # Test file output
        results = [validation_result_factory(path=Path("test.md"))]
        output_path = temp_dir / "report.json"
        
        with patch.object(controller.reporter, "generate_json_report") as mock_generate:
            controller.report(results, output_path)
            
        mock_generate.assert_called_once_with(results, output_path)
        
        # Test stdout output
        with patch.object(controller.reporter, "generate_json_report") as mock_generate:
            controller.report(results, None)
            
        mock_generate.assert_called_once_with(results, None)

    def test_report_includes_changes(self, validation_result_factory, temp_dir: Path) -> None:
        """Test that the report includes information about changes made."""
        controller = Controller(project_root=temp_dir)
        
        # Create a result with changes
        result = validation_result_factory(path=Path("test.md"))
        result.changes = {
            "removed_fields": ["tranlsators"],
            "added_fields": ["translators"],
            "modified_fields": ["title"]
        }
        
        output_path = temp_dir / "report.json"
        
        with patch.object(controller.reporter, "generate_json_report") as mock_generate:
            controller.report([result], output_path)
            
        # Verify the report includes changes
        mock_generate.assert_called_once()
        report_data = mock_generate.call_args[0][0][0]
        assert "changes" in report_data
        assert report_data["changes"]["removed_fields"] == ["tranlsators"]
        assert report_data["changes"]["added_fields"] == ["translators"]
        assert report_data["changes"]["modified_fields"] == ["title"] 