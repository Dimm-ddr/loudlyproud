from .fixer_registry import register_text_fixer

@register_text_fixer
def fix_text_content(content: str) -> tuple[str, list[str]]:
    """Fix text content issues."""
    fixes = []
    
    # Fix HTML line breaks in specific fields
    text_fields = ["book_description", "short_book_description"]
    for field in text_fields:
        fixed_content, field_fixes = fix_field_content(content, field)
        if field_fixes:
            content = fixed_content
            fixes.extend(field_fixes)
    
    return content, fixes

@register_text_fixer
def fix_yaml_structure(content: str) -> tuple[str, list[str]]:
    """Fix common YAML structural issues before parsing."""
    fixes = []
    
    # Split into frontmatter and content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content, fixes
        
    frontmatter = parts[1]
    rest = parts[2]
    
    # Fix common issues:
    # 1. Unquoted values with colons
    lines = frontmatter.split("\n")
    fixed_lines = []
    
    for line in lines:
        if ":" in line and not line.strip().startswith("#"):
            # Split only on the first colon
            key_part, value_part = line.split(":", 1)
            
            # Check if value part contains a colon that should be quoted
            if ":" in value_part and not (
                value_part.strip().startswith('"') or 
                value_part.strip().startswith("'")
            ):
                value = value_part.strip()
                fixed_line = f'{key_part}: "{value}"'
                fixes.append("Added quotes around value containing colon")
            else:
                fixed_line = line
        else:
            fixed_line = line
            
        fixed_lines.append(fixed_line)
    
    # Rebuild content if fixes were applied
    if fixes:
        new_frontmatter = "\n".join(fixed_lines)
        return f"---\n{new_frontmatter}---{rest}", fixes
        
    return content, fixes

@register_text_fixer
def fix_unbalanced_quotes(content: str) -> tuple[str, list[str]]:
    """Fix unbalanced quotes in YAML values."""
    fixes = []
    
    # Split into frontmatter and content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content, fixes
        
    frontmatter = parts[1]
    rest = parts[2]
    
    # Process each field that might have unbalanced quotes
    fields_to_check = ["book_description", "short_book_description"]
    lines = frontmatter.split("\n")
    in_multiline = False
    field_name = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check for field start
        if not in_multiline:
            for field in fields_to_check:
                if stripped.startswith(f"{field}:"):
                    # Count quotes in the value part
                    value_part = stripped.split(":", 1)[1].strip()
                    quote_count = value_part.count('"')
                    
                    # Detect unbalanced quotes
                    if quote_count > 0 and quote_count % 2 != 0:
                        # Fix unbalanced quotes by ensuring proper wrapping
                        if value_part.startswith('"""') or value_part.startswith('"'):
                            # If already has opening quotes, ensure proper closing
                            if not value_part.endswith('"'):
                                lines[i] = line.replace(value_part, f'{value_part}"')
                                fixes.append(f"Fixed unbalanced quotes in {field}")
                        else:
                            # Wrap in quotes if missing
                            lines[i] = line.replace(value_part, f'"{value_part}"')
                            fixes.append(f"Added quotes around {field} value")
                            
                    # Check for multiline start
                    if ">" in value_part or "|" in value_part:
                        in_multiline = True
                        field_name = field
                    
        # Check for orphaned continuation lines that should be indented
        elif in_multiline and not stripped.startswith(" ") and not stripped == "":
            if not stripped.startswith("-") and ":" not in stripped:
                # This is likely a continuation line that needs indentation
                lines[i] = f"  {line}"
                fixes.append(f"Fixed indentation for continuation line in {field_name}")
            else:
                # End of multiline block
                in_multiline = False
                
    # Rebuild content if fixes were applied
    if fixes:
        new_frontmatter = "\n".join(lines)
        return f"---\n{new_frontmatter}---{rest}", fixes
        
    return content, fixes

@register_text_fixer
def sanitize_yaml_content(content: str) -> tuple[str, list[str]]:
    """Sanitize YAML content by replacing problematic characters."""
    fixes = []
    
    # Split into frontmatter and content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content, fixes
        
    frontmatter = parts[1]
    rest = parts[2]
    
    # Replace tabs with spaces
    if "\t" in frontmatter:
        frontmatter = frontmatter.replace("\t", "  ")
        fixes.append("Replaced tabs with spaces")
    
    # Fix trailing spaces in multiline blocks
    lines = frontmatter.split("\n")
    
    for i, line in enumerate(lines):
        # Replace non-breaking spaces with regular spaces
        if "\u00A0" in line:
            lines[i] = line.replace("\u00A0", " ")
            fixes.append("Replaced non-breaking spaces")
            
        # Fix trailing colons in keys
        if ":" in line and not line.strip().startswith("#"):
            parts = line.split(":", 1)
            if not parts[0].strip():
                continue
                
            # Check if there's a space missing after the colon
            if len(parts) > 1 and parts[1] and not parts[1].startswith(" "):
                lines[i] = f"{parts[0]}: {parts[1]}"
                fixes.append("Added space after colon")
    
    # Rebuild content if fixes were applied
    if fixes:
        new_frontmatter = "\n".join(lines)
        return f"---\n{new_frontmatter}---{rest}", fixes
        
    return content, fixes

@register_text_fixer
def fix_multiline_indentation(content: str) -> tuple[str, list[str]]:
    """Fix indentation issues in multiline fields without block indicators."""
    fixes = []
    
    # Split into frontmatter and content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content, fixes
        
    frontmatter = parts[1]
    rest = parts[2]
    
    lines = frontmatter.split("\n")
    current_field = None
    in_field = False
    result_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            result_lines.append(line)
            continue
            
        # Check if this is a field definition (contains a colon not in a comment)
        if ":" in line and not line.strip().startswith("#"):
            indentation = len(line) - len(line.lstrip())
            if indentation == 2:  # This is a top-level field
                # Extract field name
                field_name = line.split(":", 1)[0].strip()
                current_field = field_name
                in_field = True
                result_lines.append(line)
            else:
                # This is already an indented field or sub-field
                result_lines.append(line)
                
        # Handle non-property lines that should be indented
        elif in_field and not stripped.startswith("-") and ":" not in stripped:
            # Check if this line is already indented
            if line.startswith("  "):
                result_lines.append(line)
            else:
                # This line needs to be indented as it's part of a multiline field
                # Check for Braille Unicode characters that might be trying to create a blank line
                if any(ord(c) >= 0x2800 and ord(c) <= 0x28FF for c in stripped):
                    # This is a Braille character line that should be indented
                    result_lines.append(f"  {stripped}")
                    fixes.append(f"Indented Braille character line in {current_field}")
                else:
                    # Regular content that needs indentation
                    result_lines.append(f"  {line}")
                    fixes.append(f"Fixed indentation for continuation line in {current_field}")
        else:
            # This is a new element, end the current field
            in_field = False
            result_lines.append(line)
    
    # Rebuild content if fixes were applied
    if fixes:
        new_frontmatter = "\n".join(result_lines)
        return f"---\n{new_frontmatter}---{rest}", fixes
        
    return content, fixes

@register_text_fixer
def fix_loose_quoted_content(content: str) -> tuple[str, list[str]]:
    """Fix standalone quoted lines that should be part of another field."""
    fixes = []
    
    # Split into frontmatter and content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content, fixes
        
    frontmatter = parts[1]
    rest = parts[2]
    
    lines = frontmatter.split("\n")
    processed_lines = []
    last_field = None
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Process a normal field
        if ":" in line and not line.strip().startswith("#"):
            field_indent = len(line) - len(line.lstrip())
            if field_indent == 2:  # This is a main field definition
                field_name = line.split(":", 1)[0].strip()
                last_field = field_name
                
            processed_lines.append(line)
        
        # Check for orphaned quoted strings that stand alone as their own "field"
        elif stripped.startswith('"') and stripped.endswith('"') and ":" in stripped and " :" not in stripped:
            # This looks like a quoted string with a colon inside, but formatted as if it were a field
            # It's likely part of the previous field
            if last_field and i > 0:
                # If the previous line was a field, it needs to be part of that field
                if processed_lines and ":" in processed_lines[-1]:
                    # Convert this to be a continuation of the previous field
                    processed_lines.append(f"  {stripped}")
                    fixes.append(f"Fixed orphaned quoted text as continuation of {last_field}")
                else:
                    # Otherwise, just pass it through
                    processed_lines.append(line)
            else:
                # No context to fix it
                processed_lines.append(line)
        else:
            processed_lines.append(line)
            
        i += 1
    
    # Rebuild content if fixes were applied
    if fixes:
        new_frontmatter = "\n".join(processed_lines)
        return f"---\n{new_frontmatter}---{rest}", fixes
        
    return content, fixes

@register_text_fixer
def fix_multiple_quotes(content: str) -> tuple[str, list[str]]:
    """Fix fields with excessive quotes (like triple double-quotes around text)."""
    fixes = []
    
    # Split into frontmatter and content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return content, fixes
        
    frontmatter = parts[1]
    rest = parts[2]
    
    # Look for patterns of multiple consecutive quotes
    lines = frontmatter.split("\n")
    for i, line in enumerate(lines):
        if ":" in line and not line.strip().startswith("#"):
            # This is a field - check its value
            key_part, value_part = line.split(":", 1)
            value = value_part.strip()
            
            # Check for multiple consecutive quotes
            if value.startswith('"""') or value.endswith('"""'):
                # Fix by replacing multiple quotes with a single set
                if value.startswith('"""'):
                    value = value[2:]  # Remove two of the quotes at start
                if value.endswith('"""'):
                    value = value[:-2]  # Remove two of the quotes at end
                
                # Rebuild the line
                lines[i] = f"{key_part}: {value}"
                fixes.append(f"Fixed multiple consecutive quotes in {key_part.strip()}")
                
            # Check for unbalanced quotes (odd number of quotes)
            elif value.count('"') % 2 != 0 and not (value.startswith('"') and value.endswith('"')):
                # Try to fix by ensuring quotes are balanced
                if value.startswith('"') and not value.endswith('"'):
                    value = f"{value}\""
                elif not value.startswith('"') and value.endswith('"'):
                    value = f"\"{value}"
                elif not value.startswith('"') and not value.endswith('"') and '"' in value:
                    # Escape internal quotes or add quotes at the boundaries
                    value = f"\"{value}\""
                
                # Rebuild the line
                lines[i] = f"{key_part}: {value}"
                fixes.append(f"Balanced quotes in {key_part.strip()}")
    
    # Rebuild content if fixes were applied
    if fixes:
        new_frontmatter = "\n".join(lines)
        return f"---\n{new_frontmatter}---{rest}", fixes
        
    return content, fixes

def fix_field_content(content: str, field_name: str) -> tuple[str, list[str]]:
    """Fix text content issues in a specific field."""
    fixes = []
    modified = False

    # Find the field in the content
    field_marker = f"  {field_name}: "
    start = content.find(field_marker)
    if start == -1:
        return content, fixes

    # Find the end of the field
    next_field = content.find("\n  ", start + len(field_marker))
    if next_field == -1:
        next_field = content.find("\n---", start)

    if next_field == -1:
        return content, fixes

    field_content = content[start:next_field]
    new_content = field_content

    # Fix HTML line breaks
    if "<br" in new_content:
        # Get the value part after the field marker
        value = new_content[len(field_marker):].strip()
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        
        # Replace <br> tags with newlines
        value = value.replace("<br />", "\n")
        value = value.replace("<br/>", "\n")
        value = value.replace("<br>", "\n")
        
        # Format as YAML multiline string
        new_content = f'{field_marker}|-\n    {value.replace("\n", "\n    ")}'
        modified = True
        fixes.append(f"Converted HTML line breaks to YAML multiline in {field_name}")

    # Fix \n symbols
    if "\\n" in new_content:
        temp = new_content.replace("\\n\\n", "\x00")
        temp = temp.replace("\\n", " ")
        new_content = temp.replace("\x00", "\n\n  ")
        modified = True
        fixes.append(f"Fixed line breaks in {field_name}")

    # Fix ampersands
    if "&" in new_content and "&amp;" not in new_content:
        new_content = new_content.replace("&", "&amp;")
        modified = True
        fixes.append(f"Escaped ampersands in {field_name}")

    # Ensure proper quoting of strings with quotes
    if '"' in new_content and not new_content.strip().startswith('"'):
        # If field contains quotes but isn't properly quoted, add quotes
        value = new_content[len(field_marker) :].strip()
        new_content = f'{field_marker}"{value}"'
        modified = True
        fixes.append(f"Fixed quoting in {field_name}")

    if modified:
        return content[:start] + new_content + content[next_field:], fixes

    return content, fixes

def apply_text_fixes(content: str) -> tuple[str, list[str]]:
    """Apply all text-based fixes to content."""
    all_fixes = []

    text_fields = ["book_description", "short_book_description"]
    for field in text_fields:
        fixed_content, fixes = fix_text_content(content)
        if fixes:
            content = fixed_content
            all_fixes.extend(fixes)

    return content, all_fixes
