# CHECKLIST_NOVA_INTEGRACAO — Liberacao segura de plataforma externa

## Instrucoes

Preencher este checklist para cada nova plataforma antes de liberar em producao.

Qualquer item nao atendido em **A a F** bloqueia a liberacao.

Itens de **G (Operacao)** devem ser validados em ambiente controlado antes da producao.

---

### A. Contrato (payload)

- [ ] `_payload.py` nao le `.env` nem usa `os.getenv`.
- [ ] `_payload.py` nao importa `requests`, `urllib` ou `http`.
- [ ] `_payload.py` nao contem token, board_id, column_id real.
- [ ] `_payload.py` valida que documento foi revisado (`_bool_revisado`).
- [ ] `_payload.py` valida status `pendente_integracao`.
- [ ] `_payload.py` valida campos obrigatorios (empresa, NF/chave).
- [ ] `_payload.py` aceita mapeamento de colunas por parametro.

### B. Dry-run

- [ ] Nao chama API externa.
- [ ] Nao usa token ou credencial.
- [ ] Nao altera `documentos.status` para `integrado`.
- [ ] Registra `dry_run_apto` ou `dry_run_bloqueado` no historico.
- [ ] Exibe bloqueios para o operador antes do envio real.

### C. Envio real

- [ ] Exige confirmacao humana explicita (`confirmar=sim`).
- [ ] Recebe credencial por parametro (nunca le `.env`).
- [ ] Usa `post_func`/`client` injetavel (testes sem rede).
- [ ] So marca `integrado` apos sucesso confirmado pela API externa.
- [ ] Falha na API externa nunca marca como `integrado`.
- [ ] Reenvio de documento ja integrado e bloqueado (antiduplicidade).

### D. Seguranca

- [ ] Token esta fora do Git (`.gitignore` cobre `.env`).
- [ ] Token nao aparece em documentacao da fase.
- [ ] Token nao aparece em CHANGELOG.
- [ ] Token nao aparece em logs da aplicacao.
- [ ] Token nao e salvo no banco (`integracoes.config_json` nao contem token).
- [ ] Token nao aparece em `integracao_tentativas.erro`.
- [ ] Token nao aparece em `integracao_tentativas.resposta_resumida`.
- [ ] Erros sao sanitizados antes de salvar no historico.

### E. Historico

- [ ] Salva status da tentativa.
- [ ] Salva `destino_externo_id` quando houver (ID do item criado).
- [ ] Salva `resposta_resumida` sem segredo.
- [ ] Salva `erro` sem segredo (sanitizado).

### F. Testes

- [ ] Teste especifico da plataforma passa.
- [ ] Testes de integracao da familia Monday passam.
- [ ] `pytest` completo passa.
- [ ] Nenhum teste chama internet ou API externa.
- [ ] Nenhum teste conecta MySQL real.
- [ ] Nenhum teste executa OCR real.
- [ ] Nenhum token real aparece nos arquivos de teste.

### G. Operacao (ambiente controlado)

- [ ] Dry-run executado com sucesso antes do envio real.
- [ ] Envio real feito com 1 documento (nao lote).
- [ ] Documento conferido visualmente na plataforma externa.
- [ ] Banco confirmou status `integrado` para o documento.
- [ ] Historico confirmou registro `envio_sucesso`.
- [ ] Token removido da sessao/terminal apos o teste.

---

## Aprovacao Final

- [ ] Todos os itens de A a F estao atendidos.
- [ ] Operacao (G) validada em ambiente controlado.
- [ ] Tag de versao criada.
- [ ] Documentacao da fase adicionada ao INDEX.md.
- [ ] Entrada adicionada ao CHANGELOG.md.

**A plataforma so pode ser considerada pronta para producao se todos os blocos acima estiverem verificados. Qualquer falha de seguranca (bloco D) bloqueia a liberacao automaticamente.**
