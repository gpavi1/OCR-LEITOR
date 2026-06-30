@echo off
setlocal

set "ROOT=%~dp0"
set "PY=%ROOT%.venv\Scripts\python.exe"

if not exist "%PY%" set "PY=python"

if "%~1"=="" (
    "%PY%" "%ROOT%scripts\instalar_ocr.py" --help
    exit /b %ERRORLEVEL%
)

"%PY%" "%ROOT%scripts\instalar_ocr.py" %*
exit /b %ERRORLEVEL%
