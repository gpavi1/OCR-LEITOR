# CHECKLIST DE REVISÃO DE DOCUMENTO

## 1. Identificação da nota

| Campo | Valor |
|-------|-------|
| Nome do arquivo | |
| Fornecedor / Emitente | |
| Tipo do documento | NF-e / NFS-e / Boleto / Outro |
| Data do processamento | |

## 2. Campos para conferir

### 2.1 Empresa (emitente / razão social)

- [ ] Correto (igual ao OCR bruto)
- [ ] Corrigido manualmente
- [ ] Ausente (não foi extraído)
- [ ] Suspeito (pode ser destinatário/tomador)
- [ ] Não se aplica

### 2.2 Número NF

- [ ] Correto (confere com o cabeçalho da nota)
- [ ] Corrigido manualmente
- [ ] Ausente (não foi extraído)
- [ ] Suspeito (pode ser ano, série ou protocolo)
- [ ] Não se aplica

### 2.3 Chave de acesso

- [ ] Correto (44 dígitos, confere com DANFE)
- [ ] Corrigido manualmente
- [ ] Ausente (NFS-e não tem chave — ok)
- [ ] Ausente (NF-e devia ter — verificar)
- [ ] Suspeito (pode ser junção de números soltos)
- [ ] Não se aplica

### 2.4 Vencimento

- [ ] Correto (data financeira: duplicata, fatura, parcela)
- [ ] Corrigido manualmente
- [ ] Ausente (não foi extraído)
- [ ] Suspeito (pode ser data de emissão/saída)
- [ ] Não se aplica

### 2.5 Valor total

- [ ] Correto (confere com total geral da nota/duplicata)
- [ ] Corrigido manualmente
- [ ] Ausente (não foi extraído)
- [ ] Suspeito (pode ser frete, ICMS, valor unitário)
- [ ] Não se aplica

## 3. Regras de aprovação

- ❌ **Não aprovar** se valor estiver errado
- ❌ **Não aprovar** se NF estiver errada
- ❌ **Não aprovar** se empresa estiver errada
- ❌ **Não aprovar** se chave de NF-e estiver ausente sem justificativa
- ⚠️ NFS-e sem chave de acesso: ok (não tem), mas conferir os demais campos
- ⚠️ Imagem ruim ou nota cortada: registrar e não forçar aprovação

## 4. Antes de exportar

- [ ] Todos os campos obrigatórios conferidos
- [ ] Observação preenchida (se houve divergência)
- [ ] Documento marcado como **revisado**
- [ ] Exportação feita **somente após** validação completa

## 5. Quando registrar falha

Registrar no CSV de controle se:

- OCR não leu campo que está visível na imagem
- Parser extraiu número falso como NF
- Valor veio de frete, desconto ou ICMS em vez do total
- Empresa extraída é o destinatário/tomador em vez do emitente
- Chave de acesso em NF-e não foi extraída mas está no DANFE
- Chave falsa gerada em NFS-e

## 6. Quando NÃO mexer no código

- Caso isolado (apenas 1 nota com problema)
- Imagem de baixa qualidade (borrada, torta, escura)
- Nota cortada ou incompleta na imagem
- Campo ausente no próprio documento físico
- Layout muito raro que não vale a pena tratar no parser

## 7. Quando sugerir ajuste futuro (AJUSTE-OCR-03)

- Mesmo erro se repetiu em **3 ou mais documentos** diferentes
- Erro tem evidência clara no OCR bruto
- Correção manual é sempre a mesma (padrão identificado)
- Erro foi registrado no CSV de controle do piloto
