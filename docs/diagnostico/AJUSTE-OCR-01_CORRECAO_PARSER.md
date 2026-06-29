# AJUSTE-OCR-01 — Correção Cirúrgica do Parser NF-e

## 1. Problema observado

Em teste real com OCR bruto de DANFE, o parser atual escolhia ruído como empresa e ignorava campos úteis presentes no texto.

## 2. Evidência do OCR bruto

```
ee ee ee eee
PS CALDEIRA Rémnessa: 0081736897 - Ordem: 0001805803

DOCUMENTO AUXILIAR
DE NOTA FISCAL
ELETRÔNICA

UNILIDER DISTRIBUIDORA S/A
...
```

## 3. Campos que falhavam

| Campo | Esperado | Obtido |
|-------|----------|--------|
| empresa | UNILIDER DISTRIBUIDORA S/A | EE EE EE EEE |
| numero_nf | 1281694 | null |
| vencimento | — | null (sem contexto financeiro, OK) |
| valor_total | null | null (OK) |
| chave_acesso | 44 dígitos | 44 dígitos com prefixo do endereço |

## 4. Testes criados

Arquivo: `tests/test_parser_nf_ajuste_ocr_01.py` (13 testes)

1. Não aceitar "EE EE EE EEE" como empresa.
2. Não aceitar "DOCUMENTO AUXILIAR" como empresa.
3. Não aceitar "DE NOTA FISCAL / ELETRÔNICA" como empresa.
4. Não aceitar "CHAVE DE ACESSO" como empresa.
5. Priorizar "UNILIDER DISTRIBUIDORA S/A" como empresa.
6. Extrair "1281694" como número NF.
7. Manter chave de acesso válida (44 dígitos).
8. Não confundir destinatário com emitente.
9. Não inventar valor_total.
10. Manter status parcial para texto incompleto.
11. Comportamento seguro para texto vazio.
12. Comportamento seguro para None.
13. Preservar raw no resultado.

## 5. Ajuste feito no parser

Arquivo: `parser_nf.py`

### 5.1. Bloqueio de cabeçalhos fiscais

Adicionados termos em `EMPRESA_CABECALHOS_BLOQUEADOS`:
- `NOTA FISCAL`
- `ELETRONICA`

### 5.2. Detecção de ruído OCR

Em `_eh_cabecalho_fiscal`: linhas com todas as palavras ≤ 3 caracteres (padrão de ruído OCR como "EE EE EE EEE") são rejeitadas.

### 5.3. Exigência de palavra longa para empresa sem sufixo

Em `_parece_nome_empresa`: candidatos sem sufixo empresarial (S/A, LTDA, ME, etc.) precisam ter ao menos uma palavra com 6+ caracteres. Isso elimina falsos positivos como "TEXTO CURTO SEM DADOS UTEIS".

### 5.4. Prioridade para sufixo empresarial

Em `extrair_empresa`: agora coleta todos os candidatos e retorna o primeiro que contém sufixo empresarial. Se nenhum tiver sufixo, mantém o comportamento anterior (primeiro candidato válido).

### 5.5. Padrão para número NF após marcador

Em `extrair_numero_nf`: adicionado padrão `(?:\*|#)\s*(\d{6,9})\b` para capturar números NF que aparecem após `*` ou `#` (comum em DANFE como "ARMAZ.1 * 1281694").

### 5.6. Padrão específico para chave DANFE (grupos 4x11)

Em `extrair_chave_acesso`: adicionada busca primária com padrão de 11 grupos de 4 dígitos separados por espaço/ponto/hífen. Esse formato é mais específico que a busca genérica de 44 dígitos e evita capturar números de endereço (ex.: "1362" antes da chave).

## 6. O que não foi alterado

- OCR engine (Tesseract): não mexido.
- `ocr_pipeline_s1.py`: não alterado.
- Processamento de imagem: não alterado.
- Banco/schema: não alterado.
- API/rotas Flask: não alterado.
- UI/templates/CSS: não alterado.
- `requirements.txt`: não alterado.
- Contratos JSON: não alterado.
- Exportação/relatórios: não alterado.
- Integrações (Monday/Sheets/ERP/FechaMes): não alterado.
- Scripts operacionais (DIAG-OCR-01, OPS-OCR-01): não alterado.

## 7. Limites conhecidos

- O padrão de chave DANFE (grupos 4x11) exige que a chave esteja em formato de blocos de 4 dígitos. Se o OCR produzir a chave em formato contínuo ou com separações irregulares, o fallback genérico ainda pode incluir números de endereço.

- A detecção de ruído OCR (palavras curtas) pode rejeitar empresas legítimas com nomes muito curtos, mas na prática empresas reais têm ao menos uma palavra com 6+ caracteres ou sufixo empresarial.

- O número NF após `*` ou `#` pode capturar outros números de 6-9 dígitos que apareçam após esses marcadores em contextos não-NF.

## 8. Próximo passo

Validar no painel com documento real.

Rodar o parser contra documentos reais na pasta `_amostras_privadas/` (fora do versionamento) e verificar se a extração agora produz os campos corretos.

---

AJUSTE-OCR-01 é correção cirúrgica do parser.
Não alterou OCR engine.
Não alterou pipeline.
Não alterou banco.
Não alterou API.
Não alterou UI.
