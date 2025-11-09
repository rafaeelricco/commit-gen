## Quick Assistant

Ferramenta CLI para produtividade, focada em operações rápidas no dia a dia.

### Instalação

```bash
npm install -g @rafaeelricco/quick-assistant
```

### Comando Global

Use `quick` no terminal para acessar as funcionalidades:

#### 1. Quick Translate
Tradução automática entre português ↔ inglês (ou outro idioma).
```bash
quick translate "texto" [-l <idioma>] [-d]
```

#### 2. Quick Extract
Extrai texto de documentos (PDF, DOC, DOCX, PPTX, TXT).
```bash
quick extract <arquivo> [-o <arquivo>] [--keep-format]
```

#### 3. Quick Search
Busca definições, sinônimos, exemplos e informações.
```bash
quick search "termo" [-w] [-s] [-e] [-t]
```

### Características
- Respostas rápidas (<3s)
- Cache offline para traduções/definições comuns
- Compatível com Windows, macOS, Linux
- Output colorido e organizado
- Mensagens de erro informativas

### Exemplos
- `quick translate "apple"`
- `quick extract documento.pdf -o conteudo.txt`
- `quick search "run" -e -s`
