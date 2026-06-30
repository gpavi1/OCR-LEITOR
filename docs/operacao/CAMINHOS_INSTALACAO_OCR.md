# CAMINHOS-INSTALACAO-OCR

## Objetivo

Definir a base tecnica de caminhos seguros para a futura instalacao compacta do OCR-LEITOR, separando os modos CLIENTE, DEMO e UPDATE.

Esta fase apenas documenta e valida caminhos. Ela nao instala, nao atualiza, nao faz backup, nao restaura, nao chama Monday, nao altera banco e nao altera dados operacionais.

## Caminho Padrao Cliente

```text
C:\OCR-LEITOR
```

Use este caminho para uma instalacao real de cliente.

## Caminho Padrao Demo

```text
C:\OCR-LEITOR-DEMO
```

Use este caminho para ambiente demonstrativo, testes guiados e validacoes sem credenciais reais.

## Caminhos Nao Recomendados

Evite instalar o OCR-LEITOR em:

- OneDrive.
- Desktop.
- Area de Trabalho.
- Downloads.
- Temp.
- Pasta dentro de outro projeto Git.

Esses locais aumentam risco de sincronizacao parcial, exclusao acidental, conflito de arquivos, permissao instavel ou mistura com codigo de desenvolvimento.

## Estrutura de Pastas Recomendada

- `input`
- `output`
- `processed`
- `erro`
- `logs`
- `exports`
- `backups`
- `config`
- `database`
- `web`
- `scripts`
- `conectores`
- `services`

## Separacao de Responsabilidades

- Codigo: `web`, `scripts`, `conectores`, `services`, `database` e arquivos Python da aplicacao.
- Configuracao sensivel: `.env` e `config/settings.json`.
- Dados operacionais: `input`, `output`, `processed`, `erro`, `logs` e `exports`.
- Backups: `backups`.
- Releases: pacotes gerados em area separada, sem misturar com dados reais do cliente.

## Regra do Modo DEMO

O modo DEMO deve usar preferencialmente:

```text
C:\OCR-LEITOR-DEMO
```

O modo DEMO nao deve depender de token real, banco real de cliente ou chamadas externas. Se o caminho de cliente real for usado em modo DEMO, o sistema deve alertar para evitar mistura entre demonstracao e operacao real.

## Regra do Modo CLIENTE

O modo CLIENTE deve usar preferencialmente:

```text
C:\OCR-LEITOR
```

O modo CLIENTE deve evitar OneDrive, Desktop, Area de Trabalho, Downloads, Temp e pastas dentro de outro repositorio Git. A instalacao real deve manter dados operacionais e configuracao sensivel fora de locais sincronizados ou temporarios.

## Regra do Modo UPDATE

O modo UPDATE deve rodar somente sobre uma instalacao existente detectada por sinais locais, como `.env`, `OCR-LEITOR.cmd`, `web/app.py`, `database/schema.sql`, pastas operacionais ou o futuro marcador `.ocr_leitor_install.json`.

```text
Update so deve existir depois do BACKUP-RESTORE-OCR-01.
```

Antes de existir fluxo de backup/restore, nenhum update automatico deve ser implementado.

## Dados Que Nunca Podem Ser Apagados

- `.env`
- `config/settings.json`
- banco MySQL
- `input`
- `output`
- `processed`
- `erro`
- `logs`
- `exports`
- `backups`

## Checklist Antes de Instalar

- Confirmar se a instalacao e CLIENTE ou DEMO.
- Usar `C:\OCR-LEITOR` para CLIENTE.
- Usar `C:\OCR-LEITOR-DEMO` para DEMO.
- Evitar OneDrive, Desktop, Area de Trabalho, Downloads e Temp.
- Confirmar que o caminho nao esta dentro de outro projeto Git.
- Confirmar que nao ha dados reais no destino escolhido.
- Rodar o doctor de instalacao.

## Checklist Antes de Atualizar

- Confirmar que o modo e UPDATE.
- Confirmar que existe instalacao anterior no destino.
- Confirmar que o BACKUP-RESTORE-OCR-01 ja existe.
- Criar backup antes de qualquer alteracao.
- Validar `.env`, `config/settings.json`, banco MySQL e pastas operacionais.
- Abortar se o backup falhar.

## Checklist Pos-Instalacao

- Rodar o doctor de instalacao.
- Validar `.env` sem expor segredos.
- Validar Tesseract.
- Validar MySQL.
- Confirmar existencia das pastas operacionais.
- Confirmar que logs e exports estao no caminho correto.

## O Que Esta Fase Nao Faz

- Nao instala.
- Nao atualiza.
- Nao faz backup.
- Nao restaura.
- Nao chama Monday.
- Nao altera banco.
- Nao altera parser.
- Nao altera OCR pipeline.
- Nao altera conectores.
