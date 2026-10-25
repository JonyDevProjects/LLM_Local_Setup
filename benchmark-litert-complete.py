#!/usr/bin/env python3
"""Complete benchmark for MiniCPM-V 4.7 via LiteRT - All 20 tasks."""
import json
import base64
import time
import urllib.request
import os
from datetime import datetime

# Configuration
URL = "http://127.0.0.1:11436/v1/chat/completions"
IMG_DIR = "benchmark-images"
RESULTS_DIR = "benchmark-results/minicpm-v4-liteRT-batch"
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---- TASK DEFINITIONS ----
TASKS_A = [
    # Task A1: OCR Document Extraction
    ("task-a01-ocr", f"{IMG_DIR}/task01-document-table.png", 
     "Extrae toda la información de esta factura como CSV válido. Columnas: concepto,cantidad,precio_unitario,total."),
    
    # Task A2: Chart Interpretation  
    ("task-a02-chart", f"{IMG_DIR}/task02-combined-chart.png",
     "Analiza este gráfico combinado de barras y línea. ¿Cuáles son las tendencias principales, picos más altos y valores más bajos por serie?"),
    
    # Task A3: Scene Description
    ("task-a03-scene", f"{IMG_DIR}/task03-urban-scene.png",
     "Describe detalladamente esta escena urbana. Incluye personas, edificios, árboles, vehículos y el contexto general."),
    
    # Task A4: Visual Logic Puzzle
    ("task-a04-puzzle", f"{IMG_DIR}/task04-logic-puzzle.svg",
     "¿Cuál es la regla que sigue esta secuencia de figuras? Explica tu razonamiento paso a paso y predice qué figura viene después del '?'. "),
    
    # Task A5: Screenshot Analysis
    ("task-a05-screenshot", f"{IMG_DIR}/task05-app-dashboard.png",
     "Esta es una captura de pantalla de una app móvil. Describe cada sección visible, identifica funcionalidades e indica si hay algún problema UX/UI."),
    
    # Task A6: Math from Image
    ("task-a06-math", f"{IMG_DIR}/task06-math-problem.png",
     "Resuelve paso a paso este problema matemático mostrado en la imagen. Da la respuesta final exacta."),
    
    # Task A7: Multi-image Comparison (temporal)
    ("task-a07-temporal", f"{IMG_DIR}/task07-temporal-comparison.png",
     "Compara estas dos imágenes temporalmente ('Antes' vs 'Después'). ¿Qué cambió significativamente? ¿Cuáles son las implicaciones de esos cambios?"),
    
    # Task A8: Multi-image Comparison (angles)
    ("task-a08-angles", f"{IMG_DIR}/task08-angle-variations.png",
     "Estas dos vistas muestran un objeto desde ángulos diferentes. ¿Cómo difieren las perspectivas? Construye una descripción integrada que combine ambas."),
    
    # Task A9: Diagram Reading
    ("task-a09-diagram", f"{IMG_DIR}/task09-microservices-diagram.svg",
     "Explica esta arquitectura de microservicios. ¿Cómo fluyen los datos entre componentes? ¿Cuáles son los puntos únicos de failure?"),
    
    # Task A10: Code Recognition
    ("task-a10-code", f"{IMG_DIR}/task10-code-printed.png",
     "Lee el código Python visible en esta imagen impresa. Explica qué hace el programa, identifica bugs potenciales y sugiere mejoras."),
    
    # Task A11: Handwritten Text
    ("task-a11-handwriting", f"{IMG_DIR}/task11-handwritten-notes.png",
     "Transcribe el texto escrito a mano de esta nota. Corrige errores obvios pero mantén el significado original."),
    
    # Task A12: Visual QA Counting
    ("task-a12-counting", f"{IMG_DIR}/task12-counting-scene.png",
     "¿Cuántos círculos rojos hay en esta imagen? ¿Cuántos triángulos verdes? Lista cada uno con su posición aproximada descrita."),
]

TASKS_B = [
    # Task B1: Code Generation
    ("task-b01-codegen", None, 
     "Escribe una función en Python que implemente un cache LRU con TTL (time-to-live). Incluye tests unitarios."),
    
    # Task B2: Code Debugging
    ("task-b02-debug", None,
     "Encuentra y explica el bug en este código:\ndef fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)\n# El problema: extremadamente lenta para n > 35.\n# Proponé una solución optimizada."),
    
    # Task B3: Logic Reasoning
    ("task-b03-logic", None,
     "Tres personas (A, B, C) están en una habitación. A dice 'Al menos uno de nosotros miente'. B dice 'A miente'. C dice 'B miente'. Solo uno dice la verdad. ¿Quién dice la verdad? Explica paso a paso."),
    
    # Task B4: General Knowledge
    ("task-b04-tcpudp", None,
     "Explica la diferencia entre TCP y UDP. ¿Cuándo usarías cada uno? Da ejemplos concretos de uso en producción."),
    
    # Task B5: Spanish Summary
    ("task-b05-es-summary", None,
     "Resume en 3 bullet points los conceptos clave de la arquitectura de microservicios, sus ventajas y desventajas principales."),
    
    # Task B6: English Writing
    ("task-b06-en-email", None,
     "Write a professional email declining a job offer politely, explaining that you've decided to stay at your current company. Keep it under 150 words."),
    
    # Task B7: Agentic Tool Planning
    ("task-b07-agent-plan", None,
     "Tengo un servidor Ubuntu 22.04 con Docker, Nginx y PostgreSQL. Necesito: 1) Actualizar kernel sin downtime, 2) Configurar SSL wildcard para *.miapp.com, 3) Backup automático PostgreSQL a S3. Dame plan con comandos exactos."),
    
    # Task B8: Code Refactoring
    ("task-b08-refactor", None,
     "Refactorizá este código Python para SOLID y manejo de errores:\nimport requests\ndef get_data(url): r = requests.get(url); return r.json()\ndef process(data): result=[]; [result.append(item['name'].upper()) for item in data]; return result\ndef save(data): f=open('output.json','w'); f.write(str(data)); f.close()"),
]


def encode_image(img_path):
    if img_path is None:
        return None
    with open(img_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()


def run_task(task_id, img_path, prompt_text, max_tokens=2048, stream=False):
    content_parts = [{"type": "text", "text": prompt_text}]
    img_b64 = encode_image(img_path)
    if img_b64:
        content_parts.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}})
    
    request_data = {
        "model": "minicpm-v4.7-1b",
        "messages": [{"role": "user", "content": content_parts}],
        "max_tokens": max_tokens,
        "stream": stream
    }
    
    req = urllib.request.Request(URL, data=json.dumps(request_data).encode(), headers={"Content-Type": "application/json"})
    start = time.time()
    try:
        resp = urllib.request.urlopen(req, timeout=300)
        elapsed = time.time() - start
        result = json.loads(resp.read().decode())
        
        choices = result.get("choices", [])
        message = choices[0].get("message", {}) if choices else {}
        content = message.get("content", "")
        usage = result.get("usage", {})
        
        return {
            "task_id": task_id,
            "elapsed": round(elapsed, 2),
            "content": content,
            "output_tokens": usage.get("completion_tokens", 0),
            "input_tokens": usage.get("prompt_tokens", 0),
            "wall_tps": round(usage.get("completion_tokens", 0) / elapsed, 2) if elapsed > 0 else 0,
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "task_id": task_id,
            "elapsed": round(elapsed, 2),
            "content": "",
            "output_tokens": 0,
            "input_tokens": 0,
            "wall_tps": 0,
            "error": str(e)
        }


def main():
    print("=" * 80)
    print("MiniCPM-V 4.7-1B LiteRT Benchmark — Complete Run")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    all_results = []
    
    # ---- PART 1: Multimodal Tasks (A) ----
    print("\n" + "=" * 60)
    print("PART 1: Multimodal Tasks (A) — 12 tasks")
    print("=" * 60)
    
    total_a_time = 0
    for i, (task_id, img_path, prompt) in enumerate(TASKS_A, 1):
        print(f"\n[{i}/12] {task_id}...")
        r = run_task(task_id, img_path, prompt, max_tokens=1024)
        
        if "error" in r:
            print(f"  ❌ ERROR: {r['error']}")
        else:
            print(f"  ⏱️  {r['elapsed']:.1f}s | {r['output_tokens']} tokens | {r['wall_tps']:.2f} tok/s")
            # Save individual result
            result_file = os.path.join(RESULTS_DIR, f"{task_id}.json")
            with open(result_file, 'w') as f:
                json.dump(r, f, indent=2, ensure_ascii=False)
        
        all_results.append(r)
        total_a_time += r["elapsed"]
    
    print(f"\n✅ Part 1 complete: {total_a_time:.1f}s total ({total_a_time/len(TASKS_A):.1f}s avg)")
    
    # ---- PART 2: Text-to-Text Tasks (B) ----
    print("\n" + "=" * 60)
    print("PART 2: Text-to-Text Tasks (B) — 8 tasks")
    print("=" * 60)
    
    total_b_time = 0
    for i, (task_id, _, prompt) in enumerate(TASKS_B, 1):
        print(f"\n[{i}/8] {task_id}...")
        r = run_task(task_id, None, prompt, max_tokens=2048)
        
        if "error" in r:
            print(f"  ❌ ERROR: {r['error']}")
        else:
            print(f"  ⏱️  {r['elapsed']:.1f}s | {r['output_tokens']} tokens | {r['wall_tps']:.2f} tok/s")
            result_file = os.path.join(RESULTS_DIR, f"{task_id}.json")
            with open(result_file, 'w') as f:
                json.dump(r, f, indent=2, ensure_ascii=False)
        
        all_results.append(r)
        total_b_time += r["elapsed"]
    
    print(f"\n✅ Part 2 complete: {total_b_time:.1f}s total ({total_b_time/len(TASKS_B):.1f}s avg)")
    
    # ---- SUMMARY REPORT ----
    print("\n" + "=" * 80)
    print("SUMMARY REPORT")
    print("=" * 80)
    
    # Separate by type
    a_results = [r for r in all_results if r["task_id"].startswith("task-a")]
    b_results = [r for r in all_results if r["task_id"].startswith("task-b")]
    
    a_times = [r["elapsed"] for r in a_results if "error" not in r]
    b_times = [r["elapsed"] for r in b_results if "error" not in r]
    
    print(f"\nMultimodal Tasks (A): {len(a_times)} tasks completed")
    if a_times:
        print(f"  Total: {sum(a_times):.1f}s | Avg: {sum(a_times)/len(a_times):.1f}s | Min: {min(a_times):.1f}s | Max: {max(a_times):.1f}s")
    
    print(f"\nText-to-Text Tasks (B): {len(b_times)} tasks completed")
    if b_times:
        print(f"  Total: {sum(b_times):.1f}s | Avg: {sum(b_times)/len(b_times):.1f}s | Min: {min(b_times):.1f}s | Max: {max(b_times):.1f}s")
    
    # Token stats
    a_tokens = sum(r["output_tokens"] for r in a_results)
    b_tokens = sum(r["output_tokens"] for r in b_results)
    print(f"\nTokens generated:")
    print(f"  Type A (multimodal): {a_tokens}")
    print(f"  Type B (text-only): {b_tokens}")
    print(f"  Total: {a_tokens + b_tokens}")
    
    # Errors
    errors_a = len([r for r in a_results if "error" in r])
    errors_b = len([r for r in b_results if "error" in r])
    if errors_a or errors_b:
        print(f"\n⚠️  Errors: A={errors_a}, B={errors_b}")
    
    # Save consolidated report
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "engine": "LiteRT-LM",
        "model": "minicpm-v4.7-1b",
        "tasks_completed": len(all_results),
        "part_a_multimodal": {
            "count": len(a_results),
            "completed": len(a_times),
            "failed": errors_a,
            "avg_time_s": round(sum(a_times)/len(a_times), 2) if a_times else None,
            "total_time_s": round(sum(a_times), 2),
        },
        "part_b_textual": {
            "count": len(b_results),
            "completed": len(b_times),
            "failed": errors_b,
            "avg_time_s": round(sum(b_times)/len(b_times), 2) if b_times else None,
            "total_time_s": round(sum(b_times), 2),
        },
        "results": all_results,
    }
    
    report_file = os.path.join(RESULTS_DIR, "summary.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Report saved to: {report_file}")
    print(f"📁 Individual results: {RESULTS_DIR}/")
    print("\n=== COMPLETE ===")


if __name__ == "__main__":
    main()
