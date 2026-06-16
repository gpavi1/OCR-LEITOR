# OCR LEITOR - Instruções para Copilot

## 📋 Sobre o Projeto

Este é um projeto de automação de OCR para processar notas fiscais (fotos/PDFs) e integrar com Monday.com. O projeto é executado localmente, sem custos e sem dependências pagas.

## 🎯 Objetivos Principais

1. Ler imagens e PDFs com OCR (Tesseract)
2. Extrair campos específicos via regex
3. Permitir conferência manual dos usuários
4. Integrar com Monday.com via GraphQL
5. Processar em lote automaticamente

## 📁 Estrutura

```
src/
  ├── leitor.py          # FASE 1: Leitura OCR
  ├── extrator.py        # FASE 2: Extração de campos
  ├── monday_api.py      # FASE 4: API Monday
  ├── uploader.py        # FASE 5: Gerenciamento de arquivos
  ├── main.py            # Orquestrador
  └── __init__.py

config/
  └── settings.json      # Configurações

entrada/                 # Arquivos a processar
processadas/            # Arquivos processados
erro/                   # Arquivos com erro
logs/                   # Logs de execução
```

## 🔧 Tecnologias

- **Python 3.8+**
- **Tesseract OCR** - Reconhecimento de caracteres
- **OpenCV** - Processamento de imagens
- **pdf2image** - Conversão de PDF
- **Requests** - Requisições HTTP
- **Monday GraphQL API**

## 📊 Campos Extraídos

- Empresa (razão social)
- Número NF-e
- Chave de acesso (44 dígitos)
- Data de vencimento

## 🚀 Como Executar

```bash
# Verificar instalação
python verificar_instalacao.py

# Menu interativo
python -m src.main

# Processamento em lote
python -c "from src.main import OrquestradorAutomacao; orq = OrquestradorAutomacao(); print(orq.processar_lote())"
```

## 📖 Usando os Módulos

### Fase 1: OCR
```python
from src.leitor import LeitorOCR
leitor = LeitorOCR()
texto, ok = leitor.ler_arquivo("arquivo.pdf")
```

### Fase 2: Extração
```python
from src.extrator import ExtratorCampos
extrator = ExtratorCampos()
campos = extrator.extrair_todos_campos(texto)
```

### Fase 4: Monday API
```python
from src.monday_api import MondayAPI
api = MondayAPI(api_key="token", board_id="123")
item = api.criar_item("Nome", "Empresa")
api.atualizar_campos(item_id, campos)
```

## 🔐 Configuração

- **config/settings.json**: Credenciais e padrões
- **.env** ou variáveis de ambiente: Dados sensíveis
- **Tesseract path**: Caminho do executável no Windows

## 📝 Padrões Regex

- NF-e: `N[ºo]\s*\d+`
- Chave: `\d{44}`
- Data: `\d{2}/\d{2}/\d{4}`
- Empresa: `Razão Social|Empresa|CNPJ`

Editáveis em `config/settings.json`

## 🎯 Instruções para Melhorias

Ao trabalhar neste projeto:

1. **Manter modularidade** - Cada módulo tem responsabilidade única
2. **Adicionar logs** - Sempre registrar operações importantes
3. **Validação** - Validar entrada antes de processar
4. **Tratamento de erros** - Try/except com logging apropriado
5. **Documentação** - Docstrings em português/inglês
6. **Tipagem** - Usar type hints quando possível

## 🐛 Debugging

- Verificar `logs/automacao_*.log`
- Ativar debug mode em `settings.json`: `"debug": true`
- Testar módulos individualmente

## 🔄 Fluxo Completo

```
Entrada → OCR → Extração → Validação → Conferência → Monday → Processadas
                                              ↓
                                            Erro
```

## 📌 Pontos Importantes

- ✅ Suporta múltiplas extensões (jpg, png, pdf, gif, bmp)
- ✅ Processamento em lote automático
- ✅ Modo offline (sem Monday) sempre disponível
- ✅ Cancelamento antes de confirmar
- ⚠️ Chaves de acesso têm exatamente 44 dígitos
- ⚠️ Data deve estar no formato DD/MM/YYYY

## 📚 Documentação

- **README.md** - Documentação completa
- **QUICKSTART.md** - Início rápido
- **verificar_instalacao.py** - Validação
- **config/settings.json** - Configurações

---

**Última atualização:** 2026-06-16
