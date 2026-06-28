# FECHAMES-SANDBOX-02 — Checklist de Leitura Controlada

## 1. Objetivo

Este checklist orienta uma futura leitura controlada do pacote JSON sandbox pelo FechaMes, sem importação real e sem alteração estrutural.

A finalidade é validar formato, campos e regras mínimas de segurança antes de qualquer plano de importação. Esta fase não cria código, API, importador, integração real ou escrita em banco.

## 2. Arquivo sandbox de referência

Arquivo de referência para leitura controlada futura:

```text
docs/sandbox/fechames_documento_fiscal_v1.sandbox.json
```

Esse arquivo contém dados fictícios e deve ser usado apenas como pacote estático de validação.

## 3. Regras de segurança

- Não usar cliente real.
- Não usar banco real do FechaMes.
- Não escrever no banco do FechaMes.
- Não alterar estrutura pronta.
- Não criar importação automática.
- Não processar lote real.
- Não usar credenciais reais.
- Manter modo simulado.

## 4. Pré-condições

- OCR-LEITOR com testes passando.
- Payload sandbox validado.
- Contrato `ocr_leitor.documento_fiscal.v1` validado.
- Compatibilidade com destino `fechames_fiscal` validada.
- Ambiente FechaMes separado/sandbox, quando existir.
- Backup antes de qualquer teste futuro.

## 5. O que o FechaMes poderá fazer futuramente

Em uma fase futura aprovada, o FechaMes poderá apenas ler o arquivo JSON sandbox para validar formato e campos, sem gravar nada.

A leitura controlada deve confirmar se o payload consegue ser interpretado por uma camada isolada, sem criar lançamento, cliente, fornecedor, conta, financeiro ou qualquer registro definitivo.

## 6. O que o FechaMes não deve fazer nessa fase

- Não importar definitivamente.
- Não gravar lançamento.
- Não criar cliente/fornecedor real.
- Não alterar contas.
- Não alterar tabelas.
- Não gerar financeiro.
- Não mover arquivos reais.

## 7. Critérios de aprovação da leitura sandbox

- JSON lido sem erro.
- Origem reconhecida como `OCR-LEITOR`.
- Versão do contrato reconhecida.
- Empresa lida.
- Número NF ou chave lida.
- Valor total lido.
- Modo simulado respeitado.
- Nenhuma gravação realizada.

## 8. Critérios de bloqueio

- Tentativa de escrita direta.
- Dado real detectado.
- Modo diferente de simulado.
- Contrato inválido.
- Erro de leitura.
- Necessidade de alterar estrutura do FechaMes.

## 9. Próxima fase possível

A próxima fase só poderá ser FECHAMES-SANDBOX-03 ou FECHAMES-IMPORT-PLANO-01, dependendo da decisão técnica.

Ainda não é permitido criar importador real.
