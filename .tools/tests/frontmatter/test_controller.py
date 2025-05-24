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
    
    def test_controller_init(self) -> None:
        """Test controller initialization."""
        # Test default settings
        controller = Controller()
        assert controller.verbose is False
        assert controller.reporter is not None
        
        # Test verbose mode
        controller = Controller(verbose=True)
        assert controller.verbose is True
        assert controller.reporter is not None

    def test_validate_and_fix_basic_workflow(self, file_content_factory, validation_result_factory) -> None:
        """Test basic validation and fix workflow."""
        controller = Controller()
        
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

    def test_validate_and_fix_with_fixes(self, file_content_factory, validation_result_factory) -> None:
        """Test workflow when fixes are applied."""
        controller = Controller()
        
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

    def test_validate_and_fix_extraction_error(self) -> None:
        """Test handling of frontmatter extraction errors."""
        controller = Controller()
        
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

    def test_validate_and_fix_no_files(self) -> None:
        """Test workflow when no markdown files are found."""
        controller = Controller()
        
        with patch("frontmatter.controller.get_all_markdown_files", return_value=[]), \
             patch.object(controller.reporter, "print_results") as mock_print:
            
            results = controller.validate_and_fix()
            
        assert len(results) == 0
        mock_print.assert_called_once_with([], verbose=False)

    def test_report(self, validation_result_factory, temp_dir: Path) -> None:
        """Test report generation."""
        controller = Controller()
        
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