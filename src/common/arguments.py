"""
Command-line argument parsing and configuration for the Quick Assistant CLI tool.

This module provides utilities for parsing command-line arguments, defining command types,
and configuring argument parsers for different CLI operations like translation.
"""

import argparse

from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum


class CommandType(Enum):
    """
    Enumeration of supported command types in the Quick Assistant CLI.

    Defines the different operations that can be performed by the CLI tool,
    mapping command names to their string identifiers.
    """
    TRANSLATE = "translate"
    COMMIT = "commit"
    HELP = "help"

class ParsedArgs(BaseModel):
    """
    Immutable container for parsed command-line arguments.

    Holds the parsed values from CLI arguments and provides methods to determine
    which command type was specified. Uses Pydantic's frozen model for immutability.
    """
    model_config = ConfigDict(frozen=True)
    
    translate: Optional[str] = None
    commit: Optional[str] = None

    def get_command_type(self) -> CommandType:
        """
        Determine the command type based on which argument was provided.

        Returns:
            CommandType: The identified command type, defaults to HELP if none specified.
        """
        if self.translate:
            return CommandType.TRANSLATE
        elif self.commit:
            return CommandType.COMMIT
        else:
            return CommandType.HELP

class TranslateCLIArguments:
    """
    Configuration class for translation CLI arguments.

    Defines the command-line interface configuration for the translate command,
    including help text, examples, and argument definitions.
    """

    description = "Quick Assistant - CLI tool for productivity"
    flag = "--translate"
    help = "Text to translate from any language to English"
    epilog = (
      "Examples:\n"
      "    quick --translate \"hello world\"\n"
      "    quick --translate \"bonjour monde\""
    )

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Return parser configuration for translate arguments."""
        return {
            "prog": "quick",
            "description": cls.description,
            "epilog": cls.epilog,
            "arguments": [{"flag": cls.flag, "help": cls.help}]
        }



def create_parser(config: Dict[str, Any]) -> argparse.ArgumentParser:
    """
    Create and configure a generic argument parser from configuration dictionary.

    Args:
        config: Dictionary containing parser configuration with keys:
            - prog: Program name (default: "quick")
            - description: Program description
            - epilog: Text to display after help
            - arguments: List of argument dictionaries with "flag" and "help" keys

    Returns:
        Configured ArgumentParser instance ready for parsing CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog=config.get("prog", "quick"),
        description=config.get("description", ""),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=config.get("epilog", "")
    )

    arguments = config.get("arguments", [])
    for arg in arguments:
        parser.add_argument(arg["flag"], help=arg["help"])

    return parser
