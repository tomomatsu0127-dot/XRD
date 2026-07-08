@echo off
setlocal
cd /d "%~dp0"

set "CODEX_PY=C:\Users\m236r\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if exist "%CODEX_PY%" (
  "%CODEX_PY%" src\labplot_studio\main.py
  goto end
)

where python >nul 2>nul
if %errorlevel%==0 (
  python src\labplot_studio\main.py
  goto end
)

where py >nul 2>nul
if %errorlevel%==0 (
  py src\labplot_studio\main.py
  goto end
)

echo Python was not found.
echo Install Python 3.10 or newer, then run this file again.
pause

:end
