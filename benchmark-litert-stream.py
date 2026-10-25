#!/usr/bin/env python3
"""Symmetric streaming benchmark for LiteRT-LM and Ollama.

Measures TTFT (time to first token) and inter-token generation rate via
streaming, so both engines are timed with the same methodology.

Usage:
    python benchmark-litert-stream.py <litert|ollama> [--reps N] [--tasks 1,5,7]

Requires the corresponding server already running:
    litert: poc-antigravity/.venv/bin/litert-lm serve --port 11435
    ollama: ./start-ollama.sh <model>   (or any running Ollama)
"""

import argparse
import json
import statistics
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROMPTS_FILE = SCRIPT_DIR / "benchmark-prompts.txt"
RESULTS_DIR = SCRIPT_DIR / "benchmark-results" / "experiments" / "stream"

ENGINES = {
    "litert": {
        "url": "http://127.0.0.1:11435/v1/chat/completions",
        "model": "gemma4-26b",
        "protocol": "openai",
        "dir": "litert-gemma4-26b",
    },
    "ollama": {
        "url": "http://localhost:11434/api/generate",
        "model": "gemma4:26b-a4b-it-q4_K_M",
        "protocol": "ollama",
        "dir": "ollama-gemma4-26b-q4km",
    },
}


def get_prompts() -> dict:
    text = PROMPTS_FILE.read_text()
    prompts = {}
    current = None
    for line in text.splitlines():
        if line.startswith("PROMPT_") and ":" in line:
            num, _, content = line.partition(":")
            current = int(num.replace("PROMPT_", ""))
            prompts[current] = content.strip()
        elif current is not None and line.strip():
            prompts[current] += "\n" + line
    return prompts


def stream_openai(url: str, model: str, prompt: str, timeout: int = 600):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "stream_options": {"include_usage": True},
    }).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    ttft = None
    chunks = 0
    usage = {}
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                break
            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                continue
            choices = obj.get("choices") or [{}]
            delta = choices[0].get("delta") or {}
            if delta.get("content") and ttft is None:
                ttft = time.perf_counter() - t0
            if delta.get("content"):
                chunks += 1
            if obj.get("usage"):
                usage = obj["usage"]
    total = time.perf_counter() - t0
    return {
        "ttft": ttft,
        "total": total,
        "output_tokens": usage.get("completion_tokens", chunks),
        "input_tokens": usage.get("prompt_tokens"),
        "internal_eval_duration": None,
    }


def stream_ollama(url: str, model: str, prompt: str, timeout: int = 600):
    body = json.dumps({"model": model, "prompt": prompt, "stream": True, "think": False}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    ttft = None
    usage = {}
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        for raw in resp:
            try:
                obj = json.loads(raw.decode("utf-8", errors="replace"))
            except json.JSONDecodeError:
                continue
            if obj.get("response") and ttft is None:
                ttft = time.perf_counter() - t0
            for key in ("eval_count", "eval_duration", "prompt_eval_count"):
                if key in obj:
                    usage[key] = obj[key]
    total = time.perf_counter() - t0
    return {
        "ttft": ttft,
        "total": total,
        "output_tokens": usage.get("eval_count", 0),
        "input_tokens": usage.get("prompt_eval_count"),
        "internal_eval_duration": usage.get("eval_duration"),
    }


def measure_memory(engine: str) -> str:
    try:
        if engine == "litert":
            out = subprocess.run(
                ["pgrep", "-f", "litert-lm serve"], capture_output=True, text=True, timeout=5
            ).stdout.split()
            if not out:
                return "N/A"
            out_pid = out[0]
            vm = subprocess.run(
                ["vmmap", out_pid], capture_output=True, text=True, timeout=60
            ).stdout
            for line in vm.splitlines():
                if "Physical footprint:" in line and "peak" not in line:
                    return " ".join(line.split()[2:4]) + " (vmmap footprint)"
            rss = subprocess.run(
                ["ps", "-o", "rss=", "-p", out_pid], capture_output=True, text=True, timeout=5
            ).stdout.strip()
            return f"{int(rss) / 1048576:.1f} GB RSS" if rss else "N/A"
        else:
            out = subprocess.run(
                ["ollama", "ps"], capture_output=True, text=True, timeout=10
            ).stdout.strip().splitlines()
            if len(out) > 1:
                parts = out[1].split()
                return f"{parts[2]} {parts[3]}" if len(parts) > 3 else out[1]
            return "N/A"
    except Exception as exc:
        return f"error: {exc}"


def run_once(engine: str, prompt: str) -> dict:
    cfg = ENGINES[engine]
    fn = stream_openai if cfg["protocol"] == "openai" else stream_ollama
    result = fn(cfg["url"], cfg["model"], prompt)
    ttft = result["ttft"]
    total = result["total"]
    tokens = result["output_tokens"]
    gen_time = total - ttft if ttft else None
    result["gen_tps"] = (tokens / gen_time) if (gen_time and tokens) else None
    result["wall_tps"] = (tokens / total) if total else None
    if result.get("internal_eval_duration") and tokens:
        result["ollama_internal_tps"] = tokens / (result["internal_eval_duration"] / 1e9)
    else:
        result["ollama_internal_tps"] = None
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("engine", choices=list(ENGINES))
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--tasks", default="1,2,3,4,5,6,7,8")
    args = parser.parse_args()

    engine = args.engine
    cfg = ENGINES[engine]
    out_dir = RESULTS_DIR / cfg["dir"] / f"rep{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    prompts = get_prompts()
    task_nums = [int(t) for t in args.tasks.split(",")]
    memory = measure_memory(engine)

    print(f"Engine: {engine} | Model: {cfg['model']} | Reps: {args.reps} | Memory: {memory}")
    all_results = []

    for rep in range(1, args.reps + 1):
        print(f"\n=== Repetition {rep}/{args.reps} ===")
        for num in task_nums:
            result = run_once(engine, prompts[num])
            result["rep"] = rep
            result["task"] = num
            all_results.append(result)
            ttft = f"{result['ttft']:.2f}s" if result["ttft"] else "N/A"
            gen = f"{result['gen_tps']:.2f}" if result["gen_tps"] else "N/A"
            print(
                f"Task {num:>2} | TTFT {ttft:>7} | gen {gen:>6} tok/s | "
                f"wall {result['wall_tps']:.2f} tok/s | {result['output_tokens']} tokens"
            )
            (out_dir / f"task-{num:02d}-rep{rep}.txt").write_text(json.dumps({
                k: v for k, v in result.items() if v is not None
            }, indent=2) + "\n")

    gen_rates = [r["gen_tps"] for r in all_results if r["gen_tps"]]
    ttfts = [r["ttft"] for r in all_results if r["ttft"]]
    summary = {
        "engine": engine,
        "model": cfg["model"],
        "reps": args.reps,
        "tasks": task_nums,
        "memory": memory,
        "median_gen_tps": round(statistics.median(gen_rates), 2) if gen_rates else None,
        "median_ttft_s": round(statistics.median(ttfts), 2) if ttfts else None,
        "median_wall_tps": round(statistics.median([r["wall_tps"] for r in all_results]), 2),
        "median_output_tokens": round(statistics.median([r["output_tokens"] for r in all_results])),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    sys.exit(main())
