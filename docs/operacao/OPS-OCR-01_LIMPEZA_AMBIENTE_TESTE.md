# OPS-OCR-01 - Limpeza Segura do Ambiente de Testes

## 1. Objetivo da fase

Preparar o OCR-LEITOR para novos testes reais, movendo arquivos operacionais antigos para backup antes de limpar as pastas de trabalho.

## 2. O que o script limpa

O script atua somente nestas pastas operacionais:

- `input/`
- `processed/`
- `erro/`
- `output/json/`
- `exports/json/`
- `exports/markdown/`

Os arquivos encontrados nessas pastas sao movidos para `_backup_testes/limpeza_YYYYMMDD_HHMMSS/`.

## 3. O que o script nao limpa

- Banco MySQL.
- Schema ou migrations.
- OCR/parser/core.
- `ocr_pipeline_s1.py`.
- `requirements.txt`.
- API, painel ou rotas.
- FechaMes e integracoes externas.
- Pastas fora da raiz do projeto.

## 4. Arquivos fisicos x registros do banco

A limpeza mexe apenas em arquivos fisicos das pastas operacionais. Documentos antigos podem continuar aparecendo no painel porque esses registros vêm do MySQL. Reset de banco, se necessario, sera outra fase separada.

## 5. Como rodar em modo dry-run

```bash
python scripts/limpar_ambiente_teste.py --dry-run
```

No Windows, tambem e possivel usar:

```bat
8_LIMPAR_AMBIENTE_TESTE.bat --dry-run
```

O modo dry-run mostra o que seria movido, sem alterar arquivos.

## 6. Como rodar a limpeza real

```bash
python scripts/limpar_ambiente_teste.py
```

Ou pelo atalho:

```bat
8_LIMPAR_AMBIENTE_TESTE.bat
```

## 7. Onde o backup fica salvo

O backup fica em:

```text
_backup_testes/limpeza_YYYYMMDD_HHMMSS/
```

A estrutura interna preserva a pasta operacional original, por exemplo `input/arquivo.jpg` vira `_backup_testes/limpeza_YYYYMMDD_HHMMSS/input/arquivo.jpg`.

## 8. Como restaurar manualmente um arquivo

1. Abrir a pasta `_backup_testes/`.
2. Entrar na limpeza desejada.
3. Copiar ou mover o arquivo de volta para a pasta operacional correspondente.
4. Conferir manualmente antes de processar de novo.

## 9. Por que o banco nao e apagado nesta fase

OPS-OCR-01 serve apenas para preparar arquivos fisicos de teste. Apagar ou resetar banco pode remover rastreabilidade operacional e precisa de fase separada com regras proprias.

## 10. Proximas fases

- `DIAG-OCR-01` - auditoria assistida da extracao OCR/parser com documentos reais.
- `AJUSTE-OCR-01` - correcoes cirurgicas no OCR/parser somente apos diagnostico.

## 11. Avisos de escopo

- OPS-OCR-01 nao corrige extracao.
- OPS-OCR-01 nao altera OCR/parser.
- OPS-OCR-01 apenas prepara ambiente limpo para testes novos.
- Documentos antigos no painel podem continuar aparecendo porque vêm do MySQL.
- Reset de banco, se necessario, sera outra fase separada.
