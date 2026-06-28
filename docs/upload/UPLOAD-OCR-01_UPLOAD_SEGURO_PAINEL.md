# UPLOAD-OCR-01 — Upload Seguro pelo Painel

## 1. Objetivo

Permitir que o usuário final envie documentos (imagem ou PDF) pelo navegador, sem precisar abrir a pasta `input/` manualmente.

## 2. Fluxo implementado

1. Usuário acessa `/upload` no painel web.
2. Seleciona um arquivo de imagem (JPG, JPEG, PNG) ou PDF.
3. O sistema valida extensão e tamanho do arquivo.
4. O sistema gera um nome seguro e único com timestamp e UUID.
5. O arquivo é salvo na pasta `input/` com o nome gerado.
6. O usuário recebe uma mensagem de confirmação via flash.

## 3. Extensões permitidas

- `.jpg`
- `.jpeg`
- `.png`
- `.pdf`

## 4. Limite de tamanho

- **10 MB** por arquivo.

## 5. Segurança aplicada

- Nome seguro: caminho removido, caracteres especiais normalizados, timestamp + UUID para unicidade.
- Bloqueio de extensão inválida (rejeita `.exe`, `.bat`, `.txt`, `.xml`, etc.).
- Bloqueio de arquivo vazio (nome vazio ou sem arquivo).
- Bloqueio de path traversal (`..`, `/`, `\` removidos do nome).
- Sem sobrescrita intencional (nome único por arquivo).
- Salvamento apenas dentro da pasta `input/`.
- Sem execução automática de OCR nesta fase.
- Sem gravação em banco de dados.
- Sem integração com Monday, FechaMes ou qualquer sistema externo.

## 6. O que não faz ainda

- Não processa OCR automaticamente.
- Não cria registro de documento no banco.
- Não envia para integração Monday/FechaMes.
- Não cria API pública.

## 7. Como testar

1. Iniciar o painel com `INICIAR_OCR_24H_LOCAL.bat`.
2. Acessar `http://127.0.0.1:5000/upload`.
3. Enviar um arquivo `.png` ou `.pdf` de teste (menos de 10 MB).
4. Confirmar mensagem de sucesso.
5. Verificar se o arquivo apareceu em `input/`.
6. Tentar enviar uma extensão inválida (`.exe`, `.txt`) e confirmar bloqueio.
7. Validar que `git status` exibe apenas os arquivos esperados.

## 8. Próxima fase sugerida

**UPLOAD-OCR-02** — Processamento controlado do documento enviado.
