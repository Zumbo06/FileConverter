@echo off
TITLE File Converter - Requirements Installer

echo ==========================================================
echo  File Converter - Python Requirements Installer
echo ==========================================================
echo.
echo This script will create a private Python environment for the
echo application and install all necessary packages.
echo.
echo This only needs to be run once.
echo.
pause
echo.

REM --- Check for a basic Python installation ---
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not found in your system PATH.
    echo Please install Python 3 from python.org and ensure "Add to PATH" is checked.
    echo.
    pause
    exit /b
)

echo [1/2] Creating a new Python virtual environment in a folder named 'venv'...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create the virtual environment.
    pause
    exit /b
)
echo      Done.
echo.

echo [2/2] Installing required packages from requirements.txt...
echo      (This may take a moment, please be patient.)

REM --- Use the pip.exe from within the new venv to install packages ---
call venv\Scripts\pip.exe install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python packages.
    echo Please check your internet connection and the 'requirements.txt' file.
    pause
    exit /b
)
echo      Done.
echo.


echo ==========================================================
echo  SETUP COMPLETE!
echo ==========================================================
echo.
echo You can now run the application using the 'run.bat' file.
echo.
pause