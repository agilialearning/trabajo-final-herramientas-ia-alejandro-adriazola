@echo off
REM Abre JupyterLab con el notebook del trabajo final (demo de la exposicion).
REM Usa el entorno env\ del repo si existe; si no, el de copiloto-mentiva.
cd /d "%~dp0"
if exist "env\Scripts\jupyter.exe" (
  "env\Scripts\jupyter.exe" lab --port=8888 trabajo_final.ipynb
) else (
  "C:\Users\Usuario\Desktop\CLAUDE\CODE\copiloto-mentiva\env\Scripts\jupyter.exe" lab --port=8888 trabajo_final.ipynb
)
