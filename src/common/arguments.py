"""
Command-line argument parsing and configuration for the Quick Assistant CLI tool.

This module provides utilities for parsing command-line arguments, defining command types,
and configuring argument parsers for different CLI operations.
"""

import argparse

from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum


class CommandType(Enum):
    """
    Enumeration of supported command types in the Quick Assistant CLI.

    Attributes:
        COMMIT: Commit message generation command for git operations
        UPDATE: Update command for self-updating the CLI tool
        HELP: Help command displayed when no valid command is provided
    """

    COMMIT = "commit"
    UPDATE = "update"
    HELP = "help"


class ParsedArgs(BaseModel):
    """
    Immutable container for parsed command-line arguments.

    Holds the parsed command and provides methods to determine
    which command type was specified. Uses Pydantic's frozen model for immutability.
    """

    model_config = ConfigDict(frozen=True)

    command: Optional[str] = None

    def get_command_type(self) -> CommandType:
        """
        Determine the command type based on the subcommand provided.

        Returns:
            CommandType: The identified command type, defaults to HELP if none specified.
        """
        match self.command:
            case "commit":
                return CommandType.COMMIT
            case "update":
                return CommandType.UPDATE
            case _:
                return CommandType.HELP


class QuickCLIConfig:
    """
    Main CLI configuration for Quick Assistant.

    Provides configuration for the CLI tool including program description and examples.
    """

    prog = "quick"
    description = "Quick Assistant - CLI tool for productivity"
    epilog = "Examples:\n    quick commit\n    quick update"


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser with subcommands.

    Returns:
        Configured ArgumentParser instance ready for parsing CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog=QuickCLIConfig.prog,
        description=QuickCLIConfig.description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=QuickCLIConfig.epilog,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("commit", help="Generate a commit message")
    subparsers.add_parser("update", help="Update quick-assistant to the latest version")

    return parser
