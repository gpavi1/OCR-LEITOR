# INST-OCR-06 — Pacote de Release Limpo

## Objetivo

Criar um mecanismo seguro e guiado para gerar um pacote ZIP limpo do OCR-LEITOR para entrega ou instalação.

A release deve ser gerada exclusivamente a partir de arquivos versionados pelo Git, garantindo que não entrem no pacote arquivos locais, sensíveis ou operacionais.

## Como NÃO fazer

Não zipar a pasta do projeto manualmente pelo Explorer.

Zipar a pasta inteira inclui `.env`, `.venv/`, `input/`, `output/`, `processed/`, `erro/`, `logs/`, `__pycache__/`, `.pytest_cache/` e possíveis dados reais de cliente. Esses arquivos não pertencem a uma release limpa.

## Como gerar a release limpa

### Modo dry-run (padrão, seguro)

```powershell
.\.venv\Scripts\python.exe scripts\gerar_release_limpa.py
```

Esse modo:
- verifica se o diretório é um repositório Git válido;
- verifica se o working tree está limpo;
- mostra qual seria o nome e destino do ZIP;
- não cria ZIP, pasta ou altera nada.

### Gerar o ZIP com confirmação explícita

```powershell
.\.venv\Scripts\python.exe scripts\gerar_release_limpa.py --confirmar
```

Com `--confirmar`:
- valida que o working tree está limpo (se houver alteração local, bloqueia);
- executa `git archive --format=zip HEAD`;
- gera o ZIP em `dist/OCR-LEITOR-RELEASE-LIMPA.zip` (padrão);
- não inclui `.env`, `.venv/`, pastas operacionais, `__pycache__` ou dados de cliente.

### Personalizar destino e nome

```powershell
.\.venv\Scripts\python.exe scripts\gerar_release_limpa.py --confirmar --destino-dir .\releases --nome OCR-LEITOR-v1.0.0.zip
```

```powershell
.\.venv\Scripts\python.exe scripts\gerar_release_limpa.py --confirmar --base-dir C:\OCR-LEITOR --destino-dir C:\temp --nome entrega.zip
```

## O que o ZIP contém

Apenas arquivos versionados no commit `HEAD` do Git.

Isso inclui todo o código-fonte, documentação e testes versionados. Exclui automaticamente qualquer arquivo local ou não versionado.

## O que o ZIP NÃO contém

- `.env` – variáveis de ambiente locais
- `.venv/` – ambiente virtual Python local
- `config/settings.json` – configuração local
- `input/`, `output/`, `processed/`, `erro/`, `logs/` – pastas operacionais
- `__pycache__/`, `.pytest_cache/` – cache local
- dados reais de cliente

## O que o script não faz

- não instala Python, Tesseract ou MySQL
- não cria `.env` nem `config/settings.json`
- não instala dependências Python
- não executa `pip install`
- não acessa MySQL, Tesseract ou FechaMes
- não inicia serviço Windows
- não é instalador automático

## Após gerar o ZIP

1. Extrair em uma máquina limpa
2. Configurar `.env` manualmente (ver INST-OCR-04)
3. Instalar dependências manualmente (ver INST-OCR-02)
4. Executar `scripts\doctor_instalacao.py` para validar
5. Executar `pytest` para validar integridade

## Segurança operacional

- Sempre revisar o relatório do dry-run antes de usar `--confirmar`
- O pacote gerado é uma fotografia do repositório no momento da geração
- Para nova versão, commitar as alterações desejadas antes de gerar nova release
- Não versionar a pasta `dist/` ou qualquer ZIP gerado
