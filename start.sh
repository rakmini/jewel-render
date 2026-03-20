#!/bin/bash
# JewelRender Development Server Launcher
# Starts the API server and prints access URLs for all devices on the network.

set -e

# Detect local IP address (macOS and Linux)
if command -v ipconfig &>/dev/null; then
    # macOS
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "unknown")
else
    # Linux
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "unknown")
fi

PORT="${API_PORT:-5000}"

echo ""
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║            JewelRender Dev Server             ║"
echo "  ╠══════════════════════════════════════════════╣"
echo "  ║                                              ║"
echo "  ║  Local:   http://localhost:${PORT}              ║"
echo "  ║  Network: http://${LOCAL_IP}:${PORT}       ║"
echo "  ║                                              ║"
echo "  ║  Share the Network URL with other devices    ║"
echo "  ║  on the same Wi-Fi / LAN.                   ║"
echo "  ║                                              ║"
echo "  ║  API Docs: http://${LOCAL_IP}:${PORT}/api/docs  ║"
echo "  ║                                              ║"
echo "  ╚══════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")/backend/src"
exec python main.py
