"""
Command-line interface for the frontmatter validator.
"""
import sys
from pathlib import Path

from .controller import Controller


def get_project_root() -> Path:
    """Get the absolute path to the project root directory."""
    # Since we're in .tools/frontmatter/cli.py, go up two levels to get to project root
    return Path(__file__).parent.parent.parent


def main() -> None:
    """Main entry point for the CLI."""
    project_root = get_project_root()
    
    # Output path relative to project root
    output_path = project_root / "frontmatter_validation_report.json"
    
    # Always run in verbose mode
    controller = Controller(verbose=True, project_root=project_root)
    
    # Run validation, fixing, and reporting in one go
    results = controller.validate_and_fix()
    
    # Generate report
    controller.report(results, output_path)
    
    # Exit with error code if there are any unfixed issues
    if any(not result.is_valid for result in results):
        sys.exit(1)


if __name__ == "__main__":
    main() 