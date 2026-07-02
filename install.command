#!/bin/bash
set -e

# Change directory to the directory where this script is located
cd "$(dirname "$0")"

echo "=================================================="
echo "   Installing Offline QR Text Transfer on macOS"
echo "=================================================="

# Create target directory
TARGET_DIR="$HOME/Code/qr-transfer"
mkdir -p "$TARGET_DIR"

# Only copy if we are not running from the target directory itself
ABS_CURRENT="$(pwd)"
ABS_TARGET="$(cd "$TARGET_DIR" && pwd)"

if [ "$ABS_CURRENT" != "$ABS_TARGET" ]; then
  echo "Copying files to $TARGET_DIR..."
  cp qr-gif-generator "$TARGET_DIR/"
  cp qr-scanner "$TARGET_DIR/"
  cp install_services.py "$TARGET_DIR/"
else
  echo "Already in $TARGET_DIR. Skipping copy step."
fi

# Make sure binaries are executable
chmod +x "$TARGET_DIR/qr-gif-generator"
chmod +x "$TARGET_DIR/qr-scanner"

# Remove macOS quarantine Gatekeeper flags (avoids security block warnings)
xattr -d com.apple.quarantine "$TARGET_DIR/qr-gif-generator" 2>/dev/null || true
xattr -d com.apple.quarantine "$TARGET_DIR/qr-scanner" 2>/dev/null || true

echo "Installing macOS Quick Action Services..."
python3 "$TARGET_DIR/install_services.py"

echo "=================================================="
echo "   Installation complete! You can close this."
echo "=================================================="
