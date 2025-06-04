"""
Tests for the CLI module.
"""
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from frontmatter.cli import main, get_project_root


def test_get_project_root() -> None:
    """Test getting the project root directory."""
    with patch("frontmatter.cli.Path") as mock_path:
        mock_path.return_value.parent.parent.parent = Path("/project/root")
        root = get_project_root()
        assert root == Path("/project/root")


def test_main_successful_execution() -> None:
    """Test successful CLI execution with valid files."""
    controller = Mock()
    controller.validate_and_fix.return_value = [Mock(is_valid=True)]
    
    with patch("frontmatter.cli.get_project_root", return_value=Path("/project/root")), \
         patch("frontmatter.cli.Controller", return_value=controller), \
         patch("frontmatter.cli.Path") as mock_path:
        
        main()
        
    controller.validate_and_fix.assert_called_once()
    controller.report.assert_called_once()
    mock_path.assert_called_with("/project/root/frontmatter_validation_report.json")


def test_main_exits_with_error_on_invalid_files() -> None:
    """Test CLI exits with error code when validation errors exist."""
    controller = Mock()
    controller.validate_and_fix.return_value = [Mock(is_valid=False)]
    
    with patch("frontmatter.cli.get_project_root", return_value=Path("/project/root")), \
         patch("frontmatter.cli.Controller", return_value=controller), \
         patch("frontmatter.cli.Path"), \
         pytest.raises(SystemExit) as exc_info:
        
        main()
        
    assert exc_info.value.code == 1 