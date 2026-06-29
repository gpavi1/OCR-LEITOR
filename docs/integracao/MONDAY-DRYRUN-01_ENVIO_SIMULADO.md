# MONDAY-DRYRUN-01 — Simulacao Segura de Envio para Monday

## 1. Objetivo da Fase

Criar uma simulacao segura de envio para Monday que valida o documento revisado, monta o payload logico e as column_values, e registra o resultado localmente — **sem chamar API externa, sem usar token, sem enviar nada para Monday**.

## 2. O que e Dry-run

Dry-run e uma execucao de teste que percorre todo o fluxo de validacao e montagem de dados, mas **nao executa a chamada de rede** para o Monday.com.

O objetivo e:

- Verificar se o documento esta apto para envio futuro.
- Visualizar quais campos seriam enviados.
- Identificar bloqueios ou avisos antes do envio real.
- Registrar a tentativa no historico local para auditoria.

## 3. Nenhum Dado e Enviado para Monday

A funcao `gerar_dryrun_monday()` em `conectores/monday_dryrun.py`:

- **Nao importa `requests`** ou qualquer biblioteca de rede.
- **Nao contem `api.monday.com`** em nenhum lugar do codigo.
- **Nao usa token**, board_id ou column_id real.
- **Nao envia nada para Monday**.
- **Nao chama API externa**.
- **Nao le o arquivo de configuracao de ambiente**.
- **Nao usa `os.getenv` ou `os.environ`**.

O unico mapa de colunas usado e um mapa ficticio com prefixo `dryrun_`.

## 4. Fluxo da Fase

```
Documento no painel (pendente_integracao)
  -> Usuario clica "Simular Monday"
    -> Sistema monta payload logico (conectores/monday_payload.py)
      -> Sistema monta column_values simuladas
        -> Sistema registra tentativa em integracao_tentativas
          -> Status do documento NAO muda para integrado
            -> Usuario ve resultado no historico
```

## 5. Documentos Aceitos

O dry-run so processa documentos com:

- `status = pendente_integracao`
- `revisado = true`

## 6. Documentos Bloqueados

O dry-run bloqueia documentos com os seguintes status:

- `pendente_revisao` — precisa de revisao humana primeiro.
- `erro_ocr` — erro na extracao OCR, precisa revisao.
- `recebido` — ainda nao processado.
- `processando` — em processamento.

Tambem bloqueia se:

- Documento sem `id`.
- `empresa` vazia.
- `numero_nf` e `chave_acesso` ambos vazios.
- `numero_nf` vazio (para NF-e e NFS-e).
- `chave_acesso` vazia (para NF-e).
- `revisado` nao for `true`.

## 7. Resultado Registrado em integracao_tentativas

| Status | Significado |
|--------|-------------|
| `dry_run_apto` | Documento apto para envio futuro. |
| `dry_run_bloqueado` | Documento bloqueado por uma ou mais regras. |
| `dry_run_erro` | Excecao local durante a execucao do dry-run. |

O campo `destino_externo_id` sera `monday-dryrun-documento-{id}`.

O campo `resposta_resumida` contera a mensagem descritiva do dry-run.

## 8. O Status do Documento Nao Muda

O dry-run **nao altera** o status do documento para `integrado`.

O documento permanece em `pendente_integracao` para que o operador possa:

- Corrigir bloqueios.
- Tentar o dry-run novamente.
- Avancar para o envio real em fase futura.

## 9. Como Validar no Painel

1. Acessar a fila de integracao (`/integracoes`).
2. Localizar documento com status `pendente_integracao`.
3. Clicar em "Simular Monday".
4. Ser redirecionado ao historico de integracoes.
5. Verificar se o status da tentativa e `dry_run_apto` ou `dry_run_bloqueado`.
6. Se bloqueado, ler o campo `erro` para identificar os motivos.

## 10. Como Interpretar dry_run_apto

- O documento passou em todas as validacoes.
- O payload e as column_values foram montadas com sucesso.
- O documento esta pronto para a fase `MONDAY-ENVIO-APROVADO-01`.
- O envio real ainda depende de confirmacao humana.

## 11. Como Interpretar dry_run_bloqueado

- O documento nao passou em uma ou mais validacoes.
- O campo `erro` no historico contem os motivos.
- O operador deve corrigir os bloqueios no painel e tentar novamente.
- Exemplos de bloqueio: empresa vazia, NF ausente, documento nao revisado.

## 12. Riscos Evitados

| Risco | Como o dry-run evita |
|-------|---------------------|
| Envio de documento nao revisado | Bloqueia se `revisado != true`. |
| Envio de documento com dados incompletos | Bloqueia se campos obrigatorios ausentes. |
| Vazamento de token | Nao usa token, nao le `.env`. |
| Vazamento de board_id | Usa apenas mapa ficticio `dryrun_`. |
| Chamada acidental a API | Nao importa `requests`. |
| Mutacao acidental do documento | Nao altera `status` para `integrado`. |

## 13. Proxima Fase: MONDAY-ENVIO-APROVADO-01

A fase `MONDAY-ENVIO-APROVADO-01` devera:

- Usar o mesmo fluxo de validacao do dry-run.
- Adicionar confirmacao humana explicita.
- Chamar a API Monday real com token seguro.
- Atualizar o status do documento para `integrado` apos sucesso.
- Registrar o `item_id` do Monday na tentativa.

## 14. Arquivos da Fase

| Arquivo | Descricao |
|---------|-----------|
| `conectores/monday_dryrun.py` | Modulo de simulacao segura de envio Monday |
| `tests/test_monday_dryrun_01.py` | Testes sem rede, banco ou OCR |
| `docs/integracao/MONDAY-DRYRUN-01_ENVIO_SIMULADO.md` | Esta documentacao |
| `web/app.py` | Rota POST `/integracoes/documentos/<id>/monday-dryrun` |
| `web/templates/integracoes.html` | Botao "Simular Monday" na fila de integracao |
| `web/templates/documento_detalhe.html` | Botao "Simular Monday" no detalhe do documento |
