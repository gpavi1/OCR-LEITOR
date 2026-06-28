# INST-OCR-05 — Preparação Local Guiada

## Objetivo

Este documento descreve o uso do script `scripts/preparar_instalacao_local.py`, criado para auxiliar a preparação local do OCR-LEITOR em uma máquina Windows.

O script é seguro por padrão: em execução normal ele roda em modo `dry-run`, apenas mostra o que faria e não altera arquivos ou pastas.

## Modo dry-run padrão

Comando recomendado para inspeção inicial:

```powershell
.\.venv\Scripts\python.exe scripts\preparar_instalacao_local.py
```

Nesse modo, o script:

- mostra quais pastas operacionais seriam criadas;
- informa se `.env` está ausente;
- informa se `config/settings.json` está ausente;
- não cria arquivos;
- não cria pastas;
- não altera nada no projeto.

## Uso com confirmação explícita

Para criar apenas as pastas operacionais seguras, usar:

```powershell
.\.venv\Scripts\python.exe scripts\preparar_instalacao_local.py --confirmar
```

Com `--confirmar`, o script cria somente estas pastas se estiverem ausentes:

- `input/`
- `output/`
- `processed/`
- `erro/`
- `logs/`
- `config/`

## O que o script não faz

O script não instala Python, Tesseract ou MySQL.

O script não instala dependências Python, não executa `pip`, não cria banco de dados e não inicia serviço Windows.

O script não cria `.env`, não cria `config/settings.json` e não copia `.env.example`.

O script não acessa MySQL, não acessa Tesseract e não mexe no FechaMes.

## Base directory customizada

Para testar ou preparar uma pasta específica, informar `--base-dir`:

```powershell
.\.venv\Scripts\python.exe scripts\preparar_instalacao_local.py --base-dir C:\Projetos\OCR-LEITOR
```

Para criar as pastas nessa base, combinar com `--confirmar`:

```powershell
.\.venv\Scripts\python.exe scripts\preparar_instalacao_local.py --base-dir C:\Projetos\OCR-LEITOR --confirmar
```

## Segurança operacional

Antes de usar `--confirmar`, revisar o relatório exibido em dry-run.

O script não deve ser tratado como instalador completo. Ele é apenas uma preparação local mínima de estrutura de pastas.

Instalação de dependências externas, criação de banco, configuração do `.env` e validação final continuam sendo etapas manuais e controladas.
