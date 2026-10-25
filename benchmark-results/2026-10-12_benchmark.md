# Benchmark Report — 2026-10-12

Benchmark de `ornith-1.5:35b` (MoE 35B, ~3B active, Q4_K_M, + vision projector CLIP ~900MB).
Comparado contra los resultados del benchmark del 2026-09-03 (qwen3.8:27b, qwen3.6:35b, qwen3-coder:30b).

## Resumen de Velocidad

| Modelo | Task | Duración | Tokens Out | Tokens/s | Input Tokens | GPU Mem |
|--------|------|----------|------------|----------|--------------|---------|
| ornith-1.5:35b | Task 1 | 141.49s | 3457 | 26.38 | 37 | 21 GB |
| ornith-1.5:35b | Task 2 | 38.59s | 1020 | 27.01 | 82 | 21 GB |
| ornith-1.5:35b | Task 3 | 28.41s | 751 | 27.08 | 78 | 21 GB |
| ornith-1.5:35b | Task 4 | 51.24s | 1409 | 27.76 | 38 | 21 GB |
| ornith-1.5:35b | Task 5 | 11.17s | 309 | 28.82 | 36 | 21 GB |
| ornith-1.5:35b | Task 6 | 7.20s | 192 | 28.87 | 43 | 21 GB |
| ornith-1.5:35b | Task 7 | 91.10s | 2620 | 28.97 | 84 | 21 GB |
| ornith-1.5:35b | Task 8 | 69.20s | 2072 | 30.27 | 121 | 21 GB |
| qwen3.8:27b | Task 1 | 487.950876000s | 3373 | 6.92 | 37 | 18 |
| qwen3.8:27b | Task 2 | 226.014260000s | 1313 | 5.89 | 82 | 18 |
| qwen3.8:27b | Task 3 | 600.186956000s |  | N/A |  | 18 |
| qwen3.8:27b | Task 4 | 345.340683000s | 1506 | 4.39 | 38 | 18 |
| qwen3.8:27b | Task 5 | 44.237170000s | 201 | 4.72 | 36 | 18 |
| qwen3.8:27b | Task 6 | 43.507368000s | 208 | 5.09 | 43 | 18 |
| qwen3.8:27b | Task 7 | 600.105264000s |  | N/A |  | 18 |
| qwen3.8:27b | Task 8 | 332.086531000s | 1979 | 6.04 | 121 | 18 |
| qwen3.6:35b | Task 1 | 96.224215000s | 2114 | 26.05 | 37 | 22 GB |
| qwen3.6:35b | Task 2 | 43.118946000s | 1027 | 24.24 | 82 | 22 GB |
| qwen3.6:35b | Task 3 | 411.875248000s | 8284 | 20.14 | 78 | 22 GB |
| qwen3.6:35b | Task 4 | 78.002220000s | 1636 | 21.13 | 38 | 22 GB |
| qwen3.6:35b | Task 5 | 11.103015000s | 234 | 22.71 | 36 | 22 GB |
| qwen3.6:35b | Task 6 | 6.764726000s | 149 | 24.18 | 43 | 22 GB |
| qwen3.6:35b | Task 7 | 59.854741000s | 1339 | 22.64 | 84 | 22 GB |
| qwen3.6:35b | Task 8 | 72.595197000s | 1690 | 23.57 | 121 | 22 GB |
| qwen3-coder:30b | Task 1 | 35.118815000s | 893 | 32.71 | 35 | 20 GB |
| qwen3-coder:30b | Task 2 | 21.061343000s | 675 | 33.12 | 75 | 20 GB |
| qwen3-coder:30b | Task 3 | 49.936419000s | 1620 | 32.76 | 76 | 20 GB |
| qwen3-coder:30b | Task 4 | 21.907986000s | 719 | 33.44 | 38 | 20 GB |
| qwen3-coder:30b | Task 5 | 4.703670000s | 167 | 38.56 | 38 | 20 GB |
| qwen3-coder:30b | Task 6 | 4.721404000s | 167 | 38.21 | 39 | 20 GB |
| qwen3-coder:30b | Task 7 | 46.118496000s | 1511 | 33.17 | 84 | 20 GB |
| qwen3-coder:30b | Task 8 | 50.254562000s | 1666 | 33.52 | 109 | 20 GB |

### Resumen Comparativo

| Modelo | Tipo | GPU Mem | Tokens/s Promedio | Tiempo Total | Timeouts |
|--------|------|---------|-------------------|--------------|----------|
| qwen3-coder-30b | MoE 30B (3B active) | 20 GB | 34.43 | 3m 53s | 0 |
| **ornith-1.5:35b** | **MoE 35B (3B active) + vision** | **21 GB** | **28.14** | **7m 18s** | **0** |
| qwen3.6-35b | MoE 35B (3B active) | 22 GB | 23.08 | 12m 59s | 0 |
| qwen3.8-27b | Dense 27B | 18 GB | 5.50 | 44m 39s | 2 |

## Evaluación de Calidad (1-5)

| Modelo | Code Gen (1) | Debug (2) | Logic (3) | General (4) | ES (5) | EN (6) | Agent (7) | Refactor (8) | **Promedio** |
|--------|-------------|-----------|-----------|-------------|--------|--------|-----------|--------------|-------------|
| qwen3.8-27b | 5 | 5 | N/A (timeout) | 5 | 5 | 5 | N/A (timeout) | 5 | **5.0** (6 tasks) |
| qwen3.6-35b | 5 | 5 | 4 | 5 | 5 | 4 | 5 | 5 | **4.75** |
| **ornith-1.5-35b** | **3** | **5** | **4** | **5** | **5** | **5** | **5** | **5** | **4.63** |
| qwen3-coder-30b | 4 | 5 | 3 | 4 | 4 | 4 | 5 | 5 | **4.25** |

*Las puntuaciones de los modelos Qwen provienen de la revisión manual del reporte 2026-09-03_benchmark.md (mismas respuestas).*

### Justificación por Tarea — ornith-1.5:35b

#### Task 1 — Code Gen (LRU Cache con TTL + tests) — **3/5**
- Aparentemente excelente: ~20 tests, thread-safety con RLock, TTL por entrada, stats, type hints, validación.
- **Pero tiene bugs reales**: usa un `dict` plano (`{}`) y luego llama `self._data.move_to_end(key)` y `self._data.popitem(last=False)`, métodos que solo existen en `OrderedDict`. El código no ejecuta tal como está escrito. Irónico: sus propios tests lo habrían atrapado.
- Además comenta "OrderedDict + move_to_end" en las notas de diseño sin usarlo, y tiene erratas ("Cuebas" en lugar de "Tests").
- Demuestra que un buen framework de testing no salva una implementación incorrecta.

#### Task 2 — Debug (Fibonacci) — **5/5**
- Explicación clara con árbol de llamadas visual y conteo de llamadas para n=35/40.
- 2 soluciones correctas (lru_cache e iterativa) con complejidades bien indicadas.
- Tabla comparativa final concisa. Error menor en el snippet de benchmark (`fibonacci_iter = fibonacci_iter` es nonsensical) pero no afecta el diagnóstico.

#### Task 3 — Logic Puzzle (Tres personas) — **4/5**
- Conclusión correcta: el acertijo es paradójico bajo la condición "solo uno dice la verdad" — misma conclusión que qwen3.6:35b llegó de forma exhaustiva.
- Destaca por la brevedad: 751 tokens vs 8284 de qwen3.6 para la misma rigurosidad. Detecta que A nunca puede mentir y encuentra la contradicción C→verdad.
- Pierde un punto por no explorar variantes de interpretación más allá de una nota final.

#### Task 4 — Conocimiento General (TCP vs UDP) — **5/5**
- Muy completo: tabla comparativa, handshake, ejemplos concretos en producción (VoIP, gaming, DNS, DHCP, SNMP), caso práctico de streaming y resumen visual.
- Comparable en calidad a qwen3.6:35b, más organizado.

#### Task 5 — Resumen (Microservicios en español) — **5/5**
- Respeta el formato pedido, preciso y conciso (309 tokens). Cubre conceptos, ventajas y desventajas sin relleno.

#### Task 6 — Writing (Email en inglés) — **5/5**
- Profesional, tono cálido y firme, under 150 words, placeholders bien usados. Mejor que qwen3.6 (4) e igual que qwen3.8 (5).

#### Task 7 — Agentic (Plan de ejecución servidor) — **5/5**
- El más destacado: corrige el presupuesto del prompt (imposible actualizar kernel sin downtime en un solo servidor), da alternativa con balanceador, comandos correctos (certbot DNS-01 para wildcard, pg_dump -F c con S3, .pgpass en vez de PGPASSWORD), orden de prioridades razonado y preguntas de seguimiento para afinar.
- Profesional y seguro (chmod 600, IAM acotado).

#### Task 8 — Refactoring (Código Python SOLID) — **5/5**
- OOP completo con SRP claro (DataLoader/DataProcessor/DataSaver/Pipeline), DI, excepciones custom con `raise from`, logging, type hints, json.dump con ensure_ascii=False.
- Erratas menores ("Dependencias abstrusas", "la cliente HTTP") sin impacto funcional.

## Conclusión

### Ranking por Calidad (actualizado)
1. **qwen3.8:27b** — 5.0 de promedio, pero 2 timeouts y ~7 tok/s: inviable en la práctica.
2. **qwen3.6:35b** — 4.75, buen balance, pero verbose (8284 tokens en una task) y el más lento de los MoE.
3. **ornith-1.5:35b** — 4.63, calidad casi idéntica a qwen3.6 con respuestas notablemente más concisas (3457+751 vs 2114+8284 tokens en tasks equivalentes), sin timeouts. Su único fallo serio es el bug de OrderedDict en code gen.
4. **qwen3-coder:30b** — 4.25, el más rápido pero el menos profundo.

### Ranking por Velocidad
1. qwen3-coder:30b (34.4 tok/s) → 2. **ornith-1.5:35b (28.1 tok/s)** → 3. qwen3.6:35b (23.1 tok/s) → 4. qwen3.8:27b (5.5 tok/s)

### Recomendación
- **Mejor balance general (nuevo)**: **ornith-1.5:35b** — 22% más rápido que qwen3.6:35b, calidad prácticamente igual, respuestas más directas, y además soporta visión (input de imágenes) que ningún Qwen de esta lista ofrece localmente.
- **Coding rápido / iteración**: qwen3-coder:30b sigue siendo el más veloz.
- **Profundidad máxima en código**: qwen3.8:27b, solo si el tiempo no importa (con timeouts).

### Limitaciones Detectadas
- ornith-1.5:35b: bug en code gen (dict plano vs OrderedDict) — revisar siempre el código ejecutable que genera; erratas ocasionales en español.
- qwen3.8:27b: demasiado lento (2 timeouts).
- qwen3.6:35b: respuestas excesivamente largas.
- qwen3-coder:30b: menor profundidad en razonamiento lógico.

### Archivos Generados

- `benchmark-results/2026-10-12_benchmark.md` — Este reporte
- `benchmark-results/ornith-1.5-35b/` — 8 tasks (respuesta + métricas)
- `benchmark-results/qwen3.8-27b/`, `qwen3.6-35b/`, `qwen3-coder-30b/` — Resultados del 2026-09-03

### Nota Metodológica

Las respuestas de los modelos Qwen fueron generadas el 2026-09-03 con las mismas condiciones (mismos 8 prompts, mismo `start-ollama.sh` con context 32k, KV cache q8, flash attention). ornith-1.5:35b es un modelo con visión; el projector CLIP (~900MB) no se usa en estos prompts de solo texto.
