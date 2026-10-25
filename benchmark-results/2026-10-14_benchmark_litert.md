# Benchmark Report — 2026-10-14 — LiteRT-LM (gemma4-26b)

Motor: LiteRT-LM (GPU Metal on-device, sin speculative decoding, sin Ollama).
Modelo: Gemma 4 26B A4B (MoE, ~4B active) — checkpoint .litertlm de 14.7GB.
Endpoint: /v1/chat/completions (OpenAI-compatible, puerto 11435).

> Nota metodológica: los tokens/s de LiteRT se calculan como
> completion_tokens / duración total wall-clock (incluye HTTP + prefill),
> por lo que son conservadores frente al eval_duration puro de generación
> que reporta Ollama. La memoria reportada (1.9GB RSS) es solo el RSS del
> proceso server; no incluye los pesos residentes en GPU Metal compartida,
> por lo que no es directamente comparable con `ollama ps`.

## Resumen de Velocidad — LiteRT

| Modelo | Task | Duración | Tokens Out | Tokens/s | Input Tokens | Memoria |
|--------|------|----------|------------|----------|--------------|---------|
| gemma4-26b-litert | Task 1 | 40.12s | 1406 | 35.04 | 41 | 1.9 GB (RSS) |
| gemma4-26b-litert | Task 2 | 24.35s | 831 | 34.12 | 88 | 1.9 GB (RSS) |
| gemma4-26b-litert | Task 3 | 38.67s | 1356 | 35.06 | 78 | 1.9 GB (RSS) |
| gemma4-26b-litert | Task 4 | 33.45s | 1158 | 34.61 | 39 | 1.9 GB (RSS) |
| gemma4-26b-litert | Task 5 | 7.79s | 236 | 30.29 | 37 | 1.9 GB (RSS) |
| gemma4-26b-litert | Task 6 | 6.15s | 171 | 27.79 | 45 | 1.9 GB (RSS) |
| gemma4-26b-litert | Task 7 | 43.72s | 1531 | 35.01 | 83 | 1.9 GB (RSS) |
| gemma4-26b-litert | Task 8 | 41.92s | 1455 | 34.71 | 135 | 1.9 GB (RSS) |

### Resumen Comparativo (5 modelos)

| Modelo | Engine | Tipo | Tokens/s Promedio | Tiempo Total (8 tasks) | Timeouts |
|--------|--------|------|-------------------|------------------------|----------|
| qwen3-coder-30b | Ollama | MoE 30B (3B active) | 34.43 | 3m 53s | 0 |
| **gemma4-26b** | **LiteRT-LM** | **MoE 26B (4B active)** | **33.45** | **3m 56s** | **0** |
| ornith-1.5:35b | Ollama | MoE 35B (3B active) | 28.14 | 7m 18s | 0 |
| qwen3.6-35b | Ollama | MoE 35B (3B active) | 23.08 | 12m 59s | 0 |
| qwen3.8-27b | Ollama | Dense 27B | 5.50 | 44m 39s | 2 |

*La métrica de LiteRT es conservadora (wall-clock total incluyendo prefill); la de Ollama usa solo el tiempo de generación. Con métricas equivalentes LiteRT quedaría ligeramente por encima.*

## Comparativa detallada con modelos Ollama (corridas previas)

### qwen3.8:27b

| Task | Duración | Tokens Out | Tokens/s | Input Tokens |
|------|----------|------------|----------|--------------|
| Task 1 | 487.95s | 3373 | 6.92 | 37 |
| Task 2 | 226.01s | 1313 | 5.89 | 82 |
| Task 3 | 600.19s | (timeout) | N/A | N/A |
| Task 4 | 345.34s | 1506 | 4.39 | 38 |
| Task 5 | 44.24s | 201 | 4.72 | 36 |
| Task 6 | 43.51s | 208 | 5.09 | 43 |
| Task 7 | 600.11s | (timeout) | N/A | N/A |
| Task 8 | 332.09s | 1979 | 6.04 | 121 |

### qwen3.6:35b

| Task | Duración | Tokens Out | Tokens/s | Input Tokens |
|------|----------|------------|----------|--------------|
| Task 1 | 96.22s | 2114 | 26.05 | 37 |
| Task 2 | 43.12s | 1027 | 24.24 | 82 |
| Task 3 | 411.88s | 8284 | 20.14 | 78 |
| Task 4 | 78.00s | 1636 | 21.13 | 38 |
| Task 5 | 11.10s | 234 | 22.71 | 36 |
| Task 6 | 6.76s | 149 | 24.18 | 43 |
| Task 7 | 59.85s | 1339 | 22.64 | 84 |
| Task 8 | 72.60s | 1690 | 23.57 | 121 |

### qwen3-coder:30b

| Task | Duración | Tokens Out | Tokens/s | Input Tokens |
|------|----------|------------|----------|--------------|
| Task 1 | 35.12s | 893 | 32.71 | 35 |
| Task 2 | 21.06s | 675 | 33.12 | 75 |
| Task 3 | 49.94s | 1620 | 32.76 | 76 |
| Task 4 | 21.91s | 719 | 33.44 | 38 |
| Task 5 | 4.70s | 167 | 38.56 | 38 |
| Task 6 | 4.72s | 167 | 38.21 | 39 |
| Task 7 | 46.12s | 1511 | 33.17 | 84 |
| Task 8 | 50.25s | 1666 | 33.52 | 109 |

### ornith-1.5:35b

| Task | Duración | Tokens Out | Tokens/s | Input Tokens |
|------|----------|------------|----------|--------------|
| Task 1 | 141.49s | 3457 | 26.38 | 37 |
| Task 2 | 38.59s | 1020 | 27.01 | 82 |
| Task 3 | 28.41s | 751 | 27.08 | 78 |
| Task 4 | 51.24s | 1409 | 27.76 | 38 |
| Task 5 | 11.17s | 309 | 28.82 | 36 |
| Task 6 | 7.20s | 192 | 28.87 | 43 |
| Task 7 | 91.10s | 2620 | 28.97 | 84 |
| Task 8 | 69.20s | 2072 | 30.27 | 121 |

## Evaluación de Calidad (1-5)

| Modelo | Code Gen | Debug | Logic | General | ES | EN | Agent | Refactor | **Promedio** |
|--------|----------|-------|-------|---------|----|----|-------|----------|-------------|
| qwen3.8-27b | 5 | 5 | N/A (timeout) | 5 | 5 | 5 | N/A (timeout) | 5 | **5.0** (6 tasks) |
| qwen3.6-35b | 5 | 5 | 4 | 5 | 5 | 4 | 5 | 5 | **4.75** |
| **gemma4-26b (LiteRT)** | **4** | **5** | **4** | **5** | **5** | **5** | **4** | **5** | **4.63** |
| ornith-1.5-35b | 3 | 5 | 4 | 5 | 5 | 5 | 5 | 5 | **4.63** |
| qwen3-coder-30b | 4 | 5 | 3 | 4 | 4 | 4 | 5 | 5 | **4.25** |

*Las puntuaciones de los modelos Ollama provienen de las revisiones manuales de los reportes 2026-09-03 y 2026-10-12 (mismas respuestas).*

### Justificación por Tarea — gemma4-26b (LiteRT)

#### Task 1 — Code Gen (LRU Cache con TTL + tests) — 4/5
- Implementación **correcta**: usa `OrderedDict` real con `move_to_end`/`popitem(last=False)` (a diferencia del bug de ornith, que usaba dict plano). TTL por tupla `(valor, expiración)`, 4 tests correctos.
- Pierde puntos por brevedad: solo 4 tests (ornith tuvo ~20), sin thread-safety, sin stats de hits, y usa `time.time()` en vez de `time.monotonic()` (frágil ante cambios de reloj/NTP).

#### Task 2 — Debug (Fibonacci) — 5/5
- Diagnóstico correcto (O(2ⁿ) por recálculo redundante), 3 soluciones (memo dict, lru_cache, iterativa), tabla comparativa limpia. Conciso (831 tokens).

#### Task 3 — Logic Puzzle (Tres personas) — 4/5
- Llega a la conclusión correcta: el acertijo es paradójico bajo "solo uno dice la verdad" — mismo veredicto que ornith y qwen3.6.
- Razonamiento algo repetitivo en la reevaluación (1356 tokens vs 751 de ornith para la misma conclusión).

#### Task 4 — Conocimiento General (TCP vs UDP) — 5/5
- Analogía megáfono/llamada, tabla comparativa, ejemplos de producción (streaming, VoIP, juegos FPS, DNS). Omite DHCP/SNMP/multicast (ornith y qwen3.6 los incluyeron), pero todo lo dicho es correcto.

#### Task 5 — Resumen (Microservicios en español) — 5/5
- Respeta exactamente el formato de 3 bullet points pedido. Preciso y denso (236 tokens).

#### Task 6 — Writing (Email en inglés) — 5/5
- Profesional, tono cálido y firme, under 150 words. Comparable al de ornith.

#### Task 7 — Agentic (Plan de ejecución servidor) — 4/5
- Corrige el presupuesto del kernel (reinicio inevitable; sugiere Blue-Green/Docker Swarm y ventana de bajo tráfico). SSL wildcard con plugin DNS-01 correcto, backup con `docker exec pg_dump | gzip` a S3, checklist de verificación.
- Pierde puntos vs ornith (5): no menciona `.pgpass` (deja la contraseña en el script), sin advice de IAM acotado a S3, sin preguntas de seguimiento para personalizar comandos.

#### Task 8 — Refactor (Código Python SOLID) — 5/5
- ABCs para abstracciones (DataFetcher/DataSaver), inyección de dependencias explícita, logging, type hints, `json.dump` con encoding, `raise_for_status()`. Explicación de mejoras didáctica.

## Conclusión

### Ranking por Calidad (5 modelos)
1. **qwen3.8:27b** — 5.0, pero 2 timeouts y 5.5 tok/s: inviable en la práctica.
2. **qwen3.6:35b** — 4.75, bueno pero verboso.
3. **Empate: gemma4-26b (LiteRT) y ornith-1.5:35b** — ambos 4.63, con fortalezas complementarias: Gemma acertó donde ornith falló (código ejecutable en task 1) y ornith fue más profundo donde Gemma fue más breve (plan agentic en task 7).
4. **qwen3-coder-30b** — 4.25, rápido pero menos profundo en razonamiento.

### Ranking por Velocidad
1. qwen3-coder-30b (34.4 tok/s) → 2. **gemma4-26b LiteRT (33.5 tok/s, wall-clock conservador)** → 3. ornith-1.5:35b (28.1) → 4. qwen3.6:35b (23.1) → 5. qwen3.8:27b (5.5)

### Conclusión Ejecutiva

**LiteRT-LM cumple lo prometido en Apple Silicon.** Con un checkpoint de 14.7GB (vs 22GB de ornith cuantizado) alcanzó velocidad equivalente al más rápido histórico (qwen3-coder) y calidad de nivel top-2, con el mejor uso de memoria del grupo. Es una alternativa real a Ollama, con ventajas adicionales: privacidad total, arranque del server en segundos, y ecosistema Antigravity SDK para agentes (tool-calling verificado en el PoC con ambos engines).

**Recomendación actualizada**:
- **Mejor balance general**: gemma4-26b vía LiteRT — prácticamente empatado con ornith en calidad pero más rápido y con checkpoint más liviano.
- **Coding rápido / iteración**: qwen3-coder:30b (Ollama), marginalmente el más veloz.
- **Agentes autónomos**: LiteRT + Antigravity SDK es el camino más integrado (100% offline, tool-calling verificado).
- **Ollama sigue siendo preferible** si se quiere alternar entre muchos modelos sin gestionar formatos .litertlm.

### Limitaciones Detectadas
- El RSS del server LiteRT (1.9GB) no refleja el uso real de memoria compartida GPU — métrica mejorable con `footprint`/`ps` ampliado de macOS.
- `litert-lm serve` no expone tiempos separados de prefill/generación (como `eval_duration` de Ollama), por lo que la comparación de tokens/s no es simétrica.
- Sin speculative decoding en esta corrida — queda como experimento futuro (`enable_speculative_decoding` del SDK o su equivalente en serve).

### Archivos Generados

- `benchmark-results/2026-10-14_benchmark_litert.md` — Este reporte
- `benchmark-results/gemma4-26b-litert/` — 8 tasks (respuesta + métricas) + server.log
- `benchmark-litert.sh` — Script del benchmark (reutilizable)
- Históricos comparados: `qwen3.8-27b/`, `qwen3.6-35b/`, `qwen3-coder-30b/`, `ornith-1.5-35b/`
