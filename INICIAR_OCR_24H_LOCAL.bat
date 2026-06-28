@echo off
cd /d "%~dp0"

echo =============================================
echo OCR-LEITOR - Inicializacao Local 24h
echo =============================================

IF NOT EXIST ".\.venv\Scripts\python.exe" (
    echo [ERRO] Python da venv nao encontrado.
    echo        Execute a preparacao/instalacao primeiro.
    pause
    exit /b 1
)

IF NOT EXIST "web\app.py" (
    echo [ERRO] web\app.py nao encontrado.
    echo        Verifique a instalacao do OCR-LEITOR.
    pause
    exit /b 1
)

echo.
echo Painel local:
echo http://127.0.0.1:5000
echo.
echo Para encerrar, feche esta janela ou pressione Ctrl+C.
echo.

.\.venv\Scripts\python.exe -m waitress --listen=127.0.0.1:5000 web.app:app

pause
