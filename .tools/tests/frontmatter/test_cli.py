"""
Tests for the CLI module.
"""
from unittest.mock import Mock, patch

import pytest

from frontmatter.cli import main


def test_main_successful_execution() -> None:
    """Test successful CLI execution with valid files."""
    controller = Mock()
    controller.validate_and_fix.return_value = [Mock(is_valid=True)]
    
    with patch("frontmatter.cli.Controller", return_value=controller), \
         patch("frontmatter.cli.Path"):
        
        main()
        
    controller.validate_and_fix.assert_called_once()
    controller.report.assert_called_once()


def test_main_exits_with_error_on_invalid_files() -> None:
    """Test CLI exits with error code when validation errors exist."""
    controller = Mock()
    controller.validate_and_fix.return_value = [Mock(is_valid=False)]
    
    with patch("frontmatter.cli.Controller", return_value=controller), \
         patch("frontmatter.cli.Path"), \
         pytest.raises(SystemExit) as exc_info:
        
        main()
        
    assert exc_info.value.code == 1 