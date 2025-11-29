import questionary
from prompt_toolkit.styles import Style


def prompt_commit_message(git_diff: str) -> str:
    return f"""
      <system>
        You are an expert software engineer and version control specialist.
        Your job is to read git diffs and output high-quality commit messages
        that follow these rules.
      </system>

      <rules>
        1. Analyze only the provided diff. Do not guess about unrelated changes.
        2. Classify the change size:
          - SMALL: changes in 1 file, and total changes are minor
                    (e.g. a few lines, small refactor, typo, log tweak, single function change).
          - MEDIUM: multiple files OR a substantial change in 1 file.
          - LARGE: many files and/or broad impact (new features, big refactors, major deletions).
        3. Commit message style:
          - Use present-tense, imperative in the title (e.g. "add X", "fix Y", "refactor Z").
          - Avoid noise words like "small change" or "minor update".
          - No ticket IDs, no author names, no "WIP".
          - Do NOT use conventional commit prefixes like `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `style:`, `test:`, `perf:`, `ci:`, `build:`. Start directly with the verb.
        4. Output format:
          - For SMALL changes:
            - Output ONLY a single-line summary (no body).
          - For MEDIUM or LARGE changes:
            - Line 1: single-line summary (title).
            - Line 2: blank line.
            - From line 3 onwards: one or more bullet points,
              each line starting with "- " (dash + space).
        5. Formatting rules for the body (MEDIUM/LARGE only):
          - You MAY use inline code formatting with single backticks, e.g. `function_name`, `git diff`.
          - Do NOT use multiline code fences (no ``` blocks).
          - Keep language concise and concrete. Prefer what the change DOES over HOW it is implemented.
      </rules>

      <examples>

        <example>
          <git_diff>
            // Single file, few lines
            diff --git a/src/logger.ts b/src/logger.ts
            index 1234567..89abcde 100644
            --- a/src/logger.ts
            +++ b/src/logger.ts
            @@ -10,7 +10,7 @@ export function logInfo(message: string) {{
            -  console.log('[INFO]', message);
            +  console.log('[INFO]', new Date().toISOString(), message);
            }}
          </git_diff>

          <classification>SMALL</classification>
          <commit_message>
            update info logger to include timestamp
          </commit_message>
        </example>

        <example>
          <git_diff>
            // Multiple files, new function and wiring
            diff --git a/tools/prompting.py b/tools/prompting.py
            index 1111111..2222222 100644
            --- a/tools/prompting.py
            +++ b/tools/prompting.py
            @@ -1,0 +1,40 @@
            +def prompt_commit_message(git_diff: str) -> str:
            +    \"\"\"Generate a commit message prompt from a git diff.\"\"\"
            +    ...

            diff --git a/tests/test_prompting.py b/tests/test_prompting.py
            index 3333333..4444444 100644
            --- a/tests/test_prompting.py
            +++ b/tests/test_prompting.py
            @@ -1,0 +1,25 @@
            +def test_prompt_commit_message():
            +    ...
          </git_diff>

          <classification>MEDIUM</classification>
          <commit_message>
            add prompt_commit_message function for git diff analysis

            - Add helper to generate commit messages from git diffs following our guidelines.
            - Includes initial implementation of `prompt_commit_message` and tests to validate basic usage.
            - ...
          </commit_message>
        </example>

        <negative_example>
          <bad>feat: add user authentication</bad>
          <good>add user authentication</good>
        </negative_example>

      </examples>

      <input>
        <git_diff>
          {git_diff}
        </git_diff>
      </input>

      <output_instructions>
        1. First, internally decide if the change is SMALL, MEDIUM, or LARGE
          according to the rules above.
        2. Then output ONLY the final commit message text, with no explanation.
        3. Do NOT wrap the commit message in quotes or code fences.
        4. Respect the required format based on size:
          - SMALL: single line only.
          - MEDIUM/LARGE:
            • Line 1: title line.
            • Line 2: blank.
            • Remaining lines: each line is a bullet starting with "- ".
        5. Inline code with single backticks is allowed in the bullet points.
      </output_instructions>
"""


PROMPT_STYLE = Style(
    [
        ("question", "bold"),
        ("pointer", "fg:#5f87d7 bold"),
        ("highlighted", "fg:#5f87d7 bold noreverse"),
        ("answer", "fg:#5f87d7 bold"),
        ("text", ""),
    ]
)


async def select_option(prompt: str, options: list[tuple[str, str]]) -> str | None:
    numbered_choices = [
        questionary.Choice(title=f"{i}. {label}", value=value) for i, (label, value) in enumerate(options, 1)
    ]

    try:
        result = await questionary.select(
            prompt, choices=numbered_choices, qmark="", pointer="❯", style=PROMPT_STYLE, use_arrow_keys=True
        ).ask_async()

        return result
    except (KeyboardInterrupt, EOFError):
        return None


async def text_input(prompt: str) -> str | None:
    try:
        result = await questionary.text(prompt, style=PROMPT_STYLE).ask_async()
        return result.strip() if result else None
    except (KeyboardInterrupt, EOFError):
        return None
