#!/bin/bash

set -e

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "ERROR: ngrok is not installed."
    echo ""
    echo "Please install ngrok:"
    echo "  brew install ngrok"
    echo ""
    echo "Then configure it with your auth token:"
    echo "  ngrok config add-authtoken <your-token>"
    echo ""
    echo "Get your token at: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

# Check for ngrok domain
if [ -z "$MCP_NGROK_DOMAIN" ]; then
    echo "ERROR: MCP_NGROK_DOMAIN is not set."
    echo ""
    echo "Please set MCP_NGROK_DOMAIN in your local.env file."
    echo "You can get a free static domain at: https://dashboard.ngrok.com/domains"
    echo ""
    echo "Example:"
    echo "  MCP_NGROK_DOMAIN=your-name.ngrok-free.dev"
    exit 1
fi

# Port for MCP server
MCP_PORT=${MCP_LOCAL_PORT:-3000}

# Cleanup function to kill background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    if [ ! -z "$NGROK_PID" ]; then
        kill $NGROK_PID 2>/dev/null || true
    fi
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null || true
    fi
    exit 0
}
trap cleanup EXIT INT TERM

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    pnpm install
fi

echo "🚀 Starting MCP server on port $MCP_PORT..."

# Start MCP server in background
PORT=$MCP_PORT npx tsx index.ts &
MCP_PID=$!

# Wait for server to start
sleep 3

# Start ngrok with the static domain
echo "🌐 Starting ngrok tunnel to $MCP_NGROK_DOMAIN..."
ngrok http $MCP_PORT --domain=$MCP_NGROK_DOMAIN --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok to establish tunnel
sleep 3

NGROK_URL="https://$MCP_NGROK_DOMAIN"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ MCP Server is running!"
echo ""
echo "📡 Local URL:  http://localhost:$MCP_PORT"
echo "🌐 Public URL: $NGROK_URL"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop..."

# Wait for MCP server (keeps script running)
wait $MCP_PID
