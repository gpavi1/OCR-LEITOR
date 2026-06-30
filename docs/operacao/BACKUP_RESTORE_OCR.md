# BACKUP-RESTORE-OCR-01

## Objetivo

Criar uma rotina operacional segura para backup e restore do OCR-LEITOR antes do futuro instalador compacto e antes de qualquer modo UPDATE.

Esta fase nao instala, nao atualiza, nao chama Monday, nao chama API externa, nao altera schema, nao altera parser, nao altera OCR pipeline e nao altera conectores.

## O Que o Backup Inclui

- `manifest.json`.
- `suporte/diagnostico.txt`.
- `database/schema.sql`, se existir.
- `database/resumo.json`.
- `database/dados.json`, se o backup de banco funcionar.
- `config/settings.json`, se existir.
- `config/env_mascarado.txt`, somente com `--incluir-env-mascarado`.
- `arquivos/input/`.
- `arquivos/output/`.
- `arquivos/processed/`.
- `arquivos/erro/`.
- `arquivos/logs/`.
- `arquivos/exports/`.

## O Que o Backup Nunca Inclui

- `.env` em claro.
- `.venv`.
- `__pycache__`.
- `.pytest_cache`.
- `dist`.
- `backups`.
- `_backup`.
- `_backup_testes`.
- `_backup_banco_teste`.
- `*.pyc`.
- Arquivo `.log` com indicio de segredo.

## Backup Dry-Run

```powershell
.\.venv\Scripts\python.exe scripts\backup_ocr.py --dry-run
```

O dry-run lista o que seria incluido, mas nao cria ZIP.

## Backup Real

```powershell
.\.venv\Scripts\python.exe scripts\backup_ocr.py --confirmar
```

Sem `--destino`, o ZIP sera criado em `backups/` com nome no formato:

```text
OCR-LEITOR-BACKUP-YYYYMMDD-HHMMSS.zip
```

Para escolher uma pasta de saida:

```powershell
.\.venv\Scripts\python.exe scripts\backup_ocr.py --confirmar --destino C:\OCR-LEITOR-BACKUPS
```

## Incluir `.env` Mascarado

O `.env` nunca entra em claro no ZIP.

Para incluir uma versao mascarada:

```powershell
.\.venv\Scripts\python.exe scripts\backup_ocr.py --confirmar --incluir-env-mascarado
```

O arquivo gerado sera `config/env_mascarado.txt`, com valores sensiveis substituidos por `***`.

## Validar Backup

Use restore em dry-run para validar o ZIP sem alterar arquivos:

```powershell
.\.venv\Scripts\python.exe scripts\restore_ocr.py --backup backups\OCR-LEITOR-BACKUP-YYYYMMDD-HHMMSS.zip --dry-run --restaurar-arquivos
```

## Restore Dry-Run

```powershell
.\.venv\Scripts\python.exe scripts\restore_ocr.py --backup backups\OCR-LEITOR-BACKUP-YYYYMMDD-HHMMSS.zip --dry-run --restaurar-arquivos
```

O dry-run abre o ZIP, valida `manifest.json`, lista entradas restauraveis e nao escreve nenhum arquivo.

## Restore Real

Restore real exige `--confirmar` e confirmacao textual exata:

```text
RESTAURAR BACKUP
```

Exemplo para restaurar arquivos operacionais:

```powershell
.\.venv\Scripts\python.exe scripts\restore_ocr.py --backup backups\OCR-LEITOR-BACKUP-YYYYMMDD-HHMMSS.zip --confirmar --confirmacao "RESTAURAR BACKUP" --restaurar-arquivos
```

Antes de restaurar, o script cria um backup de seguranca em `backups/restore-seguranca-YYYYMMDD-HHMMSS/` para arquivos existentes que seriam sobrescritos.

## Banco

O backup tenta exportar o banco MySQL para JSON usando as variaveis de `.env`.

Tabelas conhecidas:

- `clientes`.
- `documentos`.
- `integracoes`.
- `integracao_tentativas`.

Para ignorar banco no backup:

```powershell
.\.venv\Scripts\python.exe scripts\backup_ocr.py --confirmar --sem-banco
```

Se a exportacao falhar, o ZIP ainda pode ser gerado com aviso em `manifest.json` e `database/resumo.json`.

Restore real de banco exige flag explicita:

```powershell
.\.venv\Scripts\python.exe scripts\restore_ocr.py --backup backups\OCR-LEITOR-BACKUP-YYYYMMDD-HHMMSS.zip --dry-run --restaurar-banco
```

Nesta fase, restore real de banco fica bloqueado de forma controlada ate existir rotina segura validada. Nunca altere banco sem confirmacao forte e backup anterior.

## Update Futuro

O futuro modo UPDATE do instalador compacto deve chamar backup operacional antes de qualquer alteracao.

Se o backup falhar, o update deve abortar.

## Seguranca

- Nao commitar ZIP de backup.
- Nao enviar backup com dados reais sem autorizacao.
- Nao expor token.
- Nao expor senha.
- Validar o ZIP em dry-run antes de qualquer restore real.
- Nunca restaurar `.env` em claro.
