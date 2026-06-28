# EXPORT-OCR-01 - Exportacao JSON Validada do Documento Revisado

## 1. Objetivo da fase

Implementar a exportacao local, segura e controlada do JSON validado de um documento que ja esteja revisado/aprovado no OCR-LEITOR.

## 2. O que foi implementado

- Camada isolada em `exportacao/json_validado.py`.
- Reaproveitamento do montador oficial `contratos/montador_documento_fiscal_v1.py`.
- Reaproveitamento do validador oficial `contratos/contrato_documento_fiscal_v1.py`.
- Gravacao do arquivo validado em pasta local controlada `exports/json/`.
- Acao manual no painel para exportar o JSON validado a partir da tela do documento.
- Registro seguro da tentativa usando a estrutura ja existente de integracao manual.

## 3. O que nao foi implementado

- Nenhuma API.
- Nenhuma rota `/api`.
- Nenhum webhook.
- Nenhuma integracao com Monday, Sheets, ERP ou FechaMes.
- Nenhuma alteracao de OCR, parser, pipeline ou schema.
- Nenhum Markdown oficial de integracao.
- Nenhum processamento automatico do documento.

## 4. Por que a exportacao vem antes da API

Esta fase fecha primeiro a saida local validada. Assim o projeto prova o contrato oficial de integracao em ambiente controlado antes de abrir superficie de entrada externa. O JSON estruturado validado continua sendo a fonte oficial para integracao.

## 5. Fluxo da exportacao

1. Operador revisa e aprova o documento.
2. Operador aciona manualmente a exportacao no painel.
3. O sistema confere se o documento esta em status seguro para exportar.
4. O payload e montado com o contrato JSON oficial ja existente.
5. O payload e validado pelo validador oficial v1.
6. O arquivo e salvo localmente em `exports/json/`.
7. A tentativa fica registrada com resumo seguro.

## 6. Pasta de saida

- Pasta controlada: `exports/json/`
- Nome de arquivo: `documento_<id>_<timestamp>.json`
- O nome nao usa caminho enviado pelo usuario.
- Nao ha aceite de path externo nem path traversal.

## 7. Status permitidos

- `pendente_integracao`
- `integrado`

Nao exporta documentos em status incompleto, incluindo `recebido`, `processando`, `erro_ocr` e `pendente_revisao`.

## 8. Seguranca aplicada

- Exportacao apenas local.
- Acao apenas manual e controlada.
- Sem processamento automatico.
- Sem escrita direta em banco externo.
- Sem uso de caminho arbitrario do usuario.
- Sem exposicao do conteudo OCR bruto em logs de exportacao.
- Sem token, segredo ou integracao externa.

## 9. Limites

- Mantem o contrato JSON v1 atual sem alteracao.
- Mantem o OCR, parser e pipeline intactos.
- Mantem o schema de banco intacto.
- Mantem `requirements.txt` sem alteracao.
- Mantem Markdown fora do papel de fonte oficial de integracao.

## 10. Como testar

1. Rodar `python -m pytest`.
2. Abrir um documento revisado em status seguro.
3. Acionar `Exportar JSON validado`.
4. Confirmar que o arquivo foi salvo em `exports/json/`.
5. Confirmar que documentos nao revisados ou com status incompleto sao rejeitados.
6. Confirmar que nenhum arquivo proibido foi alterado.

## 11. Proximas fases

1. `MARKDOWN-OCR-01` para gerar relatorio humano derivado do documento validado.
2. `API-IN-01` para entrada local e controlada, sem OCR automatico.
3. Integracoes externas futuras somente depois das fases anteriores.

## 12. Observacoes de escopo

- JSON continua sendo a fonte oficial para integracao.
- Markdown sera apenas relatorio humano em fase futura.
- `API-IN-01` ainda nao foi implementada.
- Monday, Sheets, ERP e FechaMes continuam fora do escopo.
