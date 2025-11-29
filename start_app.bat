@echo off
echo ========================================
echo   ML予測アプリを起動しています...
echo ========================================
echo.

cd /d "%~dp0"
streamlit run app.py

pause
