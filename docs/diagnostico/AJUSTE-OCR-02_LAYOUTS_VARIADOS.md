# AJUSTE-OCR-02 — Melhorar parser para layouts variados

## 1. Problema observado no lote fictício

Após o reset seguro do banco (RESET-BANCO-TESTE-01), foram processadas 3 notas
fictícias para validação do parser. O OCR bruto leu corretamente as informações,
mas o parser apresentou falhas sistemáticas em 3 áreas:

### Nota 01 — DANFE Mercado Alfa

| Campo    | OCR bruto                  | Parser extraiu | Esperado             |
|----------|----------------------------|----------------|----------------------|
| NF       | NF-e No. / 100001          | ❌ não extraiu | 100001               |
| Valor    | R$ 1.250,75 (duplicata)    | ✅ 1250.75     | 1250.75              |

### Nota 02 — NFS-e Serviços Beta

| Campo    | OCR bruto                           | Parser extraiu                    | Esperado                     |
|----------|-------------------------------------|-----------------------------------|------------------------------|
| Empresa  | SERVICOS BETA TECNOLOGIA ME ...     | ❌ CLIENTE MODELO SERVICOS LTDA   | SERVICOS BETA TECNOLOGIA ME  |
| NF       | NUMERO NFS-e: 20260077              | ❌ não extraiu                    | 20260077                     |
| Chave    | (sem CHAVE DE ACESSO)               | ❌ gerou chave falsa de 44 dígitos| null                         |
| Valor    | VALOR DOS SERVICOS R$ 875,40        | ❌ não extraiu                    | 875.40                       |

### Nota 03 — DANFE Atacado Gamma

| Campo    | OCR bruto                               | Parser extraiu                      | Esperado              |
|----------|-----------------------------------------|-------------------------------------|-----------------------|
| Empresa  | ATACADO GAMMA S/A ... DESTINATARIO ...  | ❌ MERCADO COMPRADOR MODELO LTDA    | ATACADO GAMMA S/A     |
| NF       | No. 987654                              | ❌ não extraiu                      | 987654                |
| Valor    | TOTAL GERAL DA NOTA: R$ 2.300,00        | ❌ não extraiu                      | 2300.00               |

---

## 2. Evidência do OCR bruto

As fixtures de OCR bruto estão em:

- `tests/test_parser_nf_ajuste_ocr_02.py`
  - `TEXTO_FIXTURE_1_MERCADO_ALFA` → DANFE completa
  - `TEXTO_FIXTURE_2_NFSE_SERVICOS_BETA` → NFS-e completa
  - `TEXTO_FIXTURE_3_DANFE_ATACADO_GAMMA` → DANFE completa

Nenhuma fixture usa imagem, OCR real, internet ou banco.

---

## 3. Falhas corrigidas

### 3.1 Emitente vs Tomador/Destinatário

**Problema original:**
O parser varria as primeiras 60 linhas sem diferenciar emitente de
destinatário/tomador. Linhas como "CLIENTE MODELO SERVICOS LTDA" (após
"TOMADOR DOS SERVICOS") e "MERCADO COMPRADOR MODELO LTDA" (após
"DESTINATARIO") eram capturadas como empresa.

**Correção:**

1. Adicionado `EMPRESA_BOUNDARY_MARKERS = ["DESTINATARIO", "TOMADOR DOS SERVICOS"]`
2. O scanner interrompe a busca ao encontrar o primeiro marcador de fronteira
3. Adicionado `EMPRESA_SPLIT_KEYWORDS = [" NOTA FISCAL", " NF-E", " DANFE"]` para
   extrair o nome da empresa mesmo quando a linha contém boilerplate fiscal
   (ex.: "SERVICOS BETA TECNOLOGIA ME NOTA FISCAL DE SERVICOS")
4. Adicionado `EMPRESA_LINE_START_BLOCK = ["RECEBEMOS"]` para ignorar linhas
   que começam com verbos de recebimento
5. Adicionados blocos fiscais adicionais: `"DOCUMENTO"`, `"CODIGO DE VERIFICACAO"`,
   `"COMPETENCIA"`
6. Reordenada a lógica: split acontece **antes** do bloqueio por cabeçalho fiscal

**Arquivo:** `parser_nf.py` — constantes + função `extrair_empresa`

### 3.2 NF em padrões variados

**Problema original:**
O parser só reconhecia padrões limitados de número de nota:
- `NRO: 123`, `NF: 123`, `NOTA FISCAL Nº 123`, `*123456`

Não reconhecia:
- `NF-e No.\n100001` (DANFE, número em linha separada)
- `No. 987654` (DANFE com abreviatura)

**Correção:**

Adicionados padrões a `padroes_contextuais` em `extrair_numero_nf`:

```python
r"\bNF-E\s+NO?\.?\s*[:\-]?\s*(\d{1,9})\b"           # NF-e No.\n100001
r"\b(?:NUMERO\s+)?NFS-E\s*[:\-]?\s*(\d{1,9})\b"     # NUMERO NFS-e: 20260077
```

E corrigido o padrão `N[º°O]` para `N[º°Oo]` e ajustado o separador para
`[\.\s]*` a fim de consumir o ponto após `No.`.

### 3.3 Valor total por contexto

**Problema original:**
O parser só reconhecia:
- `VALOR TOTAL DA NOTA...`
- `VALOR TOTAL DA NOTA FISCAL...`
- `TOTAL DA NOTA FISCAL...`

Não reconhecia:
- `TOTAL GERAL DA NOTA: R$ 2.300,00`
- `VALOR DOS SERVICOS R$ 875,40`
- `VALOR: R$ 1.250,75` em bloco DUPLICATA/FATURA

**Correção:**

1. Adicionados padrões regex primários:
   - `TOTAL GERAL DA NOTA`
   - `VALOR DOS SERVICOS`
2. Adicionados fallbacks por linha:
   - `TOTAL GERAL DA NOTA` em linha específica
   - `VALOR DOS SERVICOS` em linha específica
3. Adicionado fallback `DUPLICATA/FATURA/PARCELA/COBRANCA` que busca o
   primeiro valor com `R$` nas proximidades

### 3.4 Chave falsa em NFS-e

**Problema original:**
O terceiro fallback de `extrair_chave_acesso` compactava **todos** os dígitos
do documento e procurava uma sequência de 44. Em NFS-e com CNPJs, números
de nota, datas e códigos de verificação, isso gerava uma chave falsa.

**Correção:**

Adicionada verificação de contexto antes do terceiro fallback:

```python
if not any(kw in texto_norm
           for kw in ["CHAVE DE ACESSO", "CHAVE ACESSO", "DANFE", "NF-E"]):
    return None
```

Se o texto não contém nenhum desses indicadores de chave real, o fallback
retorna `None` em vez de montar uma chave falsa.

---

## 4. Testes criados

### `tests/test_parser_nf_ajuste_ocr_02.py`

30 testes organizados em 4 grupos:

**Fixture 1 — DANFE Mercado Alfa** (5 testes)
- Empresa correta: MERCADO TESTE ALFA LTDA
- NF: 100001
- Chave: 44 dígitos válidos
- Vencimento: 15/07/2026
- Valor: 1250.75

**Fixture 2 — NFS-e Serviços Beta** (6 testes)
- Emitente correto: SERVICOS BETA TECNOLOGIA ME
- Não captura tomador: CLIENTE MODELO SERVICOS LTDA
- NF: 20260077
- Chave: null (sem CHAVE DE ACESSO)
- Valor: 875.40
- Vencimento: 30/07/2026

**Fixture 3 — DANFE Atacado Gamma** (6 testes)
- Emitente correto: ATACADO GAMMA S/A
- Não captura destinatário
- NF: 987654
- Chave: 44 dígitos válidos
- Valor: 2300.00
- Vencimento: 05/08/2026

**Comportamento seguro herdado** (13 testes)
- Bloqueio de ruídos (ee ee ee, cabeçalhos fiscais)
- UNILIDER DISTRIBUIDORA S/A continua funcionando
- Não inventa valor/chave sem contexto
- Texto vazio e None seguros

---

## 5. Ajuste feito no parser

### `parser_nf.py` — alterações

| Local                | Tipo            | Descrição                                      |
|----------------------|-----------------|------------------------------------------------|
| Constantes           | Adicionado      | `EMPRESA_BOUNDARY_MARKERS`                     |
| Constantes           | Adicionado      | `EMPRESA_SPLIT_KEYWORDS`                       |
| Constantes           | Adicionado      | `EMPRESA_LINE_START_BLOCK`                     |
| Constantes           | Modificado      | `EMPRESA_CABECALHOS_BLOQUEADOS` (+3 entradas)  |
| `extrair_empresa`    | Reescrevido     | Boundary scan, split antes de header check     |
| `extrair_numero_nf`  | Modificado      | +2 padrões, `[\.\s]*` e `o` em classe de char |
| `extrair_valor_total`| Modificado      | +2 patterns, +3 fallbacks contextuais          |
| `extrair_chave_acesso`| Modificado     | Context check antes do fallback de compactação |

---

## 6. O que não foi alterado

- ✅ OCR engine (pytesseract) — intacto
- ✅ `ocr_pipeline_s1.py` — intacto
- ✅ `database/schema.sql` — intacto
- ✅ `database/mysql_db.py` — intacto
- ✅ API Flask (`web/app.py`) — intacta
- ✅ Templates/UI/CSS — intactos
- ✅ `requirements.txt` — intacto
- ✅ Contratos JSON — intactos
- ✅ Exportação JSON — intacta
- ✅ Relatório Markdown — intacto
- ✅ Integração Monday/Sheets/ERP/FechaMes — intacta
- ✅ Scripts operacionais (`8_*.bat`, `9_*.bat`, `scripts/*.py`) — intactos

---

## 7. Limites conhecidos

1. **Valor duplicata vs valor total:** Quando a nota tem `VALOR TOTAL DA NOTA`
   com OCR danificado (ex.: "RSE.") e também tem DUPLICATA/FATURA, o fallback
   captura o valor da duplicata. Isso é intencional, mas pode não ser ideal
   se ambos os valores divergirem sem erro de OCR.

2. **Prefixos de linha bloqueados:** `EMPRESA_LINE_START_BLOCK` atualmente só
   contém "RECEBEMOS". Notas com outras construções de recebimento podem
   precisar de expansão.

3. **NFS-e sem "CHAVE DE ACESSO":** O parser retorna `None` para chave, o
   que está correto. Notas de serviço não têm chave de 44 dígitos.

4. **Cobertura de NCM:** O parser ainda não extrai NCM dos produtos.

---

## 8. Próximo passo

1. Rodar novamente as 3 notas fictícias no painel web para confirmar a
   extração visualmente.
2. Após confirmação, executar **LOTE-VALIDA-OCR-01** com 3 a 5 notas
   reais (ou simuladas realísticas) para validar o parser em documentos
   com ruído OCR real.

---

## 9. Validação

```
python -m pytest tests/test_parser_nf_ajuste_ocr_02.py -v   # 30/30 passed
python -m pytest tests/test_parser_nf_ajuste_ocr_01.py       # 13/13 passed
python -m pytest tests/test_parser_nf.py                     # 5/5 passed
python -m pytest                                              # 503/503 passed
```

---

## 10. Commit e tag

```
git add parser_nf.py tests/test_parser_nf_ajuste_ocr_02.py \
      docs/diagnostico/AJUSTE-OCR-02_LAYOUTS_VARIADOS.md \
      INDEX.md CHANGELOG.md
git commit -m "fix: melhora parser para layouts variados de notas"
git tag ajuste-ocr-02-layouts-variados-ok
```
