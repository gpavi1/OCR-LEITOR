# UI-OCR-04 — Layout Principal Estilo Observabilidade

## 1. Objetivo

Esta fase aplica a primeira mudança estrutural real no layout do painel OCR-LEITOR, aproximando o visual de um painel moderno de observabilidade.

## 2. Motivo da fase

As fases UI-OCR-03 e UI-OCR-03B aplicaram apenas CSS, mas o painel já possuía tema escuro e estrutura de sidebar/cards. Para gerar uma diferença perceptível, foi necessário ajustar os templates HTML — mantendo a lógica intacta.

## 3. Escopo aplicado

Foram alterados:

- `web/templates/base.html`
- `web/templates/documentos.html`
- `web/static/style.css`

Nenhuma rota, banco, OCR, parser ou lógica de negócio foi alterada.

## 4. O que mudou visualmente

- **Sidebar reorganizada**: navegação dividida em seções "Aplicação" e "Sistema" com labels
- **Links com destaque ativo**: o link da página atual fica destacado via `nav-link-active`
- **Topbar operacional**: barra superior com título e badges de status (Local, 127.0.0.1, Read-only)
- **Cards de ação rápida**: grade de 4 cards na página inicial para acesso direto às principais funções
- **Cards de métrica enriquecidos**: cada card agora tem label, valor e descrição
- **Tabela mais densa**: cabeçalho compacto, linhas mais justas, hover e alternância preservados
- **Hierarquia visual**: títulos, subtítulos e organização mais próxima de painéis de monitoramento

## 5. O que não mudou

- Rotas em `web/app.py`
- Banco de dados / schema.sql
- OCR / parser / core
- Contratos JSON
- Conectores / validadores / montadores
- `requirements.txt`
- Scripts de instalação
- `.env`, `.venv`, `config/settings.json`
- FechaMes
- Tela de login
- Tela de detalhe/revisão do documento
- Funcionalidade de exportar CSV
- Funcionalidade de health check

## 6. Segurança

- Sem API nova
- Sem integração real
- Sem escrita no FechaMes
- Sem CDN, fonte externa ou imagem externa
- Sem cópia de marca, logo ou identidade visual de produto terceiro
- Todos os links e rotas originais preservados
- Blocos Jinja e variáveis existentes intactos

## 7. Como testar visualmente

1. Parar o painel se estiver rodando (Ctrl+C)
2. Iniciar com `INICIAR_OCR_24H_LOCAL.bat`
3. Acessar `http://127.0.0.1:5000`
4. Usar Ctrl+F5 para limpar cache
5. Validar:
   - Topbar visível com status "Local", "127.0.0.1" e "Read-only"
   - Sidebar com seções "Aplicação" e "Sistema"
   - Link "Documentos" destacado como ativo na página inicial
   - Cards de ação: Revisar documentos, Fila de integração, Dashboard, Exportar CSV
   - Cards de métrica com label, valor e descrição
   - Tabela de documentos com cabeçalho compacto
   - Clique em "abrir" leva ao detalhe do documento
   - Navegação entre links da sidebar funciona
   - Logout funciona

## 8. Critérios de aprovação

- `pytest` passa com 144+ testes
- Painel abre sem erro
- Layout mudou de forma claramente perceptível
- Sidebar ficou mais profissional com seções
- Topbar aparece com badges de status
- Cards de ação aparecem na página inicial
- Documentos continuam listados na tabela
- Botão "abrir" funciona
- Tela de detalhe continua acessível
- Git limpo após commit

## 9. Próxima fase sugerida

UI-OCR-05 — Dashboard operacional com métricas e blocos analíticos, somente depois da aprovação visual da UI-OCR-04.
