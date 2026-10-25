# Documentación Completa — Benchmarks MiniCPM-V 4.7 y Proyecto Base

**Fecha de inicio:** 2026-10-24  
**Sesión activa hasta:** en curso  
**Hardware:** MacBook Pro M1 Pro (8 cores, 32GB RAM, macOS), GPU Metal

---

## 1. Objetivo del Proyecto

Evaluar modelos LLM locales para uso en hardware consumer (Apple Silicon M1 Pro, 32GB), midiendo:
- **Velocidad de generación** (tok/s) por modelo/engine
- **Calidad de respuestas** (calificación manual 1-5 por categoría)
- **Uso de memoria** (RAM unificada, footprint visualizable)
- **Latencia** (TTFT — time-to-first-token)
- **Capacidades multimodales** (vision-language) cuando aplique

---

## 2. Cronología de Experimentos y Decisiones

### Fase Previa (Septiembre-Octubre 2026) — Benchmarks Textuales Previos

#### Modelo: qwen3-coder:30b (Ollama, MoE, ~3B activos)
- **Motor:** Ollama (`ollama run`)
- **Resultados:** 34.43 tok/s promedio, 3m53s total en 8 tasks
- **Calidad:** 4.25/5 (code gen débil en algunas tareas)
- **Decisión tomada:** Este modelo sirvió como baseline rápido inicial

#### Modelo: ornith-1.5:35b (Ollama, MoE, ~3B activos)
- **Motor:** Ollama
- **Resultados:** 28.14 tok/s, 7m18s
- **Calidad:** 4.63/5
- **Hallazgo importante:** Bug fatal en código generado (`move_to_end()` sobre dict plano — crash al ejecutar). Los tests no se ejecutaron; la revisión estática pasó el bug.
- **Decisión tomada:** Valida necesidad de **ejecutar** outputs de código para evaluar calidad real

#### Modelo: qwen3.6:35b (Ollama, MoE, ~3B activos)
- **Motor:** Ollama
- **Resultados:** 23.08 tok/s, 12m59s
- **Calidad:** 4.75/5 (mejor quality textual medida)
- **Hallazgo clave:** Verbose extremadamente alto — Task 3 generó 8284 tokens vs 751 de ornith
- **Conclusión:** El tiempo total lo domina la verbosidad del modelo, no los tok/s puros

#### Modelo: qwen3.8:27b (Ollama, Dense, 27B activos)
- **Motor:** Ollama
- **Resultados:** 5.50 tok/s, 44m39s, 2 timeouts (tasks 3 y 7 superaron curl --max-time 600)
- **Calidad:** 5.0/5 en las 6 tasks completadas
- **Decisión tomada:** Dense ≥27B en 32GB es inviable para interacción — **regla operativa permanente**

#### Modelo: gemma4-26b A4B (LiteRT-LM, MoE, ~4B activos)
- **Motor:** LiteRT-LM via `litert-lm serve`
- **Resultados:** 33.45 tok/s conservadores (wall-clock), 3m56s
- **Calidad:** 4.63/5
- **Hallazgos:**
  - RSS engaña (ps muestra 1.9GB; vmmap real = 2.3GB)
  - Primera ejecución lenta (~788s por contención RAM con ornith residente + recompilación Metal)
  - Después de warm-up estable
- **Decisiones tomadas:**
  - Solo 1 engine residente a la vez (RAM contention → swap → catastrófico)
  - Usar `vmmap` no RSS para medir memoria correctamente
  - Warm-up request descartada antes de benchmark formal

### Experimento E1: Comparativa Engine con Mismo Modelo (2026-10-14)

#### Setup: Gemma 4 26B A4B idéntico en ambos engines
| Métrica | LiteRT-LM | Ollama | Ganador |
|---------|-----------|--------|---------|
| Generation tok/s (pure) | **35.43** | 21.61 | **+64% LiteRT** |
| Wall-clock tok/s | **33.69** | 21.37 | LiteRT +58% |
| TTFT (segundos) | 1.50 | **0.60** | Ollama 2.5× más rápido |
| Memory footprint (vmmap) | **2.3 GB** | 17 GB | LiteRT 7× menos |

**Conclusiones:**
- Engine importa significativamente (no marginal)
- LiteRT kernels Metal optimizados por Google dan ganancia sustancial
- Ollama tiene mejor TTFT pero LiteRT genera mucho más rápido
- ASIMETRÍA metodológica: Ollama usa eval_duration (solo generación); LiteRT usa wall-clock total (prefill+HTTP)
- Esto hace que los tok/s de LiteRT sean **conservadores** (subestimados)

### Investigación de Viabilidad Engines Alternativos

#### Strata (engine Metal propio, Qwen3.8-Flash-Next 125B MoE)
- **Decisión:** NO instalar
- **Razón:** ~2.5× más lento que LiteRT (13-14 tok/s), ~120GB disco, sin variant Mac Coder, comprimido a 2-bit

#### Splash (speculative decoding DFlash2 Apple Silicon native)
- **Decisión:** NO viable por hardware
- **Razón:** Requiere Apple M3+ (`MTGPUFamily.apple9`). M1 Pro es Apple7 — incompatibilidad de kernel

#### vLLM-Metal
- **Estado:** Tercer motor potencial
- **Complejidad:** Requiere Python env separado, plugin community
- **Uso recomendado:** Solo si Ollama + LiteRT no dan respuestas limpias

---

## 3. Fase MiniCPM-V 4.7 — Experimentos 2026-10-24

### Modelo Evaluado: MiniCPM-V 4.7 (OpenBMB)
- **Arquitectura:** Vision-Language Multimodal Model (VLMM)
- **Variantes disponibles:**
  - **1B dense** — SigLIP vision encoder + MiniCPM4 backbone
  - **35B-A3B MoE** — SigLIP vision encoder + Qwen3.5 backbone, 35B total / ~3B activos
- **Capacidades:** OCRBench, MathVista, DocVQA, multi-image reasoning, video understanding
- **Licencia:** Apache-2.0 (code), license custom libre tras registro

### Motor 1: Ollama — Pull Library

#### Intento 1: `ollama pull openbmb/minicpm-v4.7`
- **Problema:** Último shard se estancó a ~100 KB/s durante +1 hora (archivado a 21GB partial)
- **Causa probable:** CDN del registry de Ollama tiene bottleneck en shards grandes finales
- **Decisión:** Buscar alternativa de descarga directa

#### Intento 2: Descarga HF directa → Importación local GGUF
- **Archivo descargado:** `/tmp/minicpm-v4/MiniCPM-V-4_7-35B-A3B-Q4_K_M.gguf` (20GB)
- **mmproj descargado:** `mmproj-model-f16-4x.gguf` desde HF repo
- **Importación a Ollama:**
  ```bash
  ollama create minicpm-v4.7-local -f Modelfile-minicpm-direct
  # Éxito: modelo creado (21GB, sha256:9ecf...)
  ```
- **Prueba de visión:** ❌ `tokens: 0` — modelo acepta input pero no genera respuesta
- **Error diagnóstico:** "image input is not supported - hint: provide the mmproj"
- **Problema raíz:** Ollama no soporta mmproj externo vía API `/api/chat` nativamente
- **Solución intentada:** Modelfile con `FROM` directo → mismo resultado

#### Intento 3: `ollama pull openbmb/minicpm-v4.7` (reintentar)
- **Resultado:** Éxito, pero modelo solo descarga manifest pequeño (113B + 570B)
- **Archivos creados:** `sha256-bf3d1c67...` (modelo base 21GB parcial anterior reutilizado)
- **Modelo instalado:** `openbmb/minicpm-v4.7:latest` (22GB)
- **Prueba de visión:** ❌ `Tokens output: 0`
- **Error definitivo al usar CLI:** 
  ```
  error: Failed to load CLIP model from .../sha256-bff3b688e14c...
  ```
- **Diagnóstico final:** El bundle mmproj/CLIP del entry de la librería de Ollama está corrupto o incompatible

**Conclusión Ollama:** MiniCPM-V 4.7 no opera visión en Ollama actualmente — ya sea porque el mmproj de la library está corrupto, o porque el formato de importación local no integra el projector correctamente. Necesita reporte upstream a OpenBMB.

### Motor 2: LiteRT-LM — Importación Directa

#### Importación exitosa: `litert-community/MiniCPM-V-4.7-1B`
```bash
litert-lm import --from-huggingface-repo litert-community/MiniCPM-V-4.7-1B \
  MiniCPM-V-4.7-1B-VL_int8.litertlm minicpm-v4.7-1b
# Resultado: ~/.litert-lm/models/minicpm-v4.7-1b/model.litertlm
```

#### Descripción del modelo importado
- Capabilities: Text+Vision, GPU/CPU backends, Max Context 4096 tokens
- Speculative decoding: NO
- Function calling: NO
- Vision signature selection: [64, 256]

#### Servidor iniciado
```bash
litert-lm serve --host 127.0.0.1 --port 11436
# Disponible en: http://127.0.0.1:11436/v1/chat/completions
```

#### Validación individual (Fase 2)
| Task | Tiempo | Tokens | Resultado |
|------|--------|--------|-----------|
| Math ∫xe^(-x²)dx | 9.3s | 243 | Correcto paso a paso |
| Table OCR CSV | 9.0s | 226 | Estructura OK, valores aproximados |
| App Dashboard UI | 7.2s | 170 | Descripciones razonables |

### Benchmark Completo LiteRT (Todas 20 tasks)

#### Resumen de Resultados
| Type | Tasks Completadas | Avg Time | Tok/s avg | Total tokens |
|------|-------------------|----------|-----------|--------------|
| **A** (multimodal) | 10/12 | 10.5s | 22.6 | 2,686 |
| **B** (text-only) | 8/8 | 20.4s | 33.6 | 5,852 |
| **Total** | 18/20 | 13.4s | 29.5 | 8,538 |

#### Per-task Performance
| Task | Tipo | Tiempo | Tokens | Tok/s | Calificación |
|------|------|--------|--------|-------|-------------|
| OCR Table | A | 11.4s | 199 | 17.5 | Aproximado (errores OCR) |
| Chart Analysis | A | 13.7s | 382 | 27.9 | Bueno |
| Scene Description | A | 6.0s | 118 | 19.7 | Funcional |
| Puzzle Logic | A | ERROR | 0 | N/A | ✗ RuntimeError server |
| Screenshot UI | A | 15.5s | 459 | 29.6 | Excelente descripción |
| Math Integral | A | 17.0s | 531 | 31.2 | Solución correcta |
| Temporal Compare | A | 5.0s | 83 | 16.5 | Breve pero acertado |
| Angle Compare | A | 5.3s | 77 | 14.6 | Breve pero acertado |
| Architecture Diagram | A | ERROR | 0 | N/A | ✗ RuntimeError server |
| Code Recognition | A | 7.9s | 174 | 22.1 | Adecuado |
| Handwriting OCR | A | 5.5s | 103 | 18.7 | Funcional |
| Counting QA | A | 17.9s | 560 | 31.4 | Listó objetos correctos |
| Code Generation | B | 13.5s | 484 | 35.9 | Completo |
| Debugging | B | 8.7s | 300 | 34.6 | Correcto |
| Logic Reasoning | B | 109.7s | 4026 | 36.7 | Extremadamente verbose |
| TCP/UDP General | B | 9.8s | 330 | 33.7 | Bien estructurado |
| ES Summary | B | 2.4s | 71 | 29.4 | Conciso |
| EN Email | B | 2.7s | 74 | 27.1 | Correcto formato |
| Agent Planning | B | 5.8s | 191 | 32.8 | Plan estructurado |
| Code Refactoring | B | 10.9s | 376 | 34.5 | Buenas mejoras SOLID |

#### Errores Identificados (2/12 tasks multimodales fallidas)
- `task-a04-puzzle` (SVG puzzle): `HTTP Error 500: litert_lm_conversation_send_message_stream failed`
- `task-a09-diagram` (SVG diagram): Mismo error
- **Patrón detectado:** LiteRT falla consistentemente con inputs SVG o prompts complejos multi-imagen
- **Posible causa:** Buffer overflow o límite interno en procesamiento de archivos grandes/SVG

### Hallazgos Clave de MiniCPM-V 4.7-1B LiteRT

1. **Speed moderada pero consistente:** ~22.6 tok/s average multimodal, ~33.6 text-only
   - Más lento que gemma4-26b LiteRT (~33-35 tok/s) — esperado dado que es menor arquitectura
   - Token generation rate bastante homogénea entre tasks

2. **OCR functional pero imperfecto:**
   - Extrae estructura de tablas correctamente
   - Valores numéricos a veces confusos ($34,000 vs $34.000)
   - Reconoce contexto general bien

3. **Math reasoning competitivo:**
   - Resolvió ∫₀^∞ xe^(-x²)dx correctamente con procedimiento completo
   - Generó 531 tokens — detalle apropiado para tarea matemática

4. **UI analysis bueno:**
   - Describió dashboard correctamente identificando componentes funcionales
   - Flaggeó posibles problemas UX (texto oscuro sobre fondo)

5. **Verbosity variable:**
   - Math task: muy detallado (4026 tokens en task B3 — extremo)
   - Summaries: concisos (71 tokens en task B5)
   - Comportamiento similar a qwen3.6 pero menos extremo

6. **Limitaciones detectadas:**
   - Fallo con SVGs/puzzles complejos (2/12 tasks crashed)
   - Sin speculative decoding support
   - Sin function calling
   - Limitado a 4096 tokens max context

---

## 4. Decisiones Arquitecturales y Tecnológicas Tomadas

### Decision 1: LiteRT como motor primario para MiniCPM-V 4.7
**Por qué:**
- Bundle oficial disponible para 1B (litert-community/HF)
- Funciona visión + texto correctamente
- Importación trivial: `litert-lm import --from-huggingface-repo`
- Servidor estable y predecible

**Contra:**
- Solo variante 1B disponible oficialmente
- Error con SVGs complejos (2/12 tasks)
- No hay version 35B-A3B en LiteRT aún

### Decision 2: Ollama abandonado para MiniCPM-V 4.7 vision
**Por qué:**
- Library bundle tiene mmproj corrupto/incompatible
- Importación local de GGUF + mmproj no habilita visión vía API
- Errores persistentes de "Failed to load CLIP model"
- Sin workaround evidente

**Alternativas exploradas y rechazadas:**
- Strata: demasiado lento (13-14 tok/s vs 35 tok/s LiteRT)
- Splash: incompatible hardware (requiere M3+)
- vLLM-metal: complejidad desproporcionada

### Decision 3: Benchmark banco de pruebas dual (Type A + Type B)
**Por qué:**
- Type A mide capacidades VLM únicas (vision-language)
- Type B permite comparación cross-modelo con benchmarks previos (mismos 8 prompts)
- Separación permite identificar si rendimiento viene de lenguaje o comprensión visual

### Decision 4: Imágenes sintéticas generadas programáticamente
**Por qué:**
- Reproducibles determinísticamente (random seed fijo)
- Control preciso sobre dificultad y contenido
- Cobertura de múltiples dominios (tablas, gráficos, diagramas, screenshots)
- Tamaño controlado para estabilidad de inferencia

**Limitaciones:**
- No representan calidad fotográfica real
- OCR puede ser más fácil/fácil que documentos reales
- Decisiones futuras: agregar imágenes reales de fuentes públicas

### Decision 5: Medición de métricas conservadoras
**Por qué (basado en experimento E1):**
- Ollama reporta eval_duration (solo generación)
- LiteRT reportó wall-clock total (incluye HTTP+prefill)
- Para evitar sesgo, usamos wall-clock para ambos
- Esto subestima tok/s reales de generación (conservador)

---

## 5. Infraestructura Técnica Actual

### Scripts Disponibles

| Script | Propósito | Estado |
|--------|-----------|--------|
| `benchmark.sh` | Benchmark tradicional Ollama (Qwen series) | ✅ Estable |
| `benchmark-litert.sh` | Benchmark LiteRT (gemma4-26b) | ✅ Estable |
| `benchmark-litert-stream.py` | Streaming benchmark TTFT+generation simétrico | ✅ Estable |
| `generate-benchmark-images.py` | Generador imágenes principales (12 tasks A) | ✅ Funcional |
| `generate-benchmark-images-remaining.py` | Imágenes faltantes (tasks 5,7,8,10) | ✅ Funcional |
| `test-multimodal-api.py` | Test API format correcto Ollama (`images: [base64]`) | ✅ Verificado |
| `test-minicpm-liteRT-vision.py` | Validación individual LiteRT vision | ✅ Funcional |
| `test-minicpm-liteRT-batch.py` | Batch lite 3 tasks LiteRT validation | ✅ Funcional |
| `benchmark-litert-complete.py` | **Benchmark completo 20 tasks LiteRT** | ✅ Funcional, resultados guardados |
| `start-ollama.sh` | Start Ollama with M1 Pro optimizations | ✅ Funcional |

### Archivos de Configuración
| Archivo | Contenido |
|---------|-----------|
| `.env` | Optimizaciones Ollama M1 Pro (KV cache q8_0, flash attention, etc.) |
| `poc-antigravity/config-experiments.json` | LiteRT disk cache config |
| `benchmark-multimodal-prompts.txt` | 20 prompts (12 A + 8 B) actualizados |

### Servidores Corriendo
| Servicio | Puerto | Estado |
|----------|--------|--------|
| Ollama server | 11434 | ✅ Running (con gemma4, ornith, qwen3-coder, qwen3.6, qwen3.8, qwen3-vl) |
| LiteRT server | 11436 | ⏹ Stopped (se restartará cuando se necesite) |

---

## 6. Estado de Artefactos Organizados

### Directorio `benchmark-results/`

```
benchmark-results/
├── ANALYSIS.md                           ← Análisis consolidado versiones anteriores
├── 2026-09-03_benchmark.md               ← Resultados originales Qwen
├── 2026-10-12_benchmark.md               ← Results ornith comparison
├── 2026-10-14_experiments.md             ← Experimento E1 (same model, different engines)
├── 2026-10-14_benchmark_litert.md        ← Benchmark gemma4 LiteRT
├── 2026-10-24_MINICPMV47_ANALYSIS.md     ← DOCUMENTACIÓN ESTÁNDARIZADA (nuevo)
├── minicpm-v4-liteRT-batch/              ← Resultados completos MiniCPM-V 4.7-1B LiteRT
│   ├── summary.json                      ← Reporte consolidado JSON
│   ├── task-a01-ocr.json through task-a12-counting.json
│   └── task-b01-codegen.json through task-b08-refactor.json
├── qwen3.8-27b/task-XX.txt               ← Raw responses old benchmark
├── qwen3.6-35b/task-XX.txt
├── qwen3-coder-30b/task-XX.txt
└── ornith-1.5-35b/task-XX.txt
```

### Nuevo directorio: `benchmark-images/`
```
benchmark-images/
├── task01-document-table.png    ← Factura tabla (OCR)
├── task02-combined-chart.png    ← Gráfico barras+línea
├── task03-urban-scene.png       ← Escena urbana simplificada
├── task04-logic-puzzle.svg      ← Puzzle lógico visual
├── task05-app-dashboard.png     ← Mockup app móvil
├── task06-math-problem.png      ← Problema cálculo integral
├── task07-temporal-comparison.png ← Antes/Después temporal
├── task08-angle-variations.png  ← Dos ángulos objeto
├── task09-microservices-diagram.svg ← Arquitectura microservicios
├── task10-code-printed.png      ← Código impreso simulado
├── task11-handwritten-notes.png ← Notas manuscritas
└── task12-counting-scene.png    ← Escena conteo objetos
```

### Ubicación de modelos LiteRT
```
~/.litert-lm/models/
├── gemma4-26b/model.litertlm    ← Gemma 4 26B A4B
└── minicpm-v4.7-1b/model.litertlm ← MiniCPM-V 4.7-1B (nuevo)
```

### Ubicación de modelos Ollama
```
~/.ollama/models/blobs/
├── sha256-d372de8... (20GB)     ← MiniCPM-V 4.7-35B (corrupt CLIP)
├── sha256-bf3d1c67... (20GB)    ← Parcial viejo del primer pull
├── sha256-aaeb640... (20GB)     ← Another copy (duplicate)
├── sha256-7121486... (17GB)     ← gemma4-26b
├── sha256-1194192... (17GB)     ← ornith-1.5:35b (delete candidate)
├── sha256-f5f1dd8... (16GB)     ← qwen3.8:27b (delete candidate)
├── sha256-ed12a4... (5.7GB)     ← qwen3-coder:30b
└── sha256-ac3714... (888MB)     ← Gemma base
```

### Ubicación de modelos descargados (temp)
```
/tmp/minicpm-v4/
├── MiniCPM-V-4_7-35B-A3B-Q4_K_M.gguf    ← 20GB GGUF descargado de HF
├── mmproj-model-f16-4x.gguf              ← Multimodal projector
└── .cache/huggingface/                   ← Cache HF download
```

---

## 7. Línea Base — Referencias Comparativas Establecidas

### Velocidad (tok/s promedio en nuestro hardware M1 Pro 32GB)
| Modelo | Engine | Tok/s | Notas |
|--------|--------|-------|-------|
| qwen3-coder:30b | Ollama | 34.43 | Fasterest text-based |
| gemma4-26b | LiteRT | 33.45* | Conservative metric (wall-clock) |
| ornith-1.5:35b | Ollama | 28.14 | Good balance quality/speed |
| qwen3.6:35b | Ollama | 23.08 | Most verbose, high quality |
| qwen3.8:27b | Ollama | 5.50 | Dense — too slow for interactive |
| MiniCPM-V 4.7-1B | LiteRT | 22.6 | **Multimodal — NEW** |

*\*Conservative: wall-clock includes HTTP+prefill overhead, not pure decode speed*

### Calidad (evaluación manual 1-5 sobre 8 tasks estándar)
| Modelo | Score | Dominio Fuerte | Dominio Débil |
|--------|-------|---------------|--------------|
| qwen3.8:27b | 5.0 | All completed tasks | N/A (timeout on hard tasks) |
| qwen3.6:35b | 4.75 | Reasoning verbose | Verbosity hurts throughput |
| gemma4-26b | 4.63 | Balanced code/general | N/A |
| ornith-1.5:35b | 4.63 | Agentic planning, general | Code execution bugs |
| qwen3-coder:30b | 4.25 | Coding focused | General knowledge weaker |
| MiniCPM-V 4.7-1B | TBD (needs evaluation) | Vision/OCR/Multimodal | TBD on text tasks |

---

## 8. Reglas Operativas Derivadas de Experiencia

1. **Solo 1 engine inference resident a la vez** — RAM contention → swap → catastrófico
2. **Dense ≥27B en 32GB es inviable** — usar siempre MoE o ≤7B dense
3. **Medir memoria con `vmmap`, nunca con `ps` RSS** — LiteRT RSS engaña severamente
4. **Usar wall-clock metrics (TTFT + gen) para comparaciones justas** — no comparar eval_duration contra wall-clock
5. **Validar code outputs mediante ejecución, no revisión estática** — bugs fatales pueden pasar revisión
6. **Para vision models: verificar que el mmproj/CLIP esté funcional antes de benchmarkear** — problema recurrente con Ollama
7. **Imágenes sintéticas son reproducibles** pero tienen limitaciones respecto a datos reales
8. **Los benchmarks históricos de Qwen/Ollama usan formato `/api/generate`**, no `/api/chat`

---

## 9. Próximos Pasos Recomendados

### Inmediatos
- [ ] Ejecutar evaluación manual de calidad (scale 1-5) para MiniCPM-V 4.7-1B LiteRT en tasks A+B
- [ ] Agregar imágenes reales a `benchmark-images/` (fuentes públicas, dataset) para testeo más robusto
- [ ] Investigar fix para errores SVG/LiteRT (tasks a04 y a09 fallaron consistentemente)

### Mediano Plazo
- [ ] Revisar si OpenBMB publica fix para mmproj corrupto de Ollama library
- [ ] Considerar reporte upstream a litert-community sobre disponibilidad de 35B-A3B
- [ ] Explorar conversion manual GGUF→.litertlm para el 35B si se necesita comparación directa
- [ ] Integrar benchmarks LiteRT nuevos en pipeline existente (`benchmark.sh` style wrapper)

### Largoplazo
- [ ] Evaluar hardware upgrades (M2+/≥64GB) si 35B-A3B en LiteRT se vuelve prioridad
- [ ] Considerar cloud inference (API calls) como fallback para modelos >32GB cuando sea necesario
- [ ] Mantener línea de benchmarks mensual para tracking de evolución de modelos

---

## 10. Contacto y Fuentes

| Recurso | URL |
|---------|-----|
| MiniCPM-V GitHub | https://github.com/OpenBMB/MiniCPM-V |
| MiniCPM-V 4.7 Docs | https://openbmb.cn/docs/en/guides/minicpm-v/minicpm-v-4.7 |
| HuggingFace (model) | https://huggingface.co/openbmb/MiniCPM-V-4.7-35B-A3B |
| HuggingFace (GGUF) | https://huggingface.co/collections/openbmb/minicpm-v-47 |
| LiteRT-LM Docs | https://github.com/google-ai-edge/LiteRT-LM |
| Cookbook Deploy | https://github.com/OpenSQZ/MiniCPM-V-CookBook |
| Paper (Nat Commun 2025) | arXiv:2408.01800 |
