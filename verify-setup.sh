#!/bin/bash
# Verify Ollama setup for MacBook Pro M1 Pro 32GB
# Usage: ./verify-setup.sh

echo "============================================"
echo "  Ollama Setup Verification - M1 Pro 32GB"
echo "============================================"
echo ""

# Check Ollama version
echo "[1/6] Ollama version:"
ollama --version
echo ""

# Check if server is running
echo "[2/6] Server status:"
if ollama ls >/dev/null 2>&1; then
    echo "  ✓ Ollama server is running"
else
    echo "  ✗ Ollama server is NOT running"
    echo "    Run: ./start-ollama.sh"
    exit 1
fi
echo ""

# Check models
echo "[3/6] Installed models:"
ollama ls
echo ""

# Check GPU
echo "[4/6] GPU detection:"
echo "  (Check output above for 'Apple M1 Pro' and '25.0 GiB')"
echo ""

# Check environment variables
echo "[5/6] Environment variables:"
echo "  OLLAMA_FLASH_ATTENTION: ${OLLAMA_FLASH_ATTENTION:-not set}"
echo "  OLLAMA_KV_CACHE_TYPE: ${OLLAMA_KV_CACHE_TYPE:-not set}"
echo "  OLLAMA_KEEP_ALIVE: ${OLLAMA_KEEP_ALIVE:-not set}"
echo "  OLLAMA_CONTEXT_LENGTH: ${OLLAMA_CONTEXT_LENGTH:-not set}"
echo "  OLLAMA_MAX_LOADED_MODELS: ${OLLAMA_MAX_LOADED_MODELS:-not set}"
echo ""

# Test API
echo "[6/6] API connectivity test:"
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "  ✓ API is accessible at http://localhost:11434"
else
    echo "  ✗ API is not accessible"
fi
echo ""

echo "============================================"
echo "  Quick test command:"
echo "  ollama run qwen3.8:27b"
echo "============================================"
