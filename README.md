## Commit Gen

AI-powered git commit message generation with interactive flow.

### Installation

```bash
# Recommended (isolated environment)
pipx install commit-gen

# Or via pip
pip install commit-gen
```

### Windows Users

After `pipx install commit-gen`, if `commit` is not recognized:

**Step 1: Add pipx bin to PATH**
```powershell
pipx ensurepath
```

**Step 2: Restart your terminal completely**

Close and reopen PowerShell/CMD. A new tab is NOT enough - close the entire window.

**Step 3: Verify**
```powershell
commit doctor
```

**Alternative: Run directly without PATH**

If you can't restart or modify PATH, use the full path:
```powershell
# pipx installation location
%USERPROFILE%\.local\bin\commit.exe doctor
%USERPROFILE%\.local\bin\commit.exe generate
```

### Requirements

**Option 1: Run setup (recommended)**
```bash
commit setup
```

**Option 2: Environment variable (for CI/CD)**
```bash
export GOOGLE_API_KEY="your-api-key"
```

Get your API key at: https://aistudio.google.com/apikey

### Setup

On first run, Commit Gen will guide you through setup:

```bash
commit setup
```

**Configuration includes:**
- **Commit convention** - Choose your preferred style:
  - Conventional Commits (`feat:`, `fix:`, `refactor:`, etc.)
  - Imperative (simple verbs: `add`, `fix`, `update`)
  - Custom template (with `{diff}` placeholder)
- **API key** - Your Google Gemini API key

Configuration is saved to `~/.commit-gen/config.json`.

### Commands

#### Setup
Configure Commit Gen with your API key and commit style preferences.
```bash
commit setup
```

#### Generate
AI-powered git commit message generation with interactive flow.
```bash
commit generate
```

#### Update
Update Commit Gen to the latest version.
```bash
commit update
```

#### Doctor
Diagnose installation and PATH issues (especially helpful on Windows; it checks the `Scripts` and `pipx` paths).
```bash
commit doctor
```

### Features
- Fast AI-powered responses
- Colored and organized output
- Compatible with Windows, macOS, Linux
- Informative error messages

### Examples
- `commit setup` - Configure API key and commit style
- `commit generate` - Generate AI commit message
- `commit update` - Update to latest version
- `commit doctor` - Diagnose installation issues (Windows PATH)

### Uninstall

```bash
# If installed with pipx
pipx uninstall commit-gen

# If installed with pip
pip uninstall commit-gen
```
