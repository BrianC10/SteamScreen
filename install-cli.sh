#!/usr/bin/env bash
set -euo pipefail

# Set locations for files
APP_NAME="steamscreen"
APP_DIR="$HOME/.config/$APP_NAME"
BIN_DIR="$HOME/.local/bin"

echo "Installing $APP_NAME..."

# Create directories if they don't exist
mkdir -p "$APP_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$SERVICE_DIR"

# Copy files to ~/.config
echo "Copying application files..."
install -m 644 steamscreen.py "$APP_DIR/steamscreen.py"
install -m 644 requirements.txt "$APP_DIR/requirements.txt"

# Copy settings file if one doesn't already exist
if [ ! -f "$APP_DIR/settings.py" ]; then
    echo "Installing default settings..."
    install -m 644 settings.py "$APP_DIR/settings.py"
else
    echo "Existing settings.py found."
fi

# Create a virtual environment if one doesn't already exist
if [ ! -d "$APP_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$APP_DIR/.venv"
else
    echo "Existing virtual environment found."
fi

# Install dependencies
echo "Installing Python dependencies..."
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# Install 'steamscreen' to ~/.local/bin
echo "Installing launcher..."
install -m 755 steamscreen "$BIN_DIR/steamscreen"

# Completion Messages
echo
echo "Installation complete!"
echo
echo "Commandline Program:"
echo "  steamscreen -h"