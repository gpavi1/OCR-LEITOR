# OCR-LEITOR v1 - Patch de estabilização

Este pacote contém somente arquivos alterados/novos, sem `config/settings.json` real e sem token.

Arquivos:
- `ocr_to_monday.py`: fluxo ativo corrigido para parser, data financeira, upload Monday multipart e movimentação segura.
- `parser_nf.py`: parser isolado corrigido.
- `.gitignore`: adiciona `input/*`, `processed/*` e `config/settings.local.json`.
- `config/settings.example.json`: exemplo sem segredo.
- `tests/test_parser_nf.py`: testes mínimos do parser.

Antes de usar:
1. Revogue/rotacione o token antigo do Monday se ele já foi incluído em ZIP, git ou conversa.
2. Faça backup da pasta atual.
3. Copie os arquivos deste pacote para a raiz do projeto.
4. Confira os IDs das colunas em `config/settings.json`.
5. Rode:

```powershell
python -m py_compile ocr_to_monday.py parser_nf.py
python -m pytest -q tests/test_parser_nf.py
```
