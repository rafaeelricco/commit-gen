from typing import Union, Any, Dict, TypedDict
from common.errors import Fail, Forbidden, Unauthorized, BadRequest, InternalServerError


def to_response(failure: Union[Fail, Forbidden, Unauthorized, BadRequest, InternalServerError]) -> tuple[Dict[str, Any], int]:
    """Convert error types to HTTP response tuples."""
    match failure:
        case Fail():
            content = {'error': {'message': failure.message, 'details': failure.details}}
            return content, failure.code
        case Forbidden():
            content = {'error': {'message': failure.message}}
            return content, 403
        case Unauthorized():
            content = {'error': {'message': failure.message}}
            return content, 401
        case BadRequest():
            content = {'error': {'message': failure.message, 'details': failure.details}}
            return content, 400
        case InternalServerError():
            content = {'error': {'message': failure.message}}
            return content, 500


class TranslateResponse(TypedDict):
    translation: str
    success: bool

def json_response(data: Dict[str, Any], status: int = 200) -> tuple[Dict[str, Any], int]:
    """Create a JSON response tuple."""
    return data, status