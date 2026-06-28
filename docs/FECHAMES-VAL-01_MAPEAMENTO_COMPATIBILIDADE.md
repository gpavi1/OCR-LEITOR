# FECHAMES-VAL-01 — Mapeamento de Compatibilidade OCR-LEITOR → FechaMes

## 1. Objetivo

Este documento define o mapeamento inicial de compatibilidade entre o payload JSON do OCR-LEITOR e uma futura entrada controlada no FechaMes.

O OCR-LEITOR deve ser tratado como sistema externo de extração, validação e exportação de dados fiscais. Ele não modifica a estrutura interna do FechaMes, não escreve no banco do FechaMes e não assume regras fiscais ou operacionais que pertencem ao FechaMes.

Esta fase é exclusivamente documental. Ela não cria código, importador, API, conector real ou integração real.

## 2. Princípio de segurança

- OCR-LEITOR não escreve diretamente no banco do FechaMes.
- OCR-LEITOR não altera a estrutura do FechaMes.
- FechaMes continua sendo o sistema dono da regra fiscal/operacional.
- A integração futura deve ser por JSON validado, arquivo intermediário ou importador controlado.
- Qualquer importação futura deve ter confirmação, validação e possibilidade de reversão.

## 3. Fluxo seguro proposto

Fluxo seguro esperado para uma integração futura e controlada:

```text
OCR-LEITOR
→ extrai documento
→ operador revisa
→ payload JSON v1 é montado
→ contrato é validado
→ JSON é exportado
→ FechaMes, futuramente, poderá ler/importar de forma controlada
```

Esse fluxo preserva o OCR-LEITOR como origem de dados documentais revisados e mantém o FechaMes como sistema independente, responsável por validar e aplicar suas próprias regras internas antes de qualquer importação real.

## 4. Contrato usado como origem

- `versao_contrato`: `ocr_leitor.documento_fiscal.v1`
- `origem`: `OCR-LEITOR`

O contrato deve ser validado antes de qualquer consumo por sistema externo. Payloads fora da versão esperada não devem seguir para importação real sem uma etapa própria de migração ou validação.

## 5. Mapeamento inicial de campos

| Campo no OCR-LEITOR JSON | Significado | Possível destino no FechaMes | Obrigatório? | Observações |
|---|---|---|---|---|
| `documento.empresa` | Empresa/fornecedor identificado no documento | Fornecedor, descrição fiscal ou entidade relacionada | Sim | Deve ser revisado antes de importação real |
| `documento.numero_nf` | Número da nota/documento fiscal | Número do documento fiscal | Condicional | Pode ser usado junto com `chave_acesso` |
| `documento.chave_acesso` | Chave NF-e com 44 dígitos | Chave de acesso da NF-e | Condicional | Se existir, deve ter 44 dígitos numéricos |
| `documento.vencimento` | Data de vencimento | Vencimento financeiro/fiscal | Depende do fluxo | Formato deve ser confirmado antes da integração real |
| `documento.valor_total` | Valor total do documento | Valor do lançamento/documento | Sim | Deve ser validado numericamente |
| `revisao.revisado` | Indica revisão humana | Controle de aptidão para importação | Sim | Somente `revisado=True` deve seguir para integração |
| `revisao.revisado_por` | Operador responsável | Auditoria | Recomendado | Útil para rastreabilidade |
| `integracao.destino` | Destino pretendido | Identificador do módulo/importador | Sim | Exemplo atual: `fechames_fiscal` |
| `integracao.modo` | Modo de operação | Controle de segurança | Sim | Enquanto for teste, deve ser `simulado` |
| `metadados.arquivo_nome` | Nome do arquivo original | Auditoria, anexo ou referência | Recomendado | Não deve conter caminho sensível |

## 6. Campos que não devem ser usados para escrita direta

O payload do OCR-LEITOR não deve transportar comandos SQL, IDs internos do FechaMes, credenciais, caminhos locais sensíveis ou qualquer instrução de alteração estrutural.

Também não devem ser usados para escrita direta:

- nomes de tabelas internas do FechaMes;
- nomes de colunas internas do FechaMes;
- identificadores técnicos de registros do FechaMes;
- tokens, senhas ou variáveis de ambiente;
- caminhos absolutos da máquina local;
- instruções de criação, alteração ou exclusão de estrutura.

Qualquer mapeamento real deve passar por camada controlada de validação/importação, nunca por escrita direta originada pelo OCR-LEITOR.

## 7. Critérios para considerar um payload compatível

Um payload pode ser considerado compatível para avaliação futura quando atender aos seguintes critérios:

- contrato validado;
- origem `OCR-LEITOR`;
- `revisado=True`;
- empresa preenchida;
- `valor_total` válido;
- número NF ou chave de acesso presente;
- modo simulado em ambiente de teste;
- sem dados sensíveis indevidos.

Esses critérios indicam aptidão para validação de compatibilidade. Eles não autorizam importação real automática.

## 8. O que ainda falta antes de qualquer integração real

Fases futuras recomendadas antes de qualquer integração real:

- FECHAMES-VAL-02 — Validador de compatibilidade;
- FECHAMES-SANDBOX-01 — Teste isolado com arquivo JSON;
- FECHAMES-IMPORT-01 — Importador opcional e reversível, se aprovado.

Nenhuma dessas fases deve escrever em banco de produção sem aprovação explícita, modo simulado prévio e mecanismo de reversão.

## 9. Decisão arquitetural

O OCR-LEITOR deve permanecer como extrator, normalizador, validador e exportador de dados.

O FechaMes deve permanecer independente e dono das regras fiscais/operacionais.

A comunicação entre eles deve ocorrer somente por contrato validado e controlado.
