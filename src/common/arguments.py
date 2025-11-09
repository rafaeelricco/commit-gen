import argparse

from typing import Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum

class CommandType(Enum):
  TRANSLATE = "translate"
  SEARCH = "search"
  COMMIT = "commit"
  HELP = "help"

class ParsedArgs(BaseModel, frozen=True):
    translate: Optional[str] = None
    search: Optional[str] = None
    commit: Optional[str] = None

    def get_command_type(self) -> CommandType:
        if self.translate:
            return CommandType.TRANSLATE
        elif self.search:
            return CommandType.SEARCH
        elif self.commit:
            return CommandType.COMMIT
        else:
            return CommandType.HELP

class TranslateCLIArguments:
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


class SearchCLIArguments:
    description = "Quick Assistant - CLI tool for searching"
    flag = "--search"
    help = "Search for a term in the web"
    epilog = (
        "Examples:\n"
        "    quick --search \"latest news\"\n"
        "    quick --search \"weather today\""
    )

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Return parser configuration for search arguments."""
        return {
            "prog": "quick",
            "description": cls.description,
            "epilog": cls.epilog,
            "arguments": [
                {"flag": cls.flag, "help": cls.help}
            ]
        }
    
def create_parser(config: Dict[str, Any]) -> argparse.ArgumentParser:
    """Create and configure a generic argument parser."""
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
