# INST-OCR-02 — Checklist Técnico de Dependências

## 1. Objetivo

Este checklist define o que precisa existir em uma máquina Windows limpa antes de instalar o OCR-LEITOR.

O objetivo é reduzir falhas de implantação, padronizar o ambiente e permitir validação técnica antes de qualquer operação com documentos de cliente.

## 2. Perfil da máquina recomendada

- Windows 10/11 ou Windows Server compatível.
- Usuário com permissão administrativa.
- Máquina ligada durante operação.
- Acesso local ou remoto para suporte.
- Espaço em disco para documentos, logs e banco.
- Navegador instalado.
- Rede local estável, se o painel for acessado por outros computadores.

## 3. Dependências de sistema

- Python compatível.
- `pip`.
- `venv`.
- Tesseract OCR.
- Idioma português do Tesseract.
- MySQL Server.
- Git opcional.
- Editor simples opcional.
- Navegador.

## 4. Dependências Python do projeto

- `pytesseract`.
- `pdf2image`.
- `opencv-python`.
- `Pillow`.
- `requests`.
- `python-dotenv`.
- `mysql-connector-python`.
- `flask`.
- `waitress`.
- `pytest` para validação.

## 5. Dependências externas importantes

- Tesseract precisa estar instalado no Windows.
- Caminho do executável do Tesseract deve ser configurado.
- Idioma `por` precisa existir.
- MySQL precisa estar ativo.
- Usuário e senha do banco devem ser criados.
- Banco `ocr_leitor` deve existir.
- Variáveis locais devem estar no `.env`.

## 6. Pastas que devem existir na instalação

- `input/`: entrada de documentos a processar.
- `output/`: saída de JSON e artefatos gerados.
- `processed/`: documentos processados com sucesso.
- `erro/`: documentos com erro ou pendência.
- `logs/`: registros de execução e diagnóstico.
- `config/`: arquivos de configuração do OCR-LEITOR.

Essas pastas fazem parte da operação local. Dados de cliente e arquivos processados não devem ser versionados.

## 7. Arquivos de configuração esperados

- `.env` local.
- `.env.example` como referência.
- `config/settings.json`.
- `database/schema.sql`.
- `requirements.txt`.
- `requirements.add.txt`, se usado.

## 8. Verificações manuais obrigatórias

Comandos e validações recomendadas:

```powershell
python --version
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
.\.venv\Scripts\python.exe -m pytest
```

Também devem ser verificados:

- testar importação de `web.app`;
- testar Waitress;
- testar Tesseract;
- testar conexão MySQL.

## 9. Riscos comuns em máquina limpa

- Python não estar no PATH.
- Tesseract não instalado.
- Idioma português ausente.
- MySQL parado.
- Usuário do banco sem permissão.
- `.env` ausente.
- `.venv` copiada de outra máquina.
- Pastas operacionais ausentes.
- Firewall bloqueando acesso ao painel.
- Porta 5000 ocupada.

## 10. Critérios mínimos para considerar a máquina pronta

- Python local funcionando.
- `.venv` criada na própria máquina.
- Dependências instaladas.
- Tesseract validado.
- MySQL validado.
- Testes passando.
- Painel web inicia.
- Documento teste pode ser processado.
- Nenhuma credencial versionada.
- Nenhuma pasta operacional no Git.

## 11. Próxima fase

A próxima fase sugerida é INST-OCR-03 — Script de diagnóstico/doctor da instalação.
