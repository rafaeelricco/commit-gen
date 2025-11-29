"""
Markdown formatting utilities for console output.

This module provides functions for rendering markdown content to the console
with customizable padding and styling using the Rich library for enhanced
terminal output formatting.
"""

from typing import List
from rich.markdown import Markdown
from rich.padding import Padding

from common.console import get_console


class Format:
    @staticmethod
    def markdown(response: str, spacing: List[int] = [1, 0, 0, 0]) -> None:
        """
        Print markdown content to console with customizable padding.

        Args:
            response: The markdown text to be formatted and displayed
            spacing: List of 4 integers defining padding in CSS style order:
                    [top, right, bottom, left]. Default is [1, 0, 1, 0]
                    which adds 1 line above and below the content.

        Examples:
            Format.markdown("# Hello")                    # Default: 1 line above/below
            Format.markdown("Text", [2, 0, 2, 0])        # 2 lines above/below
            Format.markdown("Text", [0, 4, 1, 4])        # 4 spaces left/right, 1 line below
        """
        console = get_console()
        markdown = Markdown(response, justify="full")
        padded_content = Padding(markdown, (spacing[0], spacing[1], spacing[2], spacing[3]))
        console.print(padded_content)
