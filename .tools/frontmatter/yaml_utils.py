from io import StringIO
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

def create_yaml_parser() -> YAML:
    """Create and configure a YAML parser with standard settings."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.default_flow_style = False
    return yaml

def parse_frontmatter(content: str) -> tuple[dict | None, list[str], bool]:
    """
    Parse YAML frontmatter from content.
    
    Returns:
        Tuple containing:
        - Parsed data (or None if parsing failed)
        - List of error messages
        - Boolean indicating if YAML was valid
    """
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, ["Invalid frontmatter format"], False
        
    yaml_content = parts[1]
    yaml = create_yaml_parser()
    
    try:
        data = yaml.load(yaml_content)
        if not isinstance(data, dict):
            return None, ["Frontmatter must be a YAML mapping"], False
        return data, [], True
    except YAMLError as e:
        error_msg, fixable = classify_yaml_error(str(e))
        return None, [error_msg], fixable

def classify_yaml_error(error_msg: str) -> tuple[str, bool]:
    """
    Classify YAML error and determine if it's auto-fixable.
    
    Returns:
        Tuple of (error message, is_fixable)
    """
    # Extract line number if available
    line_info = ""
    line_num = None
    if "line " in error_msg and ", column " in error_msg:
        try:
            # Extract line number from error message
            line_part = error_msg.split("line ")[1].split(",")[0]
            line_num = int(line_part)
            line_info = f" (around line {line_num})"
        except (IndexError, ValueError):
            pass

    # Check for specific patterns in the error message
    if "while scanning a simple key" in error_msg:
        # This is typically an indentation issue
        return f"Found text that should be indented under a field{line_info}", True
    elif "while parsing a block mapping" in error_msg:
        # This could be an indentation issue or a quoting issue
        return f"YAML structure error: Check for proper indentation and quoting{line_info}", True
    elif "mapping values are not allowed here" in error_msg:
        # This is usually a colon in an unquoted string
        return f"Found unquoted text containing colon that needs to be quoted{line_info}", True
    elif "did not find expected key" in error_msg:
        # This is often due to incorrect indentation or missing quotes
        return f"Found unquoted text containing colon that needs to be quoted{line_info}", True
    elif "found character '\\t'" in error_msg or "found character that cannot start any token" in error_msg:
        # Tab characters or other special characters that cause parsing problems
        return f"Found invalid characters in YAML (possibly tabs or special characters){line_info}", True
    elif "could not find expected ':'" in error_msg:
        # A key without a colon
        return f"Missing colon after key{line_info}", True
    elif "while scanning a quoted scalar" in error_msg:
        # Unbalanced quotes in a string
        return f"Unbalanced quotes in a string value{line_info}", True
    elif "found undefined alias" in error_msg:
        # YAML anchors/aliases are used but not defined
        return f"Found reference to undefined anchor{line_info}", False
    elif "expected a mapping node" in error_msg or "expected a sequence" in error_msg:
        # Type mismatch (expecting a mapping or sequence but got something else)
        return f"YAML type error: {error_msg}{line_info}", True
    elif "expected value after key" in error_msg:
        # Key without a value
        return f"Key without a value{line_info}", True
    elif "unexpected end of stream" in error_msg:
        # YAML document ends unexpectedly
        return f"Unexpected end of YAML document{line_info}", True
    elif "special characters are not allowed" in error_msg:
        # Special characters in an unquoted string
        return f"Special characters in an unquoted string{line_info}", True
    else:
        # Unknown error type
        return f"YAML parsing error: {error_msg}", False

def dump_yaml(data: dict) -> str:
    """Dump YAML data to a string with standard formatting."""
    yaml = create_yaml_parser()
    string_stream = StringIO()
    yaml.dump(data, string_stream)
    return string_stream.getvalue()

def reconstruct_content(data: dict, body: str) -> str:
    """Reconstruct the full content with YAML frontmatter."""
    return f"---\n{dump_yaml(data)}---{body}"
