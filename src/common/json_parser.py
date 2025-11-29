"""
JSON parsing utilities with Pydantic validation.

This module provides safe JSON parsing functionality that integrates with Pydantic models
and returns Result types for functional error handling. It ensures type-safe data validation
and provides detailed error messages for validation failures.
"""

from typing import Type, TypeVar, Dict, Any
from common.result import Result, Ok, Err
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def try_parse_json(model_type: Type[T], data: Dict[str, Any]) -> Result[str, T]:
    """
    Parse JSON data into a Pydantic model safely.
    Returns Result[error_message, parsed_model].
    """
    try:
        parsed = model_type.model_validate(data)
        return Result(Ok(parsed))
    except ValidationError as e:
        error_message = "; ".join([f"{err['loc']}: {err['msg']}" for err in e.errors()])
        return Result(Err(error_message))
    except Exception as e:
        return Result(Err(str(e)))
