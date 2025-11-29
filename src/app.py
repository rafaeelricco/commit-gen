#!/usr/bin/env python3

import sys
import asyncio

from dotenv import load_dotenv
from typing import List, Optional

from common.updater import check_and_update
from common.arguments import CommandType, ParsedArgs, create_parser
from common.config import is_ready
from common.doctor import execute_doctor
from common.updater import execute_update
from domains.commit.command.commit import execute_commit
from domains.setup.command.setup import execute_setup


class QuickAssistant:
    def __init__(self):
        load_dotenv()
        self.parser = create_parser()

    def run(self, args: Optional[List[str]] = None) -> int:
        try:
            namespace = self.parser.parse_args(args)
            parsed_args = ParsedArgs(command=getattr(namespace, "command", None))
            command_type = parsed_args.get_command_type()

            if not is_ready() and command_type not in (CommandType.SETUP, CommandType.HELP, CommandType.DOCTOR):
                return asyncio.run(execute_setup())

            match command_type:
                case CommandType.COMMIT:
                    return asyncio.run(execute_commit("generate"))
                case CommandType.UPDATE:
                    return execute_update()
                case CommandType.SETUP:
                    return asyncio.run(execute_setup())
                case CommandType.DOCTOR:
                    return execute_doctor()
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
    check_and_update()

    app = QuickAssistant()
    return app.run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
