# DEP-OCR-01 — Compatibilidade de Dependências com Python 3.13

## 1. Objetivo

Atualizar o `requirements.txt` para que todas as dependências do OCR-LEITOR sejam instaláveis e executáveis em ambiente Python 3.13, sem alterar lógica do sistema, OCR, parser, banco, web, UI, FechaMes ou integrações.

## 2. Problema encontrado

Durante teste real de instalação limpa com Python 3.13.1, o comando:

```
..venv\Scripts\python.exe -m pip install -r requirements.txt
```

falhou com os seguintes erros:

- **Pillow==10.1.0**: tentou compilar extensões C nativas e falhou — Pillow 10.1.0 não fornece wheel para Python 3.13, e a compilação a partir do source tarball também falhou.
- **opencv-python==4.8.1.78**: falhou com NumPy 2.x. OpenCV 4.8.1 foi construído contra NumPy 1.x e não é compatível com a série NumPy 2.x, que é a padrão no Python 3.13.
- O `doctor_instalacao.py` acusava ausência de `pytesseract`, `PIL` e `cv2` antes da correção manual da `.venv`.

Após instalação manual com versões atualizadas (`Pillow>=11`, `opencv-python>=4.12`), todas as dependências passaram a funcionar corretamente.

## 3. Ajuste aplicado

### requirements.txt

| Dependência | Antes | Depois |
|---|---|---|
| `pytesseract` | `==0.3.10` | mantido (compatível) |
| `pdf2image` | `==1.16.3` | mantido (compatível) |
| `opencv-python` | `==4.8.1.78` | `>=4.12.0,<5` |
| `Pillow` | `==10.1.0` | `>=11.0.0,<13` |
| `requests` | `==2.31.0` | mantido (compatível) |
| `python-dotenv` | `==1.0.0` | mantido (compatível) |

### Critério para NumPy

Não foi fixado NumPy diretamente no `requirements.txt`. OpenCV 4.12+ gerencia sua própria dependência de NumPy de forma compatível com Python 3.13 e NumPy 2.x. Adicionar NumPy manualmente poderia criar conflitos de versão com o OpenCV.

## 4. O que não mudou

- OCR/parser/core (`ocr_leitor/`)
- `web/app.py`
- Templates HTML
- CSS
- Banco de dados / `schema.sql`
- Contratos JSON
- Conectores simulados
- Scripts de instalação (`doctor_instalacao.py`, `preparar_instalacao_local.py`, etc.)
- `requirements.add.txt`
- FechaMes
- `.env`, `.venv`, `config/settings.json`

## 5. Como validar em uma máquina limpa

```powershell
python -m venv .venv
..venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
..venv\Scripts\python.exe -m pip install -r requirements.txt
..venv\Scripts\python.exe -m pip install -r requirements.add.txt
..venv\Scripts\python.exe -c "from PIL import Image; print('PIL OK')"
..venv\Scripts\python.exe -c "import pytesseract; print('pytesseract OK')"
..venv\Scripts\python.exe -c "import cv2; print('cv2 OK')"
..venv\Scripts\python.exe scripts\doctor_instalacao.py
```

## 6. Observação sobre Tesseract

`pytesseract` é uma biblioteca Python que funciona como wrapper para o executável Tesseract OCR. O executável do Tesseract precisa estar instalado no Windows (ou ter seu caminho configurado em `config/settings.json`). Mesmo com `pytesseract` instalado, o `doctor_instalacao.py` pode exibir um AVISO sobre o executável não estar no PATH — isso é normal quando o Tesseract está configurado por caminho absoluto no `settings.json`.

## 7. Critérios de aprovação

- `pytest` passa (178 → 193 testes).
- `pip install -r requirements.txt` não quebra no Python 3.13.
- `from PIL import Image` funciona sem erros.
- `import pytesseract` funciona sem erros.
- `import cv2` funciona sem erros.
- `doctor_instalacao.py` reconhece os módulos `pytesseract`, `PIL` e `cv2` como OK.
- Git limpo após commit, apenas com os 3 arquivos permitidos alterados.
