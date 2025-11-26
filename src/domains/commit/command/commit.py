import os
import subprocess
import tempfile

from typing import Any, Dict, Optional
from google import genai
from google.genai import types
from common.base import BaseFrozen, ToJSON
from common.command.base_command import BaseCommand
from common.command.base_command_handler import BaseCommandHandler
from common.command.execute_command_handler import BadRequest, json_response, execute_command_handler
from common.loading import spinner
from common.prompts import prompt_commit_message, select_option, text_input
from rich.console import Console


class Command(BaseCommand):
    """Commit command input."""
    action: str

class CommandResponse(BaseFrozen, ToJSON):
    message: str
    commit_message: Optional[str] = None
    action: Optional[str] = None

class Handler(BaseCommandHandler[Command]):
    """Handler for commit command execution."""

    def _is_git_repository(self, cwd: str) -> bool:
        """Check if the given directory is inside a git repository."""
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        return result.returncode == 0

    async def handle_command(self, command: Command) -> tuple[Dict[str, Any], int]:
        """Execute google-genai to analyze the diffs to generate a commit message."""

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise BadRequest(message="GOOGLE_API_KEY not found in environment. Set it in .env file")

        if command.action != "generate":
            raise BadRequest(message=f"Unsupported commit action: '{command.action}'. Use 'generate'.")

        path = os.getcwd()

        if not self._is_git_repository(path):
            raise BadRequest(message="Not a git repository. Initialize with 'git init' or navigate to a git project.")

        git_diff = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True, cwd=path)

        if git_diff.returncode != 0:
            raise BadRequest(message=f"Git error: {git_diff.stderr.strip() or 'Failed to get staged changes'}")

        if not git_diff.stdout.strip():
            raise BadRequest(message="No staged changes found. Use 'git add <file>' to stage files before generating a commit.")

        console = Console()
        message_text = await self._generate_commit_message(api_key, git_diff.stdout)

        while True:
            console.print("")
            console.print(message_text)
            console.print("")

            selection = await select_option(
                "Select action:",
                [
                    ("Commit & Push", "commit_push"),
                    ("Commit", "commit"),
                    ("Regenerate", "regenerate"),
                    ("Adjust", "adjust"),
                    ("Cancel", "cancel"),
                ],
            )

            if not selection or selection == "cancel":
                return json_response(
                    CommandResponse(message="cancelled", commit_message=message_text, action="cancel"),
                    200,
                )

            if selection == "regenerate":
                message_text = await self._generate_commit_message(api_key, git_diff.stdout)
                continue

            if selection == "adjust":
                adjustment = await text_input("What adjustments would you like?")

                if not adjustment:
                    continue

                message_text = await self._refine_commit_message(api_key, message_text, adjustment, git_diff.stdout)
                continue

            if selection == "commit":
                success, output = self._perform_commit(message_text, path)
                console.print(output)
                status = 200 if success else 400
                return json_response(
                    CommandResponse(message="commit" if success else "commit_failed", commit_message=message_text, action="commit"),
                    status,
                )

            if selection == "commit_push":
                success_commit, output_commit = self._perform_commit(message_text, path)
                console.print(output_commit)
                if not success_commit:
                    return json_response(
                        CommandResponse(
                            message="commit_failed",
                            commit_message=message_text,
                            action="commit_push",
                        ),
                        400,
                    )

                success_push, output_push = self._perform_push(path)
                console.print(output_push)
                
                status = 200 if success_push else 400

                return json_response(
                    CommandResponse(
                        message="commit_push" if success_push else "push_failed",
                        commit_message=message_text,
                        action="commit_push",
                    ),
                    status,
                )

    def _get_text_parts(
        self, response: types.GenerateContentResponse
    ) -> tuple[types.Part, ...]:
        candidates = getattr(response, "candidates", ()) or ()
        return tuple(
            p
            for c in candidates
            for p in (getattr(getattr(c, "content", None), "parts", ()) or ())
        )

    async def _generate_commit_message(self, api_key: str, diff: str) -> str:
        with spinner("Generating…", spinner_style="dots"):
            response = await genai.Client(api_key=api_key).aio.models.generate_content(
                model="models/gemini-flash-latest",
                contents=diff,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_commit_message(diff),
                    response_mime_type="text/plain",
                ),
            )
        parts = self._get_text_parts(response)
        message_text = "".join(
            text for p in parts if (text := getattr(p, "text", None))
        )
        if not message_text.strip():
            raise BadRequest(message="Empty response from commit message generation")
        return message_text

    async def _refine_commit_message(
        self, api_key: str, current_message: str, adjustment: str, diff: str
    ) -> str:
        system = (
            "You revise commit messages. Use the diff and the user's adjustment to produce a polished commit message. "
            "Preserve required formatting rules: SMALL=single line; MEDIUM/LARGE=title, blank line, bullets prefixed with '- '."
        )
        contents = f"<diff>\n{diff}\n</diff>\n<current>\n{current_message}\n</current>\n<adjustment>\n{adjustment}\n</adjustment>"
        with spinner("Refining…", spinner_style="dots"):
            response = await genai.Client(api_key=api_key).aio.models.generate_content(
                model="models/gemini-flash-latest",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="text/plain",
                ),
            )
        parts = self._get_text_parts(response)
        refined = "".join(text for p in parts if (text := getattr(p, "text", None)))
        if not refined.strip():
            raise BadRequest(message="Empty response from commit message refinement")
        return refined

    def _perform_commit(self, message_text: str, cwd: str) -> tuple[bool, str]:
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            tmp.write(message_text)
            tmp_path = tmp.name
        try:
            result = subprocess.run(
                ["git", "commit", "-F", tmp_path],
                capture_output=True,
                text=True,
                cwd=cwd,
            )
            success = result.returncode == 0
            output = (result.stdout or "") + (result.stderr or "")
            return success, output
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def _perform_push(self, cwd: str) -> tuple[bool, str]:
        result = subprocess.run(
            ["git", "push"], capture_output=True, text=True, cwd=cwd
        )
        success = result.returncode == 0
        output = (result.stdout or "") + (result.stderr or "")
        return success, output


async def execute_commit(action: Optional[str]) -> int:
    """
    Execute commit command with CLI validation.

    Validates input, constructs command, and executes handler.

    Args:
        action: The commit action to execute (e.g., "generate")

    Returns:
        Exit code: 0 for success, 1 for failure
    """
    console = Console()

    try:
        if not action:
            console.print("[red]Error: Commit action is required[/red]")
            return 1

        request_data = {"action": action}

        response, status_code = await execute_command_handler(Command, request_data, Handler)

        if status_code != 200:
            error_msg = response.get('error', {}).get('message', 'Unknown error')
            console.print(f"[red]{error_msg}[/red]")

        return 0 if status_code == 200 else 1

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return 1
