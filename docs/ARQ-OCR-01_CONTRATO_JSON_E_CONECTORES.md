# ARQ-OCR-01 — Contrato JSON e Arquitetura de Conectores

## 1. Objetivo

Definir a arquitetura inicial para que o OCR-LEITOR exporte documentos fiscais revisados para sistemas externos por meio de contrato JSON,
arquivo intermediário, API ou conector opcional em fases futuras.

O OCR-LEITOR deve atuar como origem confiável de dados documentais revisados. A saída principal deve ser um pacote JSON padronizado,
versionado e validável, capaz de ser consumido futuramente por destinos como FechaMes Fiscal, Monday, Google Sheets, ERPs ou APIs internas.

Esta fase é exclusivamente arquitetural. Ela não implementa conector real, não cria integração real com FechaMes Fiscal, não cria API pública,
não escreve em banco externo e não altera o processamento OCR/parser/core existente.

## 2. Princípios de segurança

- OCR-LEITOR permanece produto independente.
- FechaMes Fiscal permanece produto independente.
- OCR-LEITOR não escreve direto no banco do FechaMes.
- FechaMes não acessa diretamente o banco do OCR-LEITOR.
- Nenhum documento sai sem revisão humana.
- Toda tentativa de integração deve gerar histórico.
- Toda falha deve ser reversível ou reenfileirável.
- Integrações futuras devem ser opcionais, explícitas e auditáveis.
- Dados fiscais devem trafegar por pacote validado, nunca por acoplamento direto entre bancos.
- Qualquer importação real deve ter modo simulado validado antes.

## 3. Fluxo atual do OCR-LEITOR

Fluxo conceitual atual esperado para um documento fiscal dentro do OCR-LEITOR:

```text
Documento fiscal recebido
→ OCR local
→ extração de campos
→ geração de JSON interno
→ registro no MySQL do OCR-LEITOR
→ revisão humana
→ status pendente_integracao
→ fila de integração
→ histórico de tentativa
```

Responsabilidades por etapa:

- `Documento fiscal recebido`: entrada controlada de arquivo fiscal em ambiente local.
- `OCR local`: leitura do documento por mecanismo local, sem dependência obrigatória de serviço externo.
- `extração de campos`: identificação dos campos fiscais relevantes pelo parser do OCR-LEITOR.
- `geração de JSON interno`: montagem de estrutura padronizada para persistência, revisão e exportação futura.
- `registro no MySQL do OCR-LEITOR`: rastreabilidade interna do processamento no banco próprio do OCR-LEITOR.
- `revisão humana`: conferência obrigatória antes de qualquer saída para destino externo.
- `status pendente_integracao`: documento revisado e apto para entrar em fluxo de exportação.
- `fila de integração`: preparação futura para envio, simulação ou exportação local.
- `histórico de tentativa`: registro de cada tentativa, sucesso, falha ou reenfileiramento.

## 4. Fronteira entre sistemas

O OCR-LEITOR entrega um pacote JSON validado. O sistema externo consome esse pacote sem acessar diretamente o banco do OCR-LEITOR.

A fronteira entre sistemas deve ser o contrato JSON, não o banco de dados, não os modelos internos e não imports diretos entre projetos.
Essa decisão preserva independência, reduz risco operacional e permite que cada produto evolua sem quebrar o outro.

Para integração futura com FechaMes Fiscal, a responsabilidade do OCR-LEITOR deve terminar na geração ou entrega do pacote validado.
A responsabilidade do FechaMes Fiscal, ou de um importador intermediário, deve começar na leitura desse pacote e na aplicação das próprias regras internas.

Modelo de fronteira recomendado:

```text
OCR-LEITOR
  gera documento revisado
  valida contrato JSON
  exporta pacote

Fronteira segura
  arquivo JSON, conector opcional, importador, API ou fila

Sistema externo
  consome pacote
  valida compatibilidade
  decide importação conforme suas regras
```

## 5. Contrato JSON proposto

O contrato JSON deve ser versionado, autocontido e seguro para trafegar entre produtos sem exigir acesso direto ao banco do OCR-LEITOR.

Exemplo conceitual seguro, sem dado real:

```json
{
  "origem": "OCR-LEITOR",
  "versao_contrato": "ocr_leitor.documento_fiscal.v1",
  "documento": {
    "empresa": "EMPRESA EXEMPLO LTDA",
    "numero_nf": "123456",
    "chave_acesso": "00000000000000000000000000000000000000000000",
    "vencimento": "30/08/2026",
    "valor_total": "150.00"
  },
  "revisao": {
    "revisado": true,
    "revisado_por": "operador_local",
    "revisado_em": "2026-06-28T00:00:00"
  },
  "confianca": {
    "empresa": null,
    "numero_nf": null,
    "chave_acesso": null,
    "vencimento": null,
    "valor_total": null
  },
  "integracao": {
    "status": "pronto_para_destino",
    "destino": "fechames_fiscal",
    "modo": "simulado"
  },
  "metadados": {
    "arquivo_nome": "documento.pdf",
    "json_path": "output/json/documento.json",
    "gerado_em": "2026-06-28T00:00:00"
  }
}
```

Observações sobre o contrato:

- `origem` identifica que o pacote nasceu no OCR-LEITOR.
- `versao_contrato` permite evolução controlada sem quebrar consumidores futuros.
- `documento` contém os campos fiscais revisados e normalizados.
- `revisao` comprova que houve validação humana antes da saída.
- `confianca` preserva espaço para pontuação por campo sem bloquear a fase atual.
- `integracao` descreve intenção, destino e modo, sem executar integração real nesta fase.
- `metadados` permite rastrear arquivo, JSON gerado e data de geração.

## 6. Campos obrigatórios

Campos obrigatórios para o pacote exportável:

- `origem`
- `versao_contrato`
- `revisao.revisado = true`
- status interno `pendente_integracao`
- `documento.empresa`
- `documento.numero_nf` ou `documento.chave_acesso`

Campos recomendados:

- `documento.vencimento`
- `documento.valor_total`
- `metadados.arquivo_nome`
- `revisao.revisado_por`
- `revisao.revisado_em`

Regra mínima de saída:

- Um pacote não deve ser considerado pronto se `revisao.revisado` não for `true`.
- Um pacote não deve sair sem identificação clara da empresa.
- Um pacote não deve sair sem pelo menos `numero_nf` ou `chave_acesso`.
- Um pacote não deve ser exportado para destino real se ainda não estiver no status interno `pendente_integracao`.

## 7. Status previstos

Status internos do OCR-LEITOR:

- `recebido`
- `processando`
- `erro_ocr`
- `pendente_revisao`
- `pendente_integracao`
- `integrado`
- `falha_integracao`

Status do pacote de integração:

- `pronto_para_destino`
- `exportado_simulado`
- `enviado`
- `falha_envio`
- `rejeitado_destino`
- `reenfileirado`

Interpretação recomendada:

- `pendente_revisao`: documento ainda não pode sair do OCR-LEITOR.
- `pendente_integracao`: documento revisado, validado e apto para fila ou exportação futura.
- `pronto_para_destino`: pacote JSON gerado e validado, mas ainda sem envio real.
- `exportado_simulado`: pacote gravado em local seguro para validação, sem integração real.
- `reenfileirado`: falha recuperável tratada por nova tentativa controlada.

## 8. Estratégia antes do FechaMes

Antes de qualquer integração real com FechaMes Fiscal, a evolução deve ocorrer em três etapas:

1. Conector simulado: exporta JSON validado para pasta local segura.
2. Validador de contrato: confirma campos mínimos e formatos.
3. Validação de compatibilidade com FechaMes: compara formato, sem escrever no banco do FechaMes.

A etapa simulada deve provar que o OCR-LEITOR consegue gerar pacote consistente sem depender do FechaMes Fiscal.
A validação de contrato deve impedir que documentos incompletos avancem.
A validação de compatibilidade deve comparar nomes, formatos e regras de dados sem realizar importação real.

Critério de segurança para avançar:

- O pacote simulado deve ser gerado sem rede externa.
- O pacote simulado deve ser gerado sem credenciais reais.
- O pacote simulado deve ser testável em ambiente local.
- A compatibilidade com FechaMes deve ser validada sem escrita no banco do FechaMes.

## 9. Regras para futura integração com FechaMes

- Não escrever direto no banco do FechaMes.
- Não importar documentos não revisados.
- Não misturar clientes sem identificação clara.
- Não acoplar código entre os produtos.
- Usar conector, importador, API ou arquivo intermediário.
- Toda importação real precisa de modo simulado antes.
- Toda importação real precisa de confirmação humana ou flag explícita de produção.
- Toda tentativa real deve gerar histórico de execução.
- Toda falha deve permitir auditoria e reenfileiramento.
- Toda integração deve preservar rastreabilidade entre arquivo original, JSON exportado e destino.

Formato recomendado para integração futura:

```text
OCR-LEITOR → JSON validado → conector/importador/API/fila → FechaMes Fiscal
```

Formato proibido:

```text
OCR-LEITOR → escrita direta no banco do FechaMes
FechaMes Fiscal → leitura direta no banco do OCR-LEITOR
```

## 10. Próximas fases sugeridas

- ARQ-OCR-01-B — Exemplo JSON versionado em docs/exemplos
- ARQ-OCR-01-C — Teste de validação do contrato JSON
- CONN-SIM-01 — Conector simulado local
- FECHAMES-VAL-01 — Validação de compatibilidade sem tocar no banco do FechaMes
