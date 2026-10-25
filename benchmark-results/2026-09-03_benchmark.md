# Benchmark Report — 2026-09-03

## Resumen de Velocidad

| Modelo | Task | Duración | Tokens Out | Tokens/s | Input Tokens | GPU Mem |
|--------|------|----------|------------|----------|--------------|---------|
| qwen3-coder-30b | 01 | 35.118815000s | 893 | 32.71 | 35 | 20 GB |
| qwen3-coder-30b | 02 | 21.061343000s | 675 | 33.12 | 75 | 20 GB |
| qwen3-coder-30b | 03 | 49.936419000s | 1620 | 32.76 | 76 | 20 GB |
| qwen3-coder-30b | 04 | 21.907986000s | 719 | 33.44 | 38 | 20 GB |
| qwen3-coder-30b | 05 | 4.703670000s | 167 | 38.56 | 38 | 20 GB |
| qwen3-coder-30b | 06 | 4.721404000s | 167 | 38.21 | 39 | 20 GB |
| qwen3-coder-30b | 07 | 46.118496000s | 1511 | 33.17 | 84 | 20 GB |
| qwen3-coder-30b | 08 | 50.254562000s | 1666 | 33.52 | 109 | 20 GB |
| qwen3.6-35b | 01 | 96.224215000s | 2114 | 26.05 | 37 | 22 GB |
| qwen3.6-35b | 02 | 43.118946000s | 1027 | 24.24 | 82 | 22 GB |
| qwen3.6-35b | 03 | 411.875248000s | 8284 | 20.14 | 78 | 22 GB |
| qwen3.6-35b | 04 | 78.002220000s | 1636 | 21.13 | 38 | 22 GB |
| qwen3.6-35b | 05 | 11.103015000s | 234 | 22.71 | 36 | 22 GB |
| qwen3.6-35b | 06 | 6.764726000s | 149 | 24.18 | 43 | 22 GB |
| qwen3.6-35b | 07 | 59.854741000s | 1339 | 22.64 | 84 | 22 GB |
| qwen3.6-35b | 08 | 72.595197000s | 1690 | 23.57 | 121 | 22 GB |
| qwen3.8-27b | 01 | 487.950876000s | 3373 | 6.92 | 37 | 18 GB |
| qwen3.8-27b | 02 | 226.014260000s | 1313 | 5.89 | 82 | 18 GB |
| qwen3.8-27b | 03 | 600.186956000s |  | N/A |  | 18 GB |
| qwen3.8-27b | 04 | 345.340683000s | 1506 | 4.39 | 38 | 18 GB |
| qwen3.8-27b | 05 | 44.237170000s | 201 | 4.72 | 36 | 18 GB |
| qwen3.8-27b | 06 | 43.507368000s | 208 | 5.09 | 43 | 18 GB |
| qwen3.8-27b | 07 | 600.105264000s |  | N/A |  | 18 GB |
| qwen3.8-27b | 08 | 332.086531000s | 1979 | 6.04 | 121 | 18 GB |

## Resumen Comparativo

| Modelo | Tipo | GPU Mem | Tokens/s Promedio | Tiempo Total |
|--------|------|---------|-------------------|--------------|
| qwen3-coder-30b | MoE 30B (3B active) | 20 GB | 34.43 | 3m 53s |
| qwen3.6-35b | MoE 35B (3B active) | 22 GB | 23.08 | 12m 59s |
| qwen3.8-27b | Dense 27B | 18 GB | 5.50 | 44m 39s |

## Evaluación de Calidad (1-5)

| Modelo | Code Gen (1) | Debug (2) | Logic (3) | General (4) | ES (5) | EN (6) | Agent (7) | Refactor (8) | **Promedio** |
|--------|-------------|-----------|-----------|-------------|--------|--------|-----------|--------------|-------------|
| qwen3.8-27b | 5 | 5 | N/A (timeout) | 5 | 5 | 5 | N/A (timeout) | 5 | **5.0** (6 tasks) |
| qwen3.6-35b | 5 | 5 | 4 | 5 | 5 | 4 | 5 | 5 | **4.75** |
| qwen3-coder-30b | 4 | 5 | 3 | 4 | 4 | 4 | 5 | 5 | **4.25** |

### Justificación por Tarea

#### Task 1 — Code Gen (LRU Cache con TTL + tests)
- **qwen3.8:27b (5)**: Implementación completa con 18 tests, soporte para TTL por ítem, docstrings completas, validación de inputs, personalización máxima.
- **qwen3.6:35b (5)**: Implementación muy sólida con dict separado para expiración, 14 tests, métodos extra (keys, contains, invalidate, clear). Muy profesional.
- **qwen3-coder:30b (4)**: Correcta pero más simple. Solo 5 tests, sin validación de inputs, menos métodos auxiliares. Funcional pero menos completa.

#### Task 2 — Debug (Fibonacci)
- **qwen3.8:27b (5)**: Excelente análisis con árbol de llamadas, 3 soluciones (iterativa, memoización, matricial), tabla comparativa completa de complejidades.
- **qwen3.6:35b (5)**: Análisis muy claro, 3 soluciones (memoización, iterativa, lru_cache), recomendaciones prácticas, tabla de rendimiento.
- **qwen3-coder:30b (5)**: Árbol visual claro, 2 soluciones optimizadas, tabla comparativa. Directo y efectivo.

#### Task 3 — Logic Puzzle (Tres personas)
- **qwen3.8:27b (N/A)**: Timeout — no generó respuesta.
- **qwen3.6:35b (4)**: Análisis extremadamente exhaustivo con notación matemática formal. Analiza correctamente todas las combinaciones y llega a la conclusión de que el acertijo es paradójico bajo lógica estricta. Demasiado largo (8284 tokens) pero riguroso.
- **qwen3-coder:30b (3)**: Análisis inconsistente — dice que "C es la respuesta" pero luego reconoce contradicciones. Finalmente dice "nadie puede decir la verdad" y luego retrocede. Confuso y menos riguroso.

#### Task 4 — Conocimiento General (TCP vs UDP)
- **qwen3.8:27b (5)**: Tabla comparativa clara, ejemplos muy concretos en producción, incluye mención de QUIC/HTTP3 como tendencia moderna.
- **qwen3.6:35b (5)**: El más completo — analogía final excelente (teléfono vs correos aéreos), ejemplos detallados (WebRTC, SNMP, DHCP), protocolos modernos.
- **qwen3-coder:30b (4)**: Correcto y bien organizado pero más genérico. Menos profundidad en los ejemplos de producción.

#### Task 5 — Resumen (Microservicios en español)
- **qwen3.8:27b (5)**: Conciso y preciso, bien estructurado en 3 puntos claros.
- **qwen3.6:35b (5)**: Muy completo, menciona Kubernetes y transacciones distribuidas.
- **qwen3-coder:30b (4)**: Correcto pero menos detallado.

#### Task 6 — Writing (Email en inglés)
- **qwen3.8:27b (5)**: El más profesional, tono cálido pero firme, bien estructurado.
- **qwen3.6:35b (4)**: Correcto pero un poco más corto y genérico.
- **qwen3-coder:30b (4)**: Profesional pero incluye "collaborate in the future" que puede sonar ambiguo.

#### Task 7 — Agentic (Plan de ejecución servidor)
- **qwen3.8:27b (N/A)**: Timeout — no generó respuesta.
- **qwen3.6:35b (5)**: Plan completo con livepatching, Cloudflare DNS, cron, docker-compose alternativo. Muy profesional.
- **qwen3-coder:30b (5)**: Plan sólido con certbot manual DNS, alternativa docker-compose, explicaciones claras.

#### Task 8 — Refactoring (Código Python SOLID)
- **qwen3.8:27b (5)**: Excelente — excepciones personalizadas jerárquicas, funciones puras, logging completo, type hints, timeout configurable.
- **qwen3.6:35b (5)**: OOP completo con ABC/interfaz, inyección de dependencias, logging, validación robusta.
- **qwen3-coder:30b (5)**: OOP completo con DataPipeline, DataProvider (ABC), logging, validación, manejo de encoding UTF-8.

## Conclusión

### Ranking por Calidad
1. **qwen3.8:27b** — La mejor calidad (promedio 5.0), pero tuvo 2 timeouts. Respuestas más detalladas y completas.
2. **qwen3.6:35b** — Excelente balance calidad-velocidad (promedio 4.75). Solo任务3 (logic puzzle) fue más confuso. Completó los 8 tasks.
3. **qwen3-coder:30b** — Rápido y competente (promedio 4.25), pero menos profundo en análisis complejos. Bueno para coding, menos para razonamiento.

### Recomendación
- **Uso diario/coding**: qwen3-coder:30b (más rápido, buen código)
- **Tareas que requieren razonamiento profundo**: qwen3.8:27b (mejor calidad, pero lento)
- **Mejor balance general**: qwen3.6:35b (buena calidad a buena velocidad)

### Limitaciones Detectadas
- qwen3.8:27b es demasiado lento para prompts complejos (timeout en 2 de 8 tasks)
- qwen3.6:35b puede generar respuestas excesivamente largas (8284 tokens en task 3)
- qwen3-coder:30b tiene menor profundidad en tareas de razonamiento lógico

### Archivos Generados

Cada modelo tiene 8 archivos `task-XX.txt` con la respuesta y métricas:
- `benchmark-results/qwen3.8-27b/` — 8 tasks
- `benchmark-results/qwen3.6-35b/` — 8 tasks
- `benchmark-results/qwen3-coder-30b/` — 8 tasks

### Para Revisar Calidad

Revisa cada archivo `task-XX.txt` y asigna puntuación 1-5 en la tabla.
