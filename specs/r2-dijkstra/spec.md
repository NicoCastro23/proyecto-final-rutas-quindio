# Caminos mínimos (Dijkstra y matriz de tiempos) — Requerimiento 2
Enunciado: sección 5, Requerimiento 2 (punto 1 con sus viñetas, matriz de tiempos y verificación); protocolo en sección 6; formatos en Anexo, Requerimiento 2. Peso: 20 % (40 % implementación verificada, 30 % teoría, 30 % experimental).
Estado: ☑ spec (aprobada en Puerta 1, 2026-11-10, con tres ajustes: casos de la clase, frase de la lineal y fuentes) · ☐ pruebas · ☐ código · ☐ verificado
Depende de: `r1-red-vial` (cerrado): `data/processed/grafo_componente.graphml` (peso `travel_time` en s, aristas paralelas conservadas), `data/processed/lugares_nodos.csv`, `rutas.r1.persistencia`, `rutas.r1.aristas.mejor_arista` y `rutas.medicion` (modos en proceso y en proceso hijo).

## Propósito
Implementar dos versiones propias de Dijkstra (mínimo por recorrido lineal y cola de prioridad), verificar que coinciden, medirlas según la sección 6 y calcular la matriz de tiempos entre los 42 lugares del catálogo, que usa R4.

## Entradas y salidas
**Entradas**
- Grafo de la componente cargado con `cargar_grafo_procesado()` (R1). R2 construye **su propia representación indexada** (decisión de la Puerta 2): `ids` = lista de los ids de nodo **ordenados de menor a mayor** (el índice i ∈ 0..V−1 representa al nodo `ids[i]`), `indice` = `dict` id → i, y `adyacencia` = lista de V listas, `adyacencia[i]` = lista de `(j, travel_time)`, con **todas** las aristas del MultiDiGraph (paralelas y autolazos incluidos; coherente con R1). Como los índices siguen el orden de los ids, desempatar por menor índice equivale a desempatar por menor id. Construirla es preparación de datos y queda fuera de la medición. Hoy: V = 8 791, E = 20 132; 133 pares (u, v) con aristas paralelas (máx. 3) y 37 autolazos en 24 nodos distintos.
- `lugares_nodos.csv` (R1): lugar → nodo. T03 y T05 comparten el nodo 2978288220.

**Funciones** (implementación propia; NetworkX solo en pruebas)
- `dijkstra_lineal(adyacencia, origen, destino=None)` y `dijkstra_cola(adyacencia, origen, destino=None)` trabajan con **índices** (origen y destino son índices; la ruta es una lista de índices). Una función envoltorio `consultar(red, id_origen, id_destino, version)` traduce ids ↔ índices para los scripts y R5; la traducción queda fuera de la medición.
  - Con destino → `(tiempo_s, ruta, nodos_explorados)`: `tiempo_s` float (`math.inf` si no es alcanzable); `ruta` lista de nodos origen → destino (vacía si no hay camino); `nodos_explorados` = nodos extraídos por primera vez, incluido el destino.
  - Sin destino → `(dist, pred, nodos_explorados)`: `dist` lista de tamaño V (`math.inf` en los no alcanzados), `pred` lista de tamaño V (`None` en el origen y en los no alcanzados).
- `reconstruir_ruta(pred, origen, destino)` y `detalle_ruta(G, ruta)` → suma de `travel_time` y `length` usando `mejor_arista` de R1 en cada tramo (lo que dibuja R5).

**Archivos** (resultados bajo `results/r2/`; la matriz bajo `data/processed/` porque la usa R4)
- `results/r2/r2_pares.csv`: `origen, destino, tipo (cercano|lejano), municipio_origen, municipio_destino, nodo_origen, nodo_destino` y la semilla en `results/r2/r2_pares.json`.
- `results/r2/r2_dijkstra.csv`: `origen, destino, version, tiempo_viaje_s, nodos_explorados, tiempo_ms` (columnas del Anexo, una fila por consulta y versión; `version ∈ {lineal, cola_prioridad}`), ampliado con `tipo, distancia_m, repeticiones` (columnas pueden ampliarse, no reducirse). `tiempo_viaje_s` y `distancia_m` sin redondear.
- `results/r2/r2_cociente.csv`: `mediana, minimo, maximo` del cociente `tiempo_ms lineal / tiempo_ms cola` en los 10 pares cercanos.
- `results/r2/r2_tiempo_vs_explorados.png`: nodos explorados en x, tiempo (ms) en y, un color y marcador distinto por versión, desde `r2_dijkstra.csv`. Si las dos versiones difieren en órdenes de magnitud, eje y logarítmico, indicado en la etiqueta.
- `results/r2/r2_asimetria.json`: número de pares {i, j} con `|M[i][j] − M[j][i]| > 1e-6`, el par con mayor diferencia y su valor.
- `results/r2/maquina.json` y `results/r2/tablas_r2.md` (tablas generadas desde los CSV).
- `data/processed/matriz_tiempos.csv`: primera fila y primera columna = ids de los 42 lugares en el orden del catálogo; celda (i, j) = segundos de i a j. **Sin redondear**: cada valor con la representación completa del float (`repr`), leído con `float_precision="round_trip"` (decisión del usuario), de modo que la matriz leída del archivo coincide con Dijkstra con destino dentro de 1e-6 s.

## Comportamiento
0. **Inicialización igual en ambas (decisión de la Puerta 2):** las dos versiones crean `dist = [inf] * V`, `pred = [None] * V` y `visitado = [False] * V` (O(V)), y fijan `dist[origen] = 0`. Lo **único** que cambia entre ellas es cómo se busca el siguiente nodo: recorrido lineal o `heapq`. La inicialización O(V) de la cola cuesta microsegundos; el piso grande de la lineal viene de recorrer los V nodos en **cada** extracción, y así lo explica el informe.
1. **Lineal, O(V²).** En cada iteración se recorre **todo** `dist` buscando el no visitado de menor distancia finita (O(V)); si no queda ninguno finito, termina. Hay como máximo V extracciones → O(V²) más O(E) de relajaciones.
2. **Cola de prioridad, O((V + E) log V).** Montículo binario con `heapq` de la biblioteca estándar. `heapq` no permite disminuir una prioridad: como sugiere su documentación («Priority Queue Implementation Notes»), se inserta una entrada nueva y la vieja queda obsoleta; al extraer una entrada de un nodo ya visitado se descarta **sin contarla**. La cola tiene como máximo E + 1 entradas: memoria O(V + E). Con aristas paralelas E ≤ c · V² (c = máx. paralelas por par, 3 aquí), así que log E ≤ 2 log V + log c = O(log V) y la cota se conserva.
3. **Desempate (ambas versiones):** se extrae el nodo de menor `(distancia, índice)` (= menor id, porque los índices siguen el orden de los ids). En `heapq` se logra con entradas `(distancia, índice)`; en la lineal, recorriendo los índices de 0 a V−1 y cambiando de candidato solo si la distancia es estrictamente menor (así gana el menor índice en un empate). Así las dos versiones extraen los nodos en el mismo orden y reportan **los mismos nodos explorados**.
4. **Parada:** con destino, ambas se detienen **al sacar el destino** de la cola (no al descubrirlo). Cada nodo se cuenta como explorado **una sola vez**, la primera vez que sale.
5. **Relajación:** si `dist[u] + w < dist[v]` (estricto), `dist[v] = dist[u] + w` y `pred[v] = u`. Con aristas paralelas gana sola la de menor tiempo; un autolazo nunca mejora (w ≥ 0).
6. **Ruta:** seguir `pred` desde el destino hasta el origen e invertir. El tiempo reportado es del nodo origen al nodo destino; **no incluye** el tramo entre el lugar y su nodo (R1).
7. **Pesos:** se comprueba al construir la lista de adyacencia que todo `travel_time` es finito y ≥ 0; si no, error con la arista culpable (el invariante exige pesos no negativos). Peso 0 se permite.
8. **Matriz de tiempos:** para cada uno de los 42 lugares (en el orden del catálogo), una corrida de `dijkstra_cola` **sin destino** desde su nodo; se leen las distancias a los nodos de los 42 lugares. Diagonal = 0; T03↔T05 = 0 (mismo nodo). No es simétrica. Un `inf` no debería ocurrir (componente fuertemente conexa): si ocurre, error.
9. **Argumentos de correctitud (informe):**
   - *Invariante:* al extraer un nodo u, `dist[u]` es la distancia mínima del origen a u; todos los nodos ya extraídos tienen su distancia final y los demás tienen la mejor distancia usando solo nodos extraídos como intermedios.
   - *Parar en el destino:* al extraerlo, su distancia ya es final por el invariante; seguir no la cambia.
   - *Pesos ≥ 0:* la prueba del invariante usa que alargar un camino no lo abarata; con un peso negativo un nodo extraído podría mejorar después (contraejemplo pequeño en el informe).
   - *Comparación con R4 (punto 5 de R4):* la elección voraz (el menor tentativo) es segura aquí por ese invariante.

## Selección de pares (decisión del usuario)
- Semilla fija **2026**, con `random.Random(2026)`; se documenta en `r2_pares.json`.
- Se descartan los pares cuyo origen y destino caen en el mismo nodo (hoy T03–T05) y los pares repetidos. Los pares son **ordenados** (A→B y B→A son distintos).
- **10 cercanos** (mismo municipio; se miden con ambas versiones): los 12 municipios (todos tienen ≥ 2 lugares) se barajan con la semilla; se recorren en ese orden tomando **un par por municipio en cada vuelta** (origen y destino al azar entre los lugares de ese municipio) hasta completar 10. Con 12 municipios basta una vuelta: 10 municipios distintos.
- **10 lejanos** (municipios distintos; solo cola): al azar con la misma generador, sin repetir pares.
- La versión con cola se mide en los 20 pares; la lineal en los 10 cercanos.

## Casos borde
- Origen = destino → tiempo 0, ruta `[origen]`, explorados 1.
- Destino inalcanzable → `inf`, ruta vacía; explora todo lo alcanzable.
- Arista de peso 0 → permitida. Peso negativo, `NaN` o `inf` → error al construir la adyacencia.
- Aristas paralelas → gana la de menor tiempo; la ruta y `detalle_ruta` usan esa misma arista.
- Autolazo → no cambia nada.
- Empates de distancia → desempate por menor id; ambas versiones dan la misma ruta y los mismos explorados.
- Entrada obsoleta en la cola (B entra con 4 y luego con 3) → B se cuenta una vez.
- Origen o destino que no está en la adyacencia → `KeyError` con mensaje claro.
- Dos lugares en el mismo nodo → tiempo 0 en la matriz; excluidos de los pares medidos.

## Casos de prueba
Grafo dirigido G1 (pesos en s): A→B 4, A→C 1, C→B 2, B→D 1, C→D 5, D→E 3; F aislado. (Verificado con NetworkX.) En las pruebas los nodos son enteros A=1 … F=6 para que el desempate por id sea el mismo que en la red real.

| # | Consulta | Tiempo | Ruta | Explorados (orden) |
|---|---|---|---|---|
| 1 | A→B | 3 | A, C, B | 3 (A, C, B) |
| 2 | A→D | 4 | A, C, B, D | 4 (A, C, B, D) — D entra con 6 y luego con 4: entrada obsoleta |
| 3 | A→E | 7 | A, C, B, D, E | 5 |
| 4 | A→A | 0 | A | 1 |
| 5 | A→F | inf | (vacía) | 5 (A, C, B, D, E) |
| 6 | E→A | inf | (vacía) | 1 (E) |

7. Sin destino, distancias en orden A, B, C, D, E: desde A 0, 3, 1, 4, 7; desde B inf, 0, inf, 1, 4; desde C inf, 2, 0, 3, 6; desde D inf, inf, inf, 0, 3; desde E inf, inf, inf, inf, 0.
8. Peso 0: G1 + B→E 0 → A→E = 3 por A, C, B, E.
9. Peso negativo (A→F −1), `NaN` o `inf` → error al construir la adyacencia.
10. Ambas versiones: mismo tiempo, misma ruta y mismos explorados en 1 a 8.
11. Desempate, G2: A→B 1, A→C 1, B→D 1, C→D 1 (A=1, B=2, C=3, D=4); A→D → tiempo 2, ruta A, B, D, explorados 4 (A, B, C, D) en ambas versiones.
12. Aristas paralelas y autolazo: MultiDiGraph con A→B claves 0 (50 s, 800 m) y 1 (40 s, 900 m), autolazo A→A 5 s, B→A 10 s → A→B = 40 s, ruta A, B; `detalle_ruta` = 40 s y 900 m (la arista de 40 s, vía `mejor_arista`).
13. Propiedad, semilla 2026: 200 grafos dirigidos aleatorios (5 a 30 nodos, pesos enteros 0 a 20, con algunas paralelas y autolazos): ambas versiones coinciden entre sí (tiempo exacto, explorados) y con `networkx.single_source_dijkstra_path_length` (solo en la prueba), para todos los orígenes sin destino y para pares con destino.
14. Red real (`red`): en los 10 pares cercanos, |tiempo lineal − tiempo cola| ≤ 1e-6 s y mismos `nodos_explorados`; en los 20 pares, `detalle_ruta(ruta).travel_time` = `tiempo_s` ± 1e-6 y el tiempo coincide con `nx.dijkstra_path_length(G, o, d, weight="travel_time")` ± 1e-6.
15. Pesos reales (`red`): la adyacencia construida tiene V = 8 791 claves y 20 132 entradas en total, todas finitas y ≥ 0.
16. Matriz (`red`): 42 × 42, ids en el orden del catálogo, diagonal 0, sin `inf`, T03↔T05 = 0, al menos un par asimétrico; leída del CSV, `M[i][j]` = `dijkstra_cola` con destino ± 1e-6 s en una muestra de 20 pares (semilla 2026) y en todos los pares de los 20 medidos; el CSV conserva todos los decimales (re-escribirlo da el mismo archivo byte a byte).
17. Selección de pares: con el catálogo real y semilla 2026, 10 cercanos de 10 municipios distintos, cada uno con origen y destino del mismo municipio y nodos distintos; 10 lejanos de municipios distintos; sin pares repetidos; T03–T05 nunca aparece; misma semilla → mismos pares.
18. Cociente: con un CSV sintético de mediciones, `r2_cociente.csv` da la mediana, el mínimo y el máximo esperados (resueltos a mano).

### Casos de la red de la clase (ajuste 1 de la Puerta 1)
Origen: `estudio/casos_prueba.json` (grafo de la clase de Dijkstra convertido en red dirigida, pesos en minutos, resuelto a mano y verificado con NetworkX 3.7 y SciPy 1.18.1). Como `estudio/` está en `.gitignore`, las pruebas leen una **copia versionada** con solo las secciones `red` y `R2`: `tests/datos/red_clase.json` (mismo contenido, con una nota de origen). Red: nodos 1 a 9, 24 aristas, entre ellas **dos aristas 2→3 (2 y 5 min)**; la componente fuertemente conexa es {1, …, 7} (8 y 9 quedan fuera). Los casos 19 a 23 se corren **sobre la componente 1–7** (adyacencia con las aristas entre esos nodos, paralela incluida) con ambas versiones, y los valores se comprobaron otra vez con un script de verificación independiente y con NetworkX el 2026-11-10:

19. Orden de extracción desde el nodo 1 sin destino: **1, 2, 3, 4, 5, 7, 6** (distancias 0, 1, 3, 4, 5, 8, 9 en ese orden), igual en ambas versiones.
20. Cola desde el nodo 2 sin destino: **7 nodos explorados, 9 extracciones del montículo, 2 entradas obsoletas** descartadas sin contarlas. Para poder probarlo, `dijkstra_cola` lleva un contador interno de extracciones y obsoletas que se puede consultar en las pruebas (p. ej. una variante `dijkstra_cola_con_conteo` o un parámetro `estadisticas=None` que, si se pasa un `dict`, se llena), sin cambiar su resultado ni su firma por defecto. Regla que produce esos números: se inserta en el montículo solo cuando la distancia mejora estrictamente.
21. Nodos explorados con parada desde el nodo 1: destino 2 → 2; 3 → 3; 4 → 4; 5 → 5; 6 → 7; 7 → 6.
22. Arista paralela: d(1, 3) = **3** (1→2 1 min + 2→3 la de 2 min); si se usara la de 5 min daría 6.
23. Matriz 7 × 7 (orden 1 a 7, minutos), igual a `R2.matriz_min.filas` del JSON:
    ```
    1: 0  1  3  4  5  9  8
    2: 1  0  2  5  4  8  9
    3: 3  2  0  7  5  6  9
    4: 4  5  7  0  3  7  4
    5: 5  4  5  3  0  8  7
    6: 13 12 13 11 8  0  3
    7: 16 15 16 14 11 3  0
    ```
    con **9 pares asimétricos**: {1,6}, {1,7}, {2,6}, {2,7}, {3,6}, {3,7}, {4,6}, {4,7}, {5,7}. La función que cuenta la asimetría (`r2_asimetria.json`) da 9 en esta matriz; el par de mayor diferencia es **{4,7} con 10 min** (M[4][7] = 4, M[7][4] = 14); el siguiente es {1,7} con 8.

## Complejidad esperada
- Lineal: O(V²) tiempo (V extracciones × V comparaciones, más O(E) relajaciones), O(V) memoria adicional.
- Cola binaria: O((V + E) log V) tiempo, O(V + E) memoria (hasta E + 1 entradas por inserción perezosa). Con parada temprana el costo real depende de los nodos explorados k y sus aristas: la lineal sigue pagando O(V) por extracción (≈ k · V), la cola ≈ (k + aristas relajadas) · log.
- `heapq`: `heappush`/`heappop` O(log n), montículo binario sobre una lista (documentación de Python 3.13, módulo `heapq`; código en `Lib/heapq.py` con acelerador en C `_heapq`).
- Matriz: 42 corridas sin destino → O(42 · (V + E) log V).
- Fuentes (ajuste 3 de la Puerta 1): E. W. Dijkstra, «A note on two problems in connexion with graphs», *Numerische Mathematik* 1:269–271, 1959; documentación de Python 3.13, módulo `heapq` (complejidad de `heappush`/`heappop` y «Priority Queue Implementation Notes» sobre entradas marcadas como eliminadas); diapositivas de la clase de Dijkstra del curso (de ahí sale la red de los casos 19 a 23). Cormen et al. (sección 24.3) queda **pendiente**: solo se cita si el grupo lo consulta en el libro.

## Verificación
- Casos 1 a 12 resueltos a mano (y G1 contrastado con NetworkX); casos 19 a 23 de la red de la clase, resueltos a mano y comprobados con NetworkX.
- Entre versiones: mismos tiempos (1e-6 s) y mismos explorados en todos los pares medidos con ambas (lo exige el enunciado).
- Contra NetworkX solo en pruebas (casos 13, 14).
- Suma de pesos de la ruta = tiempo reportado (caso 14).

## Medición (sección 6)
- Qué: la llamada completa `dijkstra_*(adyacencia, origen, destino)`, **incluida la inicialización O(V) de `dist`/`pred`** (es parte del algoritmo; decisión del usuario). Construir la adyacencia, cargar archivos y escribir resultados quedan fuera.
- Modos de `rutas.medicion` (decididos en R1): `dijkstra_cola` con `medir_en_proceso`; `dijkstra_lineal` con `medir_en_hijo` (cronómetro dentro del hijo, límite de 5 min → "no completada").
- 5 repeticiones, mediana en **ms**; una sola si pasa de 1 min. `nodos_explorados` y `tiempo_viaje_s` se registran de una corrida (son deterministas).
- Misma máquina para todo R2, portátil enchufado; `maquina.json`.
- Predicción a contrastar: tiempo casi lineal en los nodos explorados para ambas; ambas con un piso pequeño y común por la inicialización O(V) (microsegundos); la lineal con pendiente ∝ V (cada extracción recorre los V nodos, que es su costo dominante); la cola con pendiente ∝ grado · log. El cociente lineal/cola debería crecer con los nodos explorados.
- Reportar mediana, mínimo y máximo del cociente en los 10 pares cercanos y discutir la gráfica.
- Por qué la lineal solo se mide en 10 pares (ajuste 2 de la Puerta 1): el enunciado pide medirla en 10 pares cercanos. En esta red (V = 8 791) una consulta lineal que explore toda la componente haría del orden de V² ≈ 7,7 · 10⁷ comparaciones y tardaría **unos segundos** en Python, no minutos; el aviso del enunciado de que puede tardar varios minutos aplica a redes más grandes. Medirla en los pares lejanos no es necesario ni se pide.

## Pendientes para el documento técnico
Invariante y argumentos de correctitud (punto 9; se pueden ilustrar con la tabla de extracción del caso 19), complejidades con fuentes y costo de `heapq`, tabla de cocientes, gráfica, discusión, asimetría de la matriz (de `r2_asimetria.json`), cómo se verificó. Uso de IA en `docs/anexo-ia.md` (local; versionado pendiente del grupo).

## Decisiones
Puerta 2 (2026-11-10): representación indexada con listas de tamaño V e inicialización O(V) igual en ambas versiones; copia versionada `tests/datos/red_clase.json` de las secciones `red` y `R2` de `estudio/casos_prueba.json`; el implementer calcula la matriz real en T11 (no es medición de tiempo; el usuario la regenera en T16).

Resueltas por el grupo: Python y `heapq`; lista de adyacencia propia con **todas** las aristas (paralelas y autolazos); desempate por `(distancia, índice)` (= menor id); pares con semilla 2026 (10 cercanos del mismo municipio, un par por municipio por vuelta; 10 lejanos de municipios distintos; se descartan pares en el mismo nodo); tolerancia 1e-6 s y mismos nodos explorados entre versiones; matriz guardada sin redondear; inicialización dentro de la medición; lineal medida en proceso hijo y cola en el mismo proceso; resultados en `results/r2/`; no modificar `.gitignore` sin preguntar al usuario.
