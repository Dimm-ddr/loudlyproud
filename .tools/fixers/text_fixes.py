def fix_text_content(content: str, field_name: str) -> tuple[str, list[str]]:
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
        fixed_content, fixes = fix_text_content(content, field)
        if fixes:
            content = fixed_content
            all_fixes.extend(fixes)

    return content, all_fixes
