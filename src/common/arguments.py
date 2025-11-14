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

    Attributes:
        TRANSLATE: Translation command for converting text between languages
        COMMIT: Commit message generation command for git operations
        HELP: Help command displayed when no valid command is provided
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

    flag = "--translate"
    help = "Text to translate from any language to English"

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Return parser configuration for translate arguments.

        Returns:
            Dictionary containing parser configuration with keys:
                - flag: Command flag string ("--translate")
                - help: Help text describing the translation command's purpose
        """
        return {"flag": cls.flag, "help": cls.help}


class CommitCLIArguments:
    """
    Configuration class for commit CLI arguments.

    Defines the command-line interface configuration for the commit command,
    including help text and argument definitions.
    """

    flag = "--commit"
    help = "Generate a commit message"
    choices = ["generate"]

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Return parser configuration for commit arguments.

        Returns:
            Dictionary containing parser configuration with keys:
                - flag: Command flag string ("--commit")
                - help: Help text describing the commit command's purpose
                - choices: List of valid subcommands (e.g., ["generate"])
        """
        return {"flag": cls.flag, "help": cls.help, "choices": cls.choices}


class QuickCLIConfig:
    """
    Main CLI configuration combining all command types.
    
    Provides unified configuration for the Quick Assistant CLI tool,
    including program description, examples, and all command configurations.
    """

    description = "Quick Assistant - CLI tool for productivity"
    epilog = (
        "Examples:\n"
        "    quick --translate \"hello world\"\n"
        "    quick --translate \"bonjour monde\"\n"
        "    quick --commit generate"
    )

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Return complete parser configuration.

        Returns:
            Dictionary containing complete CLI configuration with keys:
                - prog: Program name ("quick")
                - description: CLI tool description text
                - epilog: Usage examples displayed in help text
                - commands: List of command configuration dictionaries from
                           TranslateCLIArguments and CommitCLIArguments
        """
        return {
            "prog": "quick",
            "description": cls.description,
            "epilog": cls.epilog,
            "commands": [
                TranslateCLIArguments.get_config(),
                CommitCLIArguments.get_config()
            ]
        }



def create_parser(config: Dict[str, Any]) -> argparse.ArgumentParser:
    """
    Create and configure a generic argument parser from configuration dictionary.

    Args:
        config: Dictionary containing parser configuration with keys:
            - prog: Program name (default: "quick")
            - description: Program description
            - epilog: Text to display after help
            - commands: List of command dictionaries with "flag", "help", and optional "choices" keys

    Returns:
        Configured ArgumentParser instance ready for parsing CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog=config.get("prog", "quick"),
        description=config.get("description", ""),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=config.get("epilog", "")
    )

    commands = config.get("commands", [])
    if commands:
        group = parser.add_mutually_exclusive_group()
        for cmd in commands:
            if "choices" in cmd:
                group.add_argument(cmd["flag"], help=cmd["help"], choices=cmd["choices"])
            else:
                group.add_argument(cmd["flag"], help=cmd["help"])

    return parser
