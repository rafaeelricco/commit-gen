#!/usr/bin/env python3

import sys
import asyncio

from dotenv import load_dotenv
from typing import List, Optional

from common.arguments import CommandType, ParsedArgs, create_parser
from common.updater import execute_update
from domains.commit.command.commit import execute_commit


class QuickAssistant:
    def __init__(self):
        load_dotenv()
        self.parser = create_parser()

    def run(self, args: Optional[List[str]] = None) -> int:
        try:
            namespace = self.parser.parse_args(args)
            parsed_args = ParsedArgs(command=getattr(namespace, "command", None))

            match parsed_args.get_command_type():
                case CommandType.COMMIT:
                    return asyncio.run(execute_commit("generate"))
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
    from common.updater import check_and_update

    check_and_update()

    app = QuickAssistant()
    return app.run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
