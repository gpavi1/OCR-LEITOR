# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto segue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Corrigido

- Ajuste cirúrgico do parser NF-e (`AJUSTE-OCR-01`): correção da extração de empresa, número NF e chave de acesso em DANFE com ruído OCR.
- Melhoria do parser para layouts variados (`AJUSTE-OCR-02`): distinção emitente vs tomador/destinatário, captura de NF em padrões variados (NF-e No., No., NFS-e:), captura de valor total por contexto (TOTAL GERAL DA NOTA, VALOR DOS SERVICOS, DUPLICATA/FATURA), bloqueio de chave falsa em NFS-e.

### Adicionado

- Guia operacional para uso controlado do OCR-LEITOR na empresa (`GUIA-PILOTO-EMPRESA-01`): documentação do fluxo oficial (OCR preenche → humano revisa → dado validado → exportação), checklist de revisão por documento, modelo CSV para controle do piloto, critérios para encerramento e para abertura de ajuste de parser.

### Documentação

- Implementada a fase `DIAG-OCR-01` com auditoria local da extração OCR/parser e relatórios privados.
- Implementada a fase `AJUSTE-OCR-01` com documentação da correção cirúrgica do parser.
- Implementada a fase `AJUSTE-OCR-02` com documentação da melhoria do parser para layouts variados.
- Implementada a fase `GUIA-PILOTO-EMPRESA-01` com guia operacional, checklist de revisão e modelo CSV para controle do piloto real.
- Implementada a fase `RESET-BANCO-TESTE-01` com script seguro de limpeza do banco de teste, backup obrigatório e dry-run como padrão.
- Implementada a fase `OPS-OCR-01` com limpeza segura do ambiente de testes e backup em `_backup_testes/`.
- Implementada a fase `API-IN-01` com API local autenticada para entrada controlada de documentos em `input/`.
- Implementada a fase `MARKDOWN-OCR-01` com geração local e manual do relatório Markdown humano em `exports/markdown/`.
- Implementada a fase `EXPORT-OCR-01` com exportação local, segura e validada do JSON revisado em `exports/json/`.
- Definido o ADR `docs/integracao/ADR-PLAN-INTEGRACAO-01-api-entrada.md` com a arquitetura segura da futura API de entrada.
- Registrada a ordem obrigatória `PLAN-INTEGRACAO-01 -> EXPORT-OCR-01 -> MARKDOWN-OCR-01 -> API-IN-01`.
- Formalizado que a primeira API será local e controlada, sem exposição pública inicial, sem OCR automático e sem escrita direta no banco.
- Formalizado que o JSON estruturado continuará como fonte oficial de integração e que o Markdown futuro será apenas relatório humano.

## [1.0.0] - 2026-06-16

### Adicionado

- ✨ **Fase 1 - Leitor OCR**: Suporte para leitura de imagens (JPG, PNG, GIF, BMP) e PDFs
- ✨ **Fase 2 - Extrator de Campos**: Extração automática de empresa, NF-e, chave e vencimento
- ✨ **Fase 3 - Conferência Manual**: Tela de validação interativa para o usuário
- ✨ **Fase 4 - Integração Monday**: API GraphQL para criar items e atualizar colunas
- ✨ **Fase 5 - Processamento em Lote**: Automação completa de múltiplos arquivos
- 📁 Gerenciamento automático de pastas (entrada, processadas, erro)
- 📝 Sistema de logging detalhado com arquivos de log
- ⚙️ Configuração via JSON com padrões regex customizáveis
- 📱 Menu interativo com opções de operação
- 🔍 Pré-processamento de imagens para melhorar OCR
- ✅ Validação de campos extraídos
- 🛡️ Tratamento robusto de erros
- 📚 Documentação completa (README, QUICKSTART, examples)
- 🔐 Suporte a variáveis de ambiente para credenciais

### Tecnologias

- Python 3.8+
- Tesseract OCR 5.0+
- OpenCV 4.8+
- pdf2image 1.16+
- Pillow 10.1+
- Requests 2.31+

### Documentação

- ✅ README.md - Documentação completa
- ✅ QUICKSTART.md - Guia de 5 minutos
- ✅ examples.py - 12 exemplos práticos
- ✅ copilot-instructions.md - Instruções para IA
- ✅ verificar_instalacao.py - Validação de setup

### Estrutura

```
OCR-LEITOR/
├── src/
│   ├── main.py           # Orquestrador principal
│   ├── leitor.py         # Leitor OCR
│   ├── extrator.py       # Extrator de campos
│   ├── monday_api.py     # API Monday
│   ├── uploader.py       # Gerenciador de arquivos
│   └── __init__.py
├── config/
│   └── settings.json     # Configurações
├── entrada/              # Arquivos de entrada
├── processadas/          # Arquivos processados
├── erro/                 # Arquivos com erro
├── logs/                 # Logs de execução
├── requirements.txt      # Dependências
├── README.md             # Documentação
├── QUICKSTART.md         # Início rápido
├── examples.py           # Exemplos de uso
├── verificar_instalacao.py # Validador
├── LICENSE.md            # MIT License
└── .gitignore           # Git ignore
```

## Versões Futuras

### [1.1.0] - Planejado

- [ ] Suporte para múltiplos idiomas (inglês, espanhol, francês)
- [ ] Cache de configurações para melhor performance
- [ ] Dashboard web para visualizar processamentos
- [ ] Exportação de relatórios em Excel/PDF
- [ ] Suporte a webhooks do Monday
- [ ] API REST para integração externa

### [1.2.0] - Planejado

- [ ] Detecção automática de layouts de notas
- [ ] Machine Learning para melhor extração
- [ ] Sincronização automática de múltiplos boards
- [ ] Backup automático de arquivos
- [ ] Histórico de processamentos

### [2.0.0] - Visão

- [ ] Interface gráfica (Electron/Tkinter)
- [ ] Aplicação mobile
- [ ] Cloud storage integration
- [ ] AI-powered validation
- [ ] Multi-language support

---

## Como Contribuir

1. Faça um Fork do projeto
2. Crie uma Branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Suporte

Para reportar bugs ou sugerir features, abra uma issue ou entre em contato.

---

**Desenvolvido com ❤️ para automação local e gratuita**

Última atualização: 2026-06-16
