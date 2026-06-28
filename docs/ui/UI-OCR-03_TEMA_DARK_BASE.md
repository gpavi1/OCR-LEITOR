# UI-OCR-03 — Tema Dark Base

## 1. Objetivo

Esta fase aplica a primeira camada visual real do painel OCR-LEITOR, refinando o tema escuro existente com melhor contraste, legibilidade e aparência profissional, inspirada em painéis modernos de observabilidade.

## 2. Escopo aplicado

A alteração foi limitada ao CSS. Nenhum template, rota, banco, OCR ou parser foi alterado.

## 3. Estratégia visual

- Fundo escuro com gradiente sutil
- Painéis e cartões em tons escuros com bordas discretas
- Texto claro com contraste melhorado
- Botões com transições suaves e hover
- Tabelas com linhas mais legíveis e hover destacado
- Formulários com foco realçado por anel verde
- Badges de status com cores refinadas
- Scrollbar personalizada escura
- Seleção de texto destacada em verde
- Links em azul claro com hover

## 4. Arquivo alterado

`web/static/style.css`

Uma nova seção foi adicionada ao final do arquivo com o marcador:

```
/* UI-OCR-03 — Tema dark base */
```

As variáveis CSS foram definidas em `:root` com o prefixo `--ocr-` para evitar conflito com as variáveis existentes.

O CSS existente não foi removido ou reescrito. A nova seção complementa e refina os estilos anteriores por especificidade e ordem de cascata.

## 5. Arquivos não alterados

- `web/app.py`
- Todos os templates HTML
- Banco de dados / schema.sql
- OCR / parser / core
- Contratos JSON
- Conectores / validadores / montadores
- `requirements.txt`
- Scripts de instalação
- `.env`, `.venv`, `config/settings.json`
- FechaMes

## 6. Limites desta fase

Esta fase ainda não cria:

- Sidebar nova
- Dashboard novo
- Novos cards de métricas
- Novas rotas
- Nova tela de integração
- Mudanças de fluxo operacional
- Dependência externa (CDN, fontes, imagens)

## 7. Como testar visualmente

1. Iniciar o painel com `INICIAR_OCR_24H_LOCAL.bat`
2. Acessar `http://127.0.0.1:5000`
3. Verificar login, listagem, detalhe e revisão
4. Confirmar legibilidade geral
5. Confirmar que botões e formulários continuam funcionando
6. Confirmar que tabelas e badges estão visíveis

## 8. Critérios de aprovação

- `pytest` passa com 97+ testes
- Painel abre sem erro
- Tema escuro visível com gradiente suave
- Texto legível
- Tabelas e formulários funcionais
- Botões acionáveis com hover
- Rotas e fluxos intactos
- Git limpo após commit

## 9. Próxima fase sugerida

UI-OCR-04 — Layout principal com sidebar/topbar, ainda de forma controlada.
