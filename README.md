# OCR LEITOR - Automação de Lançamento de Notas no Monday

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

## 📋 Objetivo

Automação local e gratuita para processar fotos ou PDFs de notas fiscais e registrar automaticamente os dados em um board do Monday.com.

## ✨ Características

- ✅ **OCR Local** - Processamento de imagens e PDFs com Tesseract
- ✅ **Extração Inteligente** - Reconhecimento automático de campos
- ✅ **Conferência Manual** - Validação do usuário antes de enviar
- ✅ **Integração Monday** - Envio automático via API GraphQL
- ✅ **Processamento em Lote** - Múltiplos arquivos simultâneos
- ✅ **Sem Custos** - Ferramentas open-source apenas
- ✅ **Logs Detalhados** - Rastreamento completo de operações

## 📊 Fluxo de Processamento

```
Pasta Entrada (entrada/)
        ↓
    Leitura da Imagem/PDF
        ↓
   Extração de Texto (OCR)
        ↓
  Extração de Campos (Regex)
        ↓
  Conferência Manual (Usuário)
        ↓
   Criação no Monday
        ↓
   Upload do Arquivo
        ↓
  Pasta Processadas (processadas/)
```

## 🎯 Campos Extraídos

| Campo | Descrição | Coluna Monday |
|-------|-----------|---------------|
| Empresa | Razão social do emitente | Elemento |
| NF-e | Número da nota fiscal | NUMERO NF-E |
| Chave | Chave de acesso (44 dígitos) | CH.ACESSO |
| Vencimento | Data de vencimento | VENCIMENTO |
| Arquivo | Documento original | Upload |

## 🚀 Instalação

### Pré-requisitos

- **Python 3.8+**
- **Tesseract OCR**
- **pip** (gerenciador de pacotes Python)

### 1. Instalar Tesseract OCR

#### Windows
```bash
# Baixar instalador em:
# https://github.com/UB-Mannheim/tesseract/wiki
# ou usar chocolatey:
choco install tesseract
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install tesseract-ocr
```

#### macOS
```bash
brew install tesseract
```

### 2. Clonar o Repositório

```bash
cd c:\Users\Gabriel\OneDrive\Desktop
```

### 3. Instalar Dependências Python

```bash
pip install -r requirements.txt
```

### 4. Configurar Credenciais

#### Opção A: Arquivo settings.json

Editar `config/settings.json`:

```json
{
  "monday_api_key": "YOUR_API_KEY_HERE",
  "monday_board_id": "YOUR_BOARD_ID_HERE",
  "tesseract_path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
}
```

#### Opção B: Variáveis de Ambiente

Copiar `.env.example` para `.env`:

```bash
cp .env.example .env
```

Editar `.env` com suas credenciais.

## 📖 Como Usar

### Opção 1: Menu Interativo

```bash
python -m src.main
```

Escolha uma das opções:
1. Processar arquivo específico
2. Processar todos os arquivos da pasta entrada
3. Ver estatísticas

### Opção 2: Processamento em Lote

```python
from src.main import OrquestradorAutomacao

orq = OrquestradorAutomacao()
resultados = orq.processar_lote("./entrada")
```

### Opção 3: Usar Módulos Individualmente

#### Fase 1: Ler com OCR
```python
from src.leitor import LeitorOCR

leitor = LeitorOCR()
texto, sucesso = leitor.ler_arquivo("nota.pdf")
if sucesso:
    print(texto)
```

#### Fase 2: Extrair Campos
```python
from src.extrator import ExtratorCampos

extrator = ExtratorCampos()
campos = extrator.extrair_todos_campos(texto)
print(campos)
```

#### Fase 4: Integração Monday
```python
from src.monday_api import MondayAPI

api = MondayAPI(api_key="seu_token", board_id="123456")
item = api.criar_item("ABC LTDA - NF 123456", "ABC LTDA")
```

## 📁 Estrutura do Projeto

```
OCR-LEITOR/
├── entrada/                 # Arquivos a processar
├── processadas/            # Arquivos processados com sucesso
├── erro/                   # Arquivos com erro
├── config/
│   └── settings.json       # Configurações principais
├── logs/
│   └── automacao.log       # Arquivo de log
├── src/
│   ├── __init__.py
│   ├── leitor.py          # FASE 1: Leitura OCR
│   ├── extrator.py        # FASE 2: Extração de campos
│   ├── monday_api.py      # FASE 4: Integração Monday
│   ├── uploader.py        # FASE 5: Gerenciamento de arquivos
│   └── main.py            # Orquestrador principal
├── requirements.txt        # Dependências Python
├── .env.example           # Template de variáveis de ambiente
└── README.md              # Este arquivo
```

## ⚙️ Configuração Avançada

### Padrões Regex

Editar em `config/settings.json`:

```json
{
  "regex_patterns": {
    "nfe": "N[ºo]\\s*\\d+",
    "chave": "\\d{44}",
    "data": "\\d{2}/\\d{2}/\\d{4}",
    "empresa": "Razão Social|Empresa|CNPJ"
  }
}
```

### Mapeamento de Colunas Monday

```json
{
  "colunas_monday": {
    "empresa": "Elemento",
    "nfe": "NUMERO NF-E",
    "chave": "CH.ACESSO",
    "vencimento": "VENCIMENTO",
    "arquivo": "Upload"
  }
}
```

### Extensões Suportadas

```json
{
  "extensoes_suportadas": [
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
    ".gif",
    ".bmp"
  ]
}
```

## 🔑 Obter Credenciais Monday

1. Acesse [monday.com](https://monday.com)
2. Vá para **Configurações → Administrador → API Tokens**
3. Clique em **Novo Token**
4. Copie o token gerado
5. No board desejado, copie o ID da URL: `monday.com/boards/**123456**`

## 📝 Logs

Os logs são salvos em `logs/automacao_YYYYMMDD_HHMMSS.log`

Exemplos:
```
2026-06-16 10:30:45 - src.leitor - INFO - Lendo imagem: entrada/nota.jpg
2026-06-16 10:30:46 - src.extrator - INFO - Empresa extraída: ABC LTDA
2026-06-16 10:30:47 - src.monday_api - INFO - Item criado com ID: 1234567890
```

## 🐛 Troubleshooting

### Erro: "Tesseract não encontrado"

```bash
# Windows - Ajustar caminho em settings.json
"tesseract_path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Linux
which tesseract
```

### Erro: "Nenhum texto extraído"

- Verificar qualidade da imagem
- Aumentar DPI em `config/settings.json`
- Conferir idioma: `lang='por'` para português

### Erro: "API Key inválida"

- Verificar se o token não expirou
- Confirmar se está em `config/settings.json` ou `.env`
- Testar token em https://api.monday.com/graphql

## 📊 Fase a Fase

### Fase 1: Leitura OCR
- Suporta: JPG, PNG, PDF, GIF, BMP
- Pré-processamento automático
- Extração de texto com Tesseract

### Fase 2: Extração de Campos
- Regex para campos estruturados
- Validação de formato
- Tratamento de erros

### Fase 3: Conferência Manual
- Exibição dos dados extraídos
- Confirmação do usuário
- Cancelamento se necessário

### Fase 4: Integração Monday
- Criação de item
- Atualização de colunas
- Upload de anexo

### Fase 5: Processamento em Lote
- Processamento automático
- Movimentação de arquivos
- Logs detalhados

## 🔐 Segurança

- ⚠️ **Nunca** commitar arquivo `config/settings.json` com credenciais reais
- ✅ Usar `settings.json.example` como template
- ✅ Usar variáveis de ambiente para credenciais
- ✅ Revisar `settings.json` antes de compartilhar

## 📞 Suporte

### Dúvidas Comuns

**P: Posso usar sem Monday?**
R: Sim! A automação funciona em modo offline - apenas não envia para Monday.

**P: Qual é o limite de arquivos?**
R: Sem limite técnico, mas recomenda-se processar em lotes de até 100 arquivos.

**P: Posso modificar os padrões regex?**
R: Sim, edite `config/settings.json` na seção `regex_patterns`.

**P: Funciona em Linux/Mac?**
R: Sim, basta instalar Tesseract via seu gerenciador de pacotes.

## 📄 Licença

MIT License - Veja LICENSE.md para detalhes

## 🤝 Contribuindo

1. Faça um Fork
2. Crie sua Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

**Desenvolvido com ❤️ para automação local e gratuita**
