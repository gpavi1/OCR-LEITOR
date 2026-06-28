# INST-OCR-01 — Plano de Instalação Windows em Máquina Limpa

## 1. Objetivo

Este documento define o plano inicial para que o OCR-LEITOR seja instalável em uma máquina Windows limpa, usada como máquina responsável pelo OCR no cliente.

O objetivo é orientar uma implantação segura, reproduzível e controlada, sem criar instalador automático nesta fase, sem alterar código do OCR-LEITOR e sem qualquer dependência operacional do FechaMes.

## 2. Modelo de implantação recomendado

O modelo recomendado inicial é:

- uma máquina responsável por cliente;
- OCR-LEITOR instalado localmente;
- MySQL local ou controlado;
- painel web acessível localmente/rede interna;
- documentos processados localmente;
- JSON exportado para integração futura;
- sem instalar OCR em todos os computadores.

Esse modelo reduz variação de ambiente, centraliza manutenção e facilita controle de dependências como Tesseract, MySQL e Python.

## 3. O que a máquina precisa ter

- Windows 10/11 ou Windows Server compatível.
- Acesso de administrador para instalação.
- Python compatível.
- Tesseract OCR.
- Idioma português do Tesseract.
- MySQL.
- Git ou pacote ZIP versionado.
- Navegador para acessar painel.
- Permissão em pastas locais.
- Backup local.

## 4. Ordem correta de instalação

1. Preparar pasta base, exemplo `C:\Projetos\OCR-LEITOR`.
2. Instalar Python.
3. Instalar Tesseract OCR.
4. Instalar idioma português do Tesseract.
5. Instalar MySQL.
6. Criar banco e usuário do OCR.
7. Baixar/extrair release do OCR-LEITOR.
8. Criar ambiente virtual `.venv`.
9. Instalar dependências Python.
10. Criar arquivo `.env` local a partir de `.env.example`.
11. Configurar `config/settings.json`.
12. Validar conexão MySQL.
13. Rodar testes.
14. Iniciar painel web local.
15. Validar processamento de documento teste.
16. Configurar operação 24h.

## 5. Dependências principais

- Python.
- `pip`.
- `venv`.
- Tesseract.
- Pacote de idioma `por`.
- MySQL.
- `mysql-connector-python`.
- `flask`.
- `waitress`.
- `python-dotenv`.
- `pytesseract`.
- `Pillow`.
- `opencv-python`.
- `pytest` para validação.

## 6. Pastas operacionais

- `input/`: entrada local de documentos a processar.
- `output/`: saída local de JSON e artefatos gerados.
- `processed/`: documentos processados com sucesso.
- `erro/`: documentos com erro ou pendência de correção.
- `logs/`: registros de execução e diagnóstico.
- `config/`: configurações controladas do projeto.
- `docs/`: documentação técnica e operacional.
- `web/`: painel web local do OCR-LEITOR.
- `database/`: scripts e componentes relacionados ao banco do OCR-LEITOR.

As pastas `input/`, `output/`, `processed/`, `erro/` e `logs/` são dados operacionais. Elas não devem ser versionadas com dados de cliente.

## 7. Arquivos sensíveis

- `.env` não deve ir para Git.
- `.venv` não deve ir para Git.
- `config/settings.json` pode conter caminho local e deve ser tratado com cuidado.
- Dados de cliente não devem entrar no repositório.
- ZIP de entrega deve ser gerado via `git archive` ou release controlada, nunca zipando a pasta inteira com `.env`, `.venv` ou dados operacionais.

## 8. Validações obrigatórias pós-instalação

Comandos e validações recomendadas:

```powershell
python --version
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pytest
```

Também devem ser validados:

- import de `web.app`;
- execução do Waitress;
- Tesseract instalado e acessível;
- idioma português do Tesseract disponível;
- conexão MySQL do OCR-LEITOR;
- painel web local abrindo corretamente;
- processamento de documento teste sem dado real.

## 9. Modelo de operação 24h

No piloto, a operação pode rodar com:

- máquina ligada;
- MySQL ativo;
- painel OCR ativo;
- rotina controlada;
- operador revisando documentos;
- sem API pública.

Serviço Windows ou Agendador de Tarefas podem ser fase futura, após validação da instalação manual e do comportamento em operação contínua.

## 10. O que ainda não será feito nesta fase

- Não criar instalador automático.
- Não criar serviço Windows.
- Não criar API pública.
- Não conectar com FechaMes.
- Não instalar em cliente real ainda.
- Não usar dados reais.

## 11. Próximas fases sugeridas

- INST-OCR-02 — Checklist técnico de dependências.
- INST-OCR-03 — Script de diagnóstico/doctor da instalação.
- INST-OCR-04 — Guia de instalação passo a passo.
- INST-OCR-05 — Pacote de release limpo.
- INST-OCR-06 — Inicialização 24h controlada.
