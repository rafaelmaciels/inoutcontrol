@echo off
cd /d "%~dp0"
call venv\Scripts\activate

:: Inicia o python em uma nova janela.
start /b python app.py

:: Espera 3 segundos (ajuste conforme sua necessidade)
timeout /t 3 /nobreak

:: Abre o navegador
start http://127.0.0.1:5000