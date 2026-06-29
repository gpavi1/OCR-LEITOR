# MONDAY-ENVIO-APROVADO-01 — Envio Real Controlado para Monday

## 1. Objetivo da Fase

Permitir o envio real de **1 documento revisado** para Monday.com com confirmacao humana explicita, usando configuracao segura por variaveis de ambiente.

**Nao implementa lote.**
**Nao implementa anexo.**
**Nao altera schema.**

## 2. Fluxo de Envio

```
Documento no painel (pendente_integracao)
  -> Usuario clica "Enviar para Monday"
    -> Confirmacao explicita ("Confirmar envio REAL para Monday?")
      -> Validacao do contrato (documento revisado, apto)
        -> Leitura de config (token, board_id, colunas)
          -> Criacao de item no Monday via GraphQL
            -> Preenchimento de colunas no Monday
              -> Registro de sucesso + status integrado
```

## 3. Exige Confirmacao Humana

O envio real so ocorre se o usuario confirmar explicitamente no formulario.

O campo `confirmar=sim` e obrigatorio no POST.

Sem confirmacao, o sistema exibe warning e nao envia nada.

## 4. Variaveis de Ambiente

As configuracoes sao lidas via `os.getenv` no momento da requisicao:

| Variavel | Descricao |
|----------|-----------|
| `MONDAY_API_TOKEN` | Token de autenticacao da API Monday |
| `MONDAY_BOARD_ID` | ID do board no Monday |
| `MONDAY_COLUMN_EMPRESA` | Column ID para empresa |
| `MONDAY_COLUMN_NUMERO_NF` | Column ID para numero NF |
| `MONDAY_COLUMN_CHAVE_ACESSO` | Column ID para chave de acesso |
| `MONDAY_COLUMN_VENCIMENTO` | Column ID para vencimento |
| `MONDAY_COLUMN_VALOR_TOTAL` | Column ID para valor total |
| `MONDAY_COLUMN_OBSERVACAO` | Column ID para observacao da revisao |

Nenhuma dessas variaveis e salva no banco de dados ou no codigo fonte.

## 5. Sem .env Direto

O modulo `conectores/monday_envio.py` **nao le arquivo `.env`** e **nao usa `os.getenv`**.

A leitura das variaveis e feita exclusivamente pela rota Flask em `web/app.py`, que pode herdar variaveis do ambiente do sistema operacional ou de um arquivo `.env` carregado pelo `python-dotenv` ja existente no projeto (`database/mysql_db.py` faz `load_dotenv()`).

## 6. Token Nao Fica no Banco

A configuracao de integracao do tipo `monday` e registrada na tabela `integracoes` com `config_json = JSON_OBJECT('envio_real', TRUE, 'anexo', FALSE)` — **sem token, sem board_id, sem column_ids**.

As credenciais nunca sao persistidas no banco.

## 7. Sem Lote

Cada envio processa exatamente **1 documento**.

Nao ha selecao multipla, fila de espera ou processamento batch.

O lote sera implementado em fase futura (`MONDAY-LOTE-01`).

## 8. Sem Anexo

O envio nao inclui o arquivo original da nota.

Anexo sera implementado em fase futura (`MONDAY-ANEXO-01`).

## 9. Documentos Aceitos

- `status = pendente_integracao`
- `revisado = true`
- Contrato `validar_documento_apto_monday` retorna `apto_envio = true`

## 10. Anti-Duplicidade

O sistema bloqueia reenvio se:

- `documentos.status = integrado` (ja marcado como integrado).
- Ja existir tentativa com `status = monday_envio_sucesso` e `destino_externo_id` nao nulo na tabela `integracao_tentativas` para o mesmo documento.

Reenvio so e permitido apos acao explicita do operador (ex.: reenfileirar apos falha).

## 11. Sucesso: Item ID e Status Integrado

Em caso de sucesso:

- O `item_id` retornado pelo Monday e salvo em `destino_externo_id` na tentativa.
- O status da tentativa e `monday_envio_sucesso`.
- `documentos.status` e atualizado para `integrado`.

## 12. Falha: Erro Registrado, Status Nao Muda

Em caso de falha:

- O erro e registrado em `integracao_tentativas` com status `monday_envio_falha`.
- `documentos.status` **nao e alterado**.
- O operador pode corrigir e tentar novamente.

## 13. Bloqueio: Configuracao Invalida

Se token, board_id ou colunas estiverem ausentes:

- A tentativa e registrada como `monday_envio_bloqueado`.
- Nenhuma chamada a API Monday e feita.
- O documento nao e alterado.

## 14. Status em integracao_tentativas

| Status | Significado |
|--------|-------------|
| `monday_envio_sucesso` | Item criado e colunas preenchidas no Monday |
| `monday_envio_falha` | Erro na criacao do item ou preenchimento de colunas |
| `monday_envio_bloqueado` | Configuracao ausente ou documento nao apto |

## 15. Como Configurar

1. Definir as variaveis de ambiente no sistema operacional ou no arquivo `.env`:
   ```
   MONDAY_API_TOKEN=seu_token_aqui
   MONDAY_BOARD_ID=seu_board_id_aqui
   MONDAY_COLUMN_EMPRESA=column_id_aqui
   ...
   ```
2. Nao commitar o `.env`.
3. Nao colocar valores reais em arquivos do repositorio.

## 16. Proximas Fases Recomendadas

- `MONDAY-LOTE-01`: envio batch de multiplos documentos.
- `MONDAY-ANEXO-01`: anexo do arquivo original ao item do Monday.

## 17. Arquivos da Fase

| Arquivo | Descricao |
|---------|-----------|
| `conectores/monday_envio.py` | Modulo de envio real para Monday |
| `tests/test_monday_envio_aprovado_01.py` | Testes sem rede, banco ou OCR |
| `docs/integracao/MONDAY-ENVIO-APROVADO-01_ENVIO_REAL_CONTROLADO.md` | Esta documentacao |
| `docs/integracao/MONDAY_CONFIG_EXEMPLO.md` | Exemplo de configuracao |
| `web/app.py` | Rota POST `/integracoes/documentos/<id>/enviar-monday` |
| `web/templates/integracoes.html` | Botao "Enviar para Monday" |
| `web/templates/documento_detalhe.html` | Botao condicional no detalhe |
