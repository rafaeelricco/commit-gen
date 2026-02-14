import argparse

from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum
from importlib.metadata import PackageNotFoundError, version as get_version


class CommandType(Enum):
    GENERATE = "generate"
    UPDATE = "update"
    SETUP = "setup"
    DOCTOR = "doctor"
    HELP = "help"


class ParsedArgs(BaseModel):
    model_config = ConfigDict(frozen=True)

    command: Optional[str] = None

    def get_command_type(self) -> CommandType:
        match self.command:
            case "generate":
                return CommandType.GENERATE
            case "update":
                return CommandType.UPDATE
            case "setup":
                return CommandType.SETUP
            case "doctor":
                return CommandType.DOCTOR
            case _:
                return CommandType.HELP


class CommitGenCLIConfig:
    prog = "commit"
    description = "Commit Gen - AI-powered commit message generator"
    epilog = "Examples:\n    commit generate\n    commit update"


PACKAGE_NAME = "commit-gen"


def resolve_version() -> str:
    try:
        return get_version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown"


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=CommitGenCLIConfig.prog,
        description=CommitGenCLIConfig.description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=CommitGenCLIConfig.epilog,
    )

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {resolve_version()}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("generate", help="Generate a commit message")
    subparsers.add_parser("update", help="Update commit-gen to the latest version")
    subparsers.add_parser("setup", help="Configure commit-gen")
    subparsers.add_parser("doctor", help="Diagnose installation and PATH issues")

    return parser
