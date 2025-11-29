"""Error handling types and utilities for the application.

This module defines structured error classes for different HTTP error scenarios,
providing consistent error handling and response formatting throughout the application.
All error types are immutable and inherit from Exception.
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass(frozen=True)
class Fail(Exception):
    """General failure with status code."""

    code: int
    message: str
    details: Optional[Any] = None


@dataclass(frozen=True)
class Forbidden(Exception):
    """403 Forbidden error."""

    message: str


@dataclass(frozen=True)
class Unauthorized(Exception):
    """401 Unauthorized error."""

    message: str


@dataclass(frozen=True)
class BadRequest(Exception):
    """400 Bad Request error."""

    message: str
    details: Optional[Any] = None


@dataclass(frozen=True)
class InternalServerError(Exception):
    """500 Internal Server Error."""

    message: str


def annotate(message: str, error: Exception) -> Exception:
    """Annotate an exception with additional context."""
    error.args = (f"{message}: {error.args[0]}" if error.args else message,) + error.args[1:]
    return error
