# CONTRATO-MONDAY-01 — Contrato Seguro de Payload Monday a partir de Documento Revisado

## 1. Objetivo da Fase

Criar uma camada pura, testavel e sem rede para transformar um documento revisado do OCR-LEITOR em um payload logico para futura integracao Monday.

Esta fase **nao envia nada para Monday** e **nao chama nenhuma API externa**.

## 2. Por que esta fase nao envia para Monday

O fluxo seguro definido para o projeto exige que:

1. O documento passe por revisao humana obrigatoria.
2. O status seja `pendente_integracao` (dado validado e aprovado).
3. Somente entao o payload logico pode ser montado.
4. A fase seguinte (`MONDAY-DRYRUN-01`) validara o payload sem criar items reais.
5. Somente apos dry-run bem-sucedido e confirmacao humana o envio real ocorrera.

Pular qualquer etapa quebraria a seguranca operacional.

## 3. Fluxo Seguro

```
nota/imagem
  -> OCR preenche campos
    -> humano revisa e corrige
      -> status = pendente_integracao (dado validado)
        -> CONTRATO-MONDAY-01: payload logico montado
          -> MONDAY-DRYRUN-01: validacao sem criar item (futuro)
            -> confirmacao humana
              -> envio real para Monday (futuro)
```

## 4. Campos usados do banco

O modulo `conectores/monday_payload.py` recebe um dicionario representando uma linha da tabela `documentos` com os seguintes campos esperados:

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `id` | int | sim | Identificador unico do documento |
| `cliente_id` | int | nao | Identificador do cliente |
| `arquivo_nome` | str | nao | Nome do arquivo original |
| `empresa` | str | sim | Nome da empresa/razao social |
| `numero_nf` | str | condicional | Numero da nota fiscal |
| `chave_acesso` | str | condicional | Chave de acesso de 44 digitos |
| `vencimento` | str | nao | Data de vencimento (dd/mm/yyyy ou yyyy-mm-dd) |
| `valor_total` | str/float/Decimal | nao | Valor total do documento |
| `status` | str | sim | Status atual no fluxo |
| `revisado` | bool | sim | Indicador de revisao humana |
| `revisado_por` | str | nao | Operador que revisou |
| `revisado_em` | str | nao | Data/hora da revisao |
| `observacao_revisao` | str | nao | Anotacao do revisor |
| `json_path` | str | nao | Caminho do JSON de extracao |
| `tipo_documento` | str | nao | Tipo (NF-e, NFS-e, etc.) |

## 5. Regras de Bloqueio

O documento **nao podera ser enviado** para Monday se qualquer condicao abaixo for verdadeira:

- Documento sem `id`.
- `status` diferente de `pendente_integracao`.
- `revisado` nao for `true`.
- `empresa` vazia.
- `numero_nf` e `chave_acesso` ambos vazios.
- `status` igual a `pendente_revisao`, `erro_ocr`, `recebido` ou `processando`.

Regras especificas para NF-e padrao (nao NFS-e):

- `numero_nf` vazio e `chave_acesso` presente: bloqueia.
- `chave_acesso` vazia e `numero_nf` presente: bloqueia.

Regras especificas para NFS-e:

- `numero_nf` vazio: bloqueia.
- `chave_acesso` vazia: **nao bloqueia** (apenas aviso).

## 6. Regras de Aviso (sem bloquear)

As condicoes abaixo geram avisos no payload mas **nao impedem o envio**:

- `valor_total` vazio.
- `vencimento` vazio.
- `chave_acesso` vazia em documento do tipo NFS-e/NFSE/NFS/servico.
- `observacao_revisao` vazia.
- `json_path` vazio.

## 7. Tratamento de NFS-e sem Chave

Documentos do tipo `NFS-e`, `NFSE`, `NFS` ou `servico` podem nao ter chave de acesso. Nessecaso:

- A ausencia de chave nao bloqueia o envio.
- A ausencia de chave gera um aviso no payload.
- O numero NF continua obrigatorio.

## 8. Como o Payload Logico sera usado no Futuro

O payload gerado por `normalizar_documento_para_monday()` contem:

```json
{
  "versao": "monday_payload_revisado.v1",
  "origem": "ocr-leitor.documentos",
  "documento_id": 123,
  "cliente_id": 1,
  "item_name": "EMPRESA TESTE LTDA - NF 000123",
  "apto_envio": true,
  "bloqueios": [],
  "avisos": [],
  "campos": {
    "empresa": "EMPRESA TESTE LTDA",
    "numero_nf": "000123",
    "chave_acesso": "351111...",
    "vencimento": "2026-07-10",
    "valor_total": "150.00",
    ...
  },
  "metadados": {
    "integracao": "monday",
    "envio_real": false,
    "requer_confirmacao_humana": true
  }
}
```

Na fase **MONDAY-DRYRUN-01**, este payload sera validado sem criar item no Monday.
Na fase **MONDAY-ENVIO-APROVADO-01**, o payload sera convertido em `column_values` via `montar_column_values_monday()` e enviado apos confirmacao humana.

## 9. Como o Mapa de Colunas Deve ser Fornecido em Fase Futura

A funcao `montar_column_values_monday(payload, mapa_colunas)` recebe o mapa de colunas como parametro injetado. O mapa deve ser um dicionario no formato:

```python
{
    "empresa": "col_empresa",       # column_id real do board Monday
    "numero_nf": "col_nf",          # column_id real do board Monday
    "chave_acesso": "col_chave",    # column_id real do board Monday
    "vencimento": "col_vencimento", # column_id real do board Monday
    "valor_total": "col_valor",     # column_id real do board Monday
    "observacao_revisao": "col_obs" # column_id real do board Monday
}
```

O mapa **nunca deve estar hardcoded** no codigo do modulo. Ele deve ser:

- Carregado de configuracao segura (env var ou arquivo fora do repositorio).
- Injetado pelo chamador (ex.: uma futura rota Flask).
- Testado com mapa fake em testes.

## 10. Por que nao usar token/board/column real agora

- Esta fase trata apenas do **contrato logico dos dados**.
- Incluir token, board_id ou column_id real agora introduziria risco de vazamento acidental.
- O modulo `conectores/monday_payload.py` e **puro e sem estado** — nao possui configuracoes nem depende de ambiente.
- A configuracao real sera introduzida apenas na fase **MONDAY-DRYRUN-01** ou posterior.

## 11. Codigo Antigo de Monday (ocr_to_monday.py, src/monday_api.py)

O projeto possui codigo legado de integracao Monday:

- `ocr_to_monday.py`: script que processa OCR e envia direto para Monday — **sem revisao humana obrigatoria**. Nao deve ser chamado como fluxo principal.
- `src/monday_api.py`: modulo com classes `MondayAPI`, `MondayBatch`, `MondayColumnTypes` para chamadas GraphQL ao Monday. Reutilizavel em fases futuras, mas **nao deve ser importado por esta fase** porque esta fase nao faz chamada de rede.

**Nesta fase, todo o codigo legado permanece intocado.** A fase `CONTRATO-MONDAY-01` e independente e nao depende de `src/monday_api.py` ou `ocr_to_monday.py`.

## 12. Proxima Fase Recomendada: MONDAY-DRYRUN-01

A fase `MONDAY-DRYRUN-01` devera:

- Usar `normalizar_documento_para_monday()` para obter o payload logico.
- Validar o payload sem criar item no Monday.
- Exibir o resultado para o operador no painel.
- Confirmar que o payload pode ser enviado.
- Nao enviar nada para Monday ate que o operador confirme.

## 13. Seguranca

- `conectores/monday_payload.py` nao importa `requests`, `urllib` ou `http`.
- Nao le `.env`.
- Nao usa `os.getenv` ou `os.environ`.
- Nao contem token, board_id, api_key ou column_id real.
- Nao abre arquivos (exceto o proprio codigo fonte).
- Nao conecta MySQL.
- Nao executa OCR real.
- Nao exige internet.

## 14. Arquivos da Fase

| Arquivo | Descricao |
|---------|-----------|
| `conectores/monday_payload.py` | Modulo de transformacao de dados puro |
| `tests/test_contrato_monday_01.py` | Testes sem rede, banco ou OCR |
| `docs/integracao/CONTRATO-MONDAY-01_PAYLOAD_REVISADO.md` | Esta documentacao |
