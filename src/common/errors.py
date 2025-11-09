from dataclasses import dataclass
from typing import Optional, Any
from common.base import BaseFrozen


@dataclass(frozen=True)
class Fail(Exception, BaseFrozen):
    """General failure with status code."""
    code: int
    message: str
    details: Optional[Any] = None


@dataclass(frozen=True)
class Forbidden(Exception, BaseFrozen):
    """403 Forbidden error."""
    message: str


@dataclass(frozen=True)
class Unauthorized(Exception, BaseFrozen):
    """401 Unauthorized error."""
    message: str


@dataclass(frozen=True)
class BadRequest(Exception, BaseFrozen):
    """400 Bad Request error."""
    message: str
    details: Optional[Any] = None


@dataclass(frozen=True)
class InternalServerError(Exception, BaseFrozen):
    """500 Internal Server Error."""
    message: str


def annotate(message: str, error: Exception) -> Exception:
    """Annotate an exception with additional context."""
    error.args = (f"{message}: {error.args[0]}" if error.args else message,) + error.args[1:]
    return error