#!/bin/bash
# Stop all services (Ollama + ngrok)
# Usage: ./stop-all.sh

echo "Stopping services..."

pkill ngrok 2>/dev/null && echo "  ngrok stopped" || echo "  ngrok was not running"
pkill ollama 2>/dev/null && echo "  Ollama stopped" || echo "  Ollama was not running"

echo "Done."
