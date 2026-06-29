@echo off
cd /d "%~dp0"

set "PYTHON_CMD="
if exist ".\.venv\Scripts\python.exe" (
    set "PYTHON_CMD=.\.venv\Scripts\python.exe"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [ERRO] Python nao encontrado.
        echo        Instale Python ou crie o ambiente virtual primeiro.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python"
)

if not exist "scripts\menu_operacao.py" (
    echo [ERRO] scripts\menu_operacao.py nao encontrado.
    pause
    exit /b 1
)

%PYTHON_CMD% scripts\menu_operacao.py

pause
