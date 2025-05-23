"""
Extract YAML frontmatter from markdown files.
"""
import io
from pathlib import Path

from ruamel.yaml import YAML

from .constants import FRONTMATTER_DELIMITER
from .types import FileContent


class FrontmatterExtractionError(Exception):
    """Exception raised when frontmatter extraction fails."""
    pass


def extract_frontmatter(path: Path) -> FileContent:
    """
    Extract YAML frontmatter and body from a markdown file.
    
    Args:
        path: Path to the markdown file
        
    Returns:
        FileContent object containing the frontmatter dict, body text, and raw frontmatter
        
    Raises:
        FrontmatterExtractionError: If the file does not start with YAML frontmatter
            or if the frontmatter is malformed
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if not content.startswith(FRONTMATTER_DELIMITER):
            raise FrontmatterExtractionError(f"{path} does not start with YAML frontmatter")
            
        # Split content by delimiter
        parts = content.split(FRONTMATTER_DELIMITER, 2)
        
        if len(parts) < 3:
            raise FrontmatterExtractionError(f"{path} has unterminated YAML frontmatter")
            
        # The first part should be empty (before first delimiter)
        # The second part is the frontmatter
        # The third part is the body (may include more delimiters)
        raw_frontmatter = parts[1].strip()
        body = parts[2].strip()
        
        # Check for unsupported YAML features before parsing
        _validate_yaml_features(raw_frontmatter, path)
        
        # Parse the frontmatter as YAML
        try:
            yaml = YAML(typ='safe')
            frontmatter = yaml.load(raw_frontmatter)
            if not isinstance(frontmatter, dict):
                raise FrontmatterExtractionError(f"{path} frontmatter is not a dictionary")
        except Exception as e:
            raise FrontmatterExtractionError(f"Failed to parse YAML in {path}: {str(e)}")
            
        return FileContent(
            path=path,
            frontmatter=frontmatter,
            body=body,
            raw_frontmatter=raw_frontmatter
        )
        
    except (IOError, UnicodeDecodeError) as e:
        raise FrontmatterExtractionError(f"Failed to read {path}: {str(e)}")


def _validate_yaml_features(raw_frontmatter: str, path: Path) -> None:
    """
    Validate that the YAML doesn't use features not supported by Hugo.
    
    Args:
        raw_frontmatter: Raw YAML frontmatter text
        path: Path to the file (for error messages)
        
    Raises:
        FrontmatterExtractionError: If unsupported YAML features are found
    """
    lines = raw_frontmatter.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Check for anchors and aliases
        if '&' in line and line.strip().endswith(':'):
            # This is likely an anchor definition
            raise FrontmatterExtractionError(
                f"{path} line {i}: YAML anchors (&) are not supported by Hugo"
            )
        if '*' in line and not line.strip().startswith('#'):
            # This is likely an alias reference (exclude comments)
            raise FrontmatterExtractionError(
                f"{path} line {i}: YAML aliases (*) are not supported by Hugo"
            )
        if line.strip().startswith('!'):
            # This is likely a YAML tag
            raise FrontmatterExtractionError(
                f"{path} line {i}: YAML tags (!) are not supported by Hugo"
            )


def write_frontmatter(file_content: FileContent) -> None:
    """
    Write frontmatter and body back to the file.
    
    Args:
        file_content: FileContent object with updated frontmatter
        
    Raises:
        IOError: If writing to the file fails
    """
    # Use ruamel.yaml to preserve formatting and comments
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    
    # Convert frontmatter to YAML string
    yaml_str = io.StringIO()
    yaml.dump(file_content.frontmatter, yaml_str)
    
    # Construct the full content
    full_content = f"{FRONTMATTER_DELIMITER}\n{yaml_str.getvalue()}{FRONTMATTER_DELIMITER}\n\n{file_content.body}"
    
    # Write to file
    with open(file_content.path, "w", encoding="utf-8") as f:
        f.write(full_content) 