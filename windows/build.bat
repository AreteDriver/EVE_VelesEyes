@echo off
REM Argus Overview - Windows Build Script
REM Creates standalone .exe using PyInstaller

echo ==========================================
echo Argus Overview v2.4 - Windows Build
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Install/upgrade dependencies
echo Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
pip install pyinstaller >nul 2>&1
echo Done.
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist
echo.

REM Build executable
echo Building executable...
echo This may take a few minutes...
pyinstaller build.spec
echo.

if exist "dist\Argus-Overview.exe" (
    echo ==========================================
    echo Build Complete!
    echo ==========================================
    echo.
    echo Executable created: dist\Argus-Overview.exe
    echo Size:
    dir dist\Argus-Overview.exe | find "Argus-Overview.exe"
    echo.
    echo You can now distribute dist\Argus-Overview.exe
    echo.
) else (
    echo ==========================================
    echo Build Failed!
    echo ==========================================
    echo.
    echo Check the output above for errors.
    echo.
)

pause
