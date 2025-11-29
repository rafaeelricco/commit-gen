"""
HTTP response utilities and type definitions for the Quick Assistant API.

This module provides functions for converting application errors to HTTP responses
and defines response type structures for consistent API communication.
"""

from typing import Union, Any, Dict, TypedDict
from common.errors import Fail, Forbidden, Unauthorized, BadRequest, InternalServerError
from common.json import to_json


def to_response(
    failure: Union[Fail, Forbidden, Unauthorized, BadRequest, InternalServerError],
) -> tuple[Dict[str, Any], int]:
    """
    Convert application error types to HTTP response tuples.

    Maps domain-specific error types to appropriate HTTP status codes and response bodies.
    Each error type is converted to a standardized JSON response format.

    Args:
        failure: The error instance to convert (Fail, Forbidden, Unauthorized, BadRequest, or InternalServerError)

    Returns:
        Tuple of (response_data, status_code) where:
        - response_data: Dict containing error information in JSON format
        - status_code: Appropriate HTTP status code (400, 401, 403, 500, or custom Fail code)
    """
    match failure:
        case Fail():
            content = {"error": {"message": failure.message, "details": failure.details}}
            return content, failure.code
        case Forbidden():
            content = {"error": {"message": failure.message}}
            return content, 403
        case Unauthorized():
            content = {"error": {"message": failure.message}}
            return content, 401
        case BadRequest():
            content = {"error": {"message": failure.message, "details": failure.details}}
            return content, 400
        case InternalServerError():
            content = {"error": {"message": failure.message}}
            return content, 500


class TranslateResponse(TypedDict):
    """
    Type definition for translation API response structure.

    Defines the expected format for responses from translation endpoints,
    ensuring type safety and consistent response structure.
    """

    translation: str
    success: bool


def json_response(data: Union[Dict[str, Any], Any], status: int = 200) -> tuple[Dict[str, Any], int]:
    """
    Create a standardized JSON response tuple for successful API responses.

    Wraps response data with appropriate HTTP status code for consistent API responses.
    Automatically converts objects with to_json() method to dictionaries.

    Args:
        data: The response data (dict or object with to_json method)
        status: HTTP status code (default: 200 OK)

    Returns:
        Tuple of (response_data, status_code) ready for HTTP response handling
    """
    if isinstance(data, dict):
        json_data = data
    else:
        converted = to_json(data)
        if not isinstance(converted, dict):
            raise ValueError(f"Expected dict from to_json, got {type(converted).__name__}")
        json_data = converted
    return json_data, status
