#!/usr/bin/env python3
"""Quick Assistant - CLI Tool for productivity."""

import sys
import asyncio

from dotenv import load_dotenv
from typing import List, Optional

from common.arguments import CommandType, ParsedArgs, QuickCLIConfig, create_parser
from common.updater import execute_update
from domains.commit.command.commit import execute_commit


class QuickAssistant:
    def __init__(self):
        """Initialize the CLI application."""
        load_dotenv()
        self.parser = create_parser(QuickCLIConfig.get_config())

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI application."""
        try:
            parsed_args = ParsedArgs(
                commit=getattr(self.parser.parse_args(args), "commit", None),
                update=getattr(self.parser.parse_args(args), "update", None),
            )

            match parsed_args.get_command_type():
                case CommandType.COMMIT:
                    return asyncio.run(execute_commit(parsed_args.commit))
                case CommandType.UPDATE:
                    return execute_update()
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
    from common.updater import check_and_update

    check_and_update()

    app = QuickAssistant()
    return app.run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
