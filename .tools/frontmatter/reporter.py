"""
Reporter for validation results.
"""
import json
import sys
from pathlib import Path
from typing import TextIO

from .types import ValidationResult


class Reporter:
    """Reporter for validation results."""
    
    def __init__(self, output_stream: TextIO = sys.stdout):
        """
        Initialize the reporter.
        
        Args:
            output_stream: Stream to write output to (default: stdout)
        """
        self.output_stream = output_stream
        
    def print_results(self, results: list[ValidationResult], verbose: bool = False) -> None:
        """
        Print validation results in a human-readable format.
        
        Args:
            results: List of ValidationResult objects
            verbose: Whether to include warnings and detailed information
        """
        total_files = len(results)
        valid_files = sum(1 for result in results if result.is_valid)
        files_with_errors = total_files - valid_files
        files_with_warnings = sum(1 for result in results if result.has_warnings)
        
        print(f"Validated {total_files} files:", file=self.output_stream)
        print(f"  ✓ {valid_files} files are valid", file=self.output_stream)
        
        if files_with_errors > 0:
            print(f"  ✗ {files_with_errors} files have errors", file=self.output_stream)
            
        if files_with_warnings > 0 and verbose:
            print(f"  ! {files_with_warnings} files have warnings", file=self.output_stream)
            
        # Print details for files with errors
        if files_with_errors > 0:
            print("\nFiles with errors:", file=self.output_stream)
            for result in results:
                if not result.is_valid:
                    print(f"\n{result.path}:", file=self.output_stream)
                    for error in result.errors:
                        path_str = ".".join(error.path)
                        print(f"  ✗ {path_str}: {error.message}", file=self.output_stream)
                        
        # Print details for files with warnings (if verbose)
        if files_with_warnings > 0 and verbose:
            print("\nFiles with warnings:", file=self.output_stream)
            for result in results:
                if result.has_warnings:
                    print(f"\n{result.path}:", file=self.output_stream)
                    for warning in result.warnings:
                        path_str = ".".join(warning.path)
                        print(f"  ! {path_str}: {warning.message}", file=self.output_stream)
                        
    def print_summary(self, results: list[ValidationResult]) -> None:
        """
        Print a summary of validation results.
        
        Args:
            results: List of ValidationResult objects
        """
        total_files = len(results)
        valid_files = sum(1 for result in results if result.is_valid)
        files_with_errors = total_files - valid_files
        
        print(f"Summary: {valid_files}/{total_files} files valid, {files_with_errors} files with errors", 
              file=self.output_stream)
        
        if files_with_errors > 0:
            sys.exit(1)  # Exit with error code for CI integration
            
    def generate_json_report(self, results: list[ValidationResult], output_path: Path | None = None) -> None:
        """
        Generate a JSON report of validation results.
        
        Args:
            results: List of ValidationResult objects
            output_path: Path to write the report to (if None, print to output_stream)
        """
        report = {
            "summary": {
                "total_files": len(results),
                "valid_files": sum(1 for result in results if result.is_valid),
                "files_with_errors": sum(1 for result in results if not result.is_valid),
                "files_with_warnings": sum(1 for result in results if result.has_warnings),
            },
            "files": []
        }
        
        # Add details for each file
        for result in results:
            file_report = {
                "path": str(result.path),
                "valid": result.is_valid,
                "errors": [],
                "warnings": []
            }
            
            # Add errors
            for error in result.errors:
                file_report["errors"].append({
                    "path": ".".join(error.path),
                    "message": error.message,
                    "fixable": error.fixable
                })
                
            # Add warnings
            for warning in result.warnings:
                file_report["warnings"].append({
                    "path": ".".join(warning.path),
                    "message": warning.message
                })
                
            report["files"].append(file_report)
            
        # Write report to file or print to output stream
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
        else:
            json.dump(report, self.output_stream, indent=2)
            print(file=self.output_stream)  # Add newline 