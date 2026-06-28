# ADR PLAN-INTEGRACAO-01 - Arquitetura Segura da Futura API de Entrada

## 1. Status da decisao

Status: aceito para planejamento arquitetural.

## 2. Contexto atual do OCR-LEITOR

O OCR-LEITOR opera hoje com fluxo local e controlado. O upload atual salva arquivos para processamento manual posterior, a revisao humana continua obrigatoria e o JSON estruturado gerado pelo pipeline e a base tecnica de integracao do projeto.

Nesta fase nao sera implementada nenhuma API, nenhum endpoint, nenhuma rota Flask, nenhuma alteracao de pipeline, nenhuma alteracao de banco, nenhuma alteracao de OCR e nenhuma alteracao de parser.

## 3. Decisao arquitetural principal

A ordem aprovada do projeto permanece:

1. PLAN-INTEGRACAO-01
2. EXPORT-OCR-01
3. MARKDOWN-OCR-01
4. API-IN-01
5. Integracoes externas futuras

Fica definido que `EXPORT-OCR-01` vem antes de `API-IN-01`.

## 4. Justificativa tecnica

Fechar primeiro a saida validada e mais seguro do que abrir a entrada externa antes do contrato de saida estar estabilizado.

- A exportacao JSON validada precisa estar consolidada antes de aceitar novas entradas externas.
- A fonte oficial de integracao precisa estar previsivel antes de expor qualquer superficie de ingestao.
- O relatorio Markdown sera util para leitura humana futura, mas nao substitui o contrato tecnico oficial.
- Abrir a entrada antes de fechar a saida aumentaria retrabalho, ambiguidade de contrato e risco operacional.

## 5. Decisoes obrigatorias para a futura API-IN-01

### 5.1 Escopo inicial

- A primeira API sera local e controlada.
- A primeira versao nao podera ser uma API publica.
- A implementacao inicial devera operar apenas em ambiente interno e restrito.

### 5.2 Autenticacao futura

- A autenticacao futura recomendada sera por Bearer Token.
- O token devera ser carregado via variavel de ambiente.
- Logs nao podem conter token.

### 5.3 Formato de entrada futura

- A entrada futura inicial sera `multipart/form-data`.
- A primeira versao aceitara somente upload de arquivo binario controlado.
- JSON com URL esta proibido na primeira versao.
- Base64 esta proibido na primeira versao.
- O envio de caminho arbitrario pelo usuario fica permanentemente proibido.

### 5.4 Gravacao e processamento

- `API-IN-01` apenas salvara o arquivo em `input/`.
- `API-IN-01` nao disparara OCR automaticamente.
- `API-IN-01` nao escrevera diretamente no banco.
- `API-IN-01` nao alterara o contrato JSON v1.
- `API-IN-01` nao integrara Monday, Sheets, ERP ou FechaMes.

### 5.5 Resposta e limites iniciais

- A resposta futura recomendada e `HTTP 202 Accepted`.
- O limite inicial recomendado e `10 MB` por arquivo.
- As extensoes iniciais recomendadas sao `.jpg`, `.jpeg` e `.png`.
- PDF ficara proibido nesta primeira API e so podera entrar depois de fase especifica do pipeline.

### 5.6 Seguranca operacional e logs

- Logs nao podem conter token.
- Logs nao podem conter conteudo OCR sensivel.
- Logs nao podem conter dados completos do documento.
- A API futura nao deve aceitar caminho arbitrario em nenhum cenario.

### 5.7 Idempotencia futura

- A idempotencia futura deve considerar hash `SHA-256` e/ou o cabecalho `X-Idempotency-Key`.
- A estrategia final de deduplicacao sera definida somente na fase de implementacao da API.

## 6. Fonte oficial de integracao

- O Markdown sera um relatorio humano futuro, nao a fonte oficial de integracao.
- O JSON estruturado continuara sendo a fonte oficial para integracao.

## 7. Proximas fases recomendadas

1. `EXPORT-OCR-01` - fechar exportacao de JSON validado pelo painel.
2. `MARKDOWN-OCR-01` - gerar relatorio humano derivado do documento validado.
3. `API-IN-01` - implementar a API local e controlada, sem OCR automatico e sem escrita direta no banco.
4. Integracoes externas futuras - somente depois da saida oficial e da entrada controlada estarem estabilizadas.

## 8. Fora do escopo desta fase

- Nenhuma rota `/api` sera criada agora.
- Nenhum endpoint Flask sera criado agora.
- Nenhum Blueprint sera criado agora.
- Nenhuma dependencia sera adicionada agora.
- Nenhum schema de banco sera alterado agora.
- Nenhuma integracao externa sera implementada agora.

## 9. Recomendacoes futuras sem implementacao nesta fase

- Definir codigos de erro da API apenas durante `API-IN-01`.
- Definir estrategia final de armazenamento temporario apenas quando a exportacao oficial estiver concluida.
- Revisar suporte a PDF somente apos a fase especifica do pipeline que tratar esse formato na entrada controlada.
