import os

from typing import Any, Dict
from google import genai

from common.base import BaseFrozen, ToJSON
from common.command.base_command import BaseCommand
from common.command.base_command_handler import BaseCommandHandler
from common.command.execute_command_handler import BadRequest, json_response
from common.format_markdown import Format
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

        translation_prompt = prompt_translate(command.content)

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