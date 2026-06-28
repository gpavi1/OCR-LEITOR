# UPLOAD-OCR-02 — Processamento Controlado do Documento Enviado

## Objetivo

Permitir que o usuário acione manualmente o processamento OCR dos documentos enviados para a pasta `input/` diretamente pelo painel web, sem precisar executar scripts manualmente.

## Separação entre upload e processamento

- **Upload (UPLOAD-OCR-01)**: salva o arquivo com segurança na pasta `input/`. Não processa OCR.
- **Processamento (UPLOAD-OCR-02)**: lê os arquivos de `input/`, executa OCR, salva JSON em `output/json/`, registra no banco MySQL e move os arquivos para `processed/` ou `erro/`.

As etapas são independentes. O usuário envia os arquivos primeiro e depois clica em "Processar arquivos enviados".

## Fluxo implementado

1. Usuário envia arquivos via `/upload` (UPLOAD-OCR-01).
2. Usuário clica em **"Processar arquivos enviados"** no painel.
3. O formulário faz `POST` para `/upload/processar`.
4. A rota valida se a pasta `input/` existe e contém arquivos.
5. Chama `ocr_pipeline_s1.processar_input(cliente_id=1, mover=True)`.
6. O pipeline S1:
   - Configura Tesseract a partir de `config/settings.json`.
   - Processa cada arquivo (OCR + extração de campos).
   - Gera JSON padronizado em `output/json/`.
   - Registra no banco MySQL com status de controle.
   - Move o arquivo para `processed/` (sucesso) ou `erro/` (falha).
7. O usuário recebe mensagem de confirmação via flash.

## Segurança aplicada

- Rota aceita apenas `POST` (não pode ser acionada por link direto).
- Processa apenas a pasta `input/` fixa — não aceita caminho do usuário.
- Reutiliza o pipeline OCR existente e testado (`ocr_pipeline_s1.py`).
- Não usa `shell=True` ou `subprocess`.
- Não executa código arbitrário.
- Não permite path traversal.

## O que ainda não faz

- Não processa arquivos `.pdf` (limitação do pipeline S1 atual, que só aceita imagens).
- Não permite escolher `cliente_id` (usa `1` como padrão).
- Não agenda processamento automático.
- Não integra com Monday.com.
- Não integra com FechaMes.

## Como testar

1. Iniciar o painel com `INICIAR_OCR_24H_LOCAL.bat`.
2. Acessar `http://127.0.0.1:5000/upload`.
3. Enviar um arquivo `.png` ou `.jpg` de teste (menos de 10 MB).
4. Clicar em **"Processar arquivos enviados"**.
5. Confirmar mensagem de sucesso.
6. Verificar se o arquivo foi movido para `processed/` e o JSON está em `output/json/`.
7. Verificar se o documento aparece na lista em `/documentos`.

## Próxima fase sugerida

**UPLOAD-OCR-03** — Reprocessamento manual e gerenciamento de falhas no painel.
