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
    result = ValidationResult(path=file_content.path)
    frontmatter = file_content.frontmatter
    
    # Validate required root fields
    for field in SCHEMA["root_required"]:
        if field not in frontmatter:
            result.errors.append(ValidationError(
                message=f"Missing required field: {field}",
                path=[field],
                fixable=False
            ))
    
    # Validate field types for all present fields (required and optional)
    for field in list(frontmatter.keys()):
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
                if frontmatter[field] != expected_type:
                    result.errors.append(ValidationError(
                        message=f"Field {field} must be exactly '{expected_type}', got '{frontmatter[field]}'",
                        path=[field],
                        fixable=True,
                        suggested_fix=expected_type
                    ))
            elif not isinstance(frontmatter[field], expected_type):
                result.errors.append(ValidationError(
                    message=f"Field {field} must be of type {expected_type.__name__}, got {type(frontmatter[field]).__name__}",
                    path=[field],
                    fixable=False
                ))
                
    # Validate date format if present
    for date_field in ["date", "lastmod"]:
        if date_field in frontmatter and isinstance(frontmatter[date_field], str):
            try:
                # Try to parse the date
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
    for field in list(params.keys()):
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
            validate_param_field(field, params[field], expected_type, result)
    
    # Special case for where_to_get
    if "where_to_get" in params and isinstance(params["where_to_get"], list):
        validate_where_to_get(params["where_to_get"], result)


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
        validate_list_field(field, value, item_type, result)
    else:
        # Simple type validation
        validate_simple_type(field, value, expected_type, result)


def validate_list_field(field: str, value: Any, item_type: Any, result: ValidationResult) -> None:
    """
    Validate a list field and its items.
    
    Args:
        field: Field name
        value: Field value to validate
        item_type: Expected type for list items
        result: ValidationResult to add errors to
    """
    if not isinstance(value, list):
        result.errors.append(ValidationError(
            message=f"Field params.{field} must be a list, got {type(value).__name__}",
            path=["params", field],
            fixable=True,
            suggested_fix=[value] if value else []
        ))
        return

    if isinstance(item_type, dict):
        # List of objects with specific schema
        for i, item in enumerate(value):
            if not isinstance(item, dict):
                result.errors.append(ValidationError(
                    message=f"Item {i} in params.{field} must be an object, got {type(item).__name__}",
                    path=["params", field, str(i)],
                    fixable=False
                ))
            else:
                validate_where_to_get_item(item, field, i, result)
    else:
        # List of simple types (str, int, etc.)
        for i, item in enumerate(value):
            if not isinstance(item, item_type):
                type_name = get_type_name(item_type)
                result.errors.append(ValidationError(
                    message=f"Item {i} in params.{field} must be of type {type_name}, got {type(item).__name__}",
                    path=["params", field, str(i)],
                    fixable=False
                ))


def validate_simple_type(field: str, value: Any, expected_type: Any, result: ValidationResult) -> None:
    """
    Validate a field with a simple type.
    
    Args:
        field: Field name
        value: Field value to validate
        expected_type: Expected type
        result: ValidationResult to add errors to
    """
    if not isinstance(value, expected_type):
        type_name = get_type_name(expected_type)
        result.errors.append(ValidationError(
            message=f"Field params.{field} must be of type {type_name}, got {type(value).__name__}",
            path=["params", field],
            fixable=False
        ))


def get_type_name(type_obj: Any) -> str:
    """
    Get a human-readable name for a type.
    
    Args:
        type_obj: Type object to get name for
        
    Returns:
        Human-readable type name
    """
    if hasattr(type_obj, "__name__"):
        return type_obj.__name__
    return str(type_obj)


def validate_where_to_get(where_to_get: list[dict[str, Any]], result: ValidationResult) -> None:
    """
    Validate where_to_get list items.
    
    Args:
        where_to_get: List of where_to_get items
        result: ValidationResult to add errors to
    """
    for i, item in enumerate(where_to_get):
        if not isinstance(item, dict):
            result.errors.append(ValidationError(
                message=f"Item {i} in params.where_to_get must be an object, got {type(item).__name__}",
                path=["params", "where_to_get", str(i)],
                fixable=False
            ))
            continue
            
        validate_where_to_get_item(item, "where_to_get", i, result)


def validate_where_to_get_item(item: dict[str, Any], field: str, index: int, result: ValidationResult) -> None:
    """
    Validate a single where_to_get item.
    
    Args:
        item: Item to validate
        field: Field name
        index: Index in the list
        result: ValidationResult to add errors to
    """
    # Check required fields
    for required_field in SCHEMA["where_to_get_required"]:
        if required_field not in item:
            result.errors.append(ValidationError(
                message=f"Missing required field '{required_field}' in params.{field}[{index}]",
                path=["params", field, str(index), required_field],
                fixable=False
            ))
    
    # Check field types
    for field_name, field_value in item.items():
        # Check if field is allowed
        if field_name not in SCHEMA["where_to_get_types"] and not SCHEMA["where_to_get_additionalProperties"]:
            result.errors.append(ValidationError(
                message=f"Unknown field '{field_name}' in params.{field}[{index}]",
                path=["params", field, str(index), field_name],
                fixable=True,
                suggested_fix=None  # Remove the field
            ))
            continue
            
        # Check field type
        if field_name in SCHEMA["where_to_get_types"]:
            expected_type = SCHEMA["where_to_get_types"][field_name]
            if not isinstance(field_value, expected_type):
                type_name = get_type_name(expected_type)
                result.errors.append(ValidationError(
                    message=f"Field '{field_name}' in params.{field}[{index}] must be of type {type_name}, got {type(field_value).__name__}",
                    path=["params", field, str(index), field_name],
                    fixable=False
                ))
                
            # Validate date format if it's a date field
            if field_name == "date" and isinstance(field_value, str):
                try:
                    datetime.datetime.strptime(field_value, DATE_FORMAT)
                except ValueError:
                    result.warnings.append(ValidationError(
                        message=f"Date in params.{field}[{index}].date is not in ISO format",
                        path=["params", field, str(index), "date"],
                        severity=ErrorSeverity.WARNING,
                        fixable=False
                    )) 