# LLM Local Benchmark Suite

**Benchmarking de modelos LLM locales en Apple Silicon M1/M2/M3 Pro/Max (32GB+ RAM)**

## Tabla de Contenido

- [Sobre este proyecto](#sobre-este-proyecto)
- [Modelos Evaluados](#modelos-evaluados)
- [Resultados Clave](#resultados-clave)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Cómo Usarlo](#cómo-usarlo)
- [Metodología](#metodología)
- [Hallazgos Principales](#hallazgos-principales)
- [Requisitos](#requisitos)
- [Licencia](#licencia)

---

## Sobre este proyecto

Este repositorio documenta una serie exhaustiva de benchmarks realizados sobre modelos de lenguaje locales ejecutándose en hardware Apple Silicon. El objetivo es proporcionar datos concretos y reproducibles sobre velocidad, calidad y eficiencia de diferentes engines y arquitecturas de modelos.

**Hardware de referencia:** MacBook Pro M1 Pro, 8 cores, 32GB RAM unificada.

Los benchmarks cubren dos categorías principales:
1. **Text-to-text** — Modelos puramente textuales (Qwen series, Ornith, Gemma)
2. **Vision-Language** — Modelos multimodales con capacidades de comprensión visual (MiniCPM-V 4.7)

---

## Modelos Evaluados

### Motor: Ollama (GGUF runtime + Metal GPU)

| Modelo | Arquitectura | Parámetros Activos | Tok/s Promedio | Notas |
|--------|-------------|-------------------|---------------|-------|
| `qwen3-coder:30b` | MoE | ~3B | **34.43** | Más rápido para tareas de código |
| `ornith-1.5:35b` | MoE | ~3B | **28.14** | Buen balance calidad/velocidad |
| `qwen3.6:35b` | MoE | ~3B | **23.08** | Más verboso, alta calidad textual |
| `qwen3.8:27b` | Dense | 27B | **5.50** | ❌ Demasiado lento para interacción |

### Motor: LiteRT-LM (Google kernels optimizados)

| Modelo | Arquitectura | Parámetros Activos | Tok/s Promedio | Notas |
|--------|-------------|-------------------|---------------|-------|
| `gemma4-26b A4B` | MoE | ~4B | **33.45*** | Kernels Metal optimizados por Google |
| `MiniCPM-V 4.7-1B` | Dense (VLMM) | 1B | **22.6** | ✅ Vision-Language funcional |

*\*Métrica conservadora: wall-clock total (incluye HTTP+prefill), no solo generación pura.*

---

## Resultados Clave

### Velocidad General (tok/s promedio)

```
34.43 ┤  qwen3-coder:30b (Ollama)     ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
33.45 ┤  gemma4-26b (LiteRT)          ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
28.14 ┤  ornith-1.5:35b (Ollama)      ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
23.08 ┤  qwen3.6:35b (Ollama)         ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
22.60 ┤  MiniCPM-V 4.7-1B (LiteRT)    ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰  ← Vision-Language
 5.50 ┤  qwen3.8:27b (Ollama, Dense)  ▰▰▰
```

### Comparativa Engine (mismo modelo: Gemma 4 26B)

| Métrica | Ollama | LiteRT-LM | Diferencia |
|---------|--------|-----------|------------|
| Generación tok/s (pure) | 21.61 | **35.43** | **+64%** |
| Wall-clock tok/s | 21.37 | **33.69** | **+58%** |
| TTFT (primera respuesta) | **0.60s** | 1.50s | Ollama 2.5× más rápido |
| Memoria real (vmmap) | 17 GB | **2.3 GB** | **LiteRT 7× menos** |

---

## Estructura del Proyecto

```
├── benchmark.sh                     # Script principal benchmarks Ollama
├── benchmark-litert.sh              # Script principal benchmarks LiteRT  
├── benchmark-litert-stream.py       # Benchmark streaming TTFT+generation simétrico
├── benchmark-litert-complete.py     # Benchmark completo LiteRT (20 tasks multimodal)
│
├── benchmark-images/                # Imágenes sintéticas benchmark (12 tasks)
├── benchmark-prompts.txt            # Prompts originales (8 tasks B textuales)
├── benchmark-multimodal-prompts.txt # Prompts extendidos (12 A + 8 B = 20 tasks)
│
├── benchmark-results/               # 📊 Todos los resultados y análisis
│   ├── minicpm-v4-liteRT-batch/     ← MiniCPM-V 4.7 resultados completos
│   │   └── summary.json             ← Reporte JSON consolidado
│   ├── qwen3-coder-30b/           ← Raw responses benchmarks Qwen
│   ├── qwen3.6-35b/
│   ├── qwen3.8-27b/
│   ├── ornith-1.5-35b/
│   ├── gemma4-26b-litert/
│   ├── ANALYSIS.md                  ← Análisis consolidado histórico
│   └── 2026-10-24_MINICPMV47_ANALYSIS.md  ← Documentación completa sesión actual
│
├── poc-antigravity/                 # PoC agentes autónomos (requiere SDK externo)
├── LICENSE                          # MIT License
└── README.md                        # Este archivo
```

---

## Cómo Usarlo

### 1. Instalación

```bash
git clone <repo-url>
cd llm-local-benchmark
```

### 2. Requisitos Previos

Instalar uno de los siguientes motores:

**Para Ollama:**
```bash
brew install ollama
ollama pull qwen3-coder:30b      # o cualquier modelo deseado
```

**Para LiteRT-LM:**
```bash
# Instalar litert-lm CLI desde pypi o build desde source
pip install litert-lm-cli
litert-lm import --from-huggingface-repo litert-community/gemma4-26b gemma4-26b
litert-lm serve --host 127.0.0.1 --port 11435
```

### 3. Ejecutar Benchmarks

```bash
# Benchmark tradicional con Ollama
./benchmark.sh                              # Menú interactivo
./benchmark.sh qwen3-coder:30b              # Modelo específico
./benchmark.sh all                          # Todos secuencialmente

# Benchmark con LiteRT
./benchmark-litert.sh                       # Benchmark gemma4-26b LiteRT

# Benchmark streaming simétrico (TTFT + generation rate)
python3 benchmark-litert-stream.py litert --reps 3 --tasks 1,5,7

# Benchmark completo multimodal (MiniCPM-V 4.7 via LiteRT)
python3 benchmark-litert-complete.py
```

### 4. Regenerar Imágenes

```bash
python3 generate-benchmark-images.py
python3 generate-benchmark-images-remaining.py
```

---

## Metodología

### Tasks Estándar (8 prompts text-to-text)

Las mismas 8 tareas se repiten para cada modelo/benchmark:

| Task | Tipo | Descripción |
|------|------|-------------|
| B1 | Code Generation | Implementar cache LRU con TTL + tests |
| B2 | Debugging | Encontrar bug en Fibonacci recursivo |
| B3 | Logic Reasoning | Puzzle de verdad/mentira (3 personas) |
| B4 | General Knowledge | TCP vs UDP + ejemplos producción |
| B5 | Spanish Summary | Microservicios en 3 bullet points |
| B6 | English Writing | Email profesional declining job offer |
| B7 | Agentic Planning | Plan infraestructura Ubuntu/Docker/SSL |
| B8 | Code Refactoring | SOLID refactoring Python code |

### Tasks Multimodales (12 tasks con imagen)

Solo aplican a modelos vision-language como MiniCPM-V 4.7:

| Task | Tipo | Contenido |
|------|------|-----------|
| A1 | OCR Table | Extraer factura → CSV |
| A2 | Chart Analysis | Interpretar gráfico barras+línea |
| A3 | Scene Description | Describir escena urbana |
| A4 | Logic Puzzle | Secuencia lógica visual |
| A5 | UI/Screenshot | Analizar dashboard app móvil |
| A6 | Math Problem | Resolver integral ∫xe^(-x²)dx |
| A7 | Temporal Compare | Antes/Después comparison |
| A8 | Angle Compare | Dos ángulos del mismo objeto |
| A9 | Architecture Diagram | Explicar microservicios flow |
| A10 | Code Recognition | Leer código de imagen impresa |
| A11 | Handwriting OCR | Transcribir notas manuscritas |
| A12 | Visual QA | Contar objetos específicos |

### Métricas Registradas

- **Generación tok/s** (wall-clock): tokens generados ÷ tiempo total
- **Input token count**: tokens de prompt consumidos
- **Output token count**: tokens generados por el modelo
- **Quality score** (manual): calificación 1-5 por categoría tras revisión

---

## Hallazgos Principales

### 1. MoE domina sobre Dense (factor 5-6× en velocidad)
Modelos MoE con ~3B activos logran 23-34 tok/s. Un dense de 27B activa cae a 5.5 tok/s. **Conclusión:** Dense ≥27B en 32GB RAM es inviable para uso interactivo.

### 2. Engine importa significativamente (no marginal)
Con el mismo modelo base (Gemma 4 26B), LiteRT genera tokens **64% más rápido** que Ollama usando **7× menos memoria**. La ventaja está en kernels Metal optimizados por Google.

### 3. Quality ≠ Speed correlation
La correlación entre velocidad y calidad observada es prácticamente nula. Los modelos más rápidos no son necesariamente mejores calificados. Esto valida la necesidad de evaluar ambos ejes independientemente.

### 4. Verbosity impacta throughput total
El tiempo total de una tarea lo domina cuán largo responde el modelo, no cuántos tok/s genera. Qwen3.6 puede generar 8284 tokens para una tarea donde ornith usa 751, duplicando el tiempo total sin mejorar calidad.

### 5. Validación vía ejecución necesaria
Un output con "tests unitarios" puede contener bugs fatales si nunca se ejecuta. La revisión estática no detectó un error de `AttributeError` en ornith que crashea al ejecutar. Es imprescindible validar outputs de código mediante ejecución real.

### 6. Memory measurement debe usar vmmap, no RSS
En LiteRT, `ps` muestra ~1.9GB pero `vmmap physical footprint` revela ~2.3GB reales. En Ollama, `ollama ps` muestra usage directo. Ambos son correctos dentro de su ecosistema pero incomparables directamente.

---

## Requerimientos de Hardware

| Componente | Mínimo | Recomendado | Notas |
|-----------|--------|-------------|-------|
| CPU | Apple M1 (qualquer chip) | Apple M2 Pro / M3 Pro | Más núcleos = mejor throughput |
| RAM | 16GB (models ≤7B) | 32GB (models ≤35B MoE) | Para models >35B necesitar ≥64GB |
| Storage | 50GB libre | 100GB libre | Models individuales de 17-23GB |
| GPU | Apple Silicon GPU | Apple Silicon GPU | Todos usan Metal automatically |

---

## Contribuir

Se aceptan PRs para:
- Nuevos benchmarks de modelos adicionales
- Mejoras en scripts de benchmarking
- Correcciones de metodología
- Imágenes de prueba adicionales

Por favor seguir las convenciones existentes:
- Scripts bash deben ser POSIX compatible donde sea posible
- Python usa typing hints (3.10+)
- Resultados JSON en formato compacto (<indentado>)
- Imágenes sintéticas preferidas sobre datasets externos

---

## Licencia

MIT License — ver [LICENSE](./LICENSE) para detalles completos.

Los modelos evaluados tienen sus propias licencias (varían por proveedor). Verificar compatibilidad antes de uso comercial.
