"""
Type definitions for the frontmatter validator.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


class ErrorSeverity(Enum):
    """Severity levels for validation errors."""
    WARNING = auto()
    ERROR = auto()


@dataclass
class ValidationError:
    """Represents a single validation error."""
    message: str
    path: list[str]  # Path to the error in the frontmatter (e.g., ["params", "authors"])
    severity: ErrorSeverity = ErrorSeverity.ERROR
    fixable: bool = False
    suggested_fix: Any | None = None


@dataclass
class ValidationResult:
    """Result of validating a single file."""
    path: Path
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Return True if there are no errors."""
        return len(self.errors) == 0
    
    @property
    def has_fixable_errors(self) -> bool:
        """Return True if there are fixable errors."""
        return any(error.fixable for error in self.errors)
    
    @property
    def has_warnings(self) -> bool:
        """Return True if there are warnings."""
        return len(self.warnings) > 0


@dataclass
class FileContent:
    """Content of a markdown file with frontmatter."""
    path: Path
    frontmatter: dict[str, Any]
    body: str
    raw_frontmatter: str 