#!/bin/bash
# E3: measure LiteRT cold vs warm start with disk graph cache.
set -u
BIN="poc-antigravity/.venv/bin/litert-lm"
MODEL_DIR="$HOME/.litert-lm/models/gemma4-26b"
PORT=11436
URL="http://127.0.0.1:$PORT/v1/chat/completions"
CONFIG="poc-antigravity/config-experiments.json"

wait_ready() {
  local t0=$(python3 -c 'import time;print(time.perf_counter())')
  for i in $(seq 1 300); do
    if curl -s --max-time 2 "http://127.0.0.1:$PORT/v1/models" >/dev/null 2>&1; then
      python3 -c "import time;print(f'{time.perf_counter()-$t0:.1f}')"
      return 0
    fi
    sleep 0.5
  done
  echo "TIMEOUT"; return 1
}

first_ttft() {
  python3 - "$URL" <<'PY'
import json, sys, time, urllib.request
url = sys.argv[1]
body = json.dumps({"model":"gemma4-26b","messages":[{"role":"user","content":"hi"}],"stream":True,"stream_options":{"include_usage":True}}).encode()
req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json"})
t0=time.perf_counter()
with urllib.request.urlopen(req, timeout=600) as r:
    for raw in r:
        line=raw.decode().strip()
        if not line.startswith("data:"): continue
        d=line[5:].strip()
        if d=="[DONE]": break
        try: o=json.loads(d)
        except: continue
        ch=o.get("choices") or [{}]
        if (ch[0].get("delta") or {}).get("content"):
            print(f"{time.perf_counter()-t0:.2f}"); break
PY
}

run_once() {
  local label=$1
  "$BIN" serve --config "$CONFIG" --host 127.0.0.1 --port "$PORT" >/tmp/e3_server.log 2>&1 &
  local pid=$!
  local ready=$(wait_ready)
  local ttft=$(first_ttft)
  kill $pid 2>/dev/null; wait $pid 2>/dev/null
  echo "$label | ready=${ready}s | first_token=${ttft}s"
}

echo "=== E3: LiteRT disk graph cache (config cache=disk) ==="
echo "--- graph cache dir before ---"
find "$MODEL_DIR" -type f ! -name "*.litertlm" 2>/dev/null | wc -l | xargs echo "compiled artifacts:"

echo ""
echo "--- Run 1 (COLD: compile Metal graph, no cache yet) ---"
run_once "cold"

echo "--- graph cache dir after cold run ---"
find "$MODEL_DIR" -type f ! -name "*.litertlm" 2>/dev/null -exec du -h {} \; | head

echo ""
echo "--- Run 2 (WARM: cache present on disk) ---"
run_once "warm"

echo ""
echo "--- Run 3 (WARM again, confirm stability) ---"
run_once "warm2"
