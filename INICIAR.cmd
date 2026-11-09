@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto run
where uv >nul 2>nul
if errorlevel 1 (
    echo Instala uv siguiendo el README antes de iniciar por primera vez.
    pause
    exit /b 1
)
uv venv --python 3.12
if errorlevel 1 goto error
uv pip install -r requirements.txt
if errorlevel 1 goto error
:run
".venv\Scripts\python.exe" src\gest-calc\sample_main.py %*
if errorlevel 1 goto error
exit /b 0
:error
echo No se ha podido ejecutar. Revisa el mensaje anterior y el README.
pause
exit /b 1
