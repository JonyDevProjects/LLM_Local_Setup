#!/bin/bash
# Pull all Qwen models for M1 Pro 32GB setup
# Usage: ./pull-models.sh

echo "Pulling Qwen models for MacBook Pro M1 Pro 32GB..."
echo ""

# qwen3.8:27b - Latest Qwen, general purpose
echo "[1/3] Pulling qwen3.8:27b (~17 GB)..."
ollama pull qwen3.8:27b
echo ""

# qwen3.6:35b - MoE efficient (3B active params)
echo "[2/3] Pulling qwen3.6:35b (~20 GB)..."
ollama pull qwen3.6:35b
echo ""

# qwen3-coder:30b - MoE coding focused
echo "[3/3] Pulling qwen3-coder:30b (~18 GB)..."
ollama pull qwen3-coder:30b
echo ""

echo "All models downloaded!"
echo ""
ollama ls
