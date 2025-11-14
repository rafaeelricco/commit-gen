import os

from typing import Any, Dict, Optional
from google import genai

from common.base import BaseFrozen, ToJSON
from common.command.base_command import BaseCommand
from common.command.base_command_handler import BaseCommandHandler
from common.command.execute_command_handler import BadRequest, json_response, execute_command_handler
from common.format_markdown import Format
from common.loading import spinner
from common.prompts import prompt_translate


class Command(BaseCommand):
    """Commit command input."""
    action: str

class CommandResponse(BaseFrozen, ToJSON):
    """Commit command output."""
    message: str

class Handler(BaseCommandHandler[Command]):
    """Handler for commit command execution."""

    async def handle_command(self, command: Command) -> tuple[Dict[str, Any], int]:
        """Execute google-genai to analyze the diffs to generate a commit message."""

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise BadRequest(message="GOOGLE_API_KEY not found in environment. Set it in .env file")
        
        if command.action != "generate":
            raise BadRequest(message=f"Unsupported commit action: {command.action}")
        
        print(f"Generating commit message for current directory: {os.getcwd()}")

        # with spinner("Translating…", spinner_style="dots"):
        #     response = await genai.Client(api_key=api_key).aio.models.generate_content(
        #         model='models/gemini-flash-latest',
        #         contents=translation_prompt
        #     )

        # if not response.text:
        #     raise BadRequest(message="Empty response from translation service")

        # Format.markdown(response.text)

        return json_response(CommandResponse(message="Commit message generation not yet implemented"))


async def execute_commit(action: Optional[str]) -> int:
    """
    Execute commit command with CLI validation.
    
    Validates input, constructs command, and executes handler.
    
    Args:
        action: The commit action to execute (e.g., "generate")
        
    Returns:
        Exit code: 0 for success, 1 for failure
    """
    try:
        if not action:
            print("Error: Commit action is required")
            return 1
        
        request_data = {"action": action}
        
        response, status_code = await execute_command_handler(Command, request_data, Handler)
        
        return 0 if status_code == 200 else 1
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1