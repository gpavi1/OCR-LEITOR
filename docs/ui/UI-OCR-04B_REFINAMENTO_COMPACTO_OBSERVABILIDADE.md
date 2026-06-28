# UI-OCR-04B — Refinamento compacto estilo observabilidade

## Objetivo
Reduzir o exagero visual introduzido na UI-OCR-04, deixando o painel mais compacto, discreto e profissional, com aparência de observabilidade. Nenhuma lógica de template foi alterada — apenas ajustes de CSS e títulos.

## O que mudou

### web/templates/documentos.html
- `Visão geral do OCR` → `Visão geral` (título mais enxuto)
- `Acompanhe a fila de processamento, revise documentos e gerencie integrações.` → `Fila, revisão e status dos documentos.` (subtítulo mais direto)

### web/static/style.css — Seção `/* UI-OCR-04B — Refinamento compacto estilo observabilidade */`

| Aspecto | Antes (UI-OCR-04) | Depois (UI-OCR-04B) |
|---|---|---|
| Largura da sidebar | `260px` | `220px` |
| Padding da sidebar | `20px` | `14px` |
| Tamanho do brand | `44px` / `16px` | `36px` / `14px` |
| Sombra do brand | `box-shadow` com glow verde | `box-shadow: none` |
| Nav link padding | `10px 16px` | `6px 10px` |
| Nav link ativo | `rgba(34, 197, 94, ...)` verde | `rgba(56, 189, 248, ...)` azul |
| `h1` | `font-size: 32px` | `font-size: 24px` |
| Topbar padding | `16px 0 20px` / `margin: 0 0 24px` | `8px 0 10px` / `margin: 0 0 14px` |
| Action card padding | `14px 18px` | `10px 12px` |
| Metric card padding | `14px 16px` | `10px 12px` |
| Panel padding | `16px 20px` | `12px 14px` |
| Table cell padding | `12px 14px` | `7px 8px` / `6px 8px` |
| Box shadows | Presentes em cards, panels, botões | `box-shadow: none` |
| Transform em botões | `translateY(-1px)` no hover | `transform: none` |
| Pseudo-elementos decorativos | `::before` com accent, glow, `::after` | `display: none` |

### Cores
- **Accent principal**: verde `rgba(34, 197, 94, ...)` → azul ciano `rgba(56, 189, 248, ...)`
- **Hover/accent em nav, tabela, cards e botões**: agora usam `#38bdf8` / `#7dd3fc`
- **Glows verdes removidos**: substituídos por bordas finas azul-claras

## Verificação
- `pytest tests/test_ui_layout_compacto_observabilidade.py` — 30 testes
- Nenhum teste existente foi alterado
- Nenhuma rota, lógica de banco ou configuração foi modificada
