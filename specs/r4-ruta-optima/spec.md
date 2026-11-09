# Ruta óptima de recorrido (TSP asimétrico) — Requerimiento 4
Enunciado: sección 5, Requerimiento 4 (puntos 1 a 5); protocolo en sección 6; formatos en Anexo, Requerimiento 4. Peso: 25 %.
Estado: ☐ spec (borrador, pendiente de aprobación del grupo) · ☐ pruebas · ☐ código · ☐ verificado
Depende de: `r2-dijkstra` (matriz de tiempos asimétrica entre lugares) y `r1-red-vial` (duración de visita de los atractivos).

## Propósito
Dado un lugar de partida y k lugares más, encontrar el recorrido de menor tiempo que los visita todos y regresa a la partida. Se implementan fuerza bruta, Held-Karp (exactos) y una heurística voraz, y se comparan en tiempo y calidad. Se arma además el itinerario de un día.

## Entradas y salidas
**Entradas:** matriz `T` de tiempos en segundos (`T[i][j]` = ir de i a j, asimétrica, diagonal 0); índice de partida `s`; lista de k lugares a visitar (sin repetir, sin incluir `s`); para el itinerario, duración de visita en minutos de cada atractivo.

**Salidas** (las tres funciones comparten firma) `resolver(T, s, lugares) -> (tiempo_total_s, recorrido)`
- `recorrido`: lista `[s, p1, …, pk, s]` (orden de visita, con regreso).
- Held-Karp **devuelve el recorrido**, no solo el tiempo (se reconstruye con una tabla de padres).

**Archivos**
- `results/r4_exactas.csv`: `k, tiempo_fuerza_bruta_ms, tiempo_held_karp_ms, estado_fb, estado_hk` (`estado ∈ {ok, no_completada}`).
- `results/r4_calidad.csv`: `k, instancias, brecha_promedio_pct, brecha_maxima_pct` más el detalle por instancia (`k, semilla, optimo_s, heuristica_s, brecha_pct`).
- `results/r4_itinerario.csv`: `orden, lugar, desplazamiento_min, visita_min, acumulado_h`, con una fila final de regreso y los totales (visitas, desplazamientos, jornada).
- Gráfica `results/r4_tiempo_vs_k.png`: k en x, tiempo (ms) en y, una curva por solución.

## Comportamiento
1. **Fuerza bruta:** prueba las k! permutaciones de los lugares y se queda con la de menor tiempo. Empate: la primera encontrada en orden lexicográfico de índices. **Las permutaciones se generan con un generador propio** (sobre un solo arreglo, O(k) de memoria), sin `itertools.permutations`, porque es un algoritmo de implementación propia (**[DECISIÓN del documento técnico]**). `itertools` solo puede aparecer en las pruebas de verificación.
2. **Subestructura óptima (a justificar antes de implementar Held-Karp):** si el recorrido óptimo que parte de `s`, pasa por el conjunto S y termina en j pasa por i justo antes de j, entonces su tramo hasta i es un camino óptimo sobre S∖{j} que termina en i (argumento de intercambio).
3. **Held-Karp (recurrencia):**
   - `C({j}, j) = T[s][j]`
   - `C(S, j) = min_{i ∈ S∖{j}} ( C(S∖{j}, i) + T[i][j] )` para |S| ≥ 2
   - Óptimo = `min_j ( C(L, j) + T[j][s] )`, con L = todos los lugares.
   Los subconjuntos se representan con una máscara de bits. Se guarda el mejor `i` de cada `(S, j)` para reconstruir el orden.
4. **Heurística voraz: vecino más cercano** (propuesta del documento técnico, **[DECISIÓN, confirmar]**): desde `s`, ir siempre al lugar no visitado con menor `T[actual][·]`; al terminar, volver a `s`. Empate: menor índice. Razón: usa la matriz directamente sin exigir simetría, cuesta O(k²) y se calcula en vivo en la aplicación. Su punto débil: no garantiza calidad. La cota de Rosenkrantz, Stearns y Lewis (1977), (1/2)⌈log₂ n⌉ + 1/2, vale solo para instancias métricas simétricas y esta matriz no es simétrica. Si se cambia de heurística, se actualizan los contraejemplos de los casos 4 y 4b.
5. **Experimentos:** `s` = Armenia; los k lugares se eligen al azar de todo el catálogo con semilla fija (documentada). Exactas: k de 5 a 12, o hasta que una ejecución pase el límite de 5 min; se reporta el mayor k resuelto de cada una.
6. **Calidad de la heurística:** para k ∈ {5, 8, 10, 12}, ≥ 5 instancias por k (semillas distintas, fijas). `brecha = (heurística − óptimo Held-Karp) / óptimo × 100`. Se reporta promedio y máximo.
7. **Itinerario de un día:** `s` por defecto Armenia (`C01`); entre 6 y 8 atractivos; se ordenan con Held-Karp. Duración de la jornada = Σ visitas + Σ desplazamientos (incluido el regreso). Cabe si ≤ 11 h (660 min). Si no cabe, **se quita el atractivo cuya salida ahorre más tiempo total (visita + desplazamientos)**, se recalcula con Held-Karp y se repite hasta que quepa (**[DECISIÓN del documento técnico, confirmar]**); se reporta la duración final. Ojo con el catálogo: A01, A02 y A09 duran 420 min cada uno y A03 300 min, así que con esos atractivos la jornada no cabe y la regla se ejercita casi siempre.
8. **Voraz frente a óptimo:** el informe muestra un ejemplo (caso 4) donde la heurística no es óptima y explica por qué en Dijkstra la elección voraz sí garantiza el óptimo (el invariante de nodos finalizados con pesos ≥ 0) y aquí no (decidir el siguiente lugar sin ver el costo de regreso ni de lo que queda).
9. **Memoria de Held-Karp:** tabla de `k · 2^k` celdas indexada por máscara de bits, con 8 B de costo y 4 B de predecesor por celda (12 B). Con objetos de Python el consumo real es mayor y el informe lo dice. Valores esperados del documento técnico (MB = 10⁶ B): k = 5 → 160 celdas, 0,002; k = 8 → 2 048, 0,025; k = 10 → 10 240, 0,123; k = 12 → 49 152, 0,590. Transiciones de Held-Karp: k = 5 → 170, 8 → 3 600, 12 → 135 192; tramos sumados por fuerza bruta: k = 12 → 6 227 020 800.

## Casos borde
- k = 0 → tiempo 0, recorrido `[s]`.
- k = 1 → `T[s][a] + T[a][s]`, recorrido `[s, a, s]`.
- k = 2 → compara los dos órdenes.
- Dos recorridos con el mismo tiempo → mismo tiempo total; el orden puede diferir (las pruebas comparan tiempos, y que el recorrido sea una permutación válida con ese costo).
- Matriz simétrica → el recorrido inverso cuesta lo mismo; no debe romper nada.
- Un lugar repetido en la lista → error. `s` dentro de la lista → error.
- Un `T[i][j] = inf` (inalcanzable) → el recorrido que lo use no es candidato; si ninguno es posible → error claro.
- Una ejecución pasa de 5 min → se detiene y se reporta `no_completada`; no se omite la fila.
- Ejecución de más de 1 min → se mide una sola vez.

## Casos de prueba
Matriz de 4 lugares, `T[i][j]` = i → j en segundos, partida 0:

|   | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **0** | 0 | 10 | 15 | 20 |
| **1** | 5 | 0 | 9 | 10 |
| **2** | 6 | 13 | 0 | 12 |
| **3** | 8 | 8 | 9 | 0 |

1. Todos los recorridos de [1, 2, 3] (resueltos a mano y comprobados por enumeración): 1-2-3 → 39; **1-3-2 → 35**; 2-1-3 → 46; 2-3-1 → 40; 3-1-2 → 43; 3-2-1 → 47. Óptimo = **35**, recorrido `[0, 1, 3, 2, 0]`.
2. Fuerza bruta y Held-Karp devuelven 35 y el mismo recorrido `[0, 1, 3, 2, 0]`.
3. Asimetría: `T[0][1] = 10 ≠ T[1][0] = 5`; el recorrido inverso `[0, 2, 3, 1, 0]` cuesta 15 + 12 + 8 + 5 = 40 ≠ 35.
4. **Voraz no óptimo:** vecino más cercano da `[0, 1, 2, 3, 0]` = 10 + 9 + 12 + 8 = **39** frente a 35 óptimo: brecha = (39 − 35)/35 = 11,43 %.
5. k = 1 con lugares {0, 1}: 10 + 5 = 15, recorrido `[0, 1, 0]`.
6. k = 2 con lugares {0, 1, 2}: 0-1-2-0 = 10 + 9 + 6 = 25; 0-2-1-0 = 15 + 13 + 5 = 33 → óptimo 25, `[0, 1, 2, 0]`.
7. k = 0 → `(0, [0])`.
8. Matriz con un `inf`: poner `T[1][3] = inf` en la matriz del caso 1 → el óptimo sigue siendo 35 si no usa ese arco (1-3-2 sí lo usa) → el nuevo óptimo es 39 con `[0, 1, 2, 3, 0]`.
9. Propiedad con semilla fija: 100 matrices asimétricas aleatorias con k entre 1 y 8 → fuerza bruta = Held-Karp en el tiempo total; el recorrido de Held-Karp es una permutación válida y su costo recalculado desde `T` es igual al reportado.
10. Voraz ≥ óptimo siempre (la brecha nunca es negativa); si la heurística da el óptimo la brecha es 0.
11. Itinerario, frontera de jornada: 6 atractivos con 60 min de visita (360 min) y desplazamientos que suman 300 min → 660 min = 11 h → **cabe**; con 301 min de desplazamiento → 661 min → **no cabe**, se quita un atractivo y se recalcula.
12. Con la matriz real: Held-Karp con k entre 5 y 8 sobre lugares del catálogo coincide con fuerza bruta (mismo tiempo total).
4b. **Voraz no óptimo (ejemplo a mano del documento técnico, simétrico, sobre una vía):** posiciones en minutos C = −2, A = 0, B = 1, D = 5; partida A. El voraz da A→B→C→D→A = 1 + 3 + 7 + 5 = **16**; un óptimo es A→B→D→C→A = 1 + 4 + 7 + 2 = **14** (brecha 14,3 %). De los 6 recorridos posibles, 4 cuestan 14 y 2 cuestan 16. Verificado por enumeración.
13. Memoria: para k = 12, la tabla de Held-Karp tiene 12 × 4 096 = 49 152 celdas × 12 B = 589 824 B (0,590 MB).
14. Conteos: k = 12 → 12! = 479 001 600 permutaciones y 6 227 020 800 tramos en fuerza bruta; 135 192 transiciones en Held-Karp (una prueba calcula el conteo de transiciones con la fórmula y lo compara con un contador instrumentado, solo en pruebas).
15. Permutaciones propias: para k = 4 el generador produce exactamente las 24 permutaciones distintas, sin repetir, y coincide como conjunto con `itertools.permutations` (solo en la prueba).

## Complejidad esperada
(Fuente y recurrencia en el informe.)
- Fuerza bruta: Θ(k!) permutaciones, cada una O(k) para sumar → O(k · k!) tiempo; memoria O(k).
- Held-Karp: O(k² · 2^k) tiempo; O(k · 2^k) memoria. Recurrencia: `C(S, j)` arriba; hay k·2^k subproblemas y cada uno cuesta O(k).
- Vecino más cercano: O(k²) tiempo, O(k) memoria. No garantiza óptimo; no tiene factor de aproximación constante en TSP asimétrico general.
- Fuentes candidatas: Held y Karp (1962), *A dynamic programming approach to sequencing problems*; Bellman (1962); Cormen et al., *Introduction to Algorithms*, capítulos de programación dinámica y de NP-completitud (TSP); Rosenkrantz, Stearns y Lewis (1977) para heurísticas del viajante.

## Verificación
- Casos 1 a 8 resueltos a mano y comprobados por enumeración.
- Fuerza bruta vs. Held-Karp: mismo tiempo total en todos los k que la fuerza bruta alcance a resolver (exigido por el enunciado).
- Recorrido de Held-Karp: es una permutación de los lugares y su costo, recalculado desde `T`, coincide con el reportado.
- Heurística: brecha ≥ 0 y valor consistente con el óptimo de Held-Karp.

## Medición
- Qué: tiempo de cada solución (solo el cómputo; la matriz ya está cargada y la generación de instancias queda fuera), tiempo vs. k de 5 a 12 o hasta el límite.
- Protocolo: 5 repeticiones y mediana; ejecuciones > 1 min se miden una vez; límite de 5 min → `no_completada` (y se reporta el mayor k resuelto de cada una); semilla fija documentada para elegir lugares; ms; misma máquina (CPU, RAM, SO, versión del lenguaje).
- Calidad: k = 5, 8, 10, 12, ≥ 5 instancias por k, brecha promedio y máxima en %.
- Informe: gráfica de tiempo vs. k, tabla del anexo, y un párrafo que compare el crecimiento medido con k! y 2^k.

## Decisiones
Propuestas del documento técnico, pendientes de confirmar: vecino más cercano; criterio de quitar el atractivo que más tiempo ahorra; generador de permutaciones propio.

Abiertas: tipo de dato real de la tabla en Python (afecta la estimación de memoria; el documento supone 8 B + 4 B por celda).
