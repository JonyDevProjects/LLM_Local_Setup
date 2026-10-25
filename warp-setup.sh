#!/bin/bash
# Warp + Ollama Integration Setup
# Usage: ./warp-setup.sh [ngrok-token]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL="qwen3.6:35b"

echo "============================================"
echo "  Warp + Ollama Setup"
echo "  Model: $MODEL"
echo "============================================"
echo ""

# Step 1: Check ngrok
echo "[1/5] Checking ngrok..."
if ! command -v ngrok &>/dev/null; then
    echo "  Installing ngrok..."
    brew install ngrok
fi
echo "  ngrok found: $(ngrok version 2>&1 | head -1)"
echo ""

# Step 2: Configure ngrok authtoken
echo "[2/5] Configuring ngrok authtoken..."
if [[ -f "$HOME/Library/Application Support/ngrok/ngrok.yml" ]]; then
    echo "  ngrok already configured"
else
    if [[ -n "$1" ]]; then
        ngrok config add-authtoken "$1"
        echo "  Authtoken configured"
    else
        echo "  ERROR: ngrok authtoken not configured"
        echo "  Run: ./warp-setup.sh YOUR_NGROK_TOKEN"
        echo "  Get token at: https://dashboard.ngrok.com/get-started/your-authtoken"
        exit 1
    fi
fi
echo ""

# Step 3: Check Ollama
echo "[3/5] Checking Ollama..."
if ! curl -s http://localhost:11434/ >/dev/null 2>&1; then
    echo "  Starting Ollama..."
    cd "$SCRIPT_DIR"
    export OLLAMA_HOST=0.0.0.0
    export OLLAMA_KEEP_ALIVE=-1
    export OLLAMA_FLASH_ATTENTION=1
    export OLLAMA_KV_CACHE_TYPE=q8_0
    export OLLAMA_CONTEXT_LENGTH=32768
    export OLLAMA_MAX_LOADED_MODELS=1
    ollama serve &
    sleep 3
fi
echo "  Ollama is running"
echo ""

# Step 4: Check model
echo "[4/5] Checking model $MODEL..."
if ! ollama ls 2>/dev/null | grep -q "$MODEL"; then
    echo "  Pulling $MODEL..."
    ollama pull "$MODEL"
fi
echo "  Model $MODEL is available"
echo ""

# Step 5: Start ngrok tunnel
echo "[5/5] Starting ngrok tunnel..."
echo ""
echo "============================================"
echo "  SETUP COMPLETE"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Open a new terminal and run:"
echo "   ngrok http 11434"
echo ""
echo "2. Copy the HTTPS URL from ngrok (e.g., https://abc123.ngrok-free.app)"
echo ""
echo "3. Open Warp → Settings → AI → Model Configuration"
echo "   - Set Provider to 'Custom'"
echo "   - Set API Base URL to the ngrok HTTPS URL"
echo "   - Set Model to: $MODEL"
echo ""
echo "4. Or use Warp's slash command:"
echo "   /model custom"
echo "   Then set the endpoint to the ngrok URL"
echo ""
echo "============================================"
echo "  Quick Start (copy & paste)"
echo "============================================"
echo ""
echo "  # Terminal 1: Start Ollama"
echo "  cd $SCRIPT_DIR && ./start-ollama.sh"
echo ""
echo "  # Terminal 2: Start ngrok tunnel"
echo "  ngrok http 11434"
echo ""
echo "  # Terminal 3: Use Warp with the ngrok URL"
echo ""
