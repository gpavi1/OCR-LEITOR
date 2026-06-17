@echo off
title OCR-LEITOR - Processamento de NF-e
cd /d C:\Projetos\OCR-LEITOR

echo ==========================================
echo        OCR-LEITOR - PROCESSAMENTO
echo ==========================================
echo.
echo Pasta de entrada:
echo C:\Projetos\OCR-LEITOR\input
echo.
echo Iniciando processamento...
echo.

python ocr_to_monday.py

echo.
echo ==========================================
echo Processo finalizado.
echo Verifique as pastas processed e erro.
echo ==========================================
pause