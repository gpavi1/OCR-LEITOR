# CONFIG-INTEGRACAO-SEGURA-01 — Modelo seguro de configuracao de integracoes

## 1. Contexto

O OCR-LEITOR ja possui integracao Monday validada com fluxo completo:

```
OCR -> revisao humana -> pendente_integracao -> dry-run
  -> envio real controlado -> status integrado -> historico
```

O objetivo desta fase e padronizar o modelo seguro para integracoes futuras (Monday, Google Sheets, ERPs, APIs proprias e outras plataformas externas), protegendo credenciais, historico, logs e codigo versionado.

## 2. Modelo de 4 Camadas

Toda integracao deve seguir 4 camadas distintas, cada uma com responsabilidade e nivel de acesso definidos.

```
OCR / Revisao Humana
       |
       v
Camada 1: Contrato / Payload (puro, sem estado)
       |
       v
Camada 2: Dry-run (validacao sem rede, sem credencial)
       |
       v
Camada 3: Envio real controlado (recebe credencial por parametro)
       |
       v
Camada 4: Aplicacao / Rota (le env vars, exige confirmacao humana)
       |
       v
Historico + Status integrado
```

### Camada 1: Contrato interno / Payload

- Arquivo: `conectores/<plataforma>_payload.py`
- Puro, sem rede, sem `os.getenv`, sem `.env`, sem `requests`.
- Recebe documento e mapeamento de colunas por parametro.
- Valida status, revisao humana e campos obrigatorios.
- Nao contem token, board_id, column_id real ou URL de API.

### Camada 2: Dry-run

- Arquivo: `conectores/<plataforma>_dryrun.py`
- Usa o contrato da camada 1 para montar payload e valores simulados.
- Nao usa credencial.
- Nao chama API externa.
- Nao altera status do documento para `integrado`.
- Registra resultado em `integracao_tentativas` (apto/bloqueado/erro).

### Camada 3: Envio real controlado

- Arquivo: `conectores/<plataforma>_envio.py`
- Recebe token, board_id/project_id, base_url e mapa de colunas por parametro.
- Nao le `.env` diretamente.
- Nao salva credencial em lugar nenhum.
- Usa `post_func` ou `client` injetavel para testes (zero rede).
- GraphQL via variables (nunca string interpolation).
- So retorna sucesso apos confirmacao explicita da API externa.

### Camada 4: Aplicacao / Rota

- Arquivo: `web/app.py`
- Le variaveis de ambiente controladas via helper dedicado.
- Exige confirmacao humana (`confirmar=sim`).
- Registra historico em `integracao_tentativas` sem segredo.
- Marca documento como `integrado` somente apos sucesso externo confirmado.
- Nunca grava token ou credencial no banco, erro, `resposta_resumida` ou logs.

## 3. Separacao de Responsabilidades

| Componente | Onde fica | Contem credencial? |
|------------|-----------|--------------------|
| Contrato interno | `conectores/*_payload.py` | Nao |
| Mapeamento externo | Env vars (`PLATAFORMA_COLUMN_*`) | Nao |
| Credenciais | Env vars (`PLATAFORMA_API_TOKEN`) | Sim |
| Execucao | `conectores/*_envio.py` | Recebe por parametro |
| Historico | `integracao_tentativas` | Nao (sanitizado) |
| Config da integracao | `integracoes.config_json` | Apenas metadados booleanos |

## 4. Padrao de Variaveis de Ambiente

Toda plataforma deve seguir este esquema de nomenclatura:

| Variavel | Descricao | Exemplo ficticio |
|----------|-----------|------------------|
| `PLATAFORMA_API_TOKEN` | Token de autenticacao | `PLATAFORMA_API_TOKEN="NAO_COLE_TOKEN_REAL_AQUI"` |
| `PLATAFORMA_BOARD_ID` | ID do board/projeto/base | `PLATAFORMA_BOARD_ID="board_exemplo_falso"` |
| `PLATAFORMA_BASE_URL` | URL da API (se aplicavel) | `PLATAFORMA_BASE_URL="https://api.exemplo.falso/v1"` |
| `PLATAFORMA_COLUMN_EMPRESA` | Coluna para empresa | `PLATAFORMA_COLUMN_EMPRESA="col_empresa_exemplo"` |
| `PLATAFORMA_COLUMN_NUMERO_NF` | Coluna para numero NF | `PLATAFORMA_COLUMN_NUMERO_NF="col_nf_exemplo"` |
| `PLATAFORMA_COLUMN_CHAVE_ACESSO` | Coluna para chave de acesso | `PLATAFORMA_COLUMN_CHAVE_ACESSO="col_chave_exemplo"` |
| `PLATAFORMA_COLUMN_VENCIMENTO` | Coluna para vencimento | `PLATAFORMA_COLUMN_VENCIMENTO="col_venc_exemplo"` |
| `PLATAFORMA_COLUMN_VALOR_TOTAL` | Coluna para valor total | `PLATAFORMA_COLUMN_VALOR_TOTAL="col_valor_exemplo"` |
| `PLATAFORMA_COLUMN_OBSERVACAO` | Coluna para observacao | `PLATAFORMA_COLUMN_OBSERVACAO="col_obs_exemplo"` |

Os valores acima sao **ficticios e nao funcionam**. Substituir `PLATAFORMA` pelo nome real da plataforma (ex: `MONDAY`, `GOOGLE_SHEETS`, `ERP_X`).

## 5. Regras Inviolaveis

1. Token nunca entra no Git.
2. Token nunca entra em documentacao real.
3. Token nunca entra em CHANGELOG.
4. Token nunca entra em logs.
5. Token nunca entra em banco.
6. Token nunca entra em `integracao_tentativas.erro`.
7. Token nunca entra em `integracao_tentativas.resposta_resumida`.
8. Token nunca entra no chat.
9. IDs externos (board, colunas) nunca sao hardcoded no conector.
10. Dry-run deve existir antes do envio real.
11. Status so muda para `integrado` apos sucesso externo confirmado.
12. Falha externa nunca marca como `integrado`.
13. Envio unitario vem antes de lote.
14. Anexo e fase separada do envio.
15. Plataforma nova precisa passar pelo checklist antes de producao.

## 6. Historico Seguro

O historico em `integracao_tentativas` pode conter:

| Campo | Permitido | Proibido |
|-------|-----------|----------|
| `status` | `sucesso`, `falha`, `bloqueado`, `dry_run_apto` etc. | N/A |
| `destino_externo_id` | ID do item criado na plataforma | Token, API key |
| `resposta_resumida` | Mensagem descritiva sem segredo | Token, header Authorization, payload de autenticacao |
| `erro` | Mensagem de erro sanitizada | Token, resposta bruta com segredo |

## 7. Antiduplicidade

- Documento com status `integrado` nao deve ser reenviado.
- Tentativa previa com `status = <plataforma>_envio_sucesso` e `destino_externo_id` nao nulo bloqueia reenvio.
- Reenvio so e permitido apos acao explicita do operador (ex.: reenfileirar apos falha).

## 8. Escopo Futuro (nao implementar agora)

- Banco de configuracao por cliente (armazenar mapeamento de colunas sem token).
- Painel de configuracao na UI para vincular plataformas sem editar `.env`.
- Criptografia de credenciais em repouso.
- Envio em lote.
- Anexo de arquivos.
- Webhook de retorno da plataforma.
