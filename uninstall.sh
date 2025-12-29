#!/bin/bash
# Argus Overview v2.4 - Uninstallation Script

set -e

echo "=========================================="
echo "Argus Overview v2.4 - Uninstallation"
echo "=========================================="
echo ""

# Get project directory
PROJECT_DIR="$(pwd)"

# Remove desktop entry
DESKTOP_ENTRY="$HOME/.local/share/applications/argus-overview.desktop"
if [ -f "$DESKTOP_ENTRY" ]; then
    echo "Removing desktop entry..."
    rm "$DESKTOP_ENTRY"
    echo "✓ Desktop entry removed"
else
    echo "⚠ Desktop entry not found"
fi

# Also remove old naming desktop entries if exist
OLD_DESKTOP="$HOME/.local/share/applications/eve-veles-eyes.desktop"
if [ -f "$OLD_DESKTOP" ]; then
    rm "$OLD_DESKTOP"
    echo "✓ Old desktop entry removed"
fi

OLDER_DESKTOP="$HOME/.local/share/applications/eve-overview-pro.desktop"
if [ -f "$OLDER_DESKTOP" ]; then
    rm "$OLDER_DESKTOP"
    echo "✓ Legacy desktop entry removed"
fi
echo ""

# Remove icons from hicolor theme
echo "Removing icons..."
for size in 32 48 64 128 256 512; do
    rm -f ~/.local/share/icons/hicolor/${size}x${size}/apps/argus-overview.png
    rm -f ~/.local/share/icons/hicolor/${size}x${size}/apps/eve-veles-eyes.png
done

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor/ 2>/dev/null || true
fi
echo "✓ Icons removed"
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
echo "  Config: ~/.config/argus-overview/"
echo "  Data: ~/.local/share/argus-overview/"
echo ""
read -p "Do you want to remove these directories? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "$HOME/.config/argus-overview" ]; then
        rm -rf "$HOME/.config/argus-overview"
        echo "✓ Config directory removed"
    fi

    if [ -d "$HOME/.local/share/argus-overview" ]; then
        rm -rf "$HOME/.local/share/argus-overview"
        echo "✓ Data directory removed"
    fi

    # Also remove old naming directories
    if [ -d "$HOME/.config/eve-veles-eyes" ]; then
        rm -rf "$HOME/.config/eve-veles-eyes"
        echo "✓ Old config directory removed"
    fi

    if [ -d "$HOME/.local/share/eve-veles-eyes" ]; then
        rm -rf "$HOME/.local/share/eve-veles-eyes"
        echo "✓ Old data directory removed"
    fi
else
    echo "Keeping configuration and data directories"
fi
echo ""

echo "=========================================="
echo "Uninstallation Complete!"
echo "=========================================="
echo ""
echo "Argus Overview v2.4 has been uninstalled."
echo ""
echo "Note: Virtual environment (venv) and source code remain."
echo "To completely remove, delete the project directory."
echo ""
