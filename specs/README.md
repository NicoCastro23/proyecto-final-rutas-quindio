# Specs (Spec-Driven Development)

Una carpeta por requerimiento/algoritmo, escrita **antes** del código: `specs/r2-dijkstra/spec.md`, `specs/r4-held-karp/spec.md`, etc. Junto a `spec.md` viven `plan.md`, `tasks.md` y `review.md` (los generan los agentes).

## Plantilla
```
# <Nombre> — Requerimiento <n>
Enunciado: sección/punto del PDF que cubre.
## Propósito
## Entradas y salidas  (tipos, unidades, formato de archivos)
## Comportamiento  (reglas, invariantes, qué cuenta como "nodo explorado", etc.)
## Casos borde  (vacío, un nodo, desconectado, empates, pesos 0, k=0...)
## Casos de prueba  (entrada concreta -> salida esperada, resuelto a mano o con librería de verificación)
## Complejidad esperada  (tiempo y memoria, con fuente)
## Verificación  (contra qué se compara: otra implementación, caso a mano, librería)
## Medición  (qué se mide, repeticiones, semilla, unidad)
```
Estado: ☐ spec · ☐ pruebas · ☐ código · ☐ verificado  (en cada spec, tras la línea de enunciado)
