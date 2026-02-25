#!/bin/bash
# Coffee Finder Cross-Platform Installer Builder
# This script builds standalone executables using PyInstaller
# Works on Windows, macOS, and Linux
# Usage: bash build_installer.sh

set -e

echo ""
echo "========================================"
echo "Coffee Finder Cross-Platform Builder"
echo "========================================"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*) OS_NAME="Linux";;
    Darwin*) OS_NAME="macOS";;
    MINGW*|MSYS*|CYGWIN*) OS_NAME="Windows";;
    *) OS_NAME="Unknown";;
esac

echo "Detected OS: $OS_NAME"
echo ""

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    python -m pip install pyinstaller
fi

echo "Step 1: Cleaning old builds..."
rm -rf dist build
echo "Done."

echo ""
echo "Step 2: Building CLI executable (coffee-finder)..."
python -m PyInstaller \
    --onefile \
    --console \
    --name coffee-finder \
    --distpath dist \
    --workpath build \
    coffee_finder/__main__.py

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi
echo "Done."

echo ""
echo "Step 3: Building GUI executable (coffee-finder-gui)..."
python -m PyInstaller \
    --onefile \
    --windowed \
    --name coffee-finder-gui \
    --distpath dist \
    --workpath build \
    coffee_finder/gui.py

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi
echo "Done."

echo ""
echo "Step 4: Building Tray executable (coffee-finder-tray)..."
python -m PyInstaller \
    --onefile \
    --windowed \
    --name coffee-finder-tray \
    --distpath dist \
    --workpath build \
    coffee_finder/tray.py

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi
echo "Done."

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "Executables created in: ./dist/"
echo ""
case "${OS_NAME}" in
    Windows)
        echo "Files:"
        echo "  - dist/coffee-finder.exe        (CLI with console window)"
        echo "  - dist/coffee-finder-gui.exe    (GUI application)"
        echo "  - dist/coffee-finder-tray.exe   (System tray application)"
        ;;
    macOS)
        echo "Files:"
        echo "  - dist/coffee-finder             (CLI)"
        echo "  - dist/coffee-finder-gui         (GUI application)"
        echo "  - dist/coffee-finder-tray        (System tray application)"
        echo ""
        echo "To create a macOS .app bundle, use:"
        echo "  python -m PyInstaller --onefile --windowed --name 'Coffee Finder' coffee_finder/gui.py"
        ;;
    Linux)
        echo "Files:"
        echo "  - dist/coffee-finder             (CLI)"
        echo "  - dist/coffee-finder-gui         (GUI application)"
        echo "  - dist/coffee-finder-tray        (System tray application)"
        echo ""
        echo "Make executables available system-wide by copying to /usr/local/bin:"
        echo "  sudo cp dist/coffee-finder* /usr/local/bin/"
        ;;
esac
echo ""
echo "These are fully standalone executables that do not require"
echo "Python to be installed on the target system."
echo ""
