"""
Loading indicators for long-running operations.

Provides context managers for displaying spinners and progress
indicators during async tasks using Rich library.
"""

from contextlib import contextmanager
from typing import Generator

from common.console import get_console


@contextmanager
def spinner(message: str, spinner_style: str = "dots") -> Generator[None, None, None]:
    """
    Display animated spinner during async operations.

    Args:
        message: Status text to show alongside spinner
        spinner_style: Rich spinner name (dots, line, arc, etc.)

    Yields:
        Control to calling code; spinner renders during block execution

    Examples:
        with spinner("Generating commit message…"):
            result = await api_call()

        with spinner("Processing", spinner_style="arc"):
            await long_operation()
    """
    console = get_console()
    with console.status(message, spinner=spinner_style):
        yield
