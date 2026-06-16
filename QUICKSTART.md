# 🚀 Guia de Início Rápido

## ⚡ 5 Minutos para Começar

### 1. Instalar Tesseract (2 min)

**Windows:**
```bash
# Com Chocolatey
choco install tesseract

# Ou baixar em: https://github.com/UB-Mannheim/tesseract/wiki
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 2. Instalar Dependências Python (1 min)

```bash
pip install -r requirements.txt
```

### 3. Configurar Credenciais (1 min)

Copiar `config/settings.json.example` para `config/settings.json`:

```json
{
  "monday_api_key": "SEU_TOKEN_AQUI",
  "monday_board_id": "SEU_BOARD_ID_AQUI"
}
```

**Como obter:**
- Token: monday.com → Configurações → Tokens → Novo Token
- Board ID: Na URL do seu board: `monday.com/boards/123456`

### 4. Colocar Documentos na Pasta `entrada/`

```
OCR-LEITOR/
└── entrada/
    ├── nota1.jpg
    ├── nota2.pdf
    └── nota3.png
```

### 5. Executar!

```bash
python -m src.main
```

Escolha opção **2** para processar todos os arquivos.

---

## 🎯 Exemplos Rápidos

### Processar um único arquivo
```bash
python -c "
from src.main import OrquestradorAutomacao
orq = OrquestradorAutomacao()
sucesso, resultado = orq.processar_arquivo('entrada/nota.pdf')
print(f'Sucesso: {sucesso}')
print(f'Campos: {resultado[\"campos\"]}')
"
```

### Apenas ler e extrair (sem Monday)
```bash
python -c "
from src.leitor import LeitorOCR
from src.extrator import ExtratorCampos

leitor = LeitorOCR()
texto, ok = leitor.ler_arquivo('entrada/nota.pdf')

if ok:
    extrator = ExtratorCampos()
    campos = extrator.extrair_todos_campos(texto)
    print(f'Empresa: {campos[\"empresa\"]}')
    print(f'NF-e: {campos[\"nfe\"]}')
    print(f'Chave: {campos[\"chave\"]}')
    print(f'Vencimento: {campos[\"vencimento\"]}')
"
```

---

## ✅ Checklist Inicial

- [ ] Tesseract instalado
- [ ] Python 3.8+
- [ ] `pip install -r requirements.txt` executado
- [ ] `config/settings.json` configurado (ou modo offline)
- [ ] Documentos em `entrada/`
- [ ] Primeira execução bem-sucedida

---

## 📱 Menu Interativo

```
OCR LEITOR - AUTOMAÇÃO DE NOTAS FISCAIS
============================================================

Opções:
1. Processar arquivo específico
2. Processar todos os arquivos da pasta entrada
3. Ver estatísticas
4. Sair

============================================================
```

---

## 🔍 Verificar Instalação

```bash
# Testar Tesseract
tesseract --version

# Testar Python
python --version

# Testar dependências
python -c "import pytesseract, cv2, pdf2image; print('✓ OK')"
```

---

## 🆘 Problemas Comuns

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError: No module named 'pytesseract'` | `pip install -r requirements.txt` |
| `TesseractNotFoundError` | Instalar Tesseract (ver passo 1) |
| Nenhum arquivo processado | Colocar arquivos em `entrada/` |
| Modo offline (sem Monday) | Deixar como está ou atualizar credentials |

---

## 📚 Próximos Passos

1. **Customizar padrões**: Editar `config/settings.json`
2. **Entender os logs**: Ver `logs/automacao_*.log`
3. **Usar como módulo**: Importar classes em seu código
4. **Integração com outros sistemas**: Expandir `monday_api.py`

---

## 💡 Dicas

- ✅ Coloque exemplos de notas em `entrada/` para testar
- ✅ Revise as extrações antes de confirmar (Fase 3)
- ✅ Verifique os logs se algo der errado
- ✅ Use modo offline primeiro, depois configure Monday

---

**Sucesso! 🎉**
