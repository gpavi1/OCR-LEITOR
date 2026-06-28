# MARKDOWN-OCR-01 - Relatorio Markdown Humano do Documento Revisado

## 1. Objetivo da fase

Gerar um relatorio Markdown local, manual e seguro para leitura humana, derivado do JSON oficial validado de um documento revisado/aprovado.

## 2. O que foi implementado

- Camada isolada em `exportacao/markdown_relatorio.py`.
- Reaproveitamento da camada de `EXPORT-OCR-01` para obter o payload JSON validado.
- Geracao do relatorio Markdown em `exports/markdown/`.
- Acao manual minima no painel para gerar o relatorio.
- Registro seguro da tentativa usando a estrutura manual ja existente.

## 3. O que nao foi implementado

- Nenhuma API.
- Nenhuma rota `/api`.
- Nenhum endpoint publico.
- Nenhuma integracao com Monday, Sheets, ERP ou FechaMes.
- Nenhuma alteracao de OCR, parser, core ou pipeline.
- Nenhuma alteracao de banco, schema ou requirements.
- Nenhuma substituicao do JSON oficial por Markdown.

## 4. Por que Markdown vem depois do JSON validado

O relatorio humano so passa a fazer sentido depois que a saida oficial do documento ja esta validada. Nesta ordem, o Markdown apenas apresenta para leitura e auditoria os dados seguros do payload oficial, sem virar contrato de integracao.

## 5. Fluxo da geracao Markdown

1. Operador revisa e aprova o documento.
2. Operador aciona manualmente a geracao no painel.
3. O sistema valida se o documento esta em status seguro.
4. O payload JSON oficial validado e obtido pela camada de exportacao existente.
5. O Markdown e montado a partir desse payload validado.
6. O arquivo e salvo localmente em `exports/markdown/`.

## 6. Pasta de saida

- Pasta controlada: `exports/markdown/`
- Nome de arquivo: `documento_<id>_<timestamp>.md`
- Sem uso de caminho enviado pelo usuario.
- Sem path externo e sem path traversal.

## 7. Status permitidos

- `pendente_integracao`
- `integrado`

Documentos em `recebido`, `processando`, `erro_ocr` e `pendente_revisao` continuam bloqueados para esta geracao.

## 8. Seguranca aplicada

- Markdown gerado apenas localmente.
- Acao apenas manual e controlada.
- JSON continua sendo a fonte oficial para integracao.
- Markdown e apenas relatorio humano e auditavel.
- Sem OCR bruto completo por padrao.
- Sem integracao externa.
- Sem alteracao de OCR, parser ou core.

## 9. Limites

- Nao altera o contrato JSON v1.
- Nao altera schema de banco.
- Nao adiciona dependencias.
- Nao cria API-IN-01.
- Nao substitui a exportacao JSON validada.

## 10. Como testar

1. Rodar `python -m pytest`.
2. Abrir um documento revisado em status seguro.
3. Acionar `Gerar relatorio Markdown`.
4. Confirmar que o arquivo foi salvo em `exports/markdown/`.
5. Confirmar que o topo do arquivo informa que o JSON validado continua sendo a fonte oficial.
6. Confirmar que documentos incompletos continuam bloqueados.

## 11. Proximas fases

1. `API-IN-01` para entrada local e controlada.
2. Integracoes externas futuras somente apos as fases locais estarem estabilizadas.

## 12. Observacoes de escopo

- JSON e a fonte oficial para integracao.
- Markdown e apenas relatorio humano/auditavel.
- `API-IN-01` ainda nao foi implementada.
- Monday, Sheets, ERP e FechaMes continuam fora do escopo.
- OCR, parser e core nao foram alterados.
