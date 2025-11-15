import questionary
from prompt_toolkit.styles import Style

def prompt_translate(input: str, target_language: str) -> str:
    return f"""
    <context>
      You are an expert multilingual technical translator specializing in accurate, natural translations with linguistic insights. Your goal is to translate technical content while providing linguistic analysis and usage examples.
    </context>

    <input>
      <source_text>
        {input}
      </source_text>
      <target_language>{target_language}</target_language>
    </input>

    <instructions>
      Follow these steps in order:

      1. **Language Detection**
        - Identify the source language of the input text
        - Verify target language: use "{target_language}" if provided and valid, otherwise select a reasonable default

      2. **Translation**
        - Translate the text naturally and professionally into the target language
        - For ambiguous terms, provide multiple alternatives separated by " / "

      3. **Linguistic Analysis**
        - Write a flowing paragraph analyzing grammar, naturalness, and usage context
        - If uncertain, explicitly state "I'm not certain about..."

      4. **Example Sentences**
        - Create 3 example sentences showing the term/phrase in context
        - Include both source and target language versions

      5. **Technical Abbreviations**
        - Identify and explain any technical abbreviations
        - If none exist, state: "There are no technical abbreviations in the input text."
    </instructions>

    <output_format>
      **Source Language:** [Detected Language Name]  
      **Target Language:** [Target Language Name (code)]

      **Tradução:** [Translation result, alternatives separated by " / "]

      **Análise Linguística:** [Flowing prose paragraph analyzing grammar, naturalness, context]

      **Exemplos de Sentenças:**

      1. **[Source Language]:** [Example sentence]  
        **[Target Language]:** [Translated sentence]
      2. **[Source Language]:** [Example sentence]  
        **[Target Language]:** [Translated sentence]
      3. **[Source Language]:** [Example sentence]  
        **[Target Language]:** [Translated sentence]

      **Análise de Abreviações Técnicas:** [Analysis or "Não há abreviações técnicas no texto de entrada."]
    </output_format>

    <formatting_rules>
      - NO preamble or text outside <translation_result> tags
      - NO tables - use plain text with bold labels
      - Section headings in target language when appropriate
      - Keep format clean for console rendering
    </formatting_rules>

    <quality_standards>
      - Use clear, natural, professional language
      - Never invent information when uncertain
      - Explicitly acknowledge gaps in knowledge
    </quality_standards>"""


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


# Custom minimal style for prompts
PROMPT_STYLE = Style(
    [
        ("question", "bold"),  # question text
        ("pointer", "fg:#5f87d7 bold"),  # ❯ cursor
        ("highlighted", "fg:#5f87d7 bold noreverse"),  # selected option (no bg)
        ("answer", "fg:#5f87d7 bold"),  # final answer
        ("text", ""),  # default text
    ]
)


async def select_option(
    prompt: str,
    options: list[tuple[str, str]],
) -> str | None:
    """
    Display numbered options with arrow-key navigation.

    Args:
        prompt: The question to display
        options: List of (label, value) tuples
        default: Default value to select (optional)

    Returns:
        Selected value or None if cancelled
    """
    # Prepend numbers to labels for visual scanning
    numbered_choices = [
        questionary.Choice(title=f"{i}. {label}", value=value)
        for i, (label, value) in enumerate(options, 1)
    ]

    try:
        result = await questionary.select(
            prompt,
            choices=numbered_choices,
            qmark="",
            pointer="❯",
            style=PROMPT_STYLE,
            use_arrow_keys=True,
        ).ask_async()

        return result
    except (KeyboardInterrupt, EOFError):
        return None


async def text_input(prompt: str) -> str | None:
    """
    Prompt user for text input.

    Args:
        prompt: The question to display

    Returns:
        User input or None if cancelled
    """
    try:
        result = await questionary.text(
            prompt,
            style=PROMPT_STYLE,
        ).ask_async()
        return result.strip() if result else None
    except (KeyboardInterrupt, EOFError):
        return None
