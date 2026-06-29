# GUIA-PILOTO-EMPRESA-01 — Uso controlado do OCR-LEITOR na empresa

## 1. Objetivo

Este guia documenta o uso controlado do OCR-LEITOR como apoio operacional
para reduzir digitação manual, **sem integração automática cega**.

Fluxo oficial:

```
nota/imagem → OCR preenche → humano revisa → dado validado → exportação
```

O piloto deve validar o uso real com 10 a 20 notas, medir a qualidade da
extração e registrar falhas sem alterar o código do sistema.

---

## 2. Estado atual do sistema

| Componente        | Status       |
|-------------------|--------------|
| Painel web        | Funcionando  |
| Banco MySQL       | Funcionando  |
| OCR (Tesseract)   | Funcionando  |
| Revisão humana    | Funcionando  |
| Exportação JSON   | Funcionando  |
| Relatório Markdown| Funcionando  |
| Exportação CSV    | Funcionando  |
| API local         | Funcionando  |
| Reset banco teste | Funcionando  |
| Parser NF-e/NFS-e | Ajustado até AJUSTE-OCR-02 |

---

## 3. O que esta fase NÃO faz

- Não altera parser (`parser_nf.py`)
- Não altera OCR engine (`pytesseract`)
- Não altera pipeline (`ocr_pipeline_s1.py`)
- Não altera banco (`database/schema.sql`)
- Não altera API (`web/app.py`)
- Não altera interface (`web/templates/`, `web/static/`)
- Não altera dependências (`requirements.txt`)
- Não cria integração automática com Monday/ERP
- Não expõe o sistema para internet

---

## 4. Fluxo operacional passo a passo

### 4.1 Preparar ambiente

```bash
python verificar_instalacao.py
```

Verifica se Python, Tesseract, dependências e estrutura de pastas estão
corretos. Corrigir qualquer falha apontada antes de prosseguir.

### 4.2 Iniciar painel web

```bash
INICIAR_WEB_LOCAL.bat
```

Aguardar a mensagem "Running on http://127.0.0.1:5000". Abrir o navegador
neste endereço. Fazer login com usuário e senha configurados.

### 4.3 Enviar nota

1. Navegar até **Upload** no menu lateral
2. Arrastar ou selecionar o arquivo (`.jpg`, `.jpeg`, `.png` ou `.pdf`,
   máximo 10 MB)
3. Clicar em "Upload"

### 4.4 Processar

Ainda na página de Upload, clicar no botão **"Process uploaded files"**.
Aguardar o OCR ler a imagem e o parser extrair os campos.

### 4.5 Revisar

1. Ir para **Documentos** no menu lateral
2. Localizar o documento com status `pendente_revisao`
3. Clicar no documento para abrir o painel de detalhes
4. Conferir cada campo com o OCR bruto (painel "Raw OCR Text")

### 4.6 Corrigir

1. No formulário de edição, corrigir manualmente os campos que estiverem
   errados ou ausentes
2. Preencher **Observação** se houver divergência relevante

### 4.7 Marcar revisado

1. Clicar em **"Salvar Revisão"**
2. O status muda para `pendente_integracao`
3. Neste momento os botões de exportação ficam disponíveis

### 4.8 Exportar

Opções disponíveis:

- **JSON validado:** clicar em "Exportar JSON" — salva em `exports/json/`
- **Markdown relatório:** clicar em "Gerar Markdown" — salva em
  `exports/markdown/`
- **CSV geral:** rota `/exportar/documentos.csv` (todos os documentos)

### 4.9 Registrar resultado

Preencher o CSV de controle do piloto com os dados da nota processada.
Ver seção 9 para detalhes.

---

## 5. Status operacionais

| Status no sistema | Significado | Ação esperada |
|-------------------|-------------|---------------|
| `recebido` | Upload feito, OCR não iniciou | Clicar "Processar" |
| `processando` | OCR rodando (transitório) | Aguardar |
| `pendente_revisao` | OCR concluído, aguarda humano | **Obrigatório revisar** |
| `pendente_integracao` | Revisado, pronto para exportar | Conferir antes de exportar |
| `integrado` | Exportado (ação manual) | Nenhuma |
| `erro_ocr` | Falha no OCR/processamento | Registrar falha, não insistir |

### Regra prática por status

- **pendente_revisao:** obrigatório revisar antes de qualquer ação
- **pendente_integracao:** durante o piloto, conferir novamente antes de
  exportar (prevenção extra)
- **integrado:** ocorre somente após ação humana intencional
- **erro_ocr:** registrar a falha e pular esta nota

---

## 6. Checklist de conferência

Conferir obrigatoriamente antes de marcar como revisado:

1. **Empresa** (emitente / razão social) — conferir se não é destinatário
2. **Número NF** — conferir no cabeçalho da nota
3. **Chave de acesso** — 44 dígitos do DANFE; NFS-e deve ficar vazia
4. **Vencimento** — conferir se é data financeira, não data de emissão
5. **Valor total** — conferir com duplicata/fatura ou total geral
6. **Tipo de documento** — NF-e, NFS-e ou outro
7. **Qualidade da imagem** — se a imagem está legível

Ver o arquivo `CHECKLIST_REVISAO_DOCUMENTO.md` para detalhes.

---

## 7. Como lidar com falhas

| Situação | Ação |
|----------|------|
| Campo vazio | Preencher manualmente se o dado existe no OCR bruto |
| Campo suspeito | Comparar com OCR bruto; corrigir se necessário |
| Valor errado | Digitar o valor correto manualmente |
| NF errada | Verificar no cabeçalho da nota; corrigir |
| Chave ausente em NF-e | Verificar se está no OCR bruto; digitar manualmente |
| Chave presente em NFS-e | Remover (NFS-e não tem chave de 44 dígitos) |
| Imagem ruim | Refazer o scan da nota; evitar fotos tortas |
| Layout diferente | Registrar no CSV de controle; corrigir manualmente |

---

## 8. Critério para registrar erro repetido

O mesmo problema precisa aparecer em **várias notas diferentes** antes de
virar um ajuste técnico.

- **1 nota:** corrigir manualmente, registrar
- **2 notas:** continuar observando
- **3+ notas com o mesmo padrão de erro:** avaliar AJUSTE-OCR-03
- **Erro tem evidência no OCR bruto:** só considerar ajuste se o OCR leu
  a informação correta mas o parser não extraiu

---

## 9. Critério de sucesso do piloto

Medir em 10 a 20 notas reais:

| Indicador | Meta sugerida |
|-----------|---------------|
| Empresa correta | ≥ 80% |
| NF correta | ≥ 80% |
| Chave correta (quando existir) | ≥ 90% |
| Vencimento correto | ≥ 80% |
| Valor correto | ≥ 80% |
| Tempo economizado | Registrar percepção |
| Correções manuais necessárias | Registrar quantidade |

Usar `docs/operacao/MODELO_CONTROLE_PILOTO_EMPRESA.csv` para registrar.

---

## 10. Critério para avançar para integração automática

Só avançar se:

1. Piloto concluído com 10 a 20 notas
2. Taxa de acerto ≥ 80% nos campos principais
3. Operador consegue executar o ciclo sem suporte técnico
4. Processo de revisão está documentado e claro
5. Falhas registradas e compreendidas

---

## 11. Critério para abrir AJUSTE-OCR-03

Só abrir um novo ajuste de parser se:

1. **Mesmo erro em 3 ou mais notas** com o mesmo padrão
2. **OCR bruto contém a informação correta** (o problema é no parser,
   não no OCR)
3. **Erro foi registrado** no CSV de controle do piloto
4. **Não é caso isolado** — uma nota com problema não justifica ajuste

---

## 12. Procedimento diário recomendado

1. Iniciar painel web (`INICIAR_WEB_LOCAL.bat`)
2. Fazer login
3. Fazer upload de lote pequeno (2 a 5 notas)
4. Clicar "Process uploaded files"
5. Para cada nota:
   - [ ] Abrir documento
   - [ ] Conferir campos com OCR bruto
   - [ ] Corrigir se necessário
   - [ ] Salvar revisão
   - [ ] Exportar JSON
6. Registrar no CSV de controle
7. Fechar painel (Ctrl+C no terminal)

---

## 13. Cuidados de segurança

- Não processar documentos reais sem autorização do responsável
- Não integrar automaticamente com sistemas externos
- Não commitar documentos reais ou imagens reais no Git
- Não alterar código durante o piloto (parser, pipeline, banco, API, UI)
- Manter backup antes de executar limpezas ou resets
- Não expor o painel para internet sem autenticação adicional
- Não compartilhar credenciais de acesso
- Manter o servidor em ambiente local ou rede interna confiável

---

## 14. Documentos de apoio

| Documento | Descrição |
|-----------|-----------|
| `CHECKLIST_REVISAO_DOCUMENTO.md` | Checklist diário de revisão |
| `MODELO_CONTROLE_PILOTO_EMPRESA.csv` | Planilha de controle do piloto |
| `OPS-OCR-01_LIMPEZA_AMBIENTE_TESTE.md` | Limpeza segura do ambiente |
| `RESET-BANCO-TESTE-01_LIMPEZA_BANCO_TESTE.md` | Reset seguro do banco |

---

## 15. Próximo passo

Após a conclusão deste guia, a próxima fase recomendada é:

**PILOTO-EMPRESA-01** — execução real do piloto com 10 a 20 notas,
utilizando a documentação criada nesta fase para registro e controle.
