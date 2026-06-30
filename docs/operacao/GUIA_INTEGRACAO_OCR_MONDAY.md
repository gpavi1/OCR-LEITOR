# Guia de Integração OCR-LEITOR + Monday

## Objetivo

Explicar como configurar o OCR-LEITOR para enviar documentos revisados ao Monday.

---

## Pré-requisitos

- OCR-LEITOR instalado e funcionando
- Painel web operacional (http://127.0.0.1:5000)
- MySQL rodando
- Documento revisado no sistema (status `pendente_integracao`)
- Conta Monday com permissão de API
- Token Monday gerado com segurança
- Board ID do quadro Monday
- IDs das colunas do board

---

## Variáveis necessárias

| Variável | Descrição | Obrigatória |
|----------|-----------|-------------|
| `MONDAY_API_TOKEN` | Token da API Monday | Sim |
| `MONDAY_BOARD_ID` | ID do quadro Monday | Sim |
| `MONDAY_COLUMN_EMPRESA` | Coluna da empresa/fornecedor | Sim |
| `MONDAY_COLUMN_NUMERO_NF` | Coluna do número da NF | Sim |
| `MONDAY_COLUMN_CHAVE_ACESSO` | Coluna da chave de acesso | Sim |
| `MONDAY_COLUMN_VENCIMENTO` | Coluna do vencimento | Sim |
| `MONDAY_COLUMN_VALOR_TOTAL` | Coluna do valor total | Sim |
| `MONDAY_COLUMN_OBSERVACAO` | Coluna de observações | Opcional |

Configure todas no arquivo `.env` na raiz do projeto.

---

## Fluxo seguro

1. **Configurar variáveis** — editar `.env` com os valores corretos
2. **Reiniciar o painel web** — fechar e abrir novamente
3. **Abrir Config** — acessar `/integracoes/configuracao` e validar status
4. **Revisar documento** — conferir campos extraídos no detalhe do documento
5. **Simular Monday** — usar o botão "Simular Monday" (dry-run) antes do envio real
6. **Conferir histórico** — verificar o resultado da simulação
7. **Enviar real** — usar o botão "Enviar para Monday" somente se a simulação foi bem-sucedida
8. **Conferir no Monday** — verificar se o item foi criado no board

---

## Segurança

- **Nunca** commitar o arquivo `.env` com tokens ou senhas
- **Nunca** colar o token Monday em chat, e-mail ou documentação
- **Nunca** imprimir o token em logs ou na tela
- **Não** usar token de produção em ambiente de teste
- **Revogar** o token imediatamente se houver suspeita de vazamento
- **Manter** o ambiente local isolado da internet pública sempre que possível

---

## Diagnóstico

| Problema | Causa possível | Ação |
|----------|---------------|------|
| Variável aparece AUSENTE | Variável não definida no `.env` | Adicionar a variável e reiniciar o painel |
| Variável aparece PLACEHOLDER | Valor ainda é o placeholder padrão | Substituir pelo valor real |
| Dry-run bloqueia | Documento não atende aos critérios | Verificar se o documento está revisado |
| Envio real falha | Token, Board ID ou colunas incorretos | Verificar valores no `.env` |
| Erro no histórico | Falha de comunicação com API Monday | Checar conectividade e token |

---

## O que esta fase não faz

- Não salva token pelo painel web
- Não cria integração com Google Sheets
- Não cria integração com ERP
- Não envia anexo para o Monday
- Não altera banco de dados
- Não altera OCR ou parser
