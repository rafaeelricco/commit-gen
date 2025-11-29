"""
Shared console instance for Rich terminal output.

Centralizes Console creation to prevent flicker when multiple
Rich features (status, markdown, progress) render simultaneously.
"""

from rich.console import Console

_console: Console | None = None


def get_console() -> Console:
    """
    Return singleton Console instance.

    Returns:
        Shared Console for all Rich output operations
    """
    global _console
    if _console is None:
        _console = Console()
    return _console
