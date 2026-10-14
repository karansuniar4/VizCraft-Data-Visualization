@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo   VizCraft - Data Visualization Dashboard
echo ==========================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher "py" was not found.
    echo Install Python 3.10+ from https://www.python.org/downloads/windows/
    echo Make sure Python is added to PATH, then run this file again.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -m venv .venv
    if errorlevel 1 (
        echo Could not create the virtual environment.
        pause
        exit /b 1
    )
)

echo Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo pip upgrade failed. Check your internet connection and Python installation.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed. Review the error above.
    pause
    exit /b 1
)

echo.
echo Starting VizCraft...
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 (
    echo VizCraft stopped with an error. Review the terminal output above.
    pause
    exit /b 1
)
endlocal
