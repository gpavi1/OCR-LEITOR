# UI-OCR-02 — Auditoria dos Templates Atuais

## 1. Objetivo

Esta fase audita a interface atual do OCR-LEITOR antes de qualquer alteração visual. O mapeamento permite que as próximas fases apliquem mudanças visuais sem quebrar rotas, login, revisão, banco ou OCR.

## 2. Arquivos visuais existentes

| Arquivo | Status | Descrição |
|---------|--------|-----------|
| `web/app.py` | Ativo | Rotas Flask, lógica de sessão, queries, exportação |
| `web/templates/base.html` | Ativo | Layout base com sidebar, brand, navegação, flash messages, block content |
| `web/templates/login.html` | Ativo | Tela de login com formulário usuário/senha |
| `web/templates/documentos.html` | Ativo | Listagem de documentos com cards de resumo e tabela |
| `web/templates/documento_detalhe.html` | Ativo | Detalhe do documento: campos, arquivo, edição, revisão, JSON, OCR |
| `web/templates/integracoes.html` | Ativo | Fila de integração com cards de documentos pendentes |
| `web/templates/historico_integracoes.html` | Ativo | Histórico de tentativas de integração |
| `web/templates/dashboard_integracoes.html` | Ativo | Dashboard com métricas, últimas tentativas e falhas |
| `web/static/style.css` | Ativo | 1075 linhas, tema escuro, sidebar, cards, badges, formulários, responsivo |
| `web/templates/*.bak_*` | Backup | Cópias de segurança de alterações anteriores |
| `web/static/*.bak_*` | Backup | Cópias de segurança de alterações anteriores |

## 3. Responsabilidade de cada arquivo

### `web/app.py`
- Rotas Flask principais
- Controle de sessão e login
- Queries no banco MySQL
- Lógica de exportação CSV
- Lógica de integração (marcar, registrar falha, reenfileirar)
- Passagem de variáveis para os templates

### `web/templates/base.html`
- Layout base: sidebar fixa, topbar implícita no conteúdo
- Marca OCR-LEITOR com logotipo estilizado
- Navegação: Documentos, Dashboard, Integrações, Exportar CSV, Health, Sair
- Footer da sidebar: "Modo seguro / Read-only"
- Sistema de flash messages com categorias (success, error, warning)
- Bloco `{% block content %}` para templates filhos

### `web/templates/login.html`
- Estende `base.html`
- Formulário de login centralizado com campos de usuário e senha
- Mensagem de erro quando credenciais inválidas

### `web/templates/documentos.html`
- Estende `base.html`
- Cards de resumo: Total, Pendente integração, Pendente revisão, Erros, Revisados
- Tabela de documentos: ID, Arquivo, Empresa, NF, Vencimento, Valor, Status, Revisado, Ações
- Badges de status com classes CSS específicas
- Link para abrir cada documento

### `web/templates/documento_detalhe.html`
- Estende `base.html`
- Painel de campos extraídos (cliente, empresa, NF, chave, vencimento, valor, status, revisado, JSON)
- Painel de arquivo (origem, destino, hash, erro)
- Formulário de correção manual (empresa, NF, chave, vencimento, valor, observação)
- Seção de revisão humana (marcar revisado / desfazer)
- Painel de JSON padrão
- Painel de texto OCR bruto

### `web/templates/integracoes.html`
- Estende `base.html`
- Lista de documentos pendentes de integração em formato de cards
- Ações: ver documento, exportar CSV, marcar integrado, registrar falha
- Navegação para dashboard e histórico

### `web/templates/historico_integracoes.html`
- Estende `base.html`
- Cards de tentativas de integração com status
- Detalhes: NF, integração, tipo, criado em, ID externo, erro, resposta
- Ação de reenfileirar documento

### `web/templates/dashboard_integracoes.html`
- Estende `base.html`
- Métricas: Total, Pendentes, Integrados, Falhas
- Métricas secundárias: Tentativas, Sucessos, Falhas registradas, Reenfileirados
- Últimas tentativas em formato de timeline
- Últimas falhas destacadas

### `web/static/style.css`
- Tema escuro completo com variáveis CSS (bg, surface, border, text, accent, danger, warning)
- Gradientes sutis no fundo
- Sidebar fixa com 260px
- Cards e painéis com bordas e sombras
- Badges de status com cores específicas (pendente, sucesso, erro)
- Formulários de edição e revisão
- Grid responsivo para cards, detalhes, dashboard
- Layout da fila de integração (style monday-like)
- Layout do histórico em cards
- Dashboard de integração com métricas e eventos
- Três breakpoints responsivos (1000px, 760px, 640px)

## 4. Rotas e telas observadas

| Rota | Template | Função |
|------|----------|--------|
| `/` | `documentos.html` | Listagem principal de documentos |
| `/login` | `login.html` | Autenticação local |
| `/logout` | — | Encerra sessão |
| `/documentos/<id>` | `documento_detalhe.html` | Detalhe e revisão |
| `/documentos/<id>/editar` | (POST) | Salva correções manuais |
| `/documentos/<id>/revisar` | (POST) | Marca como revisado |
| `/documentos/<id>/desfazer-revisao` | (POST) | Desfaz revisão |
| `/integracoes` | `integracoes.html` | Fila de integração |
| `/integracoes/dashboard` | `dashboard_integracoes.html` | Dashboard de integração |
| `/integracoes/historico` | `historico_integracoes.html` | Histórico de tentativas |
| `/integracoes/documentos/<id>/marcar-integrado` | (POST) | Marca documento como integrado |
| `/integracoes/documentos/<id>/registrar-falha` | (POST) | Registra falha de integração |
| `/integracoes/documentos/<id>/reenfileirar` | (POST) | Reenfileira documento |
| `/exportar/documentos.csv` | — | Exporta CSV de documentos |
| `/exportar/documentos/<id>.csv` | — | Exporta CSV de documento específico |
| `/health` | — | Endpoint de health check |

## 5. Pontos sensíveis

- Login e sessão: não quebrar autenticação
- Listagem de documentos: não quebrar queries e paginação
- Detalhe do documento: não quebrar exibição de campos
- Formulário de revisão: não quebrar POST de correção manual
- Status dos documentos: badges dependem de classes CSS `status-{valor}`
- Conexão com banco: rotas dependem de queries MySQL
- Mensagens de erro: flash messages com categorias específicas
- Navegação entre telas: links na sidebar e nos templates
- Exportação CSV: rotas de exportação
- Integração: ações de marcar integrado, registrar falha, reenfileirar
- Classes CSS de terceiros usadas em `style.css`

## 6. Plano seguro para UI-OCR-03

A próxima fase (UI-OCR-03) deve aplicar apenas tema visual base, preferencialmente via CSS, sem alterar regras de negócio. As variáveis CSS existentes em `:root` podem ser ajustadas para refinar o tema dark. Novos componentes visuais (sidebar refinada, topbar, cards de métrica) devem ser introduzidos sem remover classes existentes usadas pelos templates atuais.

## 7. Limites da próxima fase

UI-OCR-03 não deve:

- Alterar rotas em `web/app.py`
- Alterar queries no banco
- Alterar OCR/parser/core
- Alterar lógica de revisão ou edição
- Alterar contrato JSON ou conectores
- Alterar integração com FechaMes
- Remover classes CSS existentes ainda referenciadas nos templates
- Alterar estrutura de templates (extends, blocks, variáveis esperadas)

## 8. Decisão desta fase

Esta fase não altera a interface ainda. Ela apenas mapeia a estrutura atual para permitir mudanças visuais seguras nas próximas fases.
