#!/usr/bin/env bash
set -euo pipefail

APP_NAME="steamscreen"
APP_DIR="$HOME/.config/$APP_NAME"
BIN_FILE="$HOME/.local/bin/$APP_NAME"
SERVICE_FILE="$HOME/.config/systemd/user/$APP_NAME.service"

echo "Uninstalling $APP_NAME..."

# Stop and disable service if it exists
if systemctl --user is-enabled "$APP_NAME.service" >/dev/null 2>&1; then
    echo "Stopping service..."
    systemctl --user disable --now "$APP_NAME.service"
fi

# Remove service file
if [ -f "$SERVICE_FILE" ]; then
    echo "Removing service..."
    rm "$SERVICE_FILE"
fi

systemctl --user daemon-reload

# Remove launcher
if [ -f "$BIN_FILE" ]; then
    echo "Removing launcher..."
    rm "$BIN_FILE"
fi

# Remove application directory
if [ -d "$APP_DIR" ]; then
    echo
    read -rp "Remove application directory and settings too? [y/N] " answer

    if [[ "$answer" =~ ^[Yy]$ ]]; then
        rm -rf "$APP_DIR"
        echo "Removed $APP_DIR"
    else
        echo "Keeping $APP_DIR"
    fi
fi

echo
echo "Uninstall complete."