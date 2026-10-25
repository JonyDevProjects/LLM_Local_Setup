#!/bin/bash
# Benchmark script for LiteRT-LM (gemma4-26b) on M1 Pro 32GB
# Mirrors benchmark.sh but targets a LiteRT OpenAI-compatible server.
# Usage: ./benchmark-litert.sh

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/benchmark-results"
PROMPTS_FILE="$SCRIPT_DIR/benchmark-prompts.txt"
LITERT_BIN="$SCRIPT_DIR/poc-antigravity/.venv/bin/litert-lm"
MODEL="gemma4-26b"
MODEL_DIR_NAME="gemma4-26b-litert"
PORT=11435
BASE_URL="http://127.0.0.1:$PORT/v1"
DATE=$(date +%Y-%m-%d)
CURL_TIMEOUT=600

model_dir="$RESULTS_DIR/$MODEL_DIR_NAME"
mkdir -p "$model_dir"

get_prompt() {
    local prompt_num=$1
    awk "/^PROMPT_${prompt_num}:/{found=1; sub(/^PROMPT_${prompt_num}:[[:space:]]*/, \"\"); print; next} found && /^[[:space:]]*$/{exit} found{print}" "$PROMPTS_FILE"
}

get_server_mem_gb() {
    local rss_kb=$(ps -o rss= -p "$SERVER_PID" 2>/dev/null | tr -d ' ')
    if [[ -n "$rss_kb" && "$rss_kb" -gt 0 ]]; then
        echo "scale=1; $rss_kb / 1048576" | bc
    else
        echo "N/A"
    fi
}

cleanup() {
    if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "Stopping LiteRT server (PID $SERVER_PID)..."
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Preflight
if [[ ! -f "$PROMPTS_FILE" ]]; then
    echo "Error: Prompts file not found: $PROMPTS_FILE"
    exit 1
fi

if [[ ! -x "$LITERT_BIN" ]]; then
    echo "Error: litert-lm binary not found at $LITERT_BIN"
    exit 1
fi

if ollama list >/dev/null 2>&1; then
    echo "Error: Ollama server is running. Stop it first to free unified memory"
    echo "  (killall ollama) — otherwise RAM contention skews results."
    exit 1
fi

if [[ ! -f "$HOME/.litert-lm/models/$MODEL/model.litertlm" ]]; then
    echo "Error: checkpoint not found for $MODEL (run: litert-lm import ...)"
    exit 1
fi

# Start LiteRT server
echo "Starting litert-lm serve ($MODEL) on port $PORT..."
"$LITERT_BIN" serve --host 127.0.0.1 --port "$PORT" > "$model_dir/server.log" 2>&1 &
SERVER_PID=$!

echo "Waiting for server readiness..."
ready=0
for i in $(seq 1 300); do
    if curl -s --max-time 2 "$BASE_URL/models" >/dev/null 2>&1; then
        ready=1
        break
    fi
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "Error: server died during startup. See $model_dir/server.log"
        exit 1
    fi
    sleep 1
done
if [[ "$ready" != "1" ]]; then
    echo "Error: server not ready after 300s"
    exit 1
fi
echo "Server ready (PID $SERVER_PID)."

# Warm-up: first request compiles the Metal graph (can take minutes) — discard it.
echo "Warming up (Metal graph compilation, discarded)..."
curl -s --max-time $CURL_TIMEOUT "$BASE_URL/chat/completions" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":5}" \
    > /dev/null 2>&1 || true
echo "Warm-up done."

report_file="$RESULTS_DIR/${DATE}_benchmark_litert.md"

# Run each prompt
for prompt_num in {1..8}; do
    echo ""
    echo "Running Prompt $prompt_num..."
    echo "--------------------------------------------"

    prompt=$(get_prompt $prompt_num)
    echo "Prompt: ${prompt:0:100}..."

    output_file="$model_dir/task-$(printf "%02d" $prompt_num).txt"
    temp_file=$(mktemp)

    request_json=$(jq -n \
        --arg model "$MODEL" \
        --arg prompt "$prompt" \
        '{model: $model, messages: [{role: "user", content: $prompt}], stream: false}')

    start_time=$(date +%s.%N)
    curl -s --max-time $CURL_TIMEOUT "$BASE_URL/chat/completions" \
        -H "Content-Type: application/json" \
        -d "$request_json" > "$temp_file" 2>&1 || true
    end_time=$(date +%s.%N)

    duration=$(echo "$end_time - $start_time" | bc)
    response=$(jq -r '.choices[0].message.content // empty' "$temp_file" 2>/dev/null || echo "")
    eval_count=$(jq -r '.usage.completion_tokens // 0' "$temp_file" 2>/dev/null || echo "0")
    prompt_eval_count=$(jq -r '.usage.prompt_tokens // 0' "$temp_file" 2>/dev/null || echo "0")

    tokens_per_sec="N/A"
    if [[ "$eval_count" != "0" ]]; then
        tokens_per_sec=$(echo "scale=2; $eval_count / $duration" | bc 2>/dev/null || echo "N/A")
    fi

    gpu_usage="$(get_server_mem_gb) GB (RSS)"

    echo "$response" > "$output_file"
    cat >> "$output_file" << METRICS_EOF

============================================
METRICS
============================================
Model: $MODEL (LiteRT-LM)
Prompt Number: $prompt_num
Duration: ${duration}s
Output Tokens: $eval_count
Input Tokens: $prompt_eval_count
Output Tokens/s: $tokens_per_sec
GPU Memory: $gpu_usage
Timestamp: $(date)
METRICS_EOF

    rm "$temp_file"
    echo "Completed in ${duration}s | ${tokens_per_sec} tokens/s | $eval_count output tokens"
    echo "Output saved to: $output_file"
done

# Generate consolidated report with historical comparison
echo ""
echo "Generating consolidated report..."

cat > "$report_file" << EOF
# Benchmark Report — $DATE — LiteRT-LM (gemma4-26b)

Motor: LiteRT-LM (GPU Metal on-device, sin speculative decoding, sin Ollama).
Endpoint: /v1/chat/completions (OpenAI-compatible).

> Nota metodológica: los tokens/s de LiteRT se calculan como
> completion_tokens / duración total wall-clock (incluye HTTP + prefill),
> por lo que son conservadores frente al eval_duration puro de generación
> que reporta Ollama.

## Resumen de Velocidad — LiteRT

| Modelo | Task | Duración | Tokens Out | Tokens/s | Input Tokens | Memoria |
|--------|------|----------|------------|----------|--------------|---------|
EOF

for prompt_num in {1..8}; do
    output_file="$model_dir/task-$(printf "%02d" $prompt_num).txt"
    if [[ -f "$output_file" ]]; then
        duration=$(grep "Duration:" "$output_file" | awk '{print $2}' | sed 's/s//')
        gpu_usage=$(grep "GPU Memory:" "$output_file" | awk '{print $3, $4}')
        tokens_per_sec=$(grep "Output Tokens/s:" "$output_file" | awk '{print $4}')
        eval_count=$(grep "Output Tokens:" "$output_file" | awk '{print $3}')
        input_tokens=$(grep "Input Tokens:" "$output_file" | awk '{print $3}')
        echo "| gemma4-26b-litert | Task $prompt_num | ${duration}s | $eval_count | $tokens_per_sec | $input_tokens | $gpu_usage |" >> "$report_file"
    fi
done

cat >> "$report_file" << EOF

## Comparativa con modelos Ollama (corridas previas)

EOF

for model in "qwen3.8:27b" "qwen3.6:35b" "qwen3-coder:30b" "ornith-1.5:35b"; do
    hist_dir="$RESULTS_DIR/$(echo $model | tr ':' '-')"
    [[ -d "$hist_dir" ]] || continue
    echo "### $model" >> "$report_file"
    echo "" >> "$report_file"
    echo "| Task | Duración | Tokens Out | Tokens/s | Input Tokens |" >> "$report_file"
    echo "|------|----------|------------|----------|--------------|" >> "$report_file"
    for prompt_num in {1..8}; do
        output_file="$hist_dir/task-$(printf "%02d" $prompt_num).txt"
        if [[ -f "$output_file" ]]; then
            duration=$(grep "Duration:" "$output_file" | head -1 | awk '{print $2}' | sed 's/s//')
            tokens_per_sec=$(grep "Output Tokens/s:" "$output_file" | head -1 | awk '{print $4}')
            eval_count=$(grep "Output Tokens:" "$output_file" | head -1 | awk '{print $3}')
            input_tokens=$(grep "Input Tokens:" "$output_file" | head -1 | awk '{print $3}')
            echo "| Task $prompt_num | ${duration}s | $eval_count | $tokens_per_sec | ${input_tokens:-N/A} |" >> "$report_file"
        fi
    done
    echo "" >> "$report_file"
done

cat >> "$report_file" << EOF
## Evaluación de Calidad (1-5)

| Modelo | Code Gen | Debug | Logic | General | ES | EN | Agent | Refactor |
|--------|----------|-------|-------|---------|----|----|-------|----------|
| gemma4-26b-litert | ? | ? | ? | ? | ? | ? | ? | ? |

## Conclusión

[Resumen ejecutivo con recomendación — pendiente de revisión manual de calidad]
EOF

echo "Report generated: $report_file"
echo ""
echo "============================================"
echo "  LiteRT Benchmark Complete!"
echo "============================================"
echo "Results: $model_dir"
echo "Report: $report_file"
