#!/bin/bash
# EVE Overview Pro v2.1 - Installation Script for Ubuntu
# This script installs the application and creates a desktop entry

set -e

echo "=========================================="
echo "EVE Overview Pro v2.1 - Installation"
echo "=========================================="
echo ""

# Check if running from project directory
if [ ! -f "src/main.py" ]; then
    echo "ERROR: Please run this script from the eve-overview-pro directory"
    exit 1
fi

# Get project directory
PROJECT_DIR="$(pwd)"
echo "Project directory: $PROJECT_DIR"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"

PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "ERROR: Python 3.10 or higher is required"
    exit 1
fi
echo "✓ Python version OK"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✓ Dependencies installed from requirements.txt"
else
    echo "⚠ requirements.txt not found - skipping dependency installation"
fi
echo ""

# Create launcher script
LAUNCHER_SCRIPT="$PROJECT_DIR/eve-overview-pro.sh"
echo "Creating launcher script..."
cat > "$LAUNCHER_SCRIPT" << 'EOF'
#!/bin/bash
# EVE Overview Pro Launcher Script

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment and run
cd "$SCRIPT_DIR"
source .venv/bin/activate

# Add src to PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

python3 src/main.py "$@"
EOF

chmod +x "$LAUNCHER_SCRIPT"
echo "✓ Launcher script created: $LAUNCHER_SCRIPT"
echo ""

# Create application icon (if not exists)
ICON_PATH="$PROJECT_DIR/assets/icon.png"
if [ ! -f "$ICON_PATH" ]; then
    echo "Creating application icon..."
    mkdir -p "$PROJECT_DIR/assets"

    # Create a simple placeholder icon using ImageMagick (if available)
    if command -v convert &> /dev/null; then
        convert -size 256x256 xc:#1a1a2e -fill white -pointsize 60 -gravity center -annotate +0+0 "EVE\nOverview" "$ICON_PATH" 2>/dev/null || {
            echo "⚠ Could not create icon with ImageMagick"
        }
    else
        echo "⚠ ImageMagick not found - skipping icon creation"
        echo "  You can add a custom icon later at: $ICON_PATH"
    fi
fi

if [ -f "$ICON_PATH" ]; then
    echo "✓ Icon: $ICON_PATH"
else
    echo "⚠ No icon - application will use default icon"
    ICON_PATH="utilities-terminal"  # Fallback to system icon
fi
echo ""

# Create desktop entry
DESKTOP_ENTRY="$HOME/.local/share/applications/eve-overview-pro.desktop"
echo "Creating desktop entry..."

mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_ENTRY" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=EVE Overview Pro
Comment=Multi-window preview and management for EVE Online
Exec=$LAUNCHER_SCRIPT
Icon=$ICON_PATH
Terminal=false
Categories=Game;Utility;
Keywords=eve;online;overview;multiboxing;
StartupNotify=true
EOF

chmod +x "$DESKTOP_ENTRY"
echo "✓ Desktop entry created: $DESKTOP_ENTRY"
echo ""

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    echo "Updating desktop database..."
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    echo "✓ Desktop database updated"
else
    echo "⚠ update-desktop-database not found - you may need to log out and back in"
fi
echo ""

echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "EVE Overview Pro v2.1 has been installed successfully!"
echo ""
echo "You can now:"
echo "  1. Launch from applications menu (search for 'EVE Overview Pro')"
echo "  2. Add to favorites/dock by right-clicking the application icon"
echo "  3. Run directly: $LAUNCHER_SCRIPT"
echo ""
echo "Config directory: ~/.config/eve-overview-pro/"
echo "Data directory: ~/.local/share/eve-overview-pro/"
echo ""
echo "To uninstall, run: ./uninstall.sh"
echo ""
