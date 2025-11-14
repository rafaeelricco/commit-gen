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
    """Translation command input."""
    content: str
    target_language: str = "pt"

class CommandResponse(BaseFrozen, ToJSON):
    """Translation command output."""
    translated_content: str
    original_content: str
    target_language: str

class Handler(BaseCommandHandler[Command]):
    """Handler for translation command execution."""

    async def handle_command(self, command: Command) -> tuple[Dict[str, Any], int]:
        """Execute translation using google-genai and return formatted response."""

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise BadRequest(message="GOOGLE_API_KEY not found in environment. Set it in .env file")

        translation_prompt = prompt_translate(command.content, command.target_language)

        with spinner("Translating…", spinner_style="dots"):
            response = await genai.Client(api_key=api_key).aio.models.generate_content(
                model='models/gemini-flash-latest',
                contents=translation_prompt
            )

        if not response.text:
            raise BadRequest(message="Empty response from translation service")

        Format.markdown(response.text)

        return json_response(CommandResponse(
            translated_content=response.text,
            original_content=command.content,
            target_language=command.target_language
        ))


async def execute_translate(content: Optional[str]) -> int:
    """
    Execute translation command with CLI validation.
    
    Validates input, constructs command, and executes handler.
    
    Args:
        content: The text content to translate
        
    Returns:
        Exit code: 0 for success, 1 for failure
    """
    try:
        if not content:
            print("Error: Translation content is required")
            return 1
        
        request_data = {"content": content, "target_language": "pt"}
        
        response, status_code = await execute_command_handler(Command, request_data, Handler)
        
        return 0 if status_code == 200 else 1
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1