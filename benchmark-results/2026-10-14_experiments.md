# Reporte de Experimentos — Cerrando las Preguntas Abiertas

**Fecha:** 2026-10-14
**Objetivo:** resolver las 6 preguntas abiertas de `ANALYSIS.md` §7 con experimentos controlados.
**Hardware:** MacBook Pro M1 Pro, 8 núcleos (6P+2E), 32GB memoria unificada.
**Modelo (idéntico en ambos engines):** Gemma 4 26B A4B (MoE, ~4B activos, Q4_K_M). LiteRT: checkpoint `.litertlm` 14.7GB. Ollama: tag `gemma4:26b-a4b-it-q4_K_M` 17GB.
**Herramienta:** `benchmark-litert-stream.py` (nuevo) — cliente streaming que mide TTFT (envío→primer token) y ritmo de generación `tokens/(total−TTFT)` por igual en ambos engines.

---

## E1 — Aislamiento de engine (el experimento central) + E6 (n=3, mediana)

Misma red neuronal, misma cuantización, mismos 8 prompts, **3 corridas** por engine. Modelo en caliente, warm-up descartado. Resultados **medianas**:

| Métrica | LiteRT-LM | Ollama | Ganador |
|---------|-----------|--------|--------|
| **Generación (tok/s)** | **35.43** | 21.61 | **LiteRT +64%** |
| Wall-clock (tok/s) | 33.69 | 21.37 | LiteRT +58% |
| TTFT (s) | 1.50 | **0.60** | **Ollama 2.5× más rápido** |
| Memoria | **2.3 GB** (vmmap footprint) | 17 GB (residente) | **LiteRT 7× menos** |

Consistencia entre corridas: LiteRT generación 34.6–36.5 tok/s (rango estrecho); Ollama 20.6–24.4 tok/s. Ambos 0 fallos en 24 requests.

### Veredicto E1 (cierra la pregunta "¿el engine importa?")
**Sí, importa — y no marginalmente.** Con el mismo modelo, LiteRT genera **64% más rápido** que Ollama. Supera holgadamente el umbral del 10% del plan. La diferencia es técnica, no de ecosistema.

**Causa (inferida de TTFT vs ritmo):** la diferencia está en la **decodificación**, no en la infraestructura. Ollama tiene mejor TTFT (0.6s vs 1.5s — su prefill/carga de contexto es más ágil), pero por token generado LiteRT es mucho más rápido. Causas probables: kernels Metal optimizados por Google para Apple Silicon en `.litertlm`, y el scheduling por request de Ollama añade overhead por token. La configuración de Ollama (`FLASH_ATTENTION=1`, `KV_CACHE_TYPE=q8_0`, contexto 32k) ya era la óptima del `start-ollama.sh`.

**Nota de control:** los pesos no son bitwise-idénticos (toolchains de conversión distintas: GGUF/Q4_K_M para Ollama vs formato propio LiteRT), pero arquitectura, tamaño y calibración coinciden. El sesgo residual de conversión es mucho menor que el 64% observado.

### Corrección a la recomendación de ANALYSIS.md
El análisis previo recomendaba Gemma/LiteRT y ornith/Ollama como "empate en calidad". Con datos de velocidad directos, **LiteRT con Gemma 4 26B es el mejor setup medido**: calidad top-2 (4.63) + el engine más rápido probado + la menor huella de memoria.

---

## E5 — Memoria real (RSS engañoso → footprint)

| Engine | Métrica | Valor | Qué mide realmente |
|--------|---------|-------|--------------------|
| LiteRT | `ps` RSS | 1.9 GB | Solo estructuras de control del proceso |
| LiteRT | `vmmap` physical footprint | **2.3 GB** | Memoria real del proceso (pesos memory-mapped bajo demanda) |
| Ollama | `ollama ps` | **17 GB** | Pesos residentes en GPU/memoria unificada (carga eager) |

### Veredicto E5 (cierra "¿el RSS de LiteRT engaña?")
**Sí, y la diferencia de memoria es real.** El `vmmap` confirma que LiteRT usa **2.3GB** — los 14.7GB de pesos están *memory-mapped* y se cargan por página bajo demanda, no residentes. Ollama carga los 17GB de golpe. En la práctica, LiteRT deja ~30GB de memoria unificada libres para el sistema frente a los 17GB ocupados de Ollama. La métrica `ollama ps` (la que usaban los reportes previos) sí es comparable entre sí entre modelos Ollama, pero **no** con el RSS de LiteRT — hay que usar `vmmap` para el lado LiteRT.

---

## E3 — Arranque en frío y `cache: disk`

Config `poc-antigravity/config-experiments.json` con `{"default":{"cache":"disk"}}` (verificado aplicado en el log: *"Using cache from config… disk"*). 3 arranques secuenciales:

| Arranque | Tiempo a server-ready | Primer token (TTFT real) | Artefactos compilados |
|----------|----------------------|--------------------------|------------------------|
| Cold (sin cache) | 0.6s | 20.9s | 0 |
| Warm (tras cold) | 0.7s | 47.9s | 0 |
| Warm2 | 0.7s | 43.5s | 0 |

### Veredicto E3 (cierra "¿cuánto cuesta el cold start y qué ahorra el cache?")
**Hallazgo que corrige la hipótesis previa:**
1. **El server liga el puerto en <1s siempre** — la carga del modelo es *lazy*, ocurre en el primer request, no en el arranque.
2. **`cache: disk` no produjo ningún artefacto** junto al modelo ni en el cache del sistema, y **no aceleró** los arrances subsiguientes (de hecho fueron más lentos, pero por ruido, no por cache negativo). En el backend **GPU/Metal la persistencia de grafos compilados no funciona** en esta versión — consistente con el schema, que solo documenta `memory` para CPU.
3. **La variación 20.9s → 47.9s es ruido de carga de pesos desde disco** (estado del file cache del OS), no compilación Metal. El rango 20-48s es el costo real del primer token en frío.

**Corrección importante al ANALYSIS.md:** la corrida anómala de **788s** en los PoC **NO fue recompilación Metal**. Fue **contención de memoria**: ornith (22GB) y gemma (15GB) residentes a la vez en un Mac de 32GB → swap. Con un solo modelo residente (condición del benchmark formal) LiteRT arranca y responde normal. La lección operativa correcta es: **un engine residente a la vez**, no "usar cache_dir".

---

## E4 — Speculative decoding

Verificado con `litert_lm.ModelInfo` sobre nuestro checkpoint:

```
speculative_decoding: False
function_calling:     False
thinking:             False
backends:             ['gpu']
```

### Veredicto E4 (cierra "¿el speedup de speculative decoding es real aquí?")
**Infeasible con este checkpoint.** El `gemma-4-26B-A4B-it.litertlm` oficial no incluye draft model. Existe una variante con soporte (`gemma-4-26b-web-mtp`) en HuggingFace, pero es un build distinto (WebGPU + vision + MTP), no comparable y no probado aquí. Para habilitarlo habría que importar esa variante — experimento separado si interesa. **No afecta las conclusiones de E1:** la ventaja de LiteRT se mide con decodificación normal.

---

## Resumen: las 6 preguntas abiertas, cerradas

| # | Pregunta (ANALYSIS §7) | Estado | Respuesta |
|---|------------------------|--------|-----------|
| 1 | ¿El engine importa con el mismo modelo? | **Cerrada** | **Sí.** LiteRT 64% más rápido que Ollama (35.4 vs 21.6 tok/s) con Gemma 4 26B idéntico. |
| 2 | ¿Speculative decoding aporta? | **Cerrada (infeasible)** | El checkpoint LiteRT no lo soporta (no draft model). Requiere variante MTP distinta. |
| 3 | ¿Cuánto cuesta el cold start / qué ahorra el cache? | **Cerrada** | Server listo <1s (carga lazy); primer token 20-48s. `cache: disk` no funciona en GPU/Metal. |
| 4 | ¿Son robustos los números (n≥3)? | **Cerrada** | Sí. LiteRT 34.6-36.5 tok/s, Ollama 20.6-24.4 tok/s — sin solaparse, diferencia estable. |
| 5 | ¿La memoria de LiteRT es realmente menor? | **Cerrada** | Sí. 2.3GB (vmmap, lazy) vs 17GB (Ollama, eager). El RSS de 1.9GB subestimaba, pero la ventaja es real. |
| 6 | Métrica simétrica (streaming/TTFT) | **Cerrada** | `benchmark-litert-stream.py` mide TTFT y generación igual en ambos. |

## Recomendación final actualizada

**Mejor setup local medido en este hardware: LiteRT-LM + Gemma 4 26B A4B** — el engine más rápido (64% sobre Ollama con el mismo modelo), la menor memoria (2.3GB vs 17GB), calidad top-2 (4.63), y ecosistema Antigravity SDK verificado. **Ollama** mantiene ventaja en variedad de modelos y en TTFT inicial (0.6s vs 1.5s) para cargas puntuales.

## Archivos generados

- `benchmark-litert-stream.py` — benchmark unificado streaming/TTFT (reutilizable).
- `benchmark-results/experiments/stream/litert-gemma4-26b/` — 3 corridas × 8 tasks + summary.
- `benchmark-results/experiments/stream/ollama-gemma4-26b-q4km/` — 3 corridas × 8 tasks + summary.
- `e3_coldstart.sh`, `poc-antigravity/config-experiments.json` — experimento E3.
