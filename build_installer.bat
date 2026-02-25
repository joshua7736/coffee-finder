@echo off
REM Coffee Finder Windows Installer Builder
REM This script builds standalone Windows executables using PyInstaller
REM Usage: build_installer.bat

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Coffee Finder Windows Installer Builder
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

echo.
echo Step 1: Cleaning old builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec.bak" del /q "*.spec.bak"
echo Done.

echo.
echo Step 2: Building console executable (coffee-finder.exe)...
python -m PyInstaller ^
    --onefile ^
    --console ^
    --name coffee-finder ^
    --distpath dist ^
    --workpath build ^
    coffee_finder/__main__.py
if errorlevel 1 (
    echo Build failed!
    exit /b 1
)
echo Done.

echo.
echo Step 3: Building GUI executable (coffee-finder-gui.exe - no console)...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name coffee-finder-gui ^
    --distpath dist ^
    --workpath build ^
    coffee_finder/gui.py
if errorlevel 1 (
    echo Build failed!
    exit /b 1
)
echo Done.

echo.
echo Step 4: Building Tray executable (coffee-finder-tray.exe - no console)...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name coffee-finder-tray ^
    --distpath dist ^
    --workpath build ^
    coffee_finder/tray.py
if errorlevel 1 (
    echo Build failed!
    exit /b 1
)
echo Done.

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executables created in: dist\
echo.
echo Files:
echo   - dist\coffee-finder.exe        (CLI with console window)
echo   - dist\coffee-finder-gui.exe    (GUI application)
echo   - dist\coffee-finder-tray.exe   (System tray application)
echo.
echo To create a Windows installer (MSI), use the generated executables
echo with a tool like Inno Setup or NSIS. For more info, see README.md
echo.
echo Alternatively, distribute the .exe files directly - they are
echo fully standalone and do not require Python to be installed.
echo.
