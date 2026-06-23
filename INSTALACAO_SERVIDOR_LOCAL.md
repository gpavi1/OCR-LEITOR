# OCR-LEITOR — Instalação em servidor local Windows

Este guia será usado para instalar o OCR-LEITOR em uma VM ou computador da empresa que ficará ligado como servidor local.

## Ambiente recomendado

Pasta:

C:\Projetos\OCR-LEITOR

Não instalar em OneDrive.

## Programas necessários

- Python
- Git
- MySQL Server
- MySQL Workbench
- Tesseract OCR
- Idioma português do Tesseract
- Dependências Python do projeto

## Fluxo do sistema

Imagem/PDF
-> OCR
-> JSON padrão
-> MySQL
-> Painel Web local
-> Revisão humana
-> Exportação CSV
-> Futuras integrações

## Instalação básica

1. Clonar ou copiar o projeto para C:\Projetos\OCR-LEITOR
2. Criar ambiente virtual
3. Instalar dependências
4. Instalar Tesseract
5. Criar banco MySQL
6. Criar arquivo .env local
7. Rodar teste de conexão com MySQL
8. Rodar OCR
9. Rodar painel com Waitress

## Rodar painel local

.\INICIAR_WEB_LOCAL.bat

Acesso:

http://127.0.0.1:5000

## Rodar painel na rede interna

.\INICIAR_WEB_REDE_INTERNA.bat

Acesso:

http://IP-DO-SERVIDOR:5000

Se usar Radmin VPN, acessar pelo IP da VPN.

## Cuidados

- Não expor na internet pública
- Não subir .env para GitHub
- Não usar usuário root no sistema
- Não instalar dentro do OneDrive
- Fazer backup do MySQL
- Fazer backup de output/json, processed e erro

## Próximas etapas

- Login simples no painel
- Suporte PDF
- Upload pela tela
- Exportação Excel
- Conector Monday/ERP
- Instalação como serviço do Windows
