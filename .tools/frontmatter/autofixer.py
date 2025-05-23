"""
Autofixer for frontmatter validation issues.
"""
from typing import Any

from .types import FileContent, ValidationResult
from .extractor import write_frontmatter


def autofix_frontmatter(file_content: FileContent, validation_result: ValidationResult) -> bool:
    """
    Attempt to fix validation issues in frontmatter.
    
    Args:
        file_content: FileContent object with frontmatter to fix
        validation_result: ValidationResult with errors to fix
        
    Returns:
        bool: True if any fixes were applied, False otherwise
    """
    frontmatter = file_content.frontmatter
    fixed = False
    
    # Filter only fixable errors
    fixable_errors = [error for error in validation_result.errors if error.fixable]
    
    # Apply fixes
    for error in fixable_errors:
        if len(error.path) == 1 and error.path[0] in frontmatter:
            # Root level field with suggested fix
            if error.suggested_fix is not None:
                frontmatter[error.path[0]] = error.suggested_fix
                fixed = True
            # Root level field to remove
            elif error.suggested_fix is None:
                del frontmatter[error.path[0]]
                fixed = True
                
        elif len(error.path) >= 2 and error.path[0] == "params" and error.path[1] in frontmatter.get("params", {}):
            # Params field with suggested fix
            if error.suggested_fix is not None:
                if len(error.path) == 2:
                    frontmatter["params"][error.path[1]] = error.suggested_fix
                    fixed = True
            # Params field to remove
            elif error.suggested_fix is None:
                del frontmatter["params"][error.path[1]]
                fixed = True
                
        elif len(error.path) >= 4 and error.path[0] == "params" and error.path[1] == "where_to_get":
            # Try to parse the index
            try:
                index = int(error.path[2])
                field = error.path[3]
                
                # Make sure the index is valid
                if "where_to_get" in frontmatter.get("params", {}) and isinstance(frontmatter["params"]["where_to_get"], list):
                    if 0 <= index < len(frontmatter["params"]["where_to_get"]):
                        # Field with suggested fix
                        if error.suggested_fix is not None:
                            frontmatter["params"]["where_to_get"][index][field] = error.suggested_fix
                            fixed = True
                        # Field to remove
                        elif error.suggested_fix is None and field in frontmatter["params"]["where_to_get"][index]:
                            del frontmatter["params"]["where_to_get"][index][field]
                            fixed = True
            except (ValueError, IndexError):
                pass
    
    # Write fixed frontmatter back to file if changes were made
    if fixed:
        write_frontmatter(file_content)
        
    return fixed


def fix_field_order(file_content: FileContent) -> bool:
    """
    Fix the order of fields in frontmatter.
    
    Args:
        file_content: FileContent object with frontmatter to fix
        
    Returns:
        bool: True if order was fixed, False otherwise
    """
    # Define the preferred order of fields
    root_order = ["title", "draft", "slug", "type", "date", "lastmod", "weight", "description", "params"]
    params_order = [
        "authors", "book_title", "translators", "short_book_description", 
        "cover", "cover_alt", "isbn", "additional_isbns", "languages", 
        "page_count", "publication_year", "goodreads_link", "series", 
        "where_to_get", "publishers", "russian_translation_status",
        "russian_audioversion", "tags"
    ]
    
    frontmatter = file_content.frontmatter
    fixed = False
    
    # Create a new ordered frontmatter dict
    ordered_frontmatter: dict[str, Any] = {}
    
    # Add root fields in the preferred order
    for field in root_order:
        if field in frontmatter:
            ordered_frontmatter[field] = frontmatter[field]
    
    # Add any remaining fields not in the preferred order
    for field in frontmatter:
        if field not in ordered_frontmatter:
            ordered_frontmatter[field] = frontmatter[field]
    
    # If params exists and is a dict, order its fields
    if "params" in ordered_frontmatter and isinstance(ordered_frontmatter["params"], dict):
        params = ordered_frontmatter["params"]
        ordered_params: dict[str, Any] = {}
        
        # Add params fields in the preferred order
        for field in params_order:
            if field in params:
                ordered_params[field] = params[field]
        
        # Add any remaining params fields not in the preferred order
        for field in params:
            if field not in ordered_params:
                ordered_params[field] = params[field]
        
        # Replace params with ordered params
        ordered_frontmatter["params"] = ordered_params
        
        # Check if anything changed
        if ordered_params != params:
            fixed = True
    
    # Check if anything changed at the root level
    if ordered_frontmatter != frontmatter:
        fixed = True
        
    # Update frontmatter if changes were made
    if fixed:
        file_content.frontmatter = ordered_frontmatter
        write_frontmatter(file_content)
        
    return fixed 