@echo off
cd /d "%~dp0"
echo Iniciando OCR-LEITOR WEB em modo local...
echo Acesse: http://127.0.0.1:5000
waitress-serve --host=127.0.0.1 --port=5000 web.app:app
pause
