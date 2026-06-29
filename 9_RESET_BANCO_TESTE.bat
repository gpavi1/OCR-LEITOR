@echo off
title RESET BANCO TESTE - OCR LEITOR
cd /d "%~dp0"

:MENU
cls
echo ========================================
echo    RESET BANCO DE TESTE - OCR LEITOR
echo ========================================
echo.
echo  1. Simular (dry-run - padrao seguro)
echo  2. Limpar registros de teste (com confirmacao)
echo  3. Sair
echo.
choice /c 123 /n /m "Escolha uma opcao (1-3): "

if errorlevel 3 goto SAIR
if errorlevel 2 goto LIMPAR
if errorlevel 1 goto SIMULAR

goto SAIR

:SIMULAR
echo.
echo Executando simulacao (dry-run)...
echo Nenhum registro sera alterado.
echo.
python scripts/reset_banco_teste.py --dry-run
echo.
pause
goto MENU

:LIMPAR
echo.
echo ATENCAO: Isso vai apagar registros de teste do banco!
echo.
echo Para confirmar, voce precisa fornecer o texto de confirmacao.
echo.
python scripts/reset_banco_teste.py --confirmar
echo.
if %errorlevel% equ 1 (
    echo Para executar a limpeza real, use a linha de comando:
    echo   python scripts/reset_banco_teste.py --confirmar --confirmacao "RESETAR_BANCO_TESTE"
)
echo.
pause
goto MENU

:SAIR
exit /b
