@echo off
cd /d "%~dp0"
echo Iniciando OCR-LEITOR WEB na rede interna...
echo Acesse de outro computador usando o IP deste servidor e a porta 5000.
echo Exemplo: http://192.168.0.50:5000
waitress-serve --host=0.0.0.0 --port=5000 web.app:app
pause
