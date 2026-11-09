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
