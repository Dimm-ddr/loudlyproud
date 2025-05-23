"""
Controller for orchestrating the validation workflow.
"""
from pathlib import Path

from .autofixer import autofix_frontmatter, fix_field_order
from .extractor import extract_frontmatter, FrontmatterExtractionError
from .reporter import Reporter
from .scanner import get_all_markdown_files
from .types import ValidationError, ValidationResult
from .validator import validate_frontmatter


class Controller:
    """Controller for orchestrating the validation workflow."""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the controller.
        
        Args:
            verbose: Whether to include verbose output
        """
        self.verbose = verbose
        self.reporter = Reporter()
        
    def validate_and_fix(self) -> list[ValidationResult]:
        """
        Validate and fix all markdown files.
        
        Returns:
            List of ValidationResult objects after validation and fixing
        """
        files = get_all_markdown_files()
        results = []
        fixed_count = 0
        
        for file_path in files:
            try:
                # Extract frontmatter
                file_content = extract_frontmatter(file_path)
                
                # Validate frontmatter
                result = validate_frontmatter(file_content)
                
                # Fix validation issues
                if not result.is_valid and result.has_fixable_errors:
                    if autofix_frontmatter(file_content, result):
                        fixed_count += 1
                
                # Fix field order
                if fix_field_order(file_content):
                    fixed_count += 1
                    
                # Re-validate after fixes
                result = validate_frontmatter(file_content)
                results.append(result)
                
            except FrontmatterExtractionError as e:
                # Create a validation result with the extraction error
                result = ValidationResult(path=file_path)
                result.errors.append(ValidationError(
                    message=str(e),
                    path=["frontmatter"],
                    fixable=False
                ))
                results.append(result)
        
        # Print results
        if fixed_count > 0:
            print(f"Fixed issues in {fixed_count} files")
        self.reporter.print_results(results, verbose=self.verbose)
        
        return results
        
    def report(self, results: list[ValidationResult], output_path: Path | None = None) -> None:
        """
        Generate a report of validation issues.
        
        Args:
            results: List of ValidationResult objects
            output_path: Path to write the report to (if None, print to stdout)
        """
        # Generate JSON report
        self.reporter.generate_json_report(results, output_path) 