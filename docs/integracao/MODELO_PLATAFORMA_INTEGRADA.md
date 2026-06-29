# MODELO_PLATAFORMA_INTEGRADA — Template para nova integracao

## 1. Objetivo

Este documento define a estrutura esperada para criar uma nova integracao com plataforma externa no OCR-LEITOR, seguindo o modelo seguro de 4 camadas definido em `CONFIG-INTEGRACAO-SEGURA-01.md`.

Qualquer plataforma que nao seguir este template nao deve ser liberada em producao.

## 2. Estrutura de Arquivos Esperada

Para cada nova plataforma, criar os seguintes arquivos:

```
conectores/<plataforma>_payload.py      # Camada 1: contrato
conectores/<plataforma>_dryrun.py       # Camada 2: dry-run
conectores/<plataforma>_envio.py        # Camada 3: envio
docs/integracao/<PLATAFORMA>-CONTRATO-01.md
docs/integracao/<PLATAFORMA>-DRYRUN-01.md
docs/integracao/<PLATAFORMA>-ENVIO-APROVADO-01.md
tests/test_<plataforma>_payload_01.py
tests/test_<plataforma>_dryrun_01.py
tests/test_<plataforma>_envio_01.py
```

## 3. Funcoes Esperadas no Payload

Arquivo `conectores/<plataforma>_payload.py`:

| Funcao | Descricao |
|--------|-----------|
| `validar_documento_apto_<plataforma>(documento)` | Retorna `(apto, bloqueios, avisos)`. Valida revisao, status, campos obrigatorios. |
| `normalizar_documento_para_<plataforma>(documento)` | Retorna dict padrao com campos normalizados e metadados. |
| `montar_campos_externos_<plataforma>(payload, mapa_colunas)` | Retorna dict no formato esperado pela API externa. |

Regras:
- Nao importa `requests`, `urllib`, `http`.
- Nao usa `os.getenv`, `os.environ`, `.env`.
- Nao contem token, board_id, column_id real ou URL.
- Aceita `mapa_colunas` como parametro (nunca hardcode).

## 4. Funcoes Esperadas no Dry-run

Arquivo `conectores/<plataforma>_dryrun.py`:

| Funcao | Descricao |
|--------|-----------|
| `gerar_dryrun_<plataforma>(documento, mapa_colunas=None)` | Valida, monta payload e campos. Nao chama API. Nao usa token. Nao altera status. |

Regras:
- Nao contem URL de API.
- Nao contem token ou credencial.
- Usa mapa ficticio se nenhum for fornecido.
- Retorna `{"status": "apto"}` ou `{"status": "bloqueado", "bloqueios": [...]}`.
- Nao altera `documentos.status` para `integrado`.

## 5. Funcoes Esperadas no Envio

Arquivo `conectores/<plataforma>_envio.py`:

| Funcao | Descricao |
|--------|-----------|
| `enviar_documento_<plataforma>(documento, token, project_id, mapa_colunas, post_func=None)` | Envia para API externa. |

Regras:
- Recebe token, project_id/board_id e mapa de colunas por parametro (nunca le `.env`).
- Aceita `post_func` ou `client` injetavel para testes sem rede.
- Nao salva credencial em lugar nenhum.
- GraphQL ou REST usa parametros com interpolation segura.
- Retorna sucesso somente apos confirmacao da API externa.
- Em caso de falha, retorna erro sem segredo.

## 6. Helpers na Aplicacao (Rota Flask)

Em `web/app.py`, criar para cada plataforma:

| Helper | Descricao |
|--------|-----------|
| `_config_<plataforma>_envio()` | Le env vars, monta dict com token/project_id/colunas |
| `_obter_integracao_<plataforma>_envio(cliente_id)` | Busca ou cria registro em `integracoes` |
| `_validar_duplicidade_<plataforma>(documento_id)` | Verifica se ja houve envio com sucesso |

Rotas obrigatorias:

| Rota | Metodo | Funcao |
|------|--------|--------|
| `/integracoes/documentos/<id>/<plataforma>-dryrun` | POST | Executa dry-run |
| `/integracoes/documentos/<id>/enviar-<plataforma>` | POST | Envio real com `confirmar=sim` |

## 7. Padrao de Status no Historico

| Status | Significado |
|--------|-------------|
| `<plataforma>_dry_run_apto` | Dry-run: documento apto para envio |
| `<plataforma>_dry_run_bloqueado` | Dry-run: documento bloqueado |
| `<plataforma>_envio_sucesso` | Envio real: sucesso confirmado |
| `<plataforma>_envio_falha` | Envio real: falha na API externa |
| `<plataforma>_envio_bloqueado` | Envio real: configuracao ou documento invalido |

## 8. Padrao de Testes

Cada arquivo de teste deve garantir:

- Nenhuma chamada a API externa.
- Nenhuma conexao MySQL real.
- Nenhuma execucao OCR real.
- Nenhum token real no codigo.
- Nenhuma dependencia de internet.
- Uso de `post_func` ou `client` fake.
- Validacao de bloqueios para documentos invalidos.
- Validacao de sucesso para documentos aptos.
- Validacao de que o modulo nao contem `.env`, `os.getenv`, token, board_id, column_id real.

## 9. Fluxo Minimo para Liberar Plataforma

1. Contrato (payload) criado e testado.
2. Dry-run criado e testado.
3. Envio unitario criado e testado.
4. Historico registrando todos os status.
5. Documentacao das 3 fases criada.
6. Testes sem rede/banco/OCR passando.
7. Pytest completo passando.
8. Tag de versao criada.
9. Checklist `CHECKLIST_NOVA_INTEGRACAO.md` preenchido e aprovado.

## 10. Fora do Escopo deste Template

- Lote ou batch de multiplos documentos.
- Anexo de arquivos.
- Painel de configuracao na UI.
- Criptografia de credenciais.
- Webhook de retorno.
- Configuracao por cliente no banco.

Estes itens sao fases futuras e devem ser tratadas em seus proprios planos.
