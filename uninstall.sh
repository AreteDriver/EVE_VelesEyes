#!/bin/bash
# EVE Overview Pro v2.1 - Uninstallation Script

set -e

echo "=========================================="
echo "EVE Overview Pro v2.1 - Uninstallation"
echo "=========================================="
echo ""

# Get project directory
PROJECT_DIR="$(pwd)"

# Remove desktop entry
DESKTOP_ENTRY="$HOME/.local/share/applications/eve-overview-pro.desktop"
if [ -f "$DESKTOP_ENTRY" ]; then
    echo "Removing desktop entry..."
    rm "$DESKTOP_ENTRY"
    echo "✓ Desktop entry removed"
else
    echo "⚠ Desktop entry not found"
fi
echo ""

# Remove launcher script
LAUNCHER_SCRIPT="$PROJECT_DIR/eve-overview-pro.sh"
if [ -f "$LAUNCHER_SCRIPT" ]; then
    echo "Removing launcher script..."
    rm "$LAUNCHER_SCRIPT"
    echo "✓ Launcher script removed"
fi
echo ""

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    echo "Updating desktop database..."
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    echo "✓ Desktop database updated"
fi
echo ""

# Ask about config and data
echo "Configuration and data directories:"
echo "  Config: ~/.config/eve-overview-pro/"
echo "  Data: ~/.local/share/eve-overview-pro/"
echo ""
read -p "Do you want to remove these directories? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "$HOME/.config/eve-overview-pro" ]; then
        rm -rf "$HOME/.config/eve-overview-pro"
        echo "✓ Config directory removed"
    fi

    if [ -d "$HOME/.local/share/eve-overview-pro" ]; then
        rm -rf "$HOME/.local/share/eve-overview-pro"
        echo "✓ Data directory removed"
    fi
else
    echo "Keeping configuration and data directories"
fi
echo ""

echo "=========================================="
echo "Uninstallation Complete!"
echo "=========================================="
echo ""
echo "EVE Overview Pro v2.1 has been uninstalled."
echo ""
echo "Note: Virtual environment (.venv) and source code remain."
echo "To completely remove, delete the project directory."
echo ""
