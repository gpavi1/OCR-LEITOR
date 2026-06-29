# RESET-BANCO-TESTE-01 — Limpeza Segura dos Registros de Teste do Banco MySQL

## 1. Objetivo da fase

Criar uma rotina segura para limpar registros de teste do banco MySQL local, com backup obrigatório, dry-run como padrão e confirmação explícita para execução real.

## 2. Diferença entre limpar arquivos e limpar banco

As fases anteriores (`OPS-OCR-01`) limpavam apenas arquivos físicos (imagens, JSONs, relatórios). O painel web, porém, lê os dados do banco MySQL. Mesmo depois de limpar as pastas, os registros no banco continuam aparecendo no painel.

Esta fase resolve isso: limpa os registros operacionais de teste do banco, mantendo clientes, configurações e schema intactos.

## 3. Por que o painel continua mostrando registros mesmo após limpar pastas

O fluxo do OCR-LEITOR:

1. Imagem entra → OCR extrai texto → parser extrai campos
2. Dados são salvos no banco MySQL (tabela `documentos`)
3. Dados são exportados para JSON (pasta `exports/`)
4. Painel web consulta o banco MySQL para exibir a lista

Quando `OPS-OCR-01` limpa as pastas, os arquivos exportados são removidos, mas os registros no banco permanecem. O painel continua exibindo os registros porque a origem da listagem é o banco, não os arquivos.

`RESET-BANCO-TESTE-01` preenche essa lacuna limpando os registros do banco.

## 4. Como rodar dry-run

Modo seguro (padrão). Apenas simula:

```bash
python scripts/reset_banco_teste.py
```

Ou explicitamente:

```bash
python scripts/reset_banco_teste.py --dry-run
```

O dry-run:
- Conecta ao banco
- Lista tabelas existentes
- Conta registros
- Gera backup completo em `_backup_banco_teste/reset_YYYYMMDD_HHMMSS/`
- Mostra o que seria apagado
- **Não altera nenhum registro**

## 5. Como rodar limpeza real

Exige duas confirmações:

```bash
python scripts/reset_banco_teste.py --confirmar --confirmacao "RESETAR_BANCO_TESTE"
```

A limpeza real:
- Executa os mesmos passos do dry-run
- Gera backup ANTES de qualquer alteração
- Executa DELETE em transação única
- Se algo falhar, faz rollback automático
- Gera relatório com estado antes/depois

## 6. Onde o backup é salvo

```
_backup_banco_teste/
  reset_20260628_143000/
    resumo_antes.json
    documentos.json           ← apenas se houver registros
    integracao_tentativas.json ← apenas se houver registros
    resumo_depois.json
    relatorio_reset_banco_teste.md
```

A pasta `_backup_banco_teste/` é ignorada pelo Git.

## 7. Como conferir resumo antes/depois

```bash
cat _backup_banco_teste/reset_20260628_143000/resumo_antes.json
cat _backup_banco_teste/reset_20260628_143000/resumo_depois.json
```

O relatório Markdown também contém a tabela comparativa.

## 8. O que o script limpa

Por padrão (seguro):

| Tabela | Limpa? |
|--------|--------|
| `integracao_tentativas` | Sim |
| `documentos` | Sim |

Com flag `--limpar-integracoes`:

| Tabela | Limpa? |
|--------|--------|
| `integracoes` | Sim (apenas com flag explícita) |

## 9. O que o script nunca limpa

| Tabela | Limpa? |
|--------|--------|
| `clientes` | **Nunca** |

O script também nunca executa DDL (ALTER, DROP, CREATE, TRUNCATE). Apenas DELETE.

## 10. Como recuperar dados usando backup JSON

Se precisar restaurar após uma limpeza:

```bash
# Exemplo para documentos
mysql -u ocr_app -p ocr_leitor -e "INSERT INTO documentos SELECT * FROM JSON_TABLE(...)"

# Ou use um script auxiliar para carregar o JSON de volta
```

Os arquivos JSON em `_backup_banco_teste/reset_*/` contêm todos os registros exportados antes da limpeza.

## 11. Riscos e cuidados

- O script nunca deve ser usado em produção.
- Sempre rode dry-run primeiro.
- Backup é obrigatório e automático.
- A limpeza usa transação: erro durante DELETE → rollback completo.
- A tabela `integracoes` contém configurações de integração (credenciais). Só limpe se tiver certeza.
- A tabela `clientes` é sempre preservada.

## 12. Próximo passo

`LOTE-VALIDA-OCR-01` — processamento em lote controlado e validação dos documentos reais.

---

`RESET-BANCO-TESTE-01` não alterou OCR engine.
Não alterou pipeline.
Não alterou parser.
Não alterou API.
Não alterou UI.
Não alterou requirements.
Não alterou schema do banco.
Não executou reset real sem confirmação explícita.
