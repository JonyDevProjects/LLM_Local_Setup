# Análisis Consolidado — Benchmarks Locales en M1 Pro 32GB

**Fecha:** 2026-10-14
**Alcance:** síntesis de causa y efecto de 3 rondas de benchmark (2026-09-03, 2026-10-12, 2026-10-14) y 3 PoCs (Antigravity SDK × Ollama, Antigravity SDK × LiteRT, comparación de latencia entre engines).

**Hardware de referencia:** MacBook Pro M1 Pro, 8 núcleos (6P + 2E), 32GB de memoria unificada, macOS. Todos los modelos corren sobre la GPU/Metal del chip.

**Modelos evaluados:**

| Modelo | Engine | Arquitectura | Párams totales | Activos por token | Checkpoint | Cuantización |
|--------|--------|--------------|----------------|-------------------|------------|--------------|
| qwen3.8:27b | Ollama | Dense | 27B | 27B | 18 GB | Q4_K_M (aprox.) |
| qwen3.6:35b | Ollama | MoE | 35B | ~3B | 22 GB | Q4_K_M (aprox.) |
| qwen3-coder:30b | Ollama | MoE | 30B | ~3B | 20 GB | Q4_K_M (aprox.) |
| ornith-1.5:35b | Ollama | MoE | 35.5B | ~3B | 23 GB | Q4_K_M |
| gemma4-26b A4B | LiteRT-LM | MoE | 26B | ~4B | 14.7 GB | formato .litertlm (GPU) |

---

## 1. Resultado principal

| Modelo | Engine | Tok/s prom. | Total 8 tasks | Calidad (1-5) | Timeouts |
|--------|--------|-------------|---------------|---------------|----------|
| qwen3-coder-30b | Ollama | 34.43 | 3m 53s | 4.25 | 0 |
| gemma4-26b | LiteRT | 33.45* | 3m 56s | 4.63 | 0 |
| ornith-1.5:35b | Ollama | 28.14 | 7m 18s | 4.63 | 0 |
| qwen3.6-35b | Ollama | 23.08 | 12m 59s | 4.75 | 0 |
| qwen3.8:27b | Ollama | 5.50 | 44m 39s | 5.0 (6 tasks) | 2 |

*\*Métrica conservadora — ver §3.*

**Conclusión en una línea:** en este hardware y con estos modelos, la velocidad de generación la determina casi exclusivamente el número de **parámetros activos por token** (MoE vs dense), el engine (Ollama vs LiteRT) mueve la aguja un 10-20%, y la calidad no correlaciona con la velocidad.

---

## 2. Por qué los resultados son así — causas principales

### 2.1 Dense vs MoE domina todo (causa del 6× de velocidad)

qwen3.8:27b (dense, 27B activos) promedió 5.5 tok/s; los MoE con ~3B activos promediaron 23-34 tok/s. **Causa:** en un modelo denso cada token recorre todos los parámetros; en un MoE solo se activan 2-4 experts por token. Con cuantización Q4 en memoria unificada de 32GB, el cuello de botella es el **ancho de banda de la memoria**, que es proporcional a los parámetros activos, no a los totales. El ratio observado (5.5 → 28 tok/s ≈ 5×) es consistente con el ratio de activos (27B → 3B ≈ 9×) descontando overhead de routing.

**Efecto práctico:** en un M1 Pro de 32GB, un modelo dense ≥27B es inutilizable para interacción; todos los modelos viables de esta lista son MoE o ≤7B dense.

### 2.2 Los MoE entre sí: los 3B activos no implican la misma velocidad

Entre los MoE "similares" hay un 50% de diferencia (34.4 vs 23.1 tok/s) siendo todos ~3B activos. Causas identificadas:

- **Verbosidad del modelo (efecto en el tiempo total, no en tok/s):** qwen3.6:35b generó 8284 tokens en la task 3 (logic puzzle) contra 751 de ornith y 1356 de gemma para la misma pregunta. Eso explica que ornith complete el benchmark en 7m18s y qwen3.6 en 12m59s con tok/s parecidos: **el tiempo total lo domina cuánto habla el modelo, no cuán rápido habla**.
- **Arquitectura interna:** número de layers, experts por capa, y eficiencia del kernel de inferencia. No es posible aislar este efecto con los datos disponibles (no tenemos configs idénticas con un solo factor cambiado).
- **Calidad de cuantización:** todos en Q4_K_M, así que este factor es menor entre Ollama; más relevante al comparar engines (§2.4).

### 2.3 El fallo de qwen3.8:27b (dos timeouts)

Los timeouts en tasks 3 y 7 fueron por **acumulación**: a 5.5 tok/s, respuestas largas (el resto de tasks generó 1300-3400 tokens) superan el `curl --max-time 600`. No es un crash del modelo sino una consecuencia directa de §2.1. Su calidad promedio (5.0) está calculada sobre 6 tasks — **no es comparable 1:1** con los promedios de 8 tasks de los demás, y tiende al alto por selección (las dos tasks que falló son las más largas/difíciles).

### 2.4 LiteRT vs Ollama (diferencia real de engine: modesta)

gemma4-26b vía LiteRT (33.45 tok/s) y qwen3-coder vía Ollama (34.43 tok/s) están empatados técnicamente, pero **la comparación favorece a Ollama por cómo se mide** (ver §3). Ajustando cualitativamente, LiteRT con 4B activos (más que los 3B de qwen3-coder) y un checkpoint 26% más liviano (14.7 vs 20 GB) rinde por encima de lo esperado. Factores del buen desempeño de LiteRT:

- **Cuantización/calibración del formato `.litertlm`** optimizada para GPU Metal (Google afirma optimizaciones específicas para Apple Silicon; el benchmark de Gemma 4 E2B reporta 607MB de footprint físico con weights caching de XNNPACK).
- **Sin capa de servidor intermedia comparable:** Ollama añade su runtime de scheduling/KV cache management; LiteRT corre en proceso.
- **KV-cache:** Ollama corría con `OLLAMA_KV_CACHE_TYPE=q8_0` y contexto 32k para ahorrar VRAM; LiteRT usa su configuración por defecto (64k de KV según las docs del SDK, sin quantizar el KV declarado). El mayor contexto disponible de LiteRT no penalizó la velocidad en prompts cortos.

**Lo que NO se puede afirmar:** que LiteRT sea "más rápido que Ollama" en general — solo se probó 1 modelo por engine, y los modelos difieren en arquitectura, tamaño y tokenizador. Un experimento limpio requeriría el **mismo checkpoint** en ambos engines (convertido a GGUF para Ollama) o al menos modelos de idéntica arquitectura.

### 2.5 Diferencias de memoria: por qué el RSS de LiteRT engaña

Ollama reporta 20-22GB por modelo (vía `ollama ps`); el server LiteRT reportó 1.9GB de RSS. **No es que LiteRT use 10× menos memoria** — el RSS del proceso Python/C++ solo cuenta sus estructuras de control; los ~15GB de pesos viven en memoria compartida de la GPUMetal y no se atribuyen al proceso en la medición simple con `ps`. Ambos engines residentes en memoria unificada consumen lo que pesa el checkpoint más KV cache. Lo que sí es real: el checkpoint de gemma (14.7GB) es **33% más liviano** que ornith (23GB) siendo modelos de capacidad similar — cuantización más agresiva o arquitectura más eficiente (26B totales vs 35.5B).

---

## 3. La asimetría metodológica más importante (léela antes de comparar tablas)

**Ollama** reporta `eval_duration`: solo el tiempo de **generación** de tokens (excluye prefill y HTTP). Sus tok/s son "velocidad pura de decodificación".

**LiteRT** (`litert-lm serve`) no expone esa métrica; el benchmark calculó `completion_tokens / duración total wall-clock`, que **incluye** prefill, serialización JSON y HTTP. Sus tok/s son "velocidad efectiva punta a punta".

**Efecto:** las cifras de LiteRT son sistemáticamente más bajas de lo que sería su velocidad de generación pura. Con prompts cortos (37-135 input tokens) el prefill es milisegundos, así que el sesgo es pequeño (estimado <5%), pero existe. Un reporte futuro debería usar streaming y medir time-to-first-token + ritmo inter-token para igualar condiciones.

Secundario: los **contadores de input tokens difieren por tokenizador** (el mismo prompt de la task 1 contó 37 tokens en Ollama y 41 en LiteRT), por lo que las columnas "Input Tokens" no son comparables entre engines, solo dentro del mismo engine.

---

## 4. Estabilidad y arranque en frío (hallazgo de los PoCs)

El PoC de re-ejecución LiteRT tardó **788s** contra 26s del PoC Ollama en la misma prueba. Causas (diagnosticadas del log):

1. El script PoC no usó `cache_dir`, así que LiteRT **recompiló el grafo Metal desde cero** en cada lanzamiento (el warning `LiteRT warm-up request timed out` del log).
2. El modelo estaba compitiendo por la memoria unificada con ornith todavía residente en Ollama (22GB + 15GB en un Mac de 32GB → swap).

**Corrección aplicada en el benchmark formal:** Ollama se detuvo antes de correr (verificado con `killall ollama`, 93% memoria libre) y se envió 1 request de warm-up descartado antes de medir. Con esas condiciones el benchmark LiteRT corrió estable (server listo en segundos, 8/8 tasks). **Lección operativa:** el primer arranque de LiteRT paga una compilación de Metal de minutos; las corridas siguientes con `cache_dir` configurado no deberían repetirla (no medido aún).

---

## 5. Calidad: por qué las notas no siguen a la velocidad

Correlación observada: **prácticamente nula**. El más rápido entre MoE (qwen3-coder, 4.25) fue el peor calificado; el más lento (qwen3.8, 5.0) el mejor entre las completadas; ornith y gemma empataron (4.63) con perfiles complementarios:

- **ornith**: profundidad analítica (mejor plan agentic, task 7) pero con un **bug ejecutable grave** en code gen (llamó `move_to_end()`/`popitem(last=False)` sobre un `dict` plano — AttributeError en ejecución) pese a incluir ~20 tests. Los tests nunca se ejecutaron; el modelo escribió tests para código roto.
- **gemma**: código correcto (usó `OrderedDict` real) pero plan agentic menos seguro (dejó la contraseña de postgres en el script, sin advice de IAM).
- Los dos errores "técnicos" graves de la serie (bug de ornith, timeouts de qwen3.8) muestran patrón: **la generación larga no garantiza corrección ejecutable** — conviene validar código con ejecución real, no solo lectura.

**Sesgo de la evaluación:** escala 1-5 asignada por un único revisor (asistente), sin testers ciegos ni rúbrica inter-calibrada. Las notas son útiles para comparar dentro de esta serie pero no son un benchmark de calidad estándar (como AlpacaEval/LMSYS). Además la dificultad de prompts es fija y baja para modelos de esta capacidad — un techo de efecto podría ocultar diferencias (varios modelos casi empatan en 4-5).

---

## 6. Veredicto práctico para este workspace

1. **Uso general local:** gemma4-26b vía LiteRT — mejor relación calidad/velocidad/tamaño medido, y 100% offline.
2. **Uso con variedad de modelos:** Ollama sigue siendo más práctico (ecosistema de tags, cuantizaciones, actualizaciones) — ornith-1.5:35b es el mejor de los Ollama probados en balance.
3. **Agentes autónomos:** Antigravity SDK funciona bien con ambos engines (`LocalOpenAIAgentConfig` → Ollama; `LiteRTAgentConfig` → LiteRT); tool-calling verificado con ornith y gemma (2/2 herramientas invocadas correctamente en cada PoC). Velocidad de respuesta del agente: Ollama 26s vs LiteRT ~71s en la primera pasada (incluye carga) — en uso real con server persistente la diferencia se reduce.
4. **No comparar** las tablas de tokens/s entre engines sin leer §3.

## 7. Experimentos — ejecutados el 2026-10-14 (preguntas cerradas)

Los experimentos propuestos se corrieron con `benchmark-litert-stream.py` (streaming/TTFT simétrico) usando el **mismo modelo en ambos engines** (Gemma 4 26B A4B: `.litertlm` para LiteRT, tag `gemma4:26b-a4b-it-q4_K_M` para Ollama), n=3 corridas con mediana. Detalle completo en `benchmark-results/2026-10-14_experiments.md`.

| Pregunta original | Resultado |
|---|---|
| ¿El engine importa con el mismo modelo? | **Sí.** LiteRT 35.43 tok/s vs Ollama 21.61 tok/s (generación, mediana n=3) — **+64% LiteRT**. La ventaja de §2.4 era real, no artefacto del modelo. |
| Memoria real (RSS vs `ollama ps`) | **Confirmado.** LiteRT 2.3GB (`vmmap` physical footprint, pesos lazy-mmap) vs Ollama 17GB residente. El RSS de 1.9GB subrepresentaba, pero la ventaja de memoria es real (7×). |
| Arranque en frío / `cache: disk` | **Corregido.** `cache: disk` no produce artefactos en GPU/Metal (solo CPU). El server liga en <1s y la carga es *lazy*: el costo (20-48s al primer token) es carga de pesos desde disco, no compilación. La corrida de 788s del PoC fue **contención de RAM** (dos modelos residentes), no recompilación Metal. |
| Robustez (n≥3, mediana) | **Sí.** LiteRT 34.6-36.5 tok/s, Ollama 20.6-24.4 tok/s — sin solaparse. |
| Speculative decoding | **Infeasible** con este checkpoint (`ModelInfo.has_speculative_decoding_support() == False`, sin draft model). Requiere variante MTP aparte. |
| Métrica simétrica (TTFT) | **Resuelta.** Ollama gana TTFT (0.6s vs 1.5s) pero pierde generación por mucho. |

**Lección operativa final:** un engine residente a la vez en RAM; la ventaja de LiteRT (velocidad y memoria) lo convierte en el mejor setup medido sobre este hardware.

---

## Referencia de fuentes de datos

| Dato | Archivo |
|------|---------|
| Benchmark Qwen (metodología) | `benchmark-plan.md` |
| Resultados Qwen 2026-09-03 | `benchmark-results/2026-09-03_benchmark.md` |
| Resultados ornith 2026-10-12 + comparación | `benchmark-results/2026-10-12_benchmark.md` |
| Resultados gemma LiteRT 2026-10-14 + comparación | `benchmark-results/2026-10-14_benchmark_litert.md` |
| Respuestas crudas por modelo | `benchmark-results/{modelo}/task-XX.txt` |
| Script benchmark Ollama | `benchmark.sh` |
| Script benchmark LiteRT | `benchmark-litert.sh` |
| PoC agente (Ollama) | `poc-antigravity/poc_agent.py` |
| PoC agente (LiteRT) | `poc-antigravity/poc_litert_agent.py` |
| Experimentos (E1-E6, preguntas cerradas) | `benchmark-results/2026-10-14_experiments.md` |
| Investigación Strata (viabilidad, decisión: no instalar) | `~/.commandcode/plans/strata-viability.md` |
| Investigación Splash (viabilidad, decisión: no instalar) | `~/.commandcode/plans/splash-viability.md` |

## 8. Strata — investigación de viabilidad (2026-10-14, decisión: no instalar)

Se evaluó [Niko1221/Strata](https://github.com/Niko1221/Strata) (engine Metal propio para Qwen3.8-Flash-Next, 125B MoE, streaming de expertos desde SSD). **Corre en el M1 Pro** (macOS 26.6.2 cumple, modelo Q2_0 streamed, ~13-14 tok/s medidos en un M4 de 32GB), pero se decidió **no instalarlo**: ~2.5× más lento que LiteRT (35 tok/s), ~120GB de disco, el variant "Coder" no existe en Mac, y va comprimido a 2-bit. El detalle completo con la tabla de comparación está en el plan de viabilidad (archivo de la última fila). Reevaluar si sale soporte Coder en Mac o con un equipo de ≥64GB.

## 9. Splash — investigación de viabilidad (2026-10-14, decisión: no viable por hardware)

Se evaluó [incoai/splash](https://github.com/incoai/splash) (engine Metal nativo Apple Silicon con speculative decoding DFlash2; soporta Qwen3.6-35B-A3B y Qwen3.8-27B, los mismos que ya corrimos con Ollama). **No viable en el M1 Pro:** requiere **Apple M3 o superior**. Los kernels usan el *Apple9 register tile* (`MTLGPUFamily.apple9` = A17/M3/M4) y un compiler Metal 4 con `uint4b_format`; el M1 Pro es GPU family Apple7. Es un blocker de arquitectura, sin workaround (no se arregla compilando desde fuente). A diferencia de Strata (que corría lento), Splash no puede ejecutarse en este chip. Reevaluar solo con un Mac M3+. Detalle en el plan de viabilidad (última fila de la tabla).
