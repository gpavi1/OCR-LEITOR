@echo off
cd /d "%~dp0"

echo =============================================
echo OCR-LEITOR - Limpeza Segura de Testes
echo =============================================
echo.
echo A rotina move arquivos operacionais para _backup_testes antes de limpar.
echo Banco, OCR, parser, API e integracoes externas nao serao alterados.
echo.

IF NOT EXIST ".\.venv\Scripts\python.exe" (
    echo [ERRO] Python da venv nao encontrado.
    echo        Execute a preparacao/instalacao primeiro.
    pause
    exit /b 1
)

IF NOT EXIST "scripts\limpar_ambiente_teste.py" (
    echo [ERRO] scripts\limpar_ambiente_teste.py nao encontrado.
    pause
    exit /b 1
)

.\.venv\Scripts\python.exe scripts\limpar_ambiente_teste.py %*

pause
