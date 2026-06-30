# INSTALADOR-COMPACTO-OCR-01

## Objetivo

Disponibilizar uma entrada simples para preparacao, verificacao e update controlado do OCR-LEITOR:

```text
INSTALAR-OCR-LEITOR.cmd
```

O instalador compacto organiza os modos `demo`, `cliente`, `update` e `verificar` sem alterar o nucleo do OCR.

## Operacao Diaria vs Instalacao

- `OCR-LEITOR.cmd`: menu de operacao diaria para usar o sistema local.
- `INSTALAR-OCR-LEITOR.cmd`: entrada de instalacao, preparacao de ambiente, verificacao e update controlado.

## Modo Demo

Destino recomendado:

```text
C:\OCR-LEITOR-DEMO
```

Uso em dry-run:

```powershell
INSTALAR-OCR-LEITOR.cmd demo --dry-run
```

Uso confirmado:

```powershell
INSTALAR-OCR-LEITOR.cmd demo --confirmar
```

O modo demo cria estrutura isolada, gera `.env` ficticio seguro, usa `ocr_leitor_demo`, nao exige token real e orienta abrir `OCR-LEITOR.cmd` para operacao.

## Modo Cliente

Destino recomendado:

```text
C:\OCR-LEITOR
```

Uso em dry-run:

```powershell
INSTALAR-OCR-LEITOR.cmd cliente --dry-run
```

Uso confirmado:

```powershell
INSTALAR-OCR-LEITOR.cmd cliente --confirmar
```

O modo cliente valida caminho, prepara pastas, orienta criacao de `.venv`, instalacao de requirements, configuracao segura de `.env`, validacao de Tesseract, MySQL e doctor.

## Modo Update

Destino recomendado:

```text
C:\OCR-LEITOR
```

Uso em dry-run:

```powershell
INSTALAR-OCR-LEITOR.cmd update --dry-run
```

Uso confirmado:

```powershell
INSTALAR-OCR-LEITOR.cmd update --confirmar
```

O modo update exige instalacao existente, exige `.env`, bloqueia update sobre pasta demo e executa backup operacional antes de qualquer etapa confirmada.

Nesta fase, o update nao baixa arquivos da internet, nao executa `git pull` e nao aplica update remoto. A copia dos arquivos novos deve vir de pacote local/release.

## Modo Verificar

```powershell
INSTALAR-OCR-LEITOR.cmd verificar
```

O modo verificar encadeia validacoes locais existentes:

- `scripts/doctor_instalacao.py`.
- `scripts/validador_tesseract.py`.
- `scripts/validador_mysql.py`.

Ele nao altera arquivos.

## Caminhos Recomendados

- Cliente: `C:\OCR-LEITOR`.
- Demo: `C:\OCR-LEITOR-DEMO`.

Evite OneDrive, Desktop, Area de Trabalho, Downloads, Temp e pastas dentro de outro repositorio Git.

## O Que o Instalador Nunca Faz

- Nao chama Monday.
- Nao chama API externa.
- Nao executa `git pull`.
- Nao baixa arquivos da internet.
- Nao apaga `.env`.
- Nao apaga `config/settings.json`.
- Nao apaga banco.
- Nao apaga `input`, `output`, `processed`, `erro`, `logs`, `exports` ou `backups`.
- Nao altera parser.
- Nao altera OCR pipeline.
- Nao altera conectores.

## Dry-Run

Todos os modos de preparacao aceitam dry-run:

```powershell
INSTALAR-OCR-LEITOR.cmd demo --dry-run
INSTALAR-OCR-LEITOR.cmd cliente --dry-run
INSTALAR-OCR-LEITOR.cmd update --dry-run
```

Dry-run lista acoes e nao aplica alteracoes reais.

## Instalacao Confirmada

Use `--confirmar` apenas depois de validar o destino:

```powershell
INSTALAR-OCR-LEITOR.cmd demo --confirmar
INSTALAR-OCR-LEITOR.cmd cliente --confirmar
```

## Update e Backup

O update confirmado chama `scripts/backup_ocr.py` antes de qualquer alteracao.

Se o backup falhar, o update aborta.

## Checklist Pos-Instalacao

- Rodar `INSTALAR-OCR-LEITOR.cmd verificar`.
- Validar Tesseract e idiomas.
- Validar MySQL.
- Conferir `.env` sem expor segredos.
- Abrir `OCR-LEITOR.cmd`.
- Confirmar pastas operacionais.

## Checklist Pos-Update

- Confirmar backup criado em `backups/`.
- Rodar `INSTALAR-OCR-LEITOR.cmd verificar`.
- Confirmar que `.env` foi preservado.
- Confirmar que dados operacionais foram preservados.
- Abrir `OCR-LEITOR.cmd`.

## Seguranca

- Nao chama Monday.
- Nao expoe token.
- Nao apaga `.env`.
- Nao apaga dados operacionais.
- Nao transforma update em operacao sem backup.
