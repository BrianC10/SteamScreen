#!/usr/bin/env bash
set -euo pipefail

# Set locations for files
APP_NAME="steamscreen"
APP_DIR="$HOME/.config/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
SERVICE_DIR="$HOME/.config/systemd/user"

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
    echo "Existing settings.py found, leaving it alone."
fi

# Create a virtual environment if one doesn't already exist
if [ ! -d "$APP_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$APP_DIR/.venv"
else
    echo "Existing virtual environment found, leaving it alone."
fi

# Install dependencies
echo "Installing Python dependencies..."
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# Install 'steamscreen' to ~/.local/bin
echo "Installing launcher..."
install -m 755 steamscreen "$BIN_DIR/steamscreen"

# Install service file to ~/.config/systemd/user
echo "Installing systemd service..."
install -m 644 steamscreen.service "$SERVICE_DIR/steamscreen.service"

# Start the service
echo "Starting service..."
systemctl --user daemon-reload

# Completion Messages
echo
echo "$APP_NAME installed Successfully!"
echo
echo "Please configure your settings file at: $APP_DIR/settings.py"
echo
echo "\"RUN_AS_SERVICE\" must be set to \"True\" for the service to function."
echo "\"RUN_AS_SERVICE\" must be set to \"False\" for commandline use."
echo
echo "Once configured, enable the service with: systemctl --user enable steamscreen"
echo "Followed by: systemctl --user start steamscreen"
echo
echo "For commandline usage see:"
echo "      steamscreen -h"