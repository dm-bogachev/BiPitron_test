@echo off
SET SCRIPT_DIR=%cd%
cd %SCRIPT_DIR%

IF NOT EXIST .venv\ (
    echo Virtual environment not found. Creating new virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate
    pip install -r requirements.txt
) ELSE (
    call .venv\Scripts\activate
)

python webui\server.py

deactivate