## Quick Assistant

CLI tool for productivity, focused on quick daily operations.

### Installation

```bash
# Recommended (isolated environment)
pipx install quick-assistant

# Or via pip
pip install quick-assistant
```

### Requirements

Set your Google Gemini API key:

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
export GOOGLE_API_KEY="your-api-key"
```

Get your API key at: https://aistudio.google.com/apikey

### Commands

#### 1. Translate
Translate text using AI (default target: Portuguese).
```bash
quick --translate "text"
```

#### 2. Commit
AI-powered git commit message generation with interactive flow.
```bash
quick --commit generate
```

### Features
- Fast AI-powered responses
- Colored and organized output
- Compatible with Windows, macOS, Linux
- Informative error messages

### Examples
- `quick --translate "hello world"`
- `quick --commit generate`

### Uninstall

```bash
# If installed with pipx
pipx uninstall quick-assistant

# If installed with pip
pip uninstall quick-assistant
```
