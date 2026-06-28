# FECHAMES-IMPORT-PLANO-01 — Importador Opcional e Reversível

## 1. Objetivo

Este documento define o plano de um importador futuro, opcional e controlado, para que o FechaMes possa consumir JSON gerado pelo OCR-LEITOR sem acoplamento direto.

O objetivo é preservar a independência entre os produtos, manter a responsabilidade fiscal e operacional no FechaMes e garantir que qualquer consumo futuro de dados do OCR-LEITOR ocorra por contrato validado, revisão humana, confirmação explícita e possibilidade de reversão.

Esta fase é somente documentação. Ela não autoriza criação de código, API, importador real, integração real ou escrita em banco.

## 2. Decisão arquitetural

- OCR-LEITOR permanece como extrator, normalizador, validador e exportador de dados.
- FechaMes permanece como sistema dono das regras fiscais, financeiras e operacionais.
- OCR-LEITOR não escreve diretamente no banco do FechaMes.
- A comunicação deve ocorrer por JSON validado.
- O importador deve pertencer ao lado do FechaMes, não ao OCR-LEITOR.

## 3. Fluxo futuro proposto

Fluxo conceitual para uma fase futura, ainda sujeita a aprovação técnica:

```text
OCR-LEITOR
→ processa documento
→ operador revisa
→ monta payload JSON v1
→ valida contrato
→ valida compatibilidade com FechaMes
→ exporta JSON
→ FechaMes lê JSON
→ FechaMes valida novamente
→ usuário confirma
→ FechaMes grava usando suas próprias regras internas
```

O OCR-LEITOR encerra sua responsabilidade na geração/exportação do JSON validado. O FechaMes, em fase futura, deve ler o pacote e decidir se pode gravar usando suas próprias regras internas.

## 4. Regras obrigatórias do importador futuro

- Leitura manual ou controlada.
- Somente JSON com origem `OCR-LEITOR`.
- Somente `versao_contrato` `ocr_leitor.documento_fiscal.v1`.
- Somente `revisao.revisado=True`.
- Somente `integracao.destino=fechames_fiscal`.
- Em sandbox, somente `integracao.modo=simulado`.
- Validar empresa, `valor_total`, `numero_nf` ou `chave_acesso`.
- Bloquear dados reais durante sandbox.
- Exigir confirmação do usuário antes de gravar.
- Registrar log da tentativa.
- Permitir reversão ou desfazimento.
- Nunca aceitar comando SQL vindo do OCR.
- Nunca aceitar IDs internos do FechaMes vindos do OCR.

## 5. O que o OCR-LEITOR não deve fazer

- Não acessar banco do FechaMes.
- Não criar registros diretamente.
- Não alterar tabelas.
- Não chamar rotinas internas do FechaMes sem contrato.
- Não enviar credenciais.
- Não importar lote automaticamente.
- Não decidir regra fiscal.
- Não substituir validação humana.

## 6. O que o FechaMes deve fazer

- Ler o JSON.
- Validar contrato.
- Validar compatibilidade.
- Exibir prévia para o usuário.
- Permitir confirmar ou cancelar.
- Gravar somente após confirmação.
- Registrar origem OCR-LEITOR.
- Registrar arquivo importado.
- Registrar operador/data.
- Permitir rastreamento.

## 7. Etapas de segurança antes da gravação

- Abrir JSON.
- Validar estrutura.
- Validar campos obrigatórios.
- Validar modo.
- Validar duplicidade.
- Validar se número NF/chave já existe.
- Apresentar prévia.
- Solicitar confirmação.
- Gravar em transação controlada.
- Registrar log.
- Disponibilizar reversão.

## 8. Estratégia de reversão

Qualquer importação futura deve ter rastreabilidade suficiente para desfazer o lançamento criado, sem apagar histórico de auditoria.

A reversão deve preservar o registro de que houve tentativa de importação, quem executou, quando ocorreu, qual arquivo foi usado, qual payload foi lido e qual registro foi criado ou revertido.

O desfazimento não deve depender do OCR-LEITOR. Ele deve ser uma capacidade do lado do FechaMes ou do importador pertencente ao FechaMes.

## 9. Modos previstos

- `simulado`: leitura e validação, sem gravação.
- `homologacao`: gravação em base de teste.
- `producao`: somente após aprovação formal, backup e logs.

## 10. Critérios para liberar desenvolvimento real

- Sandbox validado.
- Plano aprovado.
- Backup definido.
- Ambiente de homologação separado.
- Importador com confirmação manual.
- Testes automatizados.
- Rollback definido.
- Nenhuma alteração estrutural obrigatória no FechaMes.

## 11. Decisão final desta fase

Esta fase não autoriza criação de importador real.

Esta fase apenas documenta como o importador deverá funcionar futuramente.
