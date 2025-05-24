"""
Tests for the reporter module.
"""
import io
import json
import sys
from pathlib import Path

from frontmatter.reporter import Reporter
from frontmatter.types import ErrorSeverity, ValidationError


class TestReporter:
    """Test the Reporter class."""
    
    def test_reporter_init(self) -> None:
        """Test reporter initialization."""
        # Test default stream
        reporter = Reporter()
        assert reporter.output_stream == sys.stdout
        
        # Test custom stream
        custom_stream = io.StringIO()
        reporter = Reporter(custom_stream)
        assert reporter.output_stream == custom_stream

    def test_print_results(self, validation_result_factory) -> None:
        """Test basic result printing."""
        output = io.StringIO()
        reporter = Reporter(output)
        
        # Create test data with one valid and one invalid file
        valid_result = validation_result_factory(path=Path("valid.md"))
        error_result = validation_result_factory(path=Path("invalid.md"))
        error_result.errors = [
            ValidationError("Missing field", ["title"]),
            ValidationError("Wrong type", ["draft"])
        ]
        
        results = [valid_result, error_result]
        reporter.print_results(results)
        
        output_text = output.getvalue()
        # Check only essential information
        assert "Validated 2 files" in output_text
        assert "1 files are valid" in output_text
        assert "1 files have errors" in output_text
        assert "invalid.md:" in output_text
        assert "title: Missing field" in output_text

    def test_print_results_verbose(self, validation_result_factory) -> None:
        """Test verbose output mode."""
        output = io.StringIO()
        reporter = Reporter(output)
        
        # Create result with warnings
        result = validation_result_factory(path=Path("test.md"))
        result.warnings = [ValidationError("Warning", ["field"], severity=ErrorSeverity.WARNING)]
        
        reporter.print_results([result], verbose=True)
        output_text = output.getvalue()
        
        assert "1 files have warnings" in output_text
        assert "field: Warning" in output_text

    def test_generate_json_report(self, validation_result_factory, temp_dir: Path) -> None:
        """Test JSON report generation."""
        # Test file output
        output_path = temp_dir / "report.json"
        reporter = Reporter()
        
        result = validation_result_factory(path=Path("test.md"))
        result.errors = [ValidationError("Error", ["field"])]
        
        reporter.generate_json_report([result], output_path)
        
        with open(output_path) as f:
            report = json.load(f)
            
        assert report["summary"]["total_files"] == 1
        assert report["summary"]["valid_files"] == 0
        assert len(report["files"]) == 1
        assert report["files"][0]["path"] == "test.md"
        assert len(report["files"][0]["errors"]) == 1

    def test_generate_json_report_to_stream(self, validation_result_factory) -> None:
        """Test JSON report generation to stream."""
        output = io.StringIO()
        reporter = Reporter(output)
        
        result = validation_result_factory()
        reporter.generate_json_report([result])
        
        report = json.loads(output.getvalue())
        assert report["summary"]["total_files"] == 1
        assert report["summary"]["valid_files"] == 1 