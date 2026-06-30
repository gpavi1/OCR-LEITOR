# VALIDACAO-INTEGRACAO-OPERACIONAL-OCR-01

## Validacao Operacional da Integracao OCR-LEITOR + Monday

### Objetivo

Criar uma camada clara e profissional de validacao operacional da integracao Monday.

Depois desta fase, o sistema responde de forma objetiva:

* a configuracao Monday esta completa?
* o documento pode ser simulado?
* o documento pode ser enviado de verdade?
* o que esta bloqueando?
* o que o operador deve corrigir?
* ha risco de duplicidade?
* o historico ajuda no diagnostico?

### O que o sistema valida

1. **Configuracao Monday**: token, board ID, mapa de colunas (6 colunas obrigatorias).
2. **Documento apto**: status, revisao, campos obrigatorios, regras DANFE/NFS-e.
3. **Duplicidade**: sucesso anterior ou destino externo ja preenchido bloqueiam reenvio.

### Diferenca entre simulacao e envio real

| Aspecto | Simulacao (dry-run) | Envio real |
|---------|--------------------|------------|
| Chama API Monday? | Nao | Sim |
| Exige token real? | Nao | Sim |
| Exige board ID real? | Nao | Sim |
| Exige colunas configuradas? | Nao | Sim |
| Exige documento revisado? | Sim | Sim |
| Exige confirmacao explicita? | Nao | Sim (confirmar=sim) |
| Altera status do documento? | Nao (registra tentativa) | Sim (status=integrado) |
| Cria item no Monday? | Nao | Sim |

### Criterios para simulacao (pode_simular)

* Documento deve existir e ser um dicionario valido.
* Documento deve ter `id` preenchido.
* Status deve ser `pendente_integracao`.
* Documento deve estar revisado (`revisado = True`).
* Empresa deve estar preenchida.
* Numero NF ou chave de acesso deve estar preenchido.
* Regras DANFE/NFS-e devem ser respeitadas.
* **Nao exige** configuracao Monday completa.

Se configuracao estiver incompleta, a simulacao ainda e permitida, mas um aviso
e exibido: "Simulacao permitida, mas envio real bloqueado ate concluir a
configuracao Monday."

### Criterios para envio real (pode_enviar)

Tudo da simulacao, **mais**:

* Token Monday (`MONDAY_API_TOKEN`) presente e nao placeholder.
* Board ID (`MONDAY_BOARD_ID`) presente e nao placeholder.
* Mapa de colunas presente com todas as 6 colunas obrigatorias:
  * empresa
  * numero_nf
  * chave_acesso
  * vencimento
  * valor_total
  * observacao_revisao
* Sem duplicidade: nenhum envio anterior com sucesso ou destino externo preenchido.

### Bloqueios comuns

| Bloqueio | Causa | Correcao |
|----------|-------|----------|
| Token ausente ou placeholder | MONDAY_API_TOKEN vazio, "cole seu token" ou "exemplo_" | Configurar token real no .env |
| Board ID ausente ou placeholder | MONDAY_BOARD_ID vazio ou placeholder | Configurar board ID real no .env |
| Coluna obrigatoria nao configurada | Coluna ausente no mapa | Configurar MONDAY_COLUMN_* no .env |
| Documento nao revisado | revisado = False | Aprovar documento na tela de detalhes |
| Status incorreto | Documento nao esta em pendente_integracao | Revisar documento para avancar status |
| Empresa nao preenchida | Campo empresa vazio | Preencher empresa no documento |
| NF/chave vazia | Numero NF e chave acesso ambos vazios | Preencher pelo menos um |
| Envio ja registrado | Sucesso anterior ou destino externo preenchido | Verificar historico antes de reenviar |

### Roteiro operacional com cliente

**Passo 1: Validar configuracao**
1. Acessar `/integracoes/configuracao` no painel web.
2. Verificar se Monday aparece como **CONFIGURADA**.
3. Se **INCOMPLETA**, seguir o guia de configuracao em `docs/operacao/GUIA_INTEGRACAO_OCR_MONDAY.md`.

**Passo 2: Processar documento ficticio**
1. Enviar PDF de teste via upload no painel.
2. Aguardar processamento OCR + parser.
3. Confirmar que o documento aparece na lista de documentos.

**Passo 3: Revisar documento**
1. Abrir o documento na tela de detalhes.
2. Conferir campos extraidos.
3. Clicar "Aprovar e avancar".

**Passo 4: Validar na fila de integracao**
1. Acessar `/integracoes`.
2. Confirmar que o status do documento e "Pendente integracao".
3. Verificar o card "Pronto para integrar?" com o checklist.

**Passo 5: Simular Monday (dry-run)**
1. Clicar "Simular Monday".
2. Verificar o resultado no historico de integracao.
3. Se bloqueado, corrigir os bloqueios apontados.

**Passo 6: Conferir historico**
1. Acessar `/integracoes/historico`.
2. Verificar status "Simulacao apta" no historico.

**Passo 7: Enviar real controlado**
1. Voltar para a fila de integracao.
2. Clicar "Enviar para Monday".
3. Confirmar na janela de confirmacao explicita.

**Passo 8: Conferir item no Monday**
1. Acessar o board Monday.
2. Verificar se o item foi criado com os dados corretos.

**Passo 9: Registrar evidencia**
1. Exportar CSV ou JSON do documento.
2. Anotar o ID do item Monday para referencia.

### Seguranca

* Nao cole o token Monday em chats, emails ou documentos.
* Nao commite o arquivo `.env` no repositorio.
* Nao chame a API Monday nos testes automatizados.
* Se o token vazar, revogue imediatamente no Monday e gere um novo.
* O validador nunca exibe o valor do token nas mensagens de erro.

### O que esta fase nao faz

* Nao cria integracao com Google Sheets real.
* Nao cria integracao com ERP real.
* Nao envia anexo para Monday.
* Nao altera parser NF.
* Nao altera banco de dados.
* Nao altera pipeline OCR.
* Nao altera scripts ou instalador.
* Nao altera conectores Monday (payload, dryrun, envio).
