from typing import Any, NamedTuple
import pytest
from pathlib import Path


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
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


# Add if any new fixtures are needed for clean.py tests