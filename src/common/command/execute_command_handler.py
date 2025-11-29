"""
Command execution utilities and orchestration for the CQRS system.

This module provides the core execution logic for processing commands through handlers.
It includes validation, error handling, authentication, and retry mechanisms to ensure
robust command processing with proper HTTP response generation.
"""

from typing import Type, TypeVar, Callable, Awaitable, Optional, Dict, Any, assert_never
from common.http_response import json_response as json_response, to_response
from common.json_parser import try_parse_json
from common.result import Ok, Err
from common.command.base_command import BaseCommand
from common.command.base_command_handler import BaseCommandHandler
from common.base import BaseFrozen
from common.errors import Fail, Forbidden, Unauthorized, BadRequest, InternalServerError


class BaseCommandResponse(BaseFrozen):
    """
    Immutable base class for command responses.

    Provides a standard interface for converting command results to dictionaries.
    """

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for JSON serialization."""
        return self.__dict__


C = TypeVar("C", bound=BaseCommand)


async def execute_command_handler(
    command_type: Type[C], request_data: Dict[str, Any], command_handler: Callable[[], BaseCommandHandler[C]]
) -> tuple[Dict[str, Any], int]:
    """
    Execute a command handler with validation and error handling.

    Orchestrates the complete command execution flow:
    1. Parse and validate input JSON against command schema
    2. Execute the command handler
    3. Convert exceptions to proper HTTP responses

    Args:
        command_type: The command class to validate against
        request_data: Raw request data to parse
        command_handler: Factory function returning the handler instance

    Returns:
        Tuple of (response_data, status_code) for HTTP response
    """

    rcommand = try_parse_json(command_type, request_data)
    match rcommand.inner:
        case Err(error=error):
            return to_response(BadRequest(message=f"Invalid request schema: {error}"))
        case Ok(value=value):
            command = value
        case _:
            assert_never(rcommand)

    try:
        result = await command_handler().handle_command(command)
        return result
    except Fail as failure:
        return to_response(failure)
    except Forbidden as failure:
        return to_response(failure)
    except Unauthorized as failure:
        return to_response(failure)
    except BadRequest as failure:
        return to_response(failure)
    except Exception as error:
        return to_response(InternalServerError(message=f"Internal error: {str(error)}"))


async def execute_command_handler_with_api_key(
    command_type: Type[C],
    request_data: Dict[str, Any],
    api_key_header: Optional[str],
    required_api_key: str,
    command_handler: Callable[[], BaseCommandHandler[C]],
) -> tuple[Dict[str, Any], int]:
    """
    Execute command handler with API key authentication.

    Validates API key before delegating to standard command execution.

    Args:
        command_type: The command class to validate against
        request_data: Raw request data to parse
        api_key_header: API key from request header
        required_api_key: Expected API key value
        command_handler: Factory function returning the handler instance

    Returns:
        Tuple of (response_data, status_code) for HTTP response
    """

    if api_key_header != required_api_key:
        return to_response(Unauthorized(message="Invalid API key"))

    return await execute_command_handler(command_type, request_data, command_handler)


async def retrying_on_failure(
    max_retries: int, action: Callable[[], Awaitable[tuple[Dict[str, Any], int]]]
) -> tuple[Dict[str, Any], int]:
    """
    Retry an action on failure with simple retry logic.

    Executes the action up to max_retries times, re-raising the last exception
    if all attempts fail.

    Args:
        max_retries: Maximum number of retry attempts
        action: Async function to retry

    Returns:
        Successful action result

    Raises:
        RuntimeError: If all retry attempts are exhausted
    """
    error: Optional[Exception] = None
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = await action()
            return response
        except Exception as err:
            error = err
            retry_count += 1

    if error is None:
        raise RuntimeError("Retries exhausted without an error")

    msg = f"Unable to complete after {max_retries} retries: {error}"
    raise RuntimeError(msg) from error
