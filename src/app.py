#!/usr/bin/env python3
"""
Quick Assistant - CLI Tool for Translation

A command-line interface tool for quick text translation using AI.
"""

import sys

from dotenv import load_dotenv

from common.arguments import (CommandType, ParsedArgs, TranslateCLIArguments, create_parser)
from typing import List, Optional 
from domains.translate.command.translate import Command


class QuickAssistant:
    def __init__(self):
        """Initialize the CLI application."""
        load_dotenv()
        self.parser = create_parser(TranslateCLIArguments.get_config())

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI application."""
        try:
            parsed_args = ParsedArgs(
                translate=getattr(self.parser.parse_args(args), "translate", None),
                search=getattr(self.parser.parse_args(args), "search", None),
                commit=getattr(self.parser.parse_args(args), "commit", None)
            )

            match parsed_args.get_command_type():
                case CommandType.TRANSLATE:
                    return Command.execute(self.parser.parse_args(args))
                case CommandType.SEARCH:
                    print("Search functionality is not implemented yet.")
                    return 1
                case CommandType.COMMIT:
                    print("Commit functionality is not implemented yet.")
                    return 1
                case CommandType.HELP:
                    self.parser.print_help()
                    return 1

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1


def main() -> int:
    """Main entry point for the application."""
    app = QuickAssistant()
    return app.run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
