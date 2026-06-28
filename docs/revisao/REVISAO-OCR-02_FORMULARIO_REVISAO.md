# REVISAO-OCR-02 — Formulário de Revisão dos Campos Extraídos

## 1. Objetivo

Melhorar a tela de revisão para que o operador consiga conferir, corrigir e aprovar os campos extraídos de forma clara, segura e profissional.

## 2. Motivo da fase

Depois do upload e do processamento manual, o maior valor operacional é permitir a revisão clara dos documentos parciais. A tela precisa indicar com precisão o que veio preenchido, o que ficou em branco e qual é a próxima ação humana.

## 3. O que foi melhorado

- Blocos visuais de revisão organizados por função.
- Destaque de campos ausentes ou pendentes.
- Status de revisão mais claro na própria tela de detalhe.
- Área de observação separada e legível.
- Ação de aprovação mais compreensível e explícita.

## 4. O que não mudou

- OCR/parser/core.
- `ocr_pipeline_s1.py`.
- Parser.
- Banco de dados / `schema.sql`.
- Requirements.
- Contratos JSON.
- Conectores.
- Monday.
- FechaMes.

## 5. Segurança

- Sem aprovação automática.
- Sem mudança fiscal.
- Sem alteração de schema.
- Sem integração externa.
- Sem escrita no FechaMes.
- Sem alteração do pipeline OCR.

## 6. Como testar

1. Iniciar o painel.
2. Enviar documento.
3. Processar arquivos enviados.
4. Abrir `/documentos`.
5. Abrir um documento parcial.
6. Conferir os campos extraídos.
7. Preencher ou corrigir os campos existentes.
8. Salvar a revisão.
9. Confirmar o status esperado no painel.
10. Conferir que o Git permanece limpo após commit.

## 7. Próxima fase sugerida

**EXPORT-OCR-01** — Exportar JSON validado pelo painel.
