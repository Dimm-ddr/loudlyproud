"""
Validate frontmatter against schema.
"""
import datetime
from typing import Any

from .constants import DATE_FORMAT
from .schema import SCHEMA
from .types import ErrorSeverity, FileContent, ValidationError, ValidationResult


def validate_frontmatter(file_content: FileContent) -> ValidationResult:
    """
    Validate frontmatter against schema.
    
    Args:
        file_content: FileContent object with frontmatter to validate
        
    Returns:
        ValidationResult with any errors or warnings found
    """
    result = ValidationResult(path=file_content.path, is_valid=True)
    frontmatter = file_content.frontmatter
    
    # Validate required root fields
    for field in SCHEMA["root_required"]:
        if field not in frontmatter:
            result.errors.append(ValidationError(
                message=f"Missing required field: {field}",
                path=[field],
                fixable=False
            ))
    
    # Validate field types for all present fields
    for field, value in frontmatter.items():
        # Check if field is allowed
        if field not in SCHEMA["root_required"] and field not in SCHEMA["root_optional"]:
            if not SCHEMA["root_additionalProperties"]:
                result.errors.append(ValidationError(
                    message=f"Unknown field: {field}",
                    path=[field],
                    fixable=True,
                    suggested_fix=None  # Remove the field
                ))
            continue
            
        # Check field type
        if field in SCHEMA["root_types"]:
            expected_type = SCHEMA["root_types"][field]
            if isinstance(expected_type, str):
                # Exact value check (enum with one value)
                if value != expected_type:
                    result.errors.append(ValidationError(
                        message=f"Field {field} must be exactly '{expected_type}', got '{value}'",
                        path=[field],
                        fixable=True,
                        suggested_fix=expected_type
                    ))
            elif not isinstance(value, expected_type):
                result.errors.append(ValidationError(
                    message=f"Field {field} must be of type {expected_type.__name__}, got {type(value).__name__}",
                    path=[field],
                    fixable=False
                ))
                
    # Validate date format if present
    for date_field in ["date", "lastmod"]:
        if date_field in frontmatter and isinstance(frontmatter[date_field], str):
            try:
                datetime.datetime.strptime(frontmatter[date_field], DATE_FORMAT)
            except ValueError:
                result.warnings.append(ValidationError(
                    message=f"Field {date_field} is not in ISO format (YYYY-MM-DDTHH:MM:SS+ZZZZ)",
                    path=[date_field],
                    severity=ErrorSeverity.WARNING,
                    fixable=False
                ))
    
    # If params field exists and is a dict, validate its contents
    if "params" in frontmatter and isinstance(frontmatter["params"], dict):
        validate_params(frontmatter["params"], result)
    
    if result.errors:
        result.is_valid = False
    
    return result


def validate_params(params: dict[str, Any], result: ValidationResult) -> None:
    """
    Validate params section of frontmatter.
    
    Args:
        params: Params dict from frontmatter
        result: ValidationResult to add errors to
    """
    # Validate required params fields
    for field in SCHEMA["params_required"]:
        if field not in params:
            result.errors.append(ValidationError(
                message=f"Missing required params field: {field}",
                path=["params", field],
                fixable=False
            ))
    
    # Validate field types for all present params fields
    for field, value in params.items():
        # Check if field is allowed
        if field not in SCHEMA["params_required"] and field not in SCHEMA["params_optional"]:
            if not SCHEMA["params_additionalProperties"]:
                result.errors.append(ValidationError(
                    message=f"Unknown params field: {field}",
                    path=["params", field],
                    fixable=True,
                    suggested_fix=None  # Remove the field
                ))
            continue
            
        # Check field type based on schema
        if field in SCHEMA["params_types"]:
            expected_type = SCHEMA["params_types"][field]
            validate_param_field(field, value, expected_type, result)


def validate_param_field(field: str, value: Any, expected_type: Any, result: ValidationResult) -> None:
    """
    Validate a single param field against its expected type.
    
    Args:
        field: Field name
        value: Field value to validate
        expected_type: Expected type from schema
        result: ValidationResult to add errors to
    """
    if isinstance(expected_type, tuple):
        # Enum validation
        if value not in expected_type:
            result.errors.append(ValidationError(
                message=f"Field params.{field} must be one of {expected_type}, got '{value}'",
                path=["params", field],
                fixable=False
            ))
    elif isinstance(expected_type, list) and len(expected_type) == 1:
        # List validation
        item_type = expected_type[0]
        if not isinstance(value, list):
            result.errors.append(ValidationError(
                message=f"Field params.{field} must be a list, got {type(value).__name__}",
                path=["params", field],
                fixable=True,
                suggested_fix=[value] if value else []
            ))
            return
            
        # Validate list items
        for i, item in enumerate(value):
            if isinstance(item_type, dict):
                # List of objects with specific schema
                if not isinstance(item, dict):
                    result.errors.append(ValidationError(
                        message=f"Item {i} in params.{field} must be an object, got {type(item).__name__}",
                        path=["params", field, str(i)],
                        fixable=False
                    ))
                else:
                    validate_where_to_get_item(item, field, i, result)
            elif not isinstance(item, item_type):
                result.errors.append(ValidationError(
                    message=f"Item {i} in params.{field} must be of type {item_type.__name__}, got {type(item).__name__}",
                    path=["params", field, str(i)],
                    fixable=False
                ))
    else:
        # Simple type validation
        if not isinstance(value, expected_type):
            result.errors.append(ValidationError(
                message=f"Field params.{field} must be of type {expected_type.__name__}, got {type(value).__name__}",
                path=["params", field],
                fixable=False
            ))


def validate_where_to_get_item(item: dict[str, Any], field: str, index: int, result: ValidationResult) -> None:
    """
    Validate a where_to_get item.
    
    Args:
        item: Item to validate
        field: Field name
        index: Item index
        result: ValidationResult to add errors to
    """
    # Validate required fields
    for required_field in SCHEMA["where_to_get_required"]:
        if required_field not in item:
            result.errors.append(ValidationError(
                message=f"Missing required field '{required_field}' in params.{field}[{index}]",
                path=["params", field, str(index), required_field],
                fixable=False
            ))
    
    # Validate field types and check for unknown fields
    for field_name, value in item.items():
        if field_name not in SCHEMA["where_to_get_types"]:
            if not SCHEMA["where_to_get_additionalProperties"]:
                result.errors.append(ValidationError(
                    message=f"Unknown field '{field_name}' in params.{field}[{index}]",
                    path=["params", field, str(index), field_name],
                    fixable=True,
                    suggested_fix=None  # Remove the field
                ))
            continue
            
        expected_type = SCHEMA["where_to_get_types"][field_name]
        if not isinstance(value, expected_type):
            result.errors.append(ValidationError(
                message=f"Field '{field_name}' in params.{field}[{index}] must be of type {expected_type.__name__}, got {type(value).__name__}",
                path=["params", field, str(index), field_name],
                fixable=False
            ))
                
            # Validate date format if it's a date field
            if field_name == "date" and isinstance(value, str):
                try:
                    datetime.datetime.strptime(value, DATE_FORMAT)
                except ValueError:
                    result.warnings.append(ValidationError(
                        message=f"Date in params.{field}[{index}].date is not in ISO format",
                        path=["params", field, str(index), "date"],
                        severity=ErrorSeverity.WARNING,
                        fixable=False
                    )) 