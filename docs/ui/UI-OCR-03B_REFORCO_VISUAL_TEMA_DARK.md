# UI-OCR-03B — Reforço Visual do Tema Dark

## 1. Objetivo

A fase UI-OCR-03 foi tecnicamente correta, mas visualmente conservadora: o painel já possuía aparência escura, então a primeira camada de tema dark não trouxe diferença perceptível suficiente. Esta fase reforça o impacto visual sem mexer na lógica.

## 2. Motivo da fase

O painel já era escuro antes da UI-OCR-03. A primeira camada refinou contraste e legibilidade, mas a mudança visual não foi claramente perceptível. Esta fase aplica um conjunto de melhorias com efeito visual mais forte.

## 3. Escopo aplicado

A alteração continua limitada ao CSS. Nenhum template, rota, banco, OCR, parser ou integração foi alterado.

## 4. Melhorias visuais aplicadas

- **Sidebar mais destacada**: borda esquerda com acento verde nos links, separador lateral com gradiente sutil, glow na marca
- **Cards mais evidentes**: acento superior verde-azul, sombra mais pronunciada, hover com elevação
- **Tabela com contraste melhorado**: linhas alternadas, hover destacado, cabeçalho reforçado
- **Badges/status com indicador**: dot colorido antes do texto com glow, cores distintas por status
- **Botões com elevação**: sombra verde, hover com translateY, glow no foco
- **Formulários refinados**: hover sutil, foco com anel verde e glow interno
- **Mensagens flash**: borda lateral colorida para identificar sucesso/erro/aviso
- **Hierarquia visual**: títulos com peso e cor distintos, subtítulos mais claros
- **Cards de integração/histórico**: hover com borda e sombra
- **Dashboard**: hover nos eventos com destaque
- **Scrollbar e seleção**: refinamento de cores

## 5. Arquivo alterado

`web/static/style.css`

Uma nova seção foi adicionada ao final do arquivo com o marcador:

```
/* UI-OCR-03B — Reforço visual perceptível */
```

Depois da seção `/* UI-OCR-03 — Tema dark base */`.

O CSS existente não foi removido ou reescrito. A nova seção complementa e reforça os estilos anteriores.

## 6. Arquivos não alterados

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

## 7. Como testar visualmente

1. Parar o painel se estiver rodando (Ctrl+C)
2. Iniciar novamente com `INICIAR_OCR_24H_LOCAL.bat`
3. Acessar `http://127.0.0.1:5000`
4. Usar Ctrl+F5 se necessário para limpar cache do navegador
5. Verificar:
   - Sidebar com acento verde nos links ao passar o mouse
   - Cards com linha superior verde-azul
   - Badges com dot colorido antes do texto
   - Botão "abrir" com sombra verde e elevação no hover
   - Tabela com linhas alternadas e hover visível
   - Formulário de detalhe/revisão com foco destacado

## 8. Critérios de aprovação

- `pytest` passa com 115+ testes
- Painel abre sem erro
- Mudança visual é claramente perceptível em relação à UI-OCR-03
- Texto permanece legível
- Botões continuam funcionando
- Tabela continua legível
- Formulário de detalhe/revisão continua funcional
- Git limpo após commit

## 9. Próxima fase sugerida

UI-OCR-04 — Layout principal com refinamento estrutural, somente após aprovação visual do tema reforçado.
