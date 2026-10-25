# Benchmark: Comparación de Modelos Qwen en M1 Pro 32GB

## Objetivo
Evaluar y comparar `qwen3.8:27b`, `qwen3.6:35b` y `qwen3-coder:30b` en velocidad y calidad de respuesta.

## Metricas a medir

| Métrica | Cómo se mide |
|---|---|
| Tokens/segundo | `ollama run --verbose` (linea final del output) |
| Time-to-first-token | Cronometro manual o parsing del output verbose |
| Uso de memoria GPU | `ollama ps` después de cada test |
| Calidad subjetiva | Escala 1-5 por categoría (configurada en el script) |

## Estructura del benchmark

Crear un script `benchmark.sh` en `/Users/jonathanquishpe/Desktop/Temporal/Qwen_LLM_Local_Setup/` que:

1. **Selecciona modelo** — por parámetro o menú interactivo
2. **Ejecuta 8 prompts** representativos (ver abajo)
3. **Captura métricas** de cada ejecución
4. **Genera reporte** en `benchmark-results/` con timestamp

## Prompts del benchmark (8 tareas)

### 1. Código — Generación
```
Escribe una función en Python que implemente un cache LRU con TTL (time-to-live). Incluye tests unitarios.
```

### 2. Código — Debugging
```
Encuentra y explica el bug en este código:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
# El problema: esta función es extremadamente lenta para n > 35.
# Proponé una solución optimizada.
```

### 3. Razonamiento — Lógica
```
Tres personas (A, B, C) están en una habitación. A dice "Al menos uno de nosotros miente". B dice "A miente". C dice "B miente". Asumiendo que solo uno dice la verdad, ¿quién dice la verdad? Explica tu razonamiento paso a paso.
```

### 4. Conocimiento general
```
Explica la diferencia entre TCP y UDP. ¿Cuándo usarías cada uno? Da ejemplos concretos de uso en producción.
```

### 5. Español — Resumen
```
Resume en 3 bullet points los conceptos clave de la arquitectura de microservicios, sus ventajas y desventajas principales.
```

### 6. Inglés — Writing
```
Write a professional email declining a job offer politely, explaining that you've decided to stay at your current company. Keep it under 150 words.
```

### 7. Agentic — Tool planning
```
Tengo un servidor Ubuntu 22.04 con Docker, Nginx y PostgreSQL. Necesito:
1. Actualizar el kernel sin downtime
2. Configurar SSL wildcard para *.miapp.com
3. Hacer backup automático de PostgreSQL a S3
Dame el plan de ejecución paso a paso, con comandos exactos.
```

### 8. Código — Refactoring
```
Refactorizá este código Python para que sea más mantenible, siga principios SOLID, y agregue manejo de errores:
import requests
def get_data(url):
    r = requests.get(url)
    return r.json()
def process(data):
    result = []
    for item in data:
        result.append(item['name'].upper())
    return result
def save(data):
    f = open('output.json', 'w')
    f.write(str(data))
    f.close()
```

## Output del benchmark

### Archivos generados
```
benchmark-results/
├── 2026-09-02_benchmark.md       # Reporte consolidado
├── qwen3.8-27b/
│   ├── task-01-code-gen.txt
│   ├── task-02-debug.txt
│   └── ...
├── qwen3.6-35b/
│   └── ...
└── qwen3-coder-30b/
    └── ...
```

### Formato del reporte
```markdown
# Benchmark Report — 2026-09-02

## Resumen de Velocidad
| Modelo | Task | Tokens/s | TTFT (s) | Mem GPU |
|--------|------|----------|----------|---------|
| qwen3.8:27b | Code Gen | 18.2 | 1.3 | 17.1 GB |
| ... | ... | ... | ... | ... |

## Evaluación de Calidad (1-5)
| Modelo | Code Gen | Debug | Logic | General | ES | EN | Agent | Refactor |
|--------|----------|-------|-------|---------|----|----|-------|----------|
| qwen3.8:27b | ? | ? | ? | ? | ? | ? | ? | ? |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Conclusión
[Resumen ejecutivo con recomendación]
```

## Archivos a crear

1. **`/Users/jonathanquishpe/Desktop/Temporal/Qwen_LLM_Local_Setup/benchmark.sh`** — Script principal que ejecuta el benchmark completo
2. **`/Users/jonathanquishpe/Desktop/Temporal/Qwen_LLM_Local_Setup/benchmark-prompts.txt`** — Los 8 prompts en un archivo separado para fácil edición
3. **`/Users/jonathanquishpe/Desktop/Temporal/Qwen_LLM_Local_Setup/benchmark-results/`** — Directorio de resultados

## Flujo de ejecución

```bash
cd <repo-root>
./benchmark.sh                    # Menú interactivo: elegir modelo o "all"
./benchmark.sh qwen3.8:27b        # Benchmark directo de un modelo
./benchmark.sh all                # Los 3 modelos secuencialmente
```

## Verificación

1. Ejecutar `./benchmark.sh qwen3.8:27b` primero como prueba
2. Verificar que genera archivos en `benchmark-results/`
3. Verificar que el reporte tiene métricas de velocidad
4. Revisar calidad manualmente (escala 1-5)
5. Ejecutar `./benchmark.sh all` para comparación completa
