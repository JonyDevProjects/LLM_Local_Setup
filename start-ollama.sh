#!/bin/bash
# Start Ollama with M1 Pro 32GB optimized settings
# Usage: ./start-ollama.sh [model]
# Default model: qwen3.6:35b

MODEL="${1:-qwen3.6:35b}"

export OLLAMA_HOST=0.0.0.0
export OLLAMA_KEEP_ALIVE=-1
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KV_CACHE_TYPE=q8_0
export OLLAMA_CONTEXT_LENGTH=32768
export OLLAMA_MAX_LOADED_MODELS=1

echo "Starting Ollama with M1 Pro optimized settings..."
echo "  HOST=0.0.0.0"
echo "  Model: $MODEL"
echo "  FLASH_ATTENTION=1"
echo "  KV_CACHE_TYPE=q8_0"
echo "  KEEP_ALIVE=infinite"
echo "  CONTEXT_LENGTH=32768"
echo ""

ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
for i in {1..30}; do
    if curl -s http://localhost:11434/ >/dev/null 2>&1; then
        echo "Ollama is ready. Loading $MODEL..."
        curl -s http://localhost:11434/api/generate -d "{\"model\":\"$MODEL\",\"prompt\":\"hello\",\"think\":false}" > /dev/null 2>&1
        echo "Model $MODEL loaded!"
        break
    fi
    sleep 1
done

wait $OLLAMA_PID
