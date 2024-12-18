from typing import Any, NamedTuple
import pytest
from pathlib import Path
import shutil
from ..common import DATA_DIR, CONTENT_DIR


class TestAssertContext(NamedTuple):
    """Context for test execution with detailed reporting."""

    test_name: str
    input_value: Any
    expected: Any
    actual: Any
    extra_info: dict[str, Any]


@pytest.fixture
def assert_context():
    """Fixture providing test assertion context."""

    def _make_context(
        test_name: str, input_value: Any, expected: Any, actual: Any, **extra_info: Any
    ) -> TestAssertContext:
        return TestAssertContext(
            test_name=test_name,
            input_value=input_value,
            expected=expected,
            actual=actual,
            extra_info=extra_info,
        )

    return _make_context


@pytest.fixture
def test_project(tmp_path: Path):
    """Create a test project structure with real config files."""
    # Create data directory
    test_data_dir = tmp_path / DATA_DIR.name
    test_data_dir.mkdir(parents=True)

    # Copy all files from data/tags to test directory
    real_data_dir = Path.cwd() / DATA_DIR
    for file in real_data_dir.glob("*"):
        if file.is_file():
            shutil.copy2(file, test_data_dir / file.name)

    # Create content directory
    test_content_dir = tmp_path / CONTENT_DIR.name
    test_content_dir.mkdir(parents=True)

    return tmp_path


@pytest.fixture
def test_data_dir(test_project):
    """Alias for test_project for backward compatibility."""
    return test_project


# Add if any new fixtures are needed for clean.py tests
