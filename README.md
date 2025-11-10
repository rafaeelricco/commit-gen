## Quick Assistant

CLI tool for productivity, focused on quick daily operations.

### Installation

```bash
npm install -g @rafaeelricco/quick-assistant
```

### Global Command

Use `quick` in the terminal to access functionalities:

#### 1. Quick Translate
Automatic translation between Portuguese ↔ English (or other language).
```bash
quick translate "text" [-l <language>] [-d]
```

#### 2. Quick Extract
Extract text from documents (PDF, DOC, DOCX, PPTX, TXT).
```bash
quick extract <file> [-o <output-file>] [--keep-format]
```

#### 3. Quick Search
Search definitions, synonyms, examples and information.
```bash
quick search "term" [-w] [-s] [-e] [-t]
```

### Features
- Fast responses (<3s)
- Offline cache for common translations/definitions
- Compatible with Windows, macOS, Linux
- Colored and organized output
- Informative error messages

### Examples
- `quick translate "apple"`
- `quick extract document.pdf -o content.txt`
- `quick search "run" -e -s`
