# INST-OCR-04 — Guia de Instalação Passo a Passo

## 1. Objetivo

Este guia orienta a instalação do OCR-LEITOR em uma máquina Windows limpa, usada como máquina responsável pelo OCR no cliente.

O objetivo é deixar clara a ordem correta de preparação do ambiente, instalação das dependências, configuração local e validações obrigatórias antes de qualquer operação com documentos de cliente.

## 2. Modelo recomendado

O modelo recomendado para implantação inicial é:

- uma máquina responsável por cliente;
- OCR-LEITOR instalado localmente;
- MySQL local/controlado;
- painel web local ou rede interna;
- operação 24h controlada;
- sem instalação em todos os computadores;
- sem API pública nesta fase.

## 3. Ordem geral de instalação

1. Preparar Windows e permissões.
2. Criar pasta base `C:\Projetos\OCR-LEITOR`.
3. Instalar Python.
4. Instalar Tesseract OCR.
5. Instalar idioma português do Tesseract.
6. Instalar MySQL Server.
7. Criar banco e usuário do OCR.
8. Baixar/extrair release limpa do OCR-LEITOR.
9. Criar `.venv` na própria máquina.
10. Instalar `requirements.txt`.
11. Instalar `requirements.add.txt`.
12. Criar `.env` local a partir de `.env.example`.
13. Configurar `config/settings.json`.
14. Criar/validar pastas operacionais.
15. Rodar doctor de instalação.
16. Rodar `pytest`.
17. Iniciar painel web local.
18. Processar documento teste.
19. Validar operação 24h.

## 4. Comandos base sugeridos

Comandos PowerShell de referência, sem caráter de instalador automático:

```powershell
cd C:\Projetos\OCR-LEITOR
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r requirements.add.txt
.\.venv\Scripts\python.exe scripts\doctor_instalacao.py
.\.venv\Scripts\python.exe -m pytest
```

Esses comandos pressupõem que Python, Tesseract e MySQL já foram instalados corretamente no Windows.

## 5. Dependências críticas

- `requirements.txt` contém dependências OCR/imagem.
- `requirements.add.txt` contém dependências web/banco.
- Os dois precisam ser instalados para operação completa.
- Tesseract é dependência externa do Windows.
- MySQL é dependência externa do banco.

## 6. Configuração local

- `.env` deve ser criado localmente.
- `.env` nunca deve ser versionado.
- `config/settings.json` deve apontar para o caminho local do Tesseract.
- Banco MySQL deve usar usuário próprio do OCR.
- Dados reais não devem entrar no Git.

## 7. Validação com doctor

Rodar o doctor de instalação:

```powershell
.\.venv\Scripts\python.exe scripts\doctor_instalacao.py
```

O doctor:

- não instala nada;
- não altera arquivos;
- não cria banco;
- não conecta no FechaMes;
- apenas mostra `OK`, `AVISO` ou `ERRO`.

## 8. Validação com testes

Os testes devem passar antes de operar:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Falhas em testes devem ser tratadas antes de iniciar uso operacional.

## 9. Inicialização web local

Comando de referência para iniciar o painel web local:

```powershell
.\.venv\Scripts\python.exe -m waitress --listen=127.0.0.1:5000 web.app:app
```

Acesso local:

```text
http://127.0.0.1:5000
```

## 10. Instalação em rede interna

O acesso por rede interna deve ser uma fase controlada, usando host apropriado, firewall validado e sem exposição pública.

Antes de liberar acesso interno, validar:

- endereço IP da máquina OCR;
- porta configurada;
- regras de firewall;
- acesso apenas pela rede autorizada;
- ausência de exposição pública.

## 11. Erros comuns

- Python não encontrado.
- `.venv` copiada de outra máquina.
- Tesseract fora do PATH.
- Idioma `por` ausente.
- `pytesseract`, `PIL` ou `cv2` ausentes.
- MySQL parado.
- `.env` ausente.
- Porta 5000 ocupada.
- Firewall bloqueando.
- `requirements` incompletos.

## 12. Critérios para instalação aprovada

- Doctor sem `ERRO` crítico.
- `pytest` passando.
- `web.app` importa.
- Waitress inicia.
- Tesseract validado.
- MySQL validado.
- Painel abre.
- Documento teste processa.
- Nenhum dado sensível versionado.

## 13. O que ainda não faz parte desta fase

- Instalador automático.
- Serviço Windows.
- Agendador.
- API pública.
- Integração real com FechaMes.
- Importação real.
- Cliente real em produção.

## 14. Próxima fase

A próxima fase sugerida é INST-OCR-05 — Script guiado de preparação local, ainda com confirmação e sem instalar dependências externas automaticamente.
