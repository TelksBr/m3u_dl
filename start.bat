@echo off
:: Definir o interpretador Python (ajuste o caminho se necessário)
set PYTHON_EXEC=python

:: Caminho para os scripts
set ORGANIZER_SCRIPT=oraganizer.py
set DOWNLOADER_SCRIPT=downloader.py

:: Executar o script oraganizer.py
echo Executando o organizador...
%PYTHON_EXEC% %ORGANIZER_SCRIPT%
if %ERRORLEVEL% neq 0 (
    echo Erro ao executar %ORGANIZER_SCRIPT%. Verifique o script e tente novamente.
    pause
    exit /b %ERRORLEVEL%
)

:: Executar o script downloader.py
echo Executando o downloader...
%PYTHON_EXEC% %DOWNLOADER_SCRIPT%
if %ERRORLEVEL% neq 0 (
    echo Erro ao executar %DOWNLOADER_SCRIPT%. Verifique o script e tente novamente.
    pause
    exit /b %ERRORLEVEL%
)

echo Processos concluídos com sucesso!
pause
