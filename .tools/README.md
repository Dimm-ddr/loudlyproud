# Content Management Tools

This directory contains Python-based tools for managing and validating content in the LoudlyProud project. The tools are managed using Poetry for dependency management.

## Setup

1. Install Poetry if you haven't already:
   ```bash
   # Windows (PowerShell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

   # macOS / Linux
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

## Available Tools

### Content Validation

- `check-content`: Validates content files for proper formatting and required fields
- `fix-content`: Automatically fixes common content issues

Run these tools using:
```bash
poetry run check-content
poetry run fix-content
```

### Tag Management

The `tag_tools.py` script provides utilities for managing the site's tag system:

```bash
poetry run tag-tools --help
```

Features:
- Tag validation
- Tag normalization
- Tag reference updates
- Tag metadata management

### Language Tools

The `language.py` script manages translations and language files:

```bash
poetry run language-tools --help
```

Features:
- Translation validation
- Language file management
- Translation completeness checks

## Development

### Running Tests

```bash
poetry run pytest
```

### Linting

```bash
poetry run flake8
```

### Project Structure

- `content/` - Content validation and management scripts
- `tag_tools.py` - Tag management utilities
- `language.py` - Language management utilities
- `pyproject.toml` - Poetry configuration and dependencies
- `requirements.txt` - Legacy Python package requirements

## Integration with Main Project

These tools are integrated with the main project through npm/pnpm scripts. From the project root, you can run:

```bash
# Install Python dependencies
pnpm run tools install

# Run any Poetry command
pnpm run tools <command>

# Examples:
pnpm run tools run check-content
pnpm run tools run fix-content
pnpm run tools run pytest
pnpm run tools run flake8
pnpm run tools run tag-tools
pnpm run tools run language-tools
```

## Contributing

1. Make sure you have Poetry installed
2. Install dependencies with `poetry install`
3. Run tests with `poetry run pytest`
4. Run linter with `poetry run flake8`
5. Make your changes
6. Submit a pull request 