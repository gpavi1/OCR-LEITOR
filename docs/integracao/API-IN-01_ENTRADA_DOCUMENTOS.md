# API-IN-01 - Entrada Controlada de Documentos

## 1. Objetivo da fase

Criar uma API local e controlada para receber documentos de forma autenticada, limitada e segura, salvando o arquivo recebido apenas em `input/`.

## 2. O que foi implementado

- Endpoint `POST /api/v1/documentos/entrada`.
- Autenticacao por `Authorization: Bearer <token>`.
- Token esperado lido de `OCR_API_TOKEN`.
- Entrada exclusiva por `multipart/form-data`.
- Campo obrigatorio `documento`.
- Salvamento local em `input/`.
- Calculo de hash `SHA-256` do arquivo recebido.
- Retorno `HTTP 202 Accepted` quando o arquivo e recebido com sucesso.

## 3. O que nao foi implementado

- Processamento OCR automatico.
- Parser automatico.
- Revisao automatica.
- Exportacao JSON automatica.
- Geracao Markdown automatica.
- Integracao com Monday, Sheets, ERP ou FechaMes.
- Alteracao de banco, schema, contrato JSON v1 ou dependencias.

## 4. Por que a API e local/controlada

A API-IN-01 existe apenas para entrada controlada de arquivos. Ela nao abre fluxo publico sem autenticacao e nao executa processamento. O operador continua responsavel por acionar o processamento manual pelo painel.

## 5. Autenticacao Bearer Token

A chamada deve enviar:

```http
Authorization: Bearer <token>
```

O token esperado vem da variavel de ambiente `OCR_API_TOKEN`. A comparacao e feita com `hmac.compare_digest`.

## 6. Configuracao de OCR_API_TOKEN

Defina `OCR_API_TOKEN` no ambiente local de execucao antes de iniciar o painel/API. Nao editar `.env`, nao commitar segredo e nao usar token fixo no codigo.

## 7. Formato da requisicao

```http
POST /api/v1/documentos/entrada
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

Campo obrigatorio:

- `documento`: arquivo binario.

JSON com URL, base64, download remoto e path local enviado pelo cliente continuam proibidos.

## 8. Formato da resposta

Resposta de sucesso:

```json
{
  "ok": true,
  "status": "recebido",
  "fluxo": "aguardando_processamento_manual",
  "processamento_automatico": false,
  "arquivo_nome": "nome_seguro.jpg",
  "hash_sha256": "...",
  "proxima_acao": "processar_manual_pelo_painel"
}
```

## 9. Extensoes permitidas

Nesta fase a API aceita apenas:

- `.jpg`
- `.jpeg`
- `.png`

PDF fica fora da API-IN-01.

## 10. Limite de tamanho

O limite inicial e `10 MB` por arquivo.

## 11. Seguranca aplicada

- Bearer Token obrigatorio.
- `OCR_API_TOKEN` obrigatorio no ambiente.
- Nome de arquivo sanitizado.
- Sem aceite de caminho arbitrario do usuario.
- Sem path traversal.
- Sem JSON com URL.
- Sem base64.
- Sem download remoto.
- Sem retorno ou log de token.
- Sem OCR bruto ou dados fiscais em resposta.

## 12. Idempotencia minima

A API calcula e retorna o hash `SHA-256` do arquivo. O header `X-Idempotency-Key` pode ser enviado, mas nesta fase nao ha persistencia de idempotencia, tabela nova ou dependencia externa.

## 13. Logs seguros

Quando houver logs operacionais, eles devem ser limitados a data/hora, status, nome seguro, hash e origem geral da requisicao. Token, conteudo de arquivo, OCR bruto e dados fiscais completos sao proibidos em logs.

## 14. Processamento automatico proibido

API-IN-01 apenas salva o arquivo em `input/`. O processamento continua manual pelo painel.

## 15. Integracao externa proibida

Monday, Sheets, ERP e FechaMes continuam fora do escopo. A API nao escreve no banco do FechaMes e nao envia dados para sistemas externos.

## 16. Proximas fases

- Recomendacao futura: persistencia de idempotencia com hash e/ou `X-Idempotency-Key`, sem alterar esta fase.
- Recomendacao futura: integracoes externas somente depois da entrada controlada estar estabilizada.

## 17. Relacao com JSON e Markdown

- JSON validado continua sendo a saida oficial para integracao.
- Markdown continua sendo relatorio humano.
- OCR, parser e core nao foram alterados.
