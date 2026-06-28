# FECHAMES-SANDBOX-01 - Pacote JSON sandbox

Este diretório contém um pacote JSON sandbox totalmente fictício para teste futuro de leitura controlada por uma cópia ou ambiente isolado do FechaMes.

O arquivo `fechames_documento_fiscal_v1.sandbox.json` não deve ser usado com cliente real, dado real, nota fiscal real ou ambiente de produção.

Este pacote não escreve no FechaMes, não altera banco de dados, não cria importador e não representa integração real.

Finalidade do pacote:

- permitir validação futura de leitura controlada;
- exercitar o contrato `ocr_leitor.documento_fiscal.v1` com dados fictícios;
- confirmar compatibilidade lógica antes de qualquer fase de importação;
- manter o teste restrito a documentação e payload estático.

Configuração declarada no JSON:

- destino: `fechames_fiscal`;
- modo: `simulado`.

Qualquer importação real futura precisa de nova fase aprovada, validação adicional, modo simulado prévio e confirmação explícita de operação em produção.
