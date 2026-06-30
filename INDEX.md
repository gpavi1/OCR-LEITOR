# 📑 Índice Completo - OCR LEITOR

## 🎯 Começar Aqui

1. **[PROJETO_CRIADO.md](PROJETO_CRIADO.md)** ← Leia primeiro! Resumo completo
2. **[QUICKSTART.md](QUICKSTART.md)** ← 5 minutos para começar
3. **[README.md](README.md)** ← Documentação detalhada

---

## 📁 Estrutura do Projeto

### 🔧 Configuração
- **[config/settings.json](config/settings.json)** - Credenciais e padrões regex
- **[.env.example](.env.example)** - Template de variáveis de ambiente
- **[requirements.txt](requirements.txt)** - Dependências Python

### 💻 Código Fonte (src/)
- **[src/main.py](src/main.py)** - ⭐ Orquestrador principal (TODAS AS FASES)
  - Fase 1: Leitura OCR
  - Fase 2: Extração de campos
  - Fase 3: Conferência manual
  - Fase 4: Integração Monday
  - Fase 5: Processamento em lote

- **[src/leitor.py](src/leitor.py)** - FASE 1: Leitor OCR
  - Ler imagens (JPG, PNG, GIF, BMP)
  - Converter PDFs em imagens
  - Extrair texto com Tesseract
  - Pré-processamento automático

- **[src/extrator.py](src/extrator.py)** - FASE 2: Extrator de Campos
  - Extrair empresa (razão social)
  - Extrair NF-e (número nota fiscal)
  - Extrair chave (44 dígitos)
  - Extrair vencimento (DD/MM/YYYY)
  - Validação completa

- **[src/monday_api.py](src/monday_api.py)** - FASE 4: API Monday
  - Criar items no board
  - Atualizar colunas (GraphQL)
  - Upload de anexos
  - Tratamento de erros

- **[src/uploader.py](src/uploader.py)** - FASE 5: Gerenciador
  - Mover para processadas
  - Mover para erro
  - Validar arquivos
  - Listar processados

- **[src/__init__.py](src/__init__.py)** - Pacote Python

### 📚 Documentação
- **[README.md](README.md)** - Documentação completa (1200+ linhas)
  - Instalação passo a passo
  - Como usar cada módulo
  - Troubleshooting
  - FAQ

- **[QUICKSTART.md](QUICKSTART.md)** - Início rápido em 5 minutos
  - Instalação rápida
  - Exemplos rápidos
  - Checklist inicial

- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de versões
  - v1.0.0 (atual)
  - Versões futuras
  - Roadmap

- **[PROJETO_CRIADO.md](PROJETO_CRIADO.md)** - Resumo de criação
  - Estrutura criada
  - Fases implementadas
  - Próximos passos

- **[copilot-instructions.md](copilot-instructions.md)** - Instruções para IA
  - Contexto do projeto
  - Como melhorar o projeto
  - Padrões de código

- **[LICENSE.md](LICENSE.md)** - MIT License

- **[INDEX.md](INDEX.md)** - Este arquivo (navegação)
- **[docs/integracao/ADR-PLAN-INTEGRACAO-01-api-entrada.md](docs/integracao/ADR-PLAN-INTEGRACAO-01-api-entrada.md)** - ADR da arquitetura segura da futura API de entrada
- **[docs/integracao/API-IN-01_ENTRADA_DOCUMENTOS.md](docs/integracao/API-IN-01_ENTRADA_DOCUMENTOS.md)** - API local autenticada para entrada controlada de documentos
- **[docs/exportacao/EXPORT-OCR-01_JSON_VALIDADO.md](docs/exportacao/EXPORT-OCR-01_JSON_VALIDADO.md)** - Exportação local do JSON validado revisado
- **[docs/exportacao/MARKDOWN-OCR-01_RELATORIO_HUMANO.md](docs/exportacao/MARKDOWN-OCR-01_RELATORIO_HUMANO.md)** - Relatório Markdown humano derivado do JSON validado
- **[docs/operacao/OPS-OCR-01_LIMPEZA_AMBIENTE_TESTE.md](docs/operacao/OPS-OCR-01_LIMPEZA_AMBIENTE_TESTE.md)** - Limpeza segura do ambiente de testes
- **[docs/operacao/RESET-BANCO-TESTE-01_LIMPEZA_BANCO_TESTE.md](docs/operacao/RESET-BANCO-TESTE-01_LIMPEZA_BANCO_TESTE.md)** - Limpeza segura dos registros de teste do banco MySQL
- **[docs/diagnostico/DIAG-OCR-01_AUDITORIA_EXTRACAO.md](docs/diagnostico/DIAG-OCR-01_AUDITORIA_EXTRACAO.md)** - Auditoria assistida da extração OCR/parser
- **[docs/diagnostico/AJUSTE-OCR-01_CORRECAO_PARSER.md](docs/diagnostico/AJUSTE-OCR-01_CORRECAO_PARSER.md)** - Correção cirúrgica do parser NF-e

### 🛠️ Utilidades
- **[examples.py](examples.py)** - 12 exemplos práticos
  1. Menu interativo
  2. Ler com OCR
  3. Extrair campos
  4. Conferência manual
  5. API Monday
  6. Processar arquivo
  7. Processamento em lote
  8. Gerenciador de arquivos
  9. Config customizada
  10. Logging e debug
  11. Processamento customizado
  12. Integração customizada

- **[verificar_instalacao.py](verificar_instalacao.py)** - Validador de setup
  - Verificar Python 3.8+
  - Verificar dependências
  - Verificar Tesseract
  - Verificar estrutura
  - Verificar configuração

### 📦 Outros
- **[.gitignore](.gitignore)** - Git ignore
- **[requirements.txt](requirements.txt)** - Dependências Python

### 📁 Pastas de Dados
- **[entrada/](entrada/)** - 📥 Coloque imagens/PDFs aqui
- **[processadas/](processadas/)** - ✅ Arquivos processados com sucesso
- **[erro/](erro/)** - ❌ Arquivos com erro
- **[logs/](logs/)** - 📝 Arquivos de log
- **[config/](config/)** - ⚙️ Configurações

---

## 🗺️ Mapa de Navegação

### Se você quer...

**Começar rapidamente**
→ [QUICKSTART.md](QUICKSTART.md)

**Entender tudo sobre o projeto**
→ [README.md](README.md)

**Ver código de exemplo**
→ [examples.py](examples.py)

**Validar instalação**
→ [verificar_instalacao.py](verificar_instalacao.py)

**Entender o fluxo completo**
→ [src/main.py](src/main.py)

**Usar apenas OCR**
→ [src/leitor.py](src/leitor.py)

**Extrair campos**
→ [src/extrator.py](src/extrator.py)

**Integrar com Monday**
→ [src/monday_api.py](src/monday_api.py)

**Customizar padrões**
→ [config/settings.json](config/settings.json)

**Ver histórico de mudanças**
→ [CHANGELOG.md](CHANGELOG.md)

**Entender o planejamento da futura API de entrada**
→ [docs/integracao/ADR-PLAN-INTEGRACAO-01-api-entrada.md](docs/integracao/ADR-PLAN-INTEGRACAO-01-api-entrada.md)

**Usar a API local de entrada controlada**
→ [docs/integracao/API-IN-01_ENTRADA_DOCUMENTOS.md](docs/integracao/API-IN-01_ENTRADA_DOCUMENTOS.md)

**Entender a exportação JSON validada local**
→ [docs/exportacao/EXPORT-OCR-01_JSON_VALIDADO.md](docs/exportacao/EXPORT-OCR-01_JSON_VALIDADO.md)

**Entender o relatório Markdown humano local**
→ [docs/exportacao/MARKDOWN-OCR-01_RELATORIO_HUMANO.md](docs/exportacao/MARKDOWN-OCR-01_RELATORIO_HUMANO.md)

**Limpar o ambiente de testes com backup**
→ [docs/operacao/OPS-OCR-01_LIMPEZA_AMBIENTE_TESTE.md](docs/operacao/OPS-OCR-01_LIMPEZA_AMBIENTE_TESTE.md)

**Limpar registros de teste do banco MySQL**
→ [docs/operacao/RESET-BANCO-TESTE-01_LIMPEZA_BANCO_TESTE.md](docs/operacao/RESET-BANCO-TESTE-01_LIMPEZA_BANCO_TESTE.md)

**Auditar extração OCR/parser com amostras privadas**
→ [docs/diagnostico/DIAG-OCR-01_AUDITORIA_EXTRACAO.md](docs/diagnostico/DIAG-OCR-01_AUDITORIA_EXTRACAO.md)

**Corrigir parser NF-e (AJUSTE-OCR-01)**
→ [docs/diagnostico/AJUSTE-OCR-01_CORRECAO_PARSER.md](docs/diagnostico/AJUSTE-OCR-01_CORRECAO_PARSER.md)

**Melhorar parser para layouts variados (AJUSTE-OCR-02)**
→ [docs/diagnostico/AJUSTE-OCR-02_LAYOUTS_VARIADOS.md](docs/diagnostico/AJUSTE-OCR-02_LAYOUTS_VARIADOS.md)

**Guia operacional para piloto na empresa (GUIA-PILOTO-EMPRESA-01)**
→ [docs/operacao/GUIA_PILOTO_EMPRESA_01.md](docs/operacao/GUIA_PILOTO_EMPRESA_01.md)

**Checklist de revisão de documento**
→ [docs/operacao/CHECKLIST_REVISAO_DOCUMENTO.md](docs/operacao/CHECKLIST_REVISAO_DOCUMENTO.md)

**Modelo CSV para controle do piloto**
→ [docs/operacao/MODELO_CONTROLE_PILOTO_EMPRESA.csv](docs/operacao/MODELO_CONTROLE_PILOTO_EMPRESA.csv)

**Contrato seguro de payload Monday revisado (CONTRATO-MONDAY-01)**
→ [docs/integracao/CONTRATO-MONDAY-01_PAYLOAD_REVISADO.md](docs/integracao/CONTRATO-MONDAY-01_PAYLOAD_REVISADO.md)

**Criar payload Monday a partir de documento revisado**
→ [conectores/monday_payload.py](conectores/monday_payload.py)

**Simular envio Monday sem chamada externa (MONDAY-DRYRUN-01)**
→ [docs/integracao/MONDAY-DRYRUN-01_ENVIO_SIMULADO.md](docs/integracao/MONDAY-DRYRUN-01_ENVIO_SIMULADO.md)

**Módulo de dry-run Monday**
→ [conectores/monday_dryrun.py](conectores/monday_dryrun.py)

**Enviar documento revisado para Monday (envio real controlado MONDAY-ENVIO-APROVADO-01)**
→ [docs/integracao/MONDAY-ENVIO-APROVADO-01_ENVIO_REAL_CONTROLADO.md](docs/integracao/MONDAY-ENVIO-APROVADO-01_ENVIO_REAL_CONTROLADO.md)

**Módulo de envio real Monday**
→ [conectores/monday_envio.py](conectores/monday_envio.py)

**Configuração segura das variáveis de ambiente do Monday**
→ [docs/integracao/MONDAY_CONFIG_EXEMPLO.md](docs/integracao/MONDAY_CONFIG_EXEMPLO.md)

**Modelo seguro de configuração para plataformas integradas (CONFIG-INTEGRACAO-SEGURA-01)**
→ [docs/integracao/CONFIG-INTEGRACAO-SEGURA-01.md](docs/integracao/CONFIG-INTEGRACAO-SEGURA-01.md)

**Painel web de configuração de integrações (CONFIG-PLATAFORMA-WEB-01)**
→ Disponível em `/integracoes/configuracao` no painel web

**Template para criar nova integração no OCR-LEITOR**
→ [docs/integracao/MODELO_PLATAFORMA_INTEGRADA.md](docs/integracao/MODELO_PLATAFORMA_INTEGRADA.md)

**Checklist de segurança para liberar nova plataforma externa**
→ [docs/integracao/CHECKLIST_NOVA_INTEGRACAO.md](docs/integracao/CHECKLIST_NOVA_INTEGRACAO.md)

**Menu operacional Windows (INSTALADOR-WINDOWS-OCR-01A)**
→ Disponível em `OCR-LEITOR.cmd` na raiz do projeto

**Hardening inicial de login e sessão (SEGURANCA-OCR-01A)**
→ Removido fallback inseguro da secret key; adicionado timeout de sessão, cookie hardening e rate limit no login. Sem alteração no fluxo OCR/Monday. CSRF ficará para fase seguinte.

**Proteção CSRF nos formulários POST (SEGURANCA-OCR-01B)**
→ Proteção CSRF manual nos formulários POST do painel web, sem dependências externas. Preserva API de entrada e fluxo OCR/Monday.

**Desenvolver o projeto**
→ [copilot-instructions.md](copilot-instructions.md)

---

## 📊 Fases Implementadas

### ✅ FASE 1: Leitor OCR
[src/leitor.py](src/leitor.py)
- Ler imagens: JPG, PNG, GIF, BMP
- Ler PDFs: Conversão automática em imagens
- Extrair texto com Tesseract OCR
- Pré-processamento automático
- ~200 linhas de código

### ✅ FASE 2: Extrator de Campos
[src/extrator.py](src/extrator.py)
- Extrair empresa (razão social)
- Extrair NF-e (número nota fiscal)
- Extrair chave (44 dígitos)
- Extrair vencimento (DD/MM/YYYY)
- Validação completa
- ~250 linhas de código

### ✅ FASE 3: Conferência Manual
[src/main.py](src/main.py) - método `_solicitar_confirmacao`
- Exibir dados extraídos
- Solicitar confirmação do usuário
- Permitir cancelamento
- Interface clara e intuitiva

### ✅ FASE 4: Integração Monday
[src/monday_api.py](src/monday_api.py)
- Criar items via GraphQL
- Atualizar colunas
- Upload de anexos
- Tratamento de erros
- ~300 linhas de código

### ✅ FASE 5: Processamento em Lote
[src/main.py](src/main.py) - método `processar_lote`
- Processar múltiplos arquivos
- Mover para "processadas" após sucesso
- Mover para "erro" se falhar
- Log detalhado de cada operação
- Estatísticas finais

---

## 🚀 Começar em 5 Passos

```bash
# 1. Instalar Tesseract
choco install tesseract

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar credenciais
# Editar: config/settings.json

# 4. Validar instalação
python verificar_instalacao.py

# 5. Executar
python -m src.main
```

---

## 📈 Estatísticas

| Item | Quantidade |
|------|-----------|
| Arquivos Python | 6 |
| Linhas de Código | ~1200 |
| Linhas de Documentação | ~2000 |
| Exemplos | 12 |
| Fases Implementadas | 5 |
| Pastas de Dados | 4 |
| Arquivos de Config | 3 |

---

## 🔐 Configuração Importante

### Credenciais Monday
Editar `config/settings.json`:
```json
{
  "monday_api_key": "SEU_TOKEN_AQUI",
  "monday_board_id": "SEU_BOARD_ID_AQUI"
}
```

### Tesseract Path (Windows)
```json
{
  "tesseract_path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
}
```

---

## 📞 Suporte

### Validação
```bash
python verificar_instalacao.py
```

### Ver Logs
```
logs/automacao_YYYYMMDD_HHMMSS.log
```

### Exemplos
```bash
python examples.py
```

---

## 🎯 Próximos Passos

1. Ler [PROJETO_CRIADO.md](PROJETO_CRIADO.md)
2. Ler [QUICKSTART.md](QUICKSTART.md)
3. Executar `python verificar_instalacao.py`
4. Configurar `config/settings.json`
5. Colocar um PDF em `entrada/`
6. Executar `python -m src.main`

---

## 📚 Documentação Completa

Todos os módulos estão totalmente documentados com:
- ✅ Docstrings em português
- ✅ Type hints
- ✅ Comentários explicativos
- ✅ Exemplos de uso
- ✅ Tratamento de erros

---

## 🎉 Pronto para Usar!

O projeto está **100% completo** e pronto para:
- ✅ Processar notas fiscais
- ✅ Extrair campos automaticamente
- ✅ Integrar com Monday.com
- ✅ Processar em lote
- ✅ Customizar conforme necessário

---

**Desenvolvido com ❤️ para automação local e gratuita**

Para dúvidas, consulte:
- [README.md](README.md) - Documentação completa
- [examples.py](examples.py) - Exemplos práticos
- [copilot-instructions.md](copilot-instructions.md) - Instruções

Boa sorte! 🚀
