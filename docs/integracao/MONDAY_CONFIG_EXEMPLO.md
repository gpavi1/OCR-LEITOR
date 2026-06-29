# MONDAY_CONFIG_EXEMPLO — Exemplo de Configuracao para Envio Real

## Variaveis de Ambiente

As configuracoes do Monday devem ser definidas como variaveis de ambiente no sistema operacional ou em um arquivo `.env` local (que **nunca deve ser commitado**).

## Exemplo com Valores Ficticios

```bash
# Token de API do Monday (NUNCA compartilhar)
MONDAY_API_TOKEN=exemplo_token_falso_123456

# ID do board no Monday
MONDAY_BOARD_ID=exemplo_board_falso_987654

# Column IDs (obter no Monday via API GraphQL -> boards -> columns)
MONDAY_COLUMN_EMPRESA=text_empresa_exemplo
MONDAY_COLUMN_NUMERO_NF=text_nf_exemplo
MONDAY_COLUMN_CHAVE_ACESSO=text_chave_exemplo
MONDAY_COLUMN_VENCIMENTO=date_vencimento_exemplo
MONDAY_COLUMN_VALOR_TOTAL=numbers_valor_exemplo
MONDAY_COLUMN_OBSERVACAO=text_obs_exemplo
```

Os valores acima sao **ficticios e nao funcionam**.

## Como Obter os Column IDs

1. Acessar a API GraphQL do Monday com uma query:
   ```graphql
   query {
     boards(ids: SEU_BOARD_ID) {
       columns {
         id
         title
         type
       }
     }
   }
   ```
2. Anotar os `id` de cada coluna desejada.
3. Configurar nas variaveis de ambiente.

## Regras de Seguranca

- **Nunca** colocar valores reais em arquivos do repositorio.
- **Nunca** commitar o arquivo `.env`.
- **Nunca** compartilhar o token ou board_id.
- O `.env` ja esta no `.gitignore` do projeto.
- As variaveis devem ser configuradas apenas no ambiente local da maquina que executara o OCR-LEITOR.

## Arquivo .env (Nao Commitar)

Criar um arquivo `.env` na raiz do projeto com o conteudo acima (valores reais) e manter fora do Git.

O projeto ja carrega automaticamente o `.env` via `python-dotenv` na inicializacao do modulo `database/mysql_db.py`.
