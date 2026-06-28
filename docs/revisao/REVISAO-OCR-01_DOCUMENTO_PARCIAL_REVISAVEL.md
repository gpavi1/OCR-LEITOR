# REVISAO-OCR-01 — Documento Parcial Revisável

## 1. Objetivo

Fazer com que documentos com OCR parcial, `erro_ocr` ou `pendente_revisao` fiquem claramente visíveis no painel como documentos que precisam de revisão humana, em vez de ficarem escondidos como erro técnico.

## 2. Motivo da fase

No teste real, o pipeline S1 gerou JSON com status `parcial` e moveu o arquivo para `erro/`. Embora o documento tenha sido registrado no banco como `pendente_revisao`, a interface mostrava o status técnico bruto, sem indicar visualmente que aquele documento aguarda revisão humana. Isso prejudica a operação.

## 3. Comportamento esperado

- Documentos com `pendente_revisao` ou `erro_ocr` aparecem com badge âmbar "Precisa revisão".
- A tela de detalhe mostra um alerta visual: "Este documento precisa de revisão humana."
- O formulário de correção de campos e o botão de revisão continuam disponíveis.
- O JSON de saída e o texto OCR continuam acessíveis.

## 4. Escopo aplicado

### web/app.py

- Adicionado dicionário `STATUS_LABEL` com mapeamento de status técnicos para labels amigáveis.
- Adicionado conjunto `STATUS_PRECISA_REVISAO` com status que indicam necessidade de revisão.
- Adicionada função `status_label(status)` para lookup.
- Adicionado `@app.context_processor` para injetar `status_label` e `precisa_revisao` em todos os templates.

### web/templates/documentos.html

- Status na tabela agora usa `{{ status_label(doc.status) }}` em vez do raw `{{ doc.status }}`.
- Badge ganha classe adicional `needs-review` quando o documento precisa de revisão.

### web/templates/documento_detalhe.html

- Adicionado alerta no topo: "Este documento precisa de revisão humana."
- Status agora usa label amigável via `status_label()`.

### web/static/style.css

- Seção `/* REVISAO-OCR-01 — Documento parcial revisável */` com:
  - `.needs-review`: badge âmbar para status de revisão.
  - `.review-alert`: alerta discreto com ícone para documentos que precisam revisão.
  - `.review-ok` e `.review-note`: estilos existentes mantidos.

## 5. O que não mudou

- OCR/parser/core (`src/`)
- `ocr_pipeline_s1.py`
- Banco de dados / `schema.sql`
- Requirements
- Conectores
- Monday.com
- FechaMes

## 6. Segurança

- Nenhuma aprovação automática de documento.
- Nenhuma integração automática.
- Nenhuma alteração fiscal.
- Nenhuma alteração de schema.
- Nenhuma movimentação manual de arquivos.
- Nenhuma rota nova exposta.

## 7. Como testar

1. Enviar um documento pelo painel em `/upload`.
2. Clicar em "Processar arquivos enviados".
3. Acessar `/documentos`.
4. Verificar que o documento parcial aparece com badge "Precisa revisão" (âmbar).
5. Abrir o detalhe do documento.
6. Verificar alerta "Este documento precisa de revisão humana."
7. Revisar campos e marcar como revisado.
8. Confirmar que `git status` exibe apenas os arquivos esperados.

## 8. Próxima fase sugerida

**REVISAO-OCR-02** — Melhorar formulário de revisão e aprovação dos campos extraídos.
