#!/bin/bash
# Benchmark script for Qwen models on M1 Pro 32GB
# Usage: ./benchmark.sh [model|all]
# Example: ./benchmark.sh qwen3.8:27b
#          ./benchmark.sh all

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/benchmark-results"
PROMPTS_FILE="$SCRIPT_DIR/benchmark-prompts.txt"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CURL_TIMEOUT=600

# Models to benchmark
MODELS=("qwen3.8:27b" "qwen3.6:35b" "qwen3-coder:30b")

# Create results directory
mkdir -p "$RESULTS_DIR"

# Function to display menu
show_menu() {
    echo "============================================"
    echo "  Qwen Benchmark - M1 Pro 32GB"
    echo "============================================"
    echo ""
    echo "Select model to benchmark:"
    for i in "${!MODELS[@]}"; do
        echo "  $((i+1)). ${MODELS[$i]}"
    done
    echo "  4. All models (sequential)"
    echo "  0. Exit"
    echo ""
    read -p "Enter choice [1-4]: " choice
}

# Function to extract prompt from file
get_prompt() {
    local prompt_num=$1
    awk "/^PROMPT_${prompt_num}:/{found=1; sub(/^PROMPT_${prompt_num}:[[:space:]]*/, \"\"); print; next} found && /^[[:space:]]*$/{exit} found{print}" "$PROMPTS_FILE"
}

# Function to run benchmark for a single model
run_benchmark() {
    local model=$1
    local model_dir="$RESULTS_DIR/$(echo $model | tr ':' '-')"

    echo "Benchmarking model: $model"
    echo "============================================"

    # Create model directory
    mkdir -p "$model_dir"

    # Run each prompt
    for prompt_num in {1..8}; do
        echo ""
        echo "Running Prompt $prompt_num..."
        echo "--------------------------------------------"

        # Get the prompt
        local prompt=$(get_prompt $prompt_num)
        echo "Prompt: ${prompt:0:100}..."

        # Create output file
        local output_file="$model_dir/task-$(printf "%02d" $prompt_num).txt"

        # Run Ollama API
        echo "Running ollama API for $model..."

        # Start timing
        local start_time=$(date +%s.%N)

        # Run the model using Ollama API
        local temp_file=$(mktemp)
        local request_json=$(jq -n \
            --arg model "$model" \
            --arg prompt "$prompt" \
            '{model: $model, prompt: $prompt, stream: false, think: false}')

        curl -s --max-time $CURL_TIMEOUT http://localhost:11434/api/generate \
            -d "$request_json" > "$temp_file" 2>&1 || true

        # End timing
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc)

        # Extract response text
        local response=$(jq -r '.response // empty' "$temp_file" 2>/dev/null || echo "")

        # Extract metrics from API response
        local eval_count=$(jq -r '.eval_count // 0' "$temp_file" 2>/dev/null || echo "0")
        local eval_duration_ns=$(jq -r '.eval_duration // 0' "$temp_file" 2>/dev/null || echo "0")
        local prompt_eval_count=$(jq -r '.prompt_eval_count // 0' "$temp_file" 2>/dev/null || echo "0")
        local prompt_eval_duration_ns=$(jq -r '.prompt_eval_duration // 0' "$temp_file" 2>/dev/null || echo "0")

        # Calculate tokens per second
        local tokens_per_sec="N/A"
        local prompt_tps="N/A"
        if [[ "$eval_duration_ns" != "0" && "$eval_count" != "0" ]]; then
            tokens_per_sec=$(echo "scale=2; $eval_count / ($eval_duration_ns / 1000000000)" | bc 2>/dev/null || echo "N/A")
        fi
        if [[ "$prompt_eval_duration_ns" != "0" && "$prompt_eval_count" != "0" ]]; then
            prompt_tps=$(echo "scale=2; $prompt_eval_count / ($prompt_eval_duration_ns / 1000000000)" | bc 2>/dev/null || echo "N/A")
        fi

        # Get GPU memory usage
        local gpu_usage=$(ollama ps 2>/dev/null | grep "$model" | awk '{print $3}' || echo "N/A")

        # Save response to output file
        echo "$response" > "$output_file"

        # Append metrics
        cat >> "$output_file" << METRICS_EOF

============================================
METRICS
============================================
Model: $model
Prompt Number: $prompt_num
Duration: ${duration}s
Output Tokens: $eval_count
Input Tokens: $prompt_eval_count
Output Tokens/s: $tokens_per_sec
Input Tokens/s: $prompt_tps
GPU Memory: $gpu_usage
Timestamp: $(date)
METRICS_EOF

        rm "$temp_file"

        echo "Completed in ${duration}s | ${tokens_per_sec} tokens/s | ${eval_count} output tokens"
        echo "GPU Memory: $gpu_usage"
        echo "Output saved to: $output_file"
    done

    echo ""
    echo "Benchmark completed for $model"
    echo "Results saved to: $model_dir"
}

# Function to generate consolidated report
generate_report() {
    local report_file="$RESULTS_DIR/${DATE}_benchmark.md"

    echo "Generating consolidated report..."

    cat > "$report_file" << EOF
# Benchmark Report — $DATE

## Resumen de Velocidad

| Modelo | Task | Duración | Tokens Out | Tokens/s | Input Tokens | GPU Mem |
|--------|------|----------|------------|----------|--------------|---------|
EOF

    # Add results for each model
    for model in "${MODELS[@]}"; do
        local model_dir="$RESULTS_DIR/$(echo $model | tr ':' '-')"

        for prompt_num in {1..8}; do
            local output_file="$model_dir/task-$(printf "%02d" $prompt_num).txt"

            if [[ -f "$output_file" ]]; then
                local duration=$(grep "Duration:" "$output_file" | awk '{print $2}' | sed 's/s//')
                local gpu_usage=$(grep "GPU Memory:" "$output_file" | awk '{print $3}')
                local tokens_per_sec=$(grep "Output Tokens/s:" "$output_file" | awk '{print $3}')
                local eval_count=$(grep "Output Tokens:" "$output_file" | awk '{print $3}')
                local input_tokens=$(grep "Input Tokens:" "$output_file" | awk '{print $3}')

                echo "| $model | Task $prompt_num | ${duration}s | $eval_count | $tokens_per_sec | $input_tokens | $gpu_usage |" >> "$report_file"
            fi
        done
    done

    cat >> "$report_file" << EOF

## Evaluación de Calidad (1-5)

| Modelo | Code Gen | Debug | Logic | General | ES | EN | Agent | Refactor |
|--------|----------|-------|-------|---------|----|----|-------|----------|
EOF

    # Add quality placeholders
    for model in "${MODELS[@]}"; do
        echo "| $model | ? | ? | ? | ? | ? | ? | ? | ? |" >> "$report_file"
    done

    cat >> "$report_file" << EOF

## Conclusión

[Resumen ejecutivo con recomendación]

### Archivos Generados

- \`benchmark-results/${DATE}_benchmark.md\` — Este reporte
- \`benchmark-results/qwen3.8-27b/\` — Resultados de qwen3.8:27b
- \`benchmark-results/qwen3.6-35b/\` — Resultados de qwen3.6:35b
- \`benchmark-results/qwen3-coder-30b/\` — Resultados de qwen3-coder:30b

### Para Revisar Calidad

Revisa cada archivo \`task-XX.txt\` en las carpetas de cada modelo y asigna una puntuación de 1-5 en la tabla de calidad de arriba.
EOF

    echo "Report generated: $report_file"
}

# Main script
main() {
    # Check if Ollama is running
    if ! ollama ls >/dev/null 2>&1; then
        echo "Error: Ollama server is not running"
        echo "Please run: ./start-ollama.sh"
        exit 1
    fi

    # Check if prompts file exists
    if [[ ! -f "$PROMPTS_FILE" ]]; then
        echo "Error: Prompts file not found: $PROMPTS_FILE"
        exit 1
    fi

    # Parse command line arguments
    if [[ $# -eq 1 ]]; then
        case $1 in
            "all")
                echo "Running benchmark for all models..."
                for model in "${MODELS[@]}"; do
                    run_benchmark "$model"
                done
                ;;
            *)
                if ollama show "$1" > /dev/null 2>&1; then
                    run_benchmark "$1"
                else
                    echo "Invalid model: $1 (not installed locally)"
                    echo "Installed models: $(ollama list | tail -n +2 | awk '{print $1}' | tr '\n' ' ')"
                    exit 1
                fi
                ;;
        esac
    else
        # Show interactive menu
        show_menu

        case $choice in
            1)
                run_benchmark "${MODELS[0]}"
                ;;
            2)
                run_benchmark "${MODELS[1]}"
                ;;
            3)
                run_benchmark "${MODELS[2]}"
                ;;
            4)
                for model in "${MODELS[@]}"; do
                    run_benchmark "$model"
                done
                ;;
            0)
                echo "Exiting..."
                exit 0
                ;;
            *)
                echo "Invalid choice"
                exit 1
                ;;
        esac
    fi

    # Generate consolidated report
    generate_report

    echo ""
    echo "============================================"
    echo "  Benchmark Complete!"
    echo "============================================"
    echo "Results saved to: $RESULTS_DIR"
    echo "Report: $RESULTS_DIR/${DATE}_benchmark.md"
    echo ""
    echo "Next steps:"
    echo "1. Review the results in benchmark-results/"
    echo "2. Rate quality (1-5) in the report"
    echo "3. Add conclusion based on your findings"
}

# Run main function
main "$@"
