#!/usr/bin/env python3
"""
Quick Assistant - CLI Tool for Translation

A command-line interface tool for quick text translation using AI.
"""

import sys
import asyncio

from dotenv import load_dotenv
from typing import List, Optional 

from common.arguments import (CommandType, ParsedArgs, TranslateCLIArguments, create_parser)
from common.command.execute_command_handler import execute_command_handler
from domains.translate.command.translate import Command, Handler

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
                    return asyncio.run(self._handle_translate(parsed_args.translate))
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

    async def _handle_translate(self, content: Optional[str]) -> int:
        """
        Handle translation command execution.
        
        Converts CLI input to command format and executes translation.
        
        Args:
            content: The text content to translate
            
        Returns:
            Exit code: 0 for success, 1 for failure
        """
        try:
            if not content:
                print("Error: Translation content is required")
                return 1
            
            request_data = { "content": content, "target_language": "pt" }
            
            response, status_code = await execute_command_handler(Command, request_data, Handler)
            
            if status_code == 200:
                return 0
            else:
                return 1
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1


def main() -> int:
    """Main entry point for the application."""
    app = QuickAssistant()
    return app.run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
