@echo off
TITLE File Converter Launcher

echo ==========================================================
echo  File Converter Launcher
echo ==========================================================
echo.

REM --- Step 1: Check if the Python environment has been set up ---
REM This is a hard requirement, so the script will stop if it's not done.
if not exist "venv\Scripts\python.exe" (
    echo [FATAL ERROR] The Python environment has not been set up yet.
    echo Please run the 'install_requirements.bat' script first to complete the setup.
    echo.
    pause
    exit /b
)

REM --- Step 2: Check for external dependencies (FFmpeg, 7-Zip, etc.) ---
echo Checking for optional external software...
set ALL_DEPS_FOUND=true
ffmpeg -version >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg not found. Video/Audio conversion will fail.
    set ALL_DEPS_FOUND=false
)
7z >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] 7-Zip not found. Archive conversion will fail.
    set ALL_DEPS_FOUND=false
)
soffice --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] LibreOffice not found. Document conversion will fail.
    set ALL_DEPS_FOUND=false
)
echo.

REM --- Step 3: Show a summary warning if any dependencies were missing ---
if "%ALL_DEPS_FOUND%"=="false" (
    echo ---------------------------------------------------------------------
    echo  WARNING: One or more external programs are missing.
    echo  The application will still run, but some features will not work.
    echo.
    echo  Please go to 'Help > Setup Guide' inside the application for
    echo  instructions on how to install the missing software.
    echo ---------------------------------------------------------------------
    echo.
    pause
)

echo Launching application...
echo.

REM --- Step 4: Launch the main script using the Python executable from the virtual environment ---
call venv\Scripts\python.exe main.py

echo.
echo Application has closed.
pause >nul