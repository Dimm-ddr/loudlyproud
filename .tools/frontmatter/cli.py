"""
Command-line interface for the frontmatter validator.
"""
import sys
from pathlib import Path

from .controller import Controller


def main() -> None:
    """Main entry point for the CLI."""
    # Hardcoded output path in .data folder
    output_path = Path(".data/frontmatter_validation_report.json")
    
    # Always run in verbose mode
    controller = Controller(verbose=True)
    
    # Run validation, fixing, and reporting in one go
    results = controller.validate_and_fix()
    
    # Generate report
    controller.report(results, output_path)
    
    # Exit with error code if there are any unfixed issues
    if any(not result.is_valid for result in results):
        sys.exit(1)


if __name__ == "__main__":
    main() 