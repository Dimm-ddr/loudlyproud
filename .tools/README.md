# LoudlyProud Tools

This directory contains various Python tools for managing and validating content in the LoudlyProud project.

## Overview

The tools suite provides functionality for:
- Content validation and schema checking
- Automated content fixing
- Tag management and normalization
- Language-specific content handling
- Testing and quality assurance

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Available Tools

### Content Management

#### `check_content.py`
Validates content files against defined schemas and rules.
- Validates URLs, dates, and required fields
- Checks for schema compliance
- Generates validation statistics
- Identifies auto-fixable issues

Usage:
```bash
python check_content.py
```

#### `fix_content.py`
Automatically fixes common content issues.
- Applies text-based fixes
- Handles YAML frontmatter fixes
- Supports frontmatter reordering
- Preserves formatting and quotes

Usage:
```bash
python fix_content.py
```

### Tag Management

#### `tag_tools.py`
CLI tool for managing and validating tags.

Available commands:
- `validate`: Validate tags against mapping and colors
- `sort`: Sort tags mapping and colors files
- `monitor`: Monitor tag changes in PR
- `clean`: Clean various tag-related content
  - `mapping`: Clean tag mappings
  - `colors`: Clean color tags
  - `frontmatter`: Clean frontmatter
  - `content`: Clean content

Usage:
```bash
python tag_tools.py [command] [options]
```

### Testing

#### `run_tests.py`
Runs the test suite with coverage reporting.

Usage:
```bash
python run_tests.py
```

## Project Structure

```
.tools/
├── check_content.py      # Content validation tool
├── fix_content.py        # Content fixing tool
├── tag_tools.py         # Tag management CLI
├── book_schema.py       # Schema definitions
├── run_tests.py         # Test runner
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration
├── fixers/             # Content fix implementations
├── tags/               # Tag-related functionality
├── language/           # Language-specific tools
└── docs/              # Documentation
```

## Dependencies

- `ruamel.yaml>=0.17.0`: YAML processing
- `flake8`: Code linting
- `flake8-bugbear`: Additional linting rules
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting
- `click`: CLI framework
- `tomli-w`: TOML file handling

## Development

The project uses:
- Modern Python syntax and type hints
- Comprehensive test coverage
- Automated linting and formatting
- Modular architecture for easy extension

## Contributing

1. Ensure all tests pass: `python run_tests.py`
2. Check code style: `flake8`
3. Update documentation as needed
4. Submit pull requests with clear descriptions

## License

[Add your license information here] 