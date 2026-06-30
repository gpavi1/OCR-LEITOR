# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto segue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Adicionado

- Instalador compacto (`INSTALADOR-COMPACTO-OCR-01`): adiciona `INSTALAR-OCR-LEITOR.cmd`; adiciona logica de instalacao compacta com modos demo, cliente, update e verificar; modo update exige backup e instalacao existente; separa instalador de operacao diaria; documenta uso do instalador compacto; nao altera banco, parser, OCR pipeline, conectores ou painel web.

- Backup e restore operacional (`BACKUP-RESTORE-OCR-01`): adiciona backup operacional em ZIP com manifest; inclui pastas operacionais, schema e diagnostico; permite `.env` apenas mascarado; adiciona restore dry-run e restore real com confirmacao textual; prepara update seguro para o instalador compacto; adiciona opcoes seguras ao menu operacional; nao altera banco, parser, OCR pipeline, conectores ou painel web.

- Caminhos seguros para futuro instalador (`CAMINHOS-SEGUROS-INSTALADOR-OCR-01`): adiciona modulo de classificacao de caminhos seguros de instalacao; define caminhos recomendados para cliente e demo; documenta regras para DEMO, CLIENTE e UPDATE; adiciona alertas no doctor para caminhos inseguros; prepara base para instalador compacto sem criar instalador ainda; nao altera banco, parser, OCR pipeline, conectores ou scripts destrutivos.

- Configurador seguro de ambiente (`CONFIGURADOR-PLATAFORMA-SEGURO-OCR-01`): adiciona assistente CLI seguro para configurar `.env`; configura Monday, Web e MySQL; cria backup do `.env` antes de alteracao; mascara tokens e senhas no resumo; gera WEB_SECRET_KEY quando ausente; atualiza `.env.example` para variaveis reais atuais; adiciona opcao ao menu operacional; nao altera banco, parser, OCR pipeline, conectores ou painel web.

- Validacao operacional da integracao Monday (`VALIDACAO-INTEGRACAO-OPERACIONAL-OCR-01`): adiciona validador operacional central da integracao Monday; diferencia simulacao de envio real; bloqueia envio real quando configuracao/documento/duplicidade nao estao seguros; adiciona checklist "Pronto para integrar?" na fila; melhora mensagens de bloqueio e proximos passos; cria documentacao de validacao operacional; nao altera conectores, banco, parser, OCR pipeline ou envio real.

- Acabamento visual para uso real (`FECHAMENTO-USO-REAL-OCR-01A`): melhora labels visuais de status sem alterar valores internos; adiciona tags coloridas sutis para status de documentos e integrações; corrige exibição de status técnico cru em telas de integração; melhora diferenciação visual entre simulação e envio real Monday; adiciona guia visual de configuração OCR + Monday; cria documentação de integração OCR-LEITOR + Monday; não altera banco, parser, OCR pipeline, conectores ou envio real.

- Proteção CSRF nos formulários POST do painel web (`SEGURANCA-OCR-01B`): adiciona proteção CSRF manual sem dependências; injeta token CSRF nos templates com formulários; mantém API de entrada automatizada isenta para não quebrar integrações por Bearer; adiciona testes de proteção CSRF; não altera conectores, banco, parser, OCR pipeline, scripts ou envio Monday real.

- Hardening inicial de login e sessão (`SEGURANCA-OCR-01A`): remove fallback fixo inseguro da secret key do painel web; adiciona timeout de sessão; reforça configurações de cookie de sessão; adiciona rate limit simples no login; adiciona testes de autenticação e hardening inicial; não altera conectores, banco, parser, OCR pipeline ou envio Monday.

- Menu CMD central de operacao local Windows (`INSTALADOR-WINDOWS-OCR-01A`): `OCR-LEITOR.cmd` como ponto unico de entrada; `scripts/menu_operacao.py` com 16 opcoes (ambiente, venv, requirements, Tesseract, MySQL, pastas, web, OCR 24h, health, config integracoes, testes, limpeza segura, release); validadores seguros de Tesseract (`scripts/validador_tesseract.py`) e MySQL (`scripts/validador_mysql.py`); acoes destrutivas protegidas por confirmacao textual; nao altera conectores, banco, parser, OCR pipeline, envio Monday real ou requirements.

- Painel web de configuracao de plataformas de integracao (`CONFIG-PLATAFORMA-WEB-01`): tela somente leitura em `/integracoes/configuracao` que exibe Monday como plataforma suportada e Google Sheets/ERP como plataformas planejadas; classifica variaveis como CONFIGURADO, AUSENTE ou PLACEHOLDER sem exibir valores reais; nao salva token, nao chama API externa, nao altera banco, conectores ou envio real; link no menu lateral apos Integracoes.

- Envio real controlado de 1 documento revisado para Monday (`MONDAY-ENVIO-APROVADO-01`): modulo `conectores/monday_envio.py` com funcao `enviar_documento_monday(token, board_id, mapa_colunas, post_func=...)` — duas mutacoes GraphQL via variables (create_item + change_multiple_column_values), validacao de config (token, board_id, colunas) antes de chamar API, registro de `monday_envio_sucesso/falha/bloqueado` em `integracao_tentativas`, atualiza `documentos.status` para `integrado` apenas em sucesso, bloqueia reenvio por duplicidade. Rota POST `/integracoes/documentos/<id>/enviar-monday` com `confirmar=sim` obrigatorio. Botoes "Enviar para Monday" na fila e no detalhe (condicional `pendente_integracao`). Testes injetam `post_func` fake — zero rede, zero banco, zero OCR. Tag `monday-envio-aprovado-01-ok`.

- Simulacao segura de envio Monday sem chamada externa (`MONDAY-DRYRUN-01`): modulo `conectores/monday_dryrun.py` com funcao `gerar_dryrun_monday` que valida documento revisado, monta payload e column_values simuladas; registra dry-run em `integracao_tentativas` com status `dry_run_apto`, `dry_run_bloqueado` ou `dry_run_erro`; rota POST `/integracoes/documentos/<id>/monday-dryrun` no painel; botoes "Simular Monday" na fila de integracao e no detalhe do documento; nao altera status do documento para integrado; nao chama API externa; nao usa token.

- Contrato seguro de payload Monday a partir de documento revisado (`CONTRATO-MONDAY-01`): modulo puro `conectores/monday_payload.py` com funcoes de normalizacao, validacao e montagem de column_values; bloqueia documentos sem revisao ou fora de `pendente_integracao`; adiciona avisos para campos ausentes; prepara base para dry-run sem chamada externa; nao envia dados reais para Monday; nao altera parser, pipeline, banco, API, UI ou requirements.

- Documento de configuracao exemplar (`MONDAY_CONFIG_EXEMPLO.md`): lista todas as 8 variaveis de ambiente necessarias para envio real Monday, com placeholders ficticios e instrucoes de seguranca (nunca commit .env, nunca expor token/board_id).

- Modelo seguro de configuracao para plataformas integradas (`CONFIG-INTEGRACAO-SEGURA-01`): documenta modelo de 4 camadas (contrato, dry-run, envio, rota); define separacao entre contrato interno, mapeamento externo, credenciais, execucao e historico; cria template replicavel para novas integracoes (`MODELO_PLATAFORMA_INTEGRADA.md`); cria checklist operacional e de seguranca (`CHECKLIST_NOVA_INTEGRACAO.md`); nao altera codigo, banco, parser, OCR pipeline, UI ou requirements.

### Corrigido

- Interpretação do campo revisado vindo do MySQL como inteiro 1 (`FIX-MONDAY-REVISADO-01`): corrige `_bool_revisado` em `conectores/monday_payload.py` para aceitar int 1, str "1", "true", "sim", "s", "yes" e variantes maiúsculas/minúsculas; mantém bloqueio para 0, "0", "false", "nao", "não", None, vazio, espaços; valida contrato, dry-run e envio controlado com valores booleanos e inteiros; não altera banco, parser, OCR pipeline, UI ou requirements.
- Ajuste visual e operacional dos botoes da fila de integracao (`AJUSTE-FILA-MONDAY-01`): adiciona `revisado` na SELECT da fila e `status_atual` no historico; condiciona exibicao de Simular Monday e Enviar Monday ao campo revisado; oculta reenfileirar para documentos ja na fila ou integrados; exibe indicacao textual de documento pendente de revisao, ja na fila ou ja integrado; nao altera contrato, dry-run, envio real, banco, parser, OCR pipeline ou requirements.
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
