# Rutas del Paisaje Cultural Cafetero

Proyecto final de Análisis de Algoritmos (Universidad del Quindío, 2026-2): planificación de rutas sobre la red vial del Quindío con Dijkstra, envolvente convexa, Held-Karp y una heurística voraz, midiendo la complejidad teórica contra tiempos reales.

Enunciado y anexo: `Proyecto final 2026-2.pdf` y `Anexo proyecto.pdf` (carpeta de la materia). Lenguaje: **Python**.

## Estructura

```
specs/       Una carpeta por requerimiento (r1..r5): spec.md, plan.md, tasks.md, review.md
docs/        anexo-ia.md (registro del uso de IA para el documento técnico)
.claude/     Agentes de Claude Code (coordinator, planner, implementer, reviewer)
CLAUDE.md    Reglas del proyecto para Claude Code
estudio/     Notas privadas (no se versiona)
```

## Metodología: Spec-Driven Development

Ninguna función de un requerimiento se programa antes de tener su spec aprobada: spec → pruebas → código → verificación → medición. La plantilla de spec está en `specs/README.md`. Si el código y la spec difieren, se corrige uno de los dos de forma explícita y se hace commit del cambio.

## Cómo usar el agente `coordinator`

El `coordinator` lleva un requerimiento de la spec al código revisado. Corre como **agente principal de la sesión**, no como subagente, y delega en `planner`, `implementer` y `reviewer`.

### 1. Arrancarlo

Desde la raíz del repositorio:

```bash
claude --agent coordinator
```

Los agentes de `.claude/agents/` se cargan al iniciar la sesión: si los editas, reinicia Claude Code.

### 2. Pedirle un requerimiento

Dile qué requerimiento o algoritmo quieres, por ejemplo:

```
Trabajemos r2-dijkstra
```

Si ya existe `specs/r2-dijkstra/`, retoma desde la fase en que quedó. Las specs de R1 a R5 ya existen como borrador.

### 3. Qué hace, fase por fase

| Fase | Quién | Resultado | Tu parte |
|---|---|---|---|
| 1. Specify | coordinator | `spec.md` con casos de prueba concretos | Responder sus preguntas y **aprobar la Puerta 1** |
| 2. Plan | planner | `plan.md` y `tasks.md` (test primero) | **Aprobar la Puerta 2** |
| 3. Implement | implementer | Código y pruebas, tareas marcadas en `tasks.md` | Resolver bloqueos si los reporta |
| 4. Review | reviewer | `review.md` con veredicto `APROBADO` o `CAMBIOS` (máx. 3 rondas) | Nada, salvo que no converja |
| 5. Cierre | coordinator | Resumen, pendientes para el documento técnico | Hacer tu commit |

Los agentes nunca hacen `git add`, `commit` ni `push`: el historial de commits es evidencia del trabajo de cada integrante y lo manejas tú.

### 4. Orden recomendado

R1 → R2 → R3 → R4 → R5. R2 y R4 dependen de los archivos que produce R1 (grafo procesado y asociación lugar → nodo) y de la matriz de tiempos de R2.

### 5. Reglas que el coordinator hace cumplir

- Algoritmos pedidos en **implementación propia**; NetworkX, SciPy y Shapely solo en pruebas de verificación.
- Protocolo experimental (sección 6 del enunciado): misma máquina, solo se mide el algoritmo, 5 repeticiones y mediana, semilla fija, límite de 5 min, resultados en CSV/JSON y gráficas generadas desde ellos.
- Todo uso de IA se registra en `docs/anexo-ia.md` (herramienta, para qué, cómo se verificó).
- Cada integrante debe poder explicar y modificar cualquier parte del código en la sustentación: después de cada requerimiento, repasa el código hasta explicarlo sin ayuda.

### 6. Decisiones pendientes

Las specs marcan con **[DECISIÓN]** lo que el equipo debe confirmar antes de implementar (tabla de velocidades, QuickHull, vecino más cercano, criterio para quitar atractivos del itinerario, etc.). El coordinator las vuelve a preguntar en la Puerta 1.

### 7. Cambios pequeños

Para un typo o renombrar una variable no hace falta el flujo completo: pídeselo directamente y él lo delega al `implementer`.

## Trabajo en equipo

- Commits pequeños y frecuentes, de cada integrante, con mensajes claros.
- Antes de empezar: `git pull`. Al terminar un bloque: `git add`, `git commit` y `git push`.
- El repositorio debe estar compartido con el docente.

## Reproducir R1

Todas las órdenes se corren desde la raíz del repositorio. Se usó Python 3.13.8.

### 1. Entorno

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Comandos, en orden

| Orden | Qué hace | Deja |
|---|---|---|
| `.venv/bin/python -m rutas.r1.descargar` | Descarga con OSMnx las 5 redes crudas (departamento y radios de 2, 5, 10 y 20 km). **Requiere internet** y puede tardar varios minutos. `--help` solo muestra la ayuda. | `data/raw/` (no está en git, se regenera con este comando) y `cache/` |
| `.venv/bin/python -m rutas.r1.construir_red` | Construye la red: pesos en segundos, componente fuertemente conexa, asociación de los 42 lugares al nodo más cercano. Opción `--graphml RUTA` (Plan B): usa el GraphML entregado por el docente en lugar de `data/raw/`. | `data/processed/` (grafo, `lugares_nodos.csv`, `metadatos.json`) y los CSV de tamaños, memoria y velocidades en `results/r1/` |
| `.venv/bin/python -m rutas.r1.medir_componente` | Mide el tiempo de extraer la componente en las 5 redes (5 repeticiones, mediana en ms). | `results/r1/r1_tiempos_componente.csv` y `results/r1/maquina.json` |
| `.venv/bin/python -m rutas.r1.tablas` | Genera las tablas y la gráfica desde los CSV, no a mano. | `results/r1/tablas_r1.md` y `results/r1/r1_tiempos_componente.png` (gráfica) |

Pruebas:

```bash
.venv/bin/python -m pytest -m "not red"   # sin datos descargados
.venv/bin/python -m pytest                # todas; las marcadas `red` necesitan data/processed y data/raw
```

### 3. Notas

- **Reintentos de la descarga.** Ante errores 502/504 el script espera 30, 60, 120 y 240 s y luego se rinde sugiriendo el Plan B. Si Overpass responde 504/429, OSMnx reintenta por su cuenta cada 55 s sin límite: si queda así, corta con Ctrl+C y vuelve a intentar más tarde (la caché `cache/` evita repetir lo ya descargado) o usa el Plan B (`construir_red --graphml RUTA`).
- **Forma del grafo procesado.** Puede estar como `data/processed/grafo_componente.graphml` o `grafo_componente.graphml.gz` (este último si pasa de 100 MB). Hoy es `.graphml` de unos 15 MB.
- **Medición.** Medir con el portátil enchufado y sin otros procesos pesados. Son 5 repeticiones y se reporta la mediana en ms; los resultados quedan en `results/r1/` y las tablas en `results/r1/tablas_r1.md`, generadas desde los CSV.
- **Datos actuales.** Se descargaron el 2026-11-10 (ver `fecha_descarga` en `data/processed/metadatos.json`).

## Reproducir R2

Todas las órdenes se corren desde la raíz del repositorio, con el mismo entorno de R1. **Requisito:** haber hecho R1 (debe existir `data/processed/` con el grafo y `lugares_nodos.csv`).

### Comandos, en orden

| Orden | Qué hace | Deja |
|---|---|---|
| `.venv/bin/python -m rutas.r2.matriz` | Calcula la matriz de tiempos 42×42 (Dijkstra con cola, sin destino, un origen por fila) y su asimetría. No mide tiempos. | `data/processed/matriz_tiempos.csv` y `results/r2/r2_asimetria.json` |
| `.venv/bin/python -m rutas.r2.medir_dijkstra` | Selecciona los pares con semilla 2026 y mide: la versión con cola en el mismo proceso, la lineal en un proceso hijo; 5 repeticiones, mediana en ms. Antes comprueba que las dos versiones coinciden; si no coinciden, no escribe nada. Tarda de 1 a 5 min por el arranque de los procesos hijo. Medir con el portátil enchufado y sin otros procesos pesados. | `results/r2/r2_pares.csv`, `r2_pares.json`, `r2_dijkstra.csv` y `maquina.json` |
| `.venv/bin/python -m rutas.r2.tablas` | Calcula el cociente lineal/cola, la gráfica y las tablas desde los CSV, no a mano. | `results/r2/r2_cociente.csv`, `r2_tiempo_vs_explorados.png` y `tablas_r2.md` |

Pruebas:

```bash
.venv/bin/python -m pytest -m "not red"                 # sin datos descargados
.venv/bin/python -m pytest tests/test_red_real_r2.py    # sobre la red real de R2 (necesita data/processed)
.venv/bin/python -m pytest                              # todas
```

### Notas

- Las pruebas de los casos de la clase usan la copia versionada `tests/datos/red_clase.json`, así que no necesitan datos descargados.
- La semilla de los pares (2026) queda documentada en `results/r2/r2_pares.json`.

## Reproducir R3

Todas las órdenes se corren desde la raíz del repositorio, con el mismo entorno de R1. **Requisito:** haber hecho R1 (debe existir `data/processed/` con el grafo).

### Comandos, en orden

| Orden | Qué hace | Deja |
|---|---|---|
| `.venv/bin/python -m rutas.r3.archivos` | Calcula la envolvente convexa (QuickHull propio) de la red real y la compara con SciPy antes de escribir; si difieren, no escribe nada. No mide tiempos. | `data/processed/envolvente.csv` y `data/processed/envolvente.geojson` (para R5) |
| `.venv/bin/python -m rutas.r3.medir_envolvente` | Mide la envolvente propia frente a SciPy en la red real y en cuadrados de 1 000, 10 000 y 50 000 puntos (semilla 2026, coordenadas en [0, 10⁶)²). Antes comprueba que ambas den los mismos vértices; si no, no escribe nada. 5 repeticiones, mediana en ms. Tarda unos segundos. Medir con el portátil enchufado y sin otros procesos pesados. | `results/r3/r3_envolvente.csv`, `r3_puntos.json` y `maquina.json` |
| `.venv/bin/python -m rutas.r3.tablas` | Genera las tablas y la gráfica desde los CSV, no a mano. | `results/r3/tablas_r3.md` y `r3_envolvente.png` |

Pruebas:

```bash
.venv/bin/python -m pytest -m "not red"                 # sin datos descargados
.venv/bin/python -m pytest tests/test_red_real_r3.py    # sobre la red real de R3 (necesita data/processed)
.venv/bin/python -m pytest                              # todas
.venv/bin/python -m pytest --lento tests/test_envolvente.py   # además, la prueba lenta del peor caso
```

La prueba lenta (`test_peor_caso_2k_4k_sin_recursion_error`, marcador `lento`) **no corre por defecto** en ninguna invocación, ni siquiera con `-m red` o `-m "not red"`; solo con `--lento`. Comprueba el peor caso real de QuickHull: los 1 050 puntos (2^k, 4^k), k = 0 … 1 049, dejan la recursión en profundidad n − 1 (más de 1 000, por encima del límite por defecto de Python), así que sin `sys.setrecursionlimit` fallaría con `RecursionError`. Verifica que los 1 050 sean vértices y los invariantes geométricos. Tarda unos 3 s en este portátil.

### Notas

- Los puntos se pasan a UTM 18N y se redondean con floor(x + 0.5) a enteros, quitando duplicados.
- SciPy recibe un arreglo float64 construido fuera del cronómetro; solo se mide la llamada a `ConvexHull`. Lo mismo para el algoritmo propio: la preparación de puntos queda fuera.
- Los casos de la clase usan la sección R3 de la copia versionada `tests/datos/red_clase.json`, así que no necesitan datos descargados.
- La semilla de los cuadrados (2026) queda documentada en `results/r3/r3_puntos.json`.
