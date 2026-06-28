# UI-OCR-01 — Diretriz Visual do Painel OCR

## 1. Objetivo

Esta diretriz define o padrão visual futuro do painel OCR-LEITOR, com foco em operação, revisão, rastreabilidade e integração, usando uma estética escura profissional inspirada em painéis modernos de observabilidade e dashboards analíticos.

## 2. Referência de estilo

- Inspiração em painéis dark de observabilidade (LangSmith, LangChain, ferramentas de tracing)
- Inspiração em organização analítica tipo dashboard (Power BI, ferramentas de BI)
- Inspiração em cards, métricas, tabelas e status (painéis de monitoramento)
- Não copia marcas, logos, nomes, cores exatas, textos ou identidade visual de produtos terceiros

## 3. Personalidade visual desejada

- Escuro
- Técnico
- Limpo
- Moderno
- Confiável
- Operacional
- Legível
- Profissional
- Focado em fila e status

## 4. Estrutura visual futura

- Sidebar lateral com navegação entre telas
- Topbar compacta com indicador de ambiente e usuário
- Área principal com conteúdo dinâmico
- Cards de métricas na dashboard
- Tabela de documentos com status e ações
- Painel de detalhe do documento
- Área de revisão de campos extraídos
- Área de integração JSON
- Área de compatibilidade FechaMes
- Histórico e logs de processamento

## 5. Telas principais previstas

- Dashboard geral
- Fila de documentos
- Documento pendente de revisão
- Detalhe do documento
- Edição/revisão de campos
- Fila de integração
- Histórico de integrações
- Dashboard de integração
- Painel de compatibilidade JSON/FechaMes
- Tela de configuração local

## 6. Componentes visuais

- Cards com métricas e indicadores
- Badges de status com cores distintas
- Botões primários e secundários
- Alertas com níveis OK / AVISO / ERRO
- Tabelas compactas com colunas filtráveis
- Blocos de JSON com syntax highlight
- Timeline/histórico de eventos
- Indicadores de fila (contagem, progresso)
- Indicadores de compatibilidade
- Cabeçalho de documento com metadados

## 7. Status e badges

- `recebido` — documento entrou na fila
- `processando` — OCR em execução
- `pendente_revisao` — aguardando operador
- `pendente_integracao` — pronto para exportar
- `integrado` — enviado com sucesso
- `falha_integracao` — erro na exportação
- `simulado` — fluxo simulado ativo
- `compativel` — payload OK para FechaMes
- `bloqueado` — pendência impeditiva
- `erro` — falha no processamento

## 8. Cores e contraste

- Fundo escuro geral
- Painéis e cartões em tons escuros com bordas discretas
- Texto claro para legibilidade
- Verde para status OK e sucesso
- Amarelo/laranja para avisos e pendências
- Vermelho para erros e falhas
- Azul/ciano para informação técnica e links
- Não define valores finais de CSS nesta fase

## 9. Experiência operacional

O operador deve conseguir:

- Ver rapidamente quantos documentos existem por status
- Identificar pendências sem abrir cada documento
- Revisar campos extraídos pelo OCR
- Entender erros de processamento
- Validar integração com JSON contract
- Saber se um payload é compatível com FechaMes
- Operar sem confusão visual ou excesso de informação

## 10. Regras de segurança da UI

- UI não altera regra fiscal
- UI não altera OCR/parser/core
- UI não altera banco/schema sem fase própria
- UI não executa integração real sem confirmação explícita
- UI não escreve no FechaMes
- UI não deve esconder erros críticos do operador
- Ações destrutivas ou irreversíveis devem exigir confirmação

## 11. Fases futuras sugeridas

- UI-OCR-02 — Auditoria dos templates atuais
- UI-OCR-03 — Tema dark base
- UI-OCR-04 — Layout principal com sidebar e topbar
- UI-OCR-05 — Dashboard operacional
- UI-OCR-06 — Fila de documentos
- UI-OCR-07 — Tela de detalhe e revisão
- UI-OCR-08 — Painel JSON e FechaMes
- UI-OCR-09 — Badges e estados visuais
- UI-OCR-10 — Polimento responsivo

## 12. Decisão desta fase

Esta fase não altera interface ainda. Ela apenas define a direção visual e operacional para as próximas fases.
